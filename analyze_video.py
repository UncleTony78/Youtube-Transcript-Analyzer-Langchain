import os
from dotenv import load_dotenv
from src.transcript_service import YouTubeService
from src.insight_engine import VideoInsightEngine
import json

def main():
    # Load environment variables
    load_dotenv()
    
    # Set Google API key for Gemini
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
    
    # Initialize services
    youtube_service = YouTubeService()
    insight_engine = VideoInsightEngine()
    
    # Get transcript
    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    transcript = youtube_service.get_transcript(video_id)
    
    if transcript:
        # Analyze transcript
        print("\nAnalyzing transcript...")
        results = insight_engine.analyze_transcript(transcript)
        
        # Print results in a readable format
        print("\n=== Video Analysis Results ===\n")
        
        print("Summary:")
        print("-" * 50)
        print(results['summary'])
        print("\n")
        
        print("Golden Nuggets:")
        print("-" * 50)
        for i, nugget in enumerate(results['golden_nuggets'], 1):
            print(f"\n{i}. {nugget['title']}")
            print(f"Explanation: {nugget['explanation']}")
            print(f"Relevance: {nugget['relevance']}")
            print(f"Timestamp: {nugget['timestamp']}")
    else:
        print("Failed to get transcript")

if __name__ == "__main__":
    main()
