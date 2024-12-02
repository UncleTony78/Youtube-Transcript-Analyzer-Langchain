"""
Script to run video analysis and display results.
"""

import os
from dotenv import load_dotenv
from src.main import VideoAnalyzer
from src.export_service import ExportService
from datetime import datetime

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize analyzer and export service
    analyzer = VideoAnalyzer()
    export_service = ExportService()
    
    # Example video URL
    video_url = "https://www.youtube.com/watch?v=CNBxIhxHHxM"
    
    print("\n=== Starting Video Analysis ===\n")
    
    try:
        # Get video insights
        results = analyzer.analyze_video(video_url)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"analysis_results_{timestamp}"
        
        # Export results in different formats
        csv_file = export_service.to_csv(results, base_filename)
        json_file = export_service.to_json(results, base_filename)
        pdf_file = export_service.to_pdf(results, base_filename)
        
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
            
        # Send email if configured
        recipient_email = os.getenv("RECIPIENT_EMAIL")
        if recipient_email:
            email_subject = f"Video Analysis Results - {results['metadata']['title']}"
            email_body = f"""
            Hello,

            Please find attached the analysis results for the video:
            {results['metadata']['title']}

            The analysis includes:
            - Detailed transcript analysis
            - Key insights and golden nuggets
            - Fact checks and verification
            - Complete summary

            The results are provided in CSV, JSON, and PDF formats for your convenience.

            Best regards,
            YouTube Transcript Analysis Tool
            """
            
            attachments = [csv_file, json_file, pdf_file]
            if export_service.send_email(recipient_email, email_subject, email_body, attachments):
                print("\nResults have been emailed successfully!")
            else:
                print("\nFailed to send email. Please check your email configuration.")
        
        print("\n=== Analysis Complete ===")
        print(f"\nExported results to:")
        print(f"CSV: {csv_file}")
        print(f"JSON: {json_file}")
        print(f"PDF: {pdf_file}")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()
