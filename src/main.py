"""
Main interface for the YouTube Video Insight Engine.
Provides high-level functions for video analysis and interaction.
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from typing import Dict, Any, List
from dotenv import load_dotenv
import os
import json
from datetime import datetime

from .insight_engine import VideoInsightEngine
from .transcript_service import YouTubeService
from .analysis_utils import format_timestamp, deduplicate_insights

class VideoAnalyzer:
    def __init__(self):
        """Initialize the video analyzer with required services."""
        load_dotenv()
        self.youtube_service = YouTubeService()
        self.insight_engine = VideoInsightEngine()
        self.current_video_data = None
        self.current_video_metadata = None
        self._cache = {}

    def get_transcript(self, video_url: str) -> Dict[str, Any]:
        """Fetch just the transcript and metadata for a video."""
        try:
            # Check cache first
            if video_url in self._cache and 'transcript' in self._cache[video_url]:
                return self._cache[video_url]

            video_data = self.youtube_service.get_video_data(video_url)
            if not video_data:
                raise ValueError(f"Could not fetch video data for URL: {video_url}")
                
            self.current_video_data = video_data['transcript']
            self.current_video_metadata = video_data['metadata']
            self.current_video_metadata.update({
                'url': video_url,
                'analysis_timestamp': datetime.now().isoformat()
            })
            
            result = {
                'transcript': self.current_video_data,
                'metadata': self.current_video_metadata
            }

            # Cache the result
            if video_url not in self._cache:
                self._cache[video_url] = {}
            self._cache[video_url].update(result)
            
            return result
        except Exception as e:
            raise ValueError(f"Error fetching transcript: {str(e)}")

    def analyze_sentiment(self, video_url: str) -> Dict[str, Any]:
        """Analyze sentiment separately for faster processing."""
        try:
            # Ensure we have the transcript
            if not self.current_video_data:
                self.get_transcript(video_url)

            # Process sentiment analysis
            return self.insight_engine.analyze_sentiment(self.current_video_data)
        except Exception as e:
            raise ValueError(f"Error analyzing sentiment: {str(e)}")

    def extract_key_points(self, video_url: str) -> List[str]:
        """Extract key points separately for faster processing."""
        try:
            # Ensure we have the transcript
            if not self.current_video_data:
                self.get_transcript(video_url)

            # Extract key points
            return self.insight_engine.extract_key_points(self.current_video_data)
        except Exception as e:
            raise ValueError(f"Error extracting key points: {str(e)}")

    def analyze_video(self, video_url: str) -> Dict[str, Any]:
        """Full video analysis (kept for compatibility)."""
        try:
            # Get transcript first
            transcript_data = self.get_transcript(video_url)
            
            # Run analyses
            sentiment = self.analyze_sentiment(video_url)
            key_points = self.extract_key_points(video_url)
            
            return {
                'metadata': transcript_data['metadata'],
                'transcript': transcript_data['transcript'],
                'sentiment': sentiment,
                'keyPoints': key_points
            }
        except Exception as e:
            raise ValueError(f"Error during video analysis: {str(e)}")

    def chat_with_video(self, question: str, history: list = None) -> str:
        """
        Interactive chat about the video content.
        
        Args:
            question: User's question about the video
            history: Optional list of previous chat messages
            
        Returns:
            AI-generated response
        """
        if not self.current_video_data:
            raise ValueError("No video has been analyzed yet. Please analyze a video first.")
        
        chat_interface = self.insight_engine.create_chat_interface()
        return chat_interface({
            "question": question,
            "history": history or []
        })

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
        
        transcript = self.current_video_data
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
            json.dump({
                'metadata': self.current_video_metadata,
                'insights': deduplicate_insights(self.insight_engine.generate_insights(self.current_video_data))
            }, f, indent=2)

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
    # Example: Using a TED Talk about AI
    video_url = "https://www.youtube.com/watch?v=aircAruvnKk"  # 3Blue1Brown Neural Networks video
    analyzer = VideoAnalyzer()
    results = analyzer.analyze_video(video_url)
    print(json.dumps(results, indent=2))
