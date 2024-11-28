"""
Video Insight Engine - Core analysis and processing module.
Handles video content analysis, storage, and interactive querying.
"""

from langchain.chains import LLMChain, SequentialChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.embeddings import VertexAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import GoogleGenerativeAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import pinecone
from typing import List, Dict, Any
import json
import os

class VideoInsightEngine:
    def __init__(self):
        """Initialize the Video Insight Engine with necessary components."""
        # Initialize LLM
        self.llm = GoogleGenerativeAI(model="gemini-pro")
        
        # Initialize embeddings
        self.embeddings = VertexAIEmbeddings(model_name="textembedding-gecko")
        
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENV')
        )
        self.index_name = "youtube-transcripts"
        
        # Initialize memory for chat
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    def store_video_content(self, video_data: Dict[str, Any]) -> None:
        """
        Store video transcript and metadata in vector database.
        
        Args:
            video_data: Dictionary containing video transcript and metadata
        """
        transcript_chunks = video_data['transcript']
        metadata = video_data['metadata']
        
        texts = [chunk['text'] for chunk in transcript_chunks]
        metadatas = [{
            'video_id': metadata['video_id'],
            'timestamp': chunk['start'],
            'duration': chunk['duration'],
            'title': metadata['title'],
            'channel': metadata['channel_title']
        } for chunk in transcript_chunks]
        
        self.vectorstore = Pinecone.from_texts(
            texts=texts,
            embedding=self.embeddings,
            index_name=self.index_name,
            metadatas=metadatas
        )

    def extract_golden_nuggets(self, video_data: Dict[str, Any]) -> List[Dict]:
        """
        Extract key insights and golden nuggets from the video.
        
        Args:
            video_data: Dictionary containing video content and metadata
            
        Returns:
            List of dictionaries containing golden nuggets
        """
        nuggets_prompt = PromptTemplate(
            template="""
            Analyze this video segment and extract the most valuable insights (golden nuggets).
            Consider practical advice, unique perspectives, and actionable takeaways.
            
            Video Context: {video_context}
            Segment: {segment}
            
            Extract golden nuggets in this format:
            1. [Nugget Title]: [Brief explanation]
            
            For each nugget, also provide:
            - Relevance (Why this matters)
            - Actionability (How to apply this)
            - Source Context (Timestamp and surrounding context)
            """,
            input_variables=["video_context", "segment"]
        )
        
        nuggets_chain = LLMChain(
            llm=self.llm,
            prompt=nuggets_prompt,
            output_key="golden_nuggets"
        )
        
        results = []
        for chunk in self._get_meaningful_chunks(video_data):
            nuggets = nuggets_chain.run(
                video_context=video_data['metadata'],
                segment=chunk
            )
            results.append(nuggets)
            
        return self._consolidate_nuggets(results)

    def generate_comprehensive_summary(self, video_data: Dict[str, Any]) -> Dict:
        """
        Generate a detailed, structured summary of the video.
        
        Args:
            video_data: Dictionary containing video content and metadata
            
        Returns:
            Dictionary containing structured summary
        """
        summary_prompt = PromptTemplate(
            template="""
            Create a comprehensive summary of this video content.
            
            Video Metadata:
            {metadata}
            
            Content to Summarize:
            {content}
            
            Provide a structured analysis including:
            1. Main Themes and Key Points
            2. Narrative Structure and Flow
            3. Key Arguments and Evidence
            4. Practical Applications
            5. Notable Quotes or Statements
            6. Areas for Further Exploration
            
            Format the response as a structured JSON object.
            """,
            input_variables=["metadata", "content"]
        )
        
        summary_chain = LLMChain(
            llm=self.llm,
            prompt=summary_prompt,
            output_key="structured_summary"
        )
        
        return json.loads(summary_chain.run(
            metadata=video_data['metadata'],
            content=self._get_full_content(video_data)
        ))

    def fact_check_content(self, video_data: Dict[str, Any]) -> List[Dict]:
        """
        Identify and fact-check claims made in the video.
        
        Args:
            video_data: Dictionary containing video content and metadata
            
        Returns:
            List of dictionaries containing fact-check results
        """
        fact_check_prompt = PromptTemplate(
            template="""
            Analyze this video segment and:
            1. Identify specific claims that need verification
            2. Evaluate the evidence provided
            3. Flag potential misinformation
            4. Suggest reliable sources for verification
            
            Segment: {segment}
            
            Provide analysis in this format:
            - Claim: [Specific claim made]
            - Context: [When/how it was mentioned]
            - Evidence Provided: [What evidence was given]
            - Verification Status: [Verified/Needs Verification/Potentially Incorrect]
            - Recommended Sources: [Where to verify]
            """,
            input_variables=["segment"]
        )
        
        fact_check_chain = LLMChain(
            llm=self.llm,
            prompt=fact_check_prompt,
            output_key="fact_checks"
        )
        
        results = []
        for chunk in self._get_meaningful_chunks(video_data):
            checks = fact_check_chain.run(segment=chunk)
            results.append(checks)
            
        return self._consolidate_fact_checks(results)

    def create_chat_interface(self) -> ConversationalRetrievalChain:
        """
        Create an interactive chat interface for querying video insights.
        
        Returns:
            ConversationalRetrievalChain for interactive querying
        """
        # Create a context-aware retriever
        compressor = LLMChainExtractor.from_llm(self.llm)
        compression_retriever = ContextualCompressionRetriever(
            base_retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            ),
            doc_compressor=compressor
        )
        
        # Custom prompt for chat responses
        qa_prompt = PromptTemplate(
            template="""
            You are an AI assistant helping users understand video content.
            Use the following context and chat history to provide detailed,
            accurate responses. Always cite specific parts of the video
            (with timestamps) when relevant.

            Context: {context}
            Chat History: {chat_history}
            Question: {question}

            Provide a response that:
            1. Directly answers the question
            2. References relevant video segments
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

    def _get_meaningful_chunks(self, video_data: Dict[str, Any]) -> List[str]:
        """
        Get semantically meaningful chunks of the transcript.
        
        Args:
            video_data: Dictionary containing video content
            
        Returns:
            List of meaningful content chunks
        """
        # TODO: Implement smart chunking logic
        transcript = video_data['transcript']
        chunk_size = 5  # Number of transcript segments per chunk
        
        chunks = []
        current_chunk = []
        
        for segment in transcript:
            current_chunk.append(segment['text'])
            if len(current_chunk) >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:  # Add remaining segments
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def _consolidate_nuggets(self, nuggets: List[Dict]) -> List[Dict]:
        """
        Consolidate and deduplicate golden nuggets.
        
        Args:
            nuggets: List of extracted nuggets
            
        Returns:
            List of consolidated nuggets
        """
        # TODO: Implement deduplication and consolidation logic
        return nuggets

    def _get_full_content(self, video_data: Dict[str, Any]) -> str:
        """
        Get full video content in a processable format.
        
        Args:
            video_data: Dictionary containing video content
            
        Returns:
            String containing full content
        """
        return ' '.join([segment['text'] for segment in video_data['transcript']])

    def _consolidate_fact_checks(self, checks: List[Dict]) -> List[Dict]:
        """
        Consolidate and organize fact checks.
        
        Args:
            checks: List of fact check results
            
        Returns:
            List of consolidated fact checks
        """
        # TODO: Implement fact check consolidation logic
        return checks
