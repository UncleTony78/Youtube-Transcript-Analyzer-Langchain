from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from textblob import TextBlob
import os
from dotenv import load_dotenv
import logging
from langsmith.run_helpers import traceable
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google AI and LangSmith
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "soomi-ai"

class TranscriptProcessor:
    def __init__(self):
        # Initialize the LLM with proper configuration
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            max_output_tokens=2048,
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Store video context
        self.video_context = None

    @traceable(name="initial_context_analysis")
    def analyze_video_context(self, metadata):
        """Analyze video metadata to establish initial context."""
        try:
            context_prompt = PromptTemplate(
                input_variables=["title", "channel", "description"],
                template="""Analyze this video's context from its metadata:
                Title: {title}
                Channel: {channel}
                Description: {description}
                
                Provide a brief analysis of what this video is likely about and what key themes or topics to look for in the transcript."""
            )
            
            chain = LLMChain(llm=self.llm, prompt=context_prompt)
            response = chain.invoke({
                "title": metadata.get('title', ''),
                "channel": metadata.get('channel_title', ''),
                "description": metadata.get('description', '')
            })
            
            self.video_context = response['text']
            return self.video_context
        except Exception as e:
            logger.error(f"Error analyzing video context: {str(e)}")
            return None

    def prepare_transcript(self, transcript_data):
        """Convert transcript data to text and split into chunks."""
        try:
            # Extract text from transcript
            transcript_text = " ".join([item['text'] for item in transcript_data])
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(transcript_text)
            return chunks
        except Exception as e:
            logger.error(f"Error preparing transcript: {str(e)}")
            return None

    def analyze_sentiment(self, text):
        """Perform sentiment analysis on text."""
        try:
            sentiment = TextBlob(text).sentiment
            return {
                'polarity': sentiment.polarity,
                'subjectivity': sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return None

    @traceable(name="summarize_chunk")
    def summarize_chunk(self, chunk, chunk_index, total_chunks):
        """Generate a context-aware summary for a chunk of text."""
        try:
            summary_prompt = PromptTemplate(
                input_variables=["context", "chunk", "chunk_index", "total_chunks", "text"],
                template="""Context: {context}
                This is chunk {chunk_index} of {total_chunks} from the transcript.
                
                Given this context and position in the transcript, summarize the following text, focusing on how it relates to the video's main themes:
                
                {text}"""
            )
            
            chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            response = chain.invoke({
                "context": self.video_context,
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "text": chunk
            })
            return response['text']
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None

    @traceable(name="extract_key_points")
    def extract_key_points(self, chunk, chunk_index, total_chunks):
        """Extract context-aware key points from a chunk of text."""
        try:
            key_points_prompt = PromptTemplate(
                input_variables=["context", "chunk_index", "total_chunks", "text"],
                template="""Context: {context}
                This is chunk {chunk_index} of {total_chunks} from the transcript.
                
                Given this context and position in the transcript, extract 3-5 key points from this text that are most relevant to the video's themes:
                
                {text}"""
            )
            
            chain = LLMChain(llm=self.llm, prompt=key_points_prompt)
            response = chain.invoke({
                "context": self.video_context,
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "text": chunk
            })
            return response['text']
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return None

    @traceable(name="generate_final_summary")
    def generate_final_summary(self, chunk_results):
        """Generate a comprehensive final summary based on all chunk analyses."""
        try:
            # Combine all summaries and key points
            all_summaries = "\n".join([f"Chunk {i+1} Summary: {r['summary']}\nKey Points: {r['key_points']}"
                                     for i, r in enumerate(chunk_results)])
            
            final_summary_prompt = PromptTemplate(
                input_variables=["context", "summaries"],
                template="""Context of the video: {context}

                Based on the analysis of all transcript chunks:
                {summaries}
                
                Provide a comprehensive summary of the entire video that:
                1. Captures the main narrative or argument
                2. Highlights the most important points across all chunks
                3. Shows how these points connect to the video's overall context
                4. Identifies any progression or development of ideas throughout the video"""
            )
            
            chain = LLMChain(llm=self.llm, prompt=final_summary_prompt)
            response = chain.invoke({
                "context": self.video_context,
                "summaries": all_summaries
            })
            return response['text']
        except Exception as e:
            logger.error(f"Error generating final summary: {str(e)}")
            return None

    @traceable(name="process_transcript")
    def process_transcript(self, video_data):
        """Process the entire transcript with context awareness."""
        try:
            # First analyze video context from metadata
            self.video_context = self.analyze_video_context(video_data['metadata'])
            
            # Prepare transcript chunks
            chunks = self.prepare_transcript(video_data['transcript'])
            if not chunks:
                return None

            total_chunks = len(chunks)
            chunk_results = []
            
            # Process each chunk with context
            for i, chunk in enumerate(chunks, 1):
                chunk_analysis = {
                    'text': chunk,
                    'summary': self.summarize_chunk(chunk, i, total_chunks),
                    'sentiment': self.analyze_sentiment(chunk),
                    'key_points': self.extract_key_points(chunk, i, total_chunks)
                }
                chunk_results.append(chunk_analysis)

            # Generate final comprehensive summary
            final_summary = self.generate_final_summary(chunk_results)
            
            return {
                'context_analysis': self.video_context,
                'chunk_analyses': chunk_results,
                'final_summary': final_summary
            }
            
        except Exception as e:
            logger.error(f"Error in process_transcript: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    from transcript_service import YouTubeService
    
    # Initialize services
    youtube_service = YouTubeService()
    processor = TranscriptProcessor()
    
    # Get video data
    video_url = input("Enter YouTube video URL: ")
    video_data = youtube_service.get_video_data(video_url)
    
    if video_data and video_data['transcript']:
        # Process transcript
        results = processor.process_transcript(video_data)
        
        if results:
            print("\nAnalysis Results:")
            print(f"Context Analysis: {results['context_analysis']}")
            for i, chunk_result in enumerate(results['chunk_analyses'], 1):
                print(f"\nChunk {i}:")
                print(f"Summary: {chunk_result['summary']}")
                print(f"Sentiment: {chunk_result['sentiment']}")
                print(f"Key Points: {chunk_result['key_points']}")
            print(f"\nFinal Summary: {results['final_summary']}")
        else:
            print("Failed to process transcript")
