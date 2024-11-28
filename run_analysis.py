"""
Script to run video analysis and display results.
"""

import os
from dotenv import load_dotenv
from src.main import VideoAnalyzer

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize analyzer
    analyzer = VideoAnalyzer()
    
    # Example video URL
    video_url = "https://www.youtube.com/watch?v=CNBxIhxHHxM"
    
    print("\n=== Starting Video Analysis ===\n")
    
    try:
        # Get video insights
        results = analyzer.analyze_video(video_url)
        
        print("\n=== Analysis Results ===\n")
        print("1. Video Information:")
        print(f"Title: {results['metadata']['title']}")
        print(f"Channel: {results['metadata']['channel_title']}")
        print(f"Duration: {results['metadata']['duration']} seconds")
        
        print("\n2. Golden Nuggets:")
        for i, nugget in enumerate(results['golden_nuggets'], 1):
            print(f"\nNugget {i}:")
            print(f"Title: {nugget['title']}")
            print(f"Explanation: {nugget['explanation']}")
            print(f"Relevance: {nugget['relevance']}")
            print(f"Timestamp: {nugget['timestamp']}")
        
        print("\n3. Summary:")
        print(results['summary'])
        
        print("\n4. Key Facts:")
        for i, fact in enumerate(results['fact_checks'], 1):
            print(f"\nFact {i}:")
            print(f"Statement: {fact['statement']}")
            print(f"Verification: {fact['verification']}")
            print(f"Confidence: {fact['confidence']}")
        
        print("\n=== Analysis Complete ===\n")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")

if __name__ == "__main__":
    main()
