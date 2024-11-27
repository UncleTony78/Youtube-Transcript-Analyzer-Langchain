import pytest
from transcript_service import YouTubeService

def test_video_id_extraction():
    service = YouTubeService()
    
    # Test different URL formats
    assert service.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert service.extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert service.extract_video_id('dQw4w9WgXcQ') == 'dQw4w9WgXcQ'

def test_video_metadata():
    service = YouTubeService()
    
    # Test with a known video
    video_id = 'dQw4w9WgXcQ'
    metadata = service.get_video_metadata(video_id)
    
    assert metadata is not None
    assert 'title' in metadata
    assert 'channel_title' in metadata
    assert 'view_count' in metadata

def test_transcript_retrieval():
    service = YouTubeService()
    
    # Test with a known video that has transcripts
    video_id = 'dQw4w9WgXcQ'
    transcript = service.get_transcript(video_id)
    
    assert transcript is not None
    assert len(transcript) > 0
    assert 'text' in transcript[0]
    assert 'start' in transcript[0]
