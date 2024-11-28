"""
Main interface for the YouTube Video Insight Engine.
Provides high-level functions for video analysis and interaction.
"""

from typing import Dict, Any, List
from insight_engine import VideoInsightEngine
from transcript_service import YouTubeService
from analysis_utils import format_timestamp, deduplicate_insights
import json

class VideoAnalyzer:
    def __init__(self):
        """Initialize the video analyzer with required services."""
        self.youtube_service = YouTubeService()
        self.insight_engine = VideoInsightEngine()
        self.current_video_data = None

    def analyze_video(self, video_url: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a YouTube video.
        
        Args:
            video_url: URL of the YouTube video
            
        Returns:
            Dictionary containing analysis results
        """
        # Get video data
        self.current_video_data = self.youtube_service.get_video_data(video_url)
        
        # Store in vector database
        self.insight_engine.store_video_content(self.current_video_data)
        
        # Perform analysis
        analysis_results = {
            "metadata": self.current_video_data['metadata'],
            "golden_nuggets": self.insight_engine.extract_golden_nuggets(self.current_video_data),
            "summary": self.insight_engine.generate_comprehensive_summary(self.current_video_data),
            "fact_checks": self.insight_engine.fact_check_content(self.current_video_data)
        }
        
        return self._format_analysis_results(analysis_results)

    def chat_with_video(self, question: str) -> str:
        """
        Interactive chat about the video content.
        
        Args:
            question: User's question about the video
            
        Returns:
            AI-generated response
        """
        if not self.current_video_data:
            raise ValueError("No video has been analyzed yet. Please analyze a video first.")
        
        chat_interface = self.insight_engine.create_chat_interface()
        return chat_interface({"question": question})

    def get_segment_context(self, timestamp: float, context_window: int = 30) -> Dict[str, Any]:
        """
        Get context around a specific timestamp.
        
        Args:
            timestamp: Time in seconds
            context_window: Window size in seconds
            
        Returns:
            Dictionary containing context information
        """
        if not self.current_video_data:
            raise ValueError("No video has been analyzed yet. Please analyze a video first.")
        
        transcript = self.current_video_data['transcript']
        relevant_segments = []
        
        for segment in transcript:
            if (segment['start'] >= timestamp - context_window and 
                segment['start'] <= timestamp + context_window):
                relevant_segments.append(segment)
        
        return {
            'timestamp': format_timestamp(timestamp),
            'context': ' '.join([s['text'] for s in relevant_segments]),
            'segments': relevant_segments
        }

    def export_analysis(self, filepath: str) -> None:
        """
        Export analysis results to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
        """
        if not self.current_video_data:
            raise ValueError("No video has been analyzed yet. Please analyze a video first.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self._format_analysis_results(self.current_video_data), f, indent=2)

    def _format_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format analysis results for output.
        
        Args:
            results: Raw analysis results
            
        Returns:
            Formatted results dictionary
        """
        formatted = {
            "metadata": {
                "title": results["metadata"]["title"],
                "channel": results["metadata"]["channel_title"],
                "video_id": results["metadata"]["video_id"],
                "duration": format_timestamp(results["metadata"]["duration"])
            },
            "analysis": {
                "summary": results.get("summary", {}),
                "golden_nuggets": deduplicate_insights(results.get("golden_nuggets", [])),
                "fact_checks": results.get("fact_checks", [])
            }
        }
        
        return formatted

# Example usage
if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    
    # Analyze a video
    video_url = "https://www.youtube.com/watch?v=example"
    results = analyzer.analyze_video(video_url)
    
    # Print analysis results
    print("Video Analysis Results:")
    print(json.dumps(results, indent=2))
    
    # Chat with the video
    response = analyzer.chat_with_video("What are the main points discussed?")
    print("\nChat Response:")
    print(response)
    
    # Get context for a specific timestamp
    context = analyzer.get_segment_context(120)  # Get context at 2 minutes
    print("\nContext at 2:00:")
    print(context['context'])
