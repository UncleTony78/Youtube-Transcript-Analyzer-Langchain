"""
Test script to demonstrate the full video analysis pipeline with LangChain and Pinecone integration.
"""

from src.insight_engine import VideoInsightEngine
from src.transcript_service import YouTubeService
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize services
    youtube_service = YouTubeService()
    insight_engine = VideoInsightEngine()
    
    # Test video (Friendship and Mental Health)
    video_url = "https://www.youtube.com/watch?v=CNBxIhxHHxM"
    
    try:
        # Extract video ID and get metadata
        video_id = youtube_service.extract_video_id(video_url)
        metadata = youtube_service.get_video_metadata(video_id)
        
        if not metadata:
            logger.error("Failed to get video metadata")
            return
            
        # Get transcript
        transcript = youtube_service.get_transcript(video_id)
        if not transcript:
            logger.error("Failed to get video transcript")
            return
            
        logger.info("Successfully retrieved video transcript and metadata")
        
        # Process through insight engine
        logger.info("Processing transcript through LangChain and storing in Pinecone...")
        analysis_results = insight_engine.analyze_transcript(transcript, metadata)
        
        # Print results
        print("\n=== Analysis Results ===")
        print("\nGolden Nuggets:")
        pprint(analysis_results["golden_nuggets"])
        
        print("\nSummary:")
        print(analysis_results["summary"])
        
        # Test vector similarity search
        print("\n=== Testing Vector Similarity Search ===")
        queries = [
            "How does friendship impact mental health?",
            "What are the key benefits of maintaining friendships?",
            "How can we prioritize friendships in our busy lives?"
        ]
        
        for query in queries:
            print(f"\nResults for query: '{query}'")
            insights = insight_engine.query_video_insights(query, video_id=video_id)
            for i, insight in enumerate(insights, 1):
                print(f"\n{i}. Content (Score: {insight['score']:.3f}):")
                print(f"   Timestamp: {insight['timestamp']:.2f}s")
                print(f"   {insight['content']}")
            
        # Test chat interface
        print("\n=== Testing Chat Interface ===")
        chat_chain = insight_engine.create_chat_interface()
        
        test_questions = [
            "What is the relationship between friendship and mental well-being?",
            "How can leaders promote a culture of friendship in the workplace?",
            "What are the consequences of neglecting friendships?"
        ]
        
        for question in test_questions:
            print(f"\nQ: {question}")
            response = chat_chain({"question": question})
            print(f"A: {response['answer']}")
            
    except Exception as e:
        logger.error(f"Error during pipeline test: {str(e)}")
        raise

if __name__ == "__main__":
    main()
