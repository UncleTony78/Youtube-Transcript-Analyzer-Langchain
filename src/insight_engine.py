"""
Video Insight Engine - Core analysis and processing module.
Handles video content analysis, storage, and interactive querying.
"""

from typing import List, Dict, Any
import json
import os
from dotenv import load_dotenv
import re
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone as LangChainPinecone
from langchain.retrievers import ParentDocumentRetriever
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.retrievers.document_compressors import LLMChainExtractor
from pinecone import Pinecone
import google.generativeai as genai

# Load environment variables
load_dotenv()

class VideoInsightEngine:
    def __init__(self):
        """Initialize the Video Insight Engine with necessary components."""
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize embeddings (using a model with 1024 dimensions to match Pinecone)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en-v1.5"
        )
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = self.pc.Index(os.getenv('PINECONE_INDEX', 'youtube-video-analysis'))
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize memory for chat
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def _process_transcript_through_langchain(self, transcript: List[Dict[str, Any]], metadata: Dict[str, Any]) -> List[Document]:
        """Process transcript through LangChain and prepare for Pinecone storage."""
        # Combine transcript segments into documents with metadata
        documents = []
        for chunk in transcript:
            doc = Document(
                page_content=chunk['text'],
                metadata={
                    'video_id': metadata.get('video_id', ''),
                    'timestamp': chunk['start'],
                    'duration': chunk['duration'],
                    'title': metadata.get('title', ''),
                    'channel': metadata.get('channel_title', '')
                }
            )
            documents.append(doc)
        
        # Split documents into smaller chunks if needed
        split_docs = []
        for doc in documents:
            splits = self.text_splitter.split_documents([doc])
            split_docs.extend(splits)
        
        return split_docs
        
    def store_video_content(self, transcript: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
        """Store video transcript and metadata in Pinecone through LangChain."""
        # Process transcript through LangChain
        documents = self._process_transcript_through_langchain(transcript, metadata)
        
        # Convert documents to vectors using embeddings
        vectors = []
        for i, doc in enumerate(documents):
            vector_id = f"{metadata.get('video_id', uuid.uuid4().hex)}_{i}"
            embedding = self.embeddings.embed_documents([doc.page_content])[0]
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    **doc.metadata,
                    "content": doc.page_content
                }
            })
        
        # Store vectors in Pinecone in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(
                vectors=batch,
                namespace=f"video_{metadata.get('video_id', 'default')}"
            )
        
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown and code block formatting."""
        # Remove markdown code block formatting
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        # Remove any non-JSON text before or after
        try:
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                response = response[start:end]
        except:
            pass
        return response.strip()
        
    def analyze_transcript(self, transcript: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze video transcript to extract insights."""
        # First store the content in Pinecone through LangChain
        if metadata:
            self.store_video_content(transcript, metadata)
        
        # Combine transcript segments into full text
        full_text = " ".join([segment['text'] for segment in transcript])
        
        # Extract golden nuggets
        nuggets_prompt = PromptTemplate(
            template="""System: You are an AI trained to analyze video transcripts and extract valuable insights. You must respond with ONLY a JSON array containing the insights, with no additional text or formatting.
            
            Analyze this transcript and identify the key insights or "golden nuggets".
            
            Transcript:
            {transcript}
            
            Extract 3-5 key insights and format them as a JSON array with each object having:
            - "title": A concise title for the insight
            - "explanation": A clear explanation of the insight
            - "relevance": Why this insight is valuable or important
            - "timestamp": Approximate timestamp from the transcript
            """,
            input_variables=["transcript"]
        )
        
        nuggets_chain = LLMChain(llm=self.llm, prompt=nuggets_prompt)
        nuggets_result = nuggets_chain.run(transcript=full_text)
        
        try:
            # Clean the response before parsing
            cleaned_result = self._clean_json_response(nuggets_result)
            golden_nuggets = json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            print(f"Failed to parse nuggets JSON: {nuggets_result}")
            print(f"Error: {str(e)}")
            golden_nuggets = []
            
        # Generate summary
        summary_prompt = PromptTemplate(
            template="""You are an AI trained to create comprehensive video summaries.
            
            Create a clear and insightful summary of this video transcript.
            
            Transcript:
            {transcript}
            
            Focus on:
            1. Main themes and key points
            2. Notable quotes or statements
            3. Overall message and purpose
            
            Provide a well-structured summary that captures the essence of the content.""",
            input_variables=["transcript"]
        )
        
        summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        summary = summary_chain.run(transcript=full_text)
        
        return {
            "golden_nuggets": golden_nuggets,
            "summary": summary,
            "metadata": metadata or {}
        }

    def query_video_insights(self, query: str, video_id: str = None, top_k: int = 3) -> List[Dict]:
        """Query video insights from Pinecone."""
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Prepare query parameters
        query_params = {
            "vector": query_embedding,
            "top_k": top_k,
            "include_values": True,
            "include_metadata": True
        }
        
        # Add namespace filter if video_id is provided
        if video_id:
            query_params["namespace"] = f"video_{video_id}"
        
        # Query Pinecone
        results = self.index.query(**query_params)
        
        # Format results
        insights = []
        for match in results.matches:
            insights.append({
                "content": match.metadata.get("content", ""),
                "timestamp": match.metadata.get("timestamp", 0),
                "title": match.metadata.get("title", ""),
                "score": match.score
            })
        
        return insights

    def create_chat_interface(self) -> ConversationalRetrievalChain:
        """Create an interactive chat interface for querying video insights."""
        # Create a context-aware retriever using LangChain's Pinecone integration
        vectorstore = LangChainPinecone(
            self.index,
            self.embeddings,
            "content"  # text key field in metadata
        )
        
        # Create the base retriever
        base_retriever = vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )
        
        # Create the compressor
        compressor = LLMChainExtractor.from_llm(self.llm)
        
        # Create the compression retriever
        compression_retriever = ContextualCompressionRetriever(
            base_retriever=base_retriever,
            base_compressor=compressor,
            search_kwargs={"k": 4}
        )
        
        # Custom prompt for chat responses
        qa_prompt = PromptTemplate(
            template="""You are an AI assistant helping users understand video content.
            Use the following context and chat history to provide detailed responses.
            
            Context: {context}
            Chat History: {chat_history}
            Question: {question}

            Provide a response that:
            1. Directly answers the question
            2. References specific content with timestamps
            3. Suggests related topics from the video
            4. Encourages deeper exploration
            """,
            input_variables=["context", "chat_history", "question"]
        )
        
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=compression_retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": qa_prompt}
        )

    def generate_insights(self, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights from the video transcript.
        
        Args:
            transcript: List of transcript segments
            
        Returns:
            List of insights with titles, explanations, and timestamps
        """
        # Combine transcript segments into full text
        full_text = " ".join([segment['text'] for segment in transcript])
        
        # Create prompt for insight generation
        prompt = PromptTemplate(
            template="""You are an AI trained to analyze video transcripts and extract valuable insights.
            
            Analyze this transcript and identify the key insights:
            
            {text}
            
            Generate 3-5 key insights. For each insight, provide:
            1. A clear and concise title
            2. A detailed explanation
            3. Why it's important or valuable
            4. The relevant context from the transcript
            
            Format your response as a JSON array of objects with these fields:
            - title: string
            - explanation: string
            - importance: string
            - context: string
            
            Focus on the most significant and actionable insights.""",
            input_variables=["text"]
        )
        
        # Create chain for insight generation
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Generate insights
        response = chain.run(text=full_text)
        
        # Clean and parse response
        try:
            cleaned_response = self._clean_json_response(response)
            insights = json.loads(cleaned_response)
            return insights
        except json.JSONDecodeError:
            # If parsing fails, return a basic insight
            return [{
                "title": "Transcript Analysis",
                "explanation": "The transcript has been processed but insights could not be structured properly.",
                "importance": "Further analysis may be needed.",
                "context": "Full transcript available in storage."
            }]
