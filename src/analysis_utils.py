"""
Utility functions for video content analysis and processing.
"""

from typing import List, Dict, Any
from textblob import TextBlob
import re

def chunk_transcript(transcript: List[Dict], chunk_size: int = 5) -> List[Dict]:
    """
    Split transcript into meaningful chunks while preserving context.
    
    Args:
        transcript: List of transcript segments
        chunk_size: Number of segments per chunk
        
    Returns:
        List of chunked transcript segments
    """
    chunks = []
    current_chunk = []
    current_duration = 0
    
    for segment in transcript:
        current_chunk.append(segment)
        current_duration += segment['duration']
        
        # Create new chunk if size limit reached or at natural break
        if (len(current_chunk) >= chunk_size or 
            current_duration >= 30 or  # 30 seconds per chunk
            _is_natural_break(segment['text'])):
            
            chunks.append({
                'text': ' '.join([s['text'] for s in current_chunk]),
                'start': current_chunk[0]['start'],
                'duration': current_duration,
                'segments': current_chunk
            })
            current_chunk = []
            current_duration = 0
    
    # Add remaining segments
    if current_chunk:
        chunks.append({
            'text': ' '.join([s['text'] for s in current_chunk]),
            'start': current_chunk[0]['start'],
            'duration': current_duration,
            'segments': current_chunk
        })
    
    return chunks

def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze sentiment of text segment.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing polarity and subjectivity scores
    """
    analysis = TextBlob(text)
    return {
        'polarity': analysis.sentiment.polarity,
        'subjectivity': analysis.sentiment.subjectivity
    }

def extract_key_phrases(text: str) -> List[str]:
    """
    Extract important phrases from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of key phrases
    """
    blob = TextBlob(text)
    return [phrase for phrase in blob.noun_phrases]

def _is_natural_break(text: str) -> bool:
    """
    Check if text segment ends at a natural break point.
    
    Args:
        text: Text segment to check
        
    Returns:
        Boolean indicating if segment ends at natural break
    """
    # Check for sentence-ending punctuation
    if re.search(r'[.!?]$', text.strip()):
        return True
    
    # Check for common transition phrases
    transition_phrases = [
        'however,', 'moreover,', 'furthermore,', 'in addition,',
        'next,', 'finally,', 'consequently,', 'therefore,'
    ]
    return any(text.strip().lower().endswith(phrase) for phrase in transition_phrases)

def format_timestamp(seconds: float) -> str:
    """
    Format timestamp in human-readable format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

def deduplicate_insights(insights: List[Dict], similarity_threshold: float = 0.8) -> List[Dict]:
    """
    Remove duplicate insights based on content similarity.
    
    Args:
        insights: List of insight dictionaries
        similarity_threshold: Threshold for considering insights as duplicates
        
    Returns:
        List of unique insights
    """
    unique_insights = []
    
    for insight in insights:
        is_duplicate = False
        for unique in unique_insights:
            similarity = _calculate_similarity(insight['explanation'], unique['explanation'])
            if similarity > similarity_threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_insights.append(insight)
    
    return unique_insights

def _calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text segments.
    
    Args:
        text1: First text segment
        text2: Second text segment
        
    Returns:
        Similarity score between 0 and 1
    """
    # TODO: Implement more sophisticated similarity calculation
    # Currently using simple word overlap
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0
