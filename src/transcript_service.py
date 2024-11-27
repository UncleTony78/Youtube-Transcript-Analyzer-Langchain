from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL."""
        if 'youtu.be' in url:
            return url.split('/')[-1]
        elif 'youtube.com' in url:
            if 'v=' in url:
                return url.split('v=')[1].split('&')[0]
        return url  # Assume it's already a video ID

    def get_video_metadata(self, video_id):
        """Retrieve video metadata using YouTube Data API."""
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                logger.error(f"No video found for ID: {video_id}")
                return None

            video_data = response['items'][0]
            metadata = {
                'title': video_data['snippet']['title'],
                'description': video_data['snippet']['description'],
                'channel_title': video_data['snippet']['channelTitle'],
                'published_at': video_data['snippet']['publishedAt'],
                'view_count': video_data['statistics'].get('viewCount', 0),
                'like_count': video_data['statistics'].get('likeCount', 0),
                'comment_count': video_data['statistics'].get('commentCount', 0),
                'duration': video_data['contentDetails']['duration']
            }
            return metadata

        except HttpError as e:
            logger.error(f"Error fetching video metadata: {str(e)}")
            return None

    def get_transcript(self, video_id):
        """Retrieve transcript using YouTube Transcript API."""
        try:
            # First try to get all available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                # If no English transcript, try to get auto-generated English transcript
                try:
                    transcript = transcript_list.find_manually_created_transcript()
                except:
                    # If no manually created transcript, get any available transcript
                    try:
                        transcript = transcript_list.find_generated_transcript(['en'])
                    except:
                        # Get the first available transcript and translate it to English
                        transcript = next(iter(transcript_list)).translate('en')
            
            # Get the actual transcript data
            return transcript.fetch()
            
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            return None

    def get_video_data(self, video_url):
        """Get both transcript and metadata for a video."""
        video_id = self.extract_video_id(video_url)
        
        metadata = self.get_video_metadata(video_id)
        if not metadata:
            return None

        transcript = self.get_transcript(video_id)
        if not transcript:
            return None

        return {
            'metadata': metadata,
            'transcript': transcript
        }

# Example usage
if __name__ == "__main__":
    # Create service instance
    service = YouTubeService()
    
    # Test with a video URL
    video_url = input("Enter YouTube video URL: ")
    
    # Get video data
    video_data = service.get_video_data(video_url)
    
    if video_data:
        print("\nVideo Metadata:")
        for key, value in video_data['metadata'].items():
            print(f"{key}: {value}")
        
        print("\nTranscript Preview (first 3 entries):")
        for entry in video_data['transcript'][:3]:
            print(entry)
    else:
        print("Failed to retrieve video data")
