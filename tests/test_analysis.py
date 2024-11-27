from transcript_service import YouTubeService
from langchain_processor import TranscriptProcessor
import logging
import json
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set console encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def format_sentiment(sentiment):
    """Format sentiment scores in a readable way"""
    if not sentiment:
        return "N/A"
    polarity = sentiment['polarity']
    subjectivity = sentiment['subjectivity']
    
    # Convert polarity to description
    if polarity > 0.5:
        pol_desc = "Very Positive"
    elif polarity > 0:
        pol_desc = "Slightly Positive"
    elif polarity < -0.5:
        pol_desc = "Very Negative"
    elif polarity < 0:
        pol_desc = "Slightly Negative"
    else:
        pol_desc = "Neutral"
    
    # Convert subjectivity to description
    if subjectivity > 0.7:
        subj_desc = "Very Subjective"
    elif subjectivity > 0.3:
        subj_desc = "Somewhat Subjective"
    else:
        subj_desc = "Mostly Objective"
    
    return f"{pol_desc} ({polarity:.2f}), {subj_desc} ({subjectivity:.2f})"

def test_video_analysis():
    try:
        # Initialize services
        youtube_service = YouTubeService()
        processor = TranscriptProcessor()

        # Get video data
        video_url = 'https://www.youtube.com/watch?v=FsztuzyXdhY'
        logger.info(f"Fetching transcript for video: {video_url}")
        
        video_data = youtube_service.get_video_data(video_url)

        if video_data and video_data['transcript']:
            print('\n=== Video Information ===')
            print('Title:', video_data['metadata']['title'])
            print('Channel:', video_data['metadata']['channel_title'])
            print('\nDescription:', video_data['metadata'].get('description', '')[:200] + '...' if video_data['metadata'].get('description') else 'No description available')
            print('\n=== Processing Transcript ===')
            
            results = processor.process_transcript(video_data)
            
            if results:
                # Save results to file for reference
                with open('analysis_results.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print('\n=== Initial Context Analysis ===')
                print(results['context_analysis'])
                
                print('\n=== Chunk Analyses ===')
                for i, chunk_result in enumerate(results['chunk_analyses'], 1):
                    print(f'\nChunk {i}:')
                    print(f'Summary: {chunk_result["summary"]}')
                    print(f'Sentiment: {format_sentiment(chunk_result["sentiment"])}')
                    print(f'Key Points: {chunk_result["key_points"]}')
                
                print('\n=== Final Comprehensive Summary ===')
                print(results['final_summary'])
                
                print('\nFull analysis results have been saved to analysis_results.json')
            else:
                print('Failed to process transcript')
        else:
            print('Failed to retrieve video data')
            
    except Exception as e:
        logger.error(f"Error in test_video_analysis: {str(e)}")
        raise

if __name__ == "__main__":
    test_video_analysis()
