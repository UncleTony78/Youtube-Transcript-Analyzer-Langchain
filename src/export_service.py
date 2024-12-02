"""
Export service for handling various export formats and email functionality.
"""
import os
import json
import pandas as pd
from fpdf import FPDF
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from email_validator import validate_email, EmailNotValidError
from typing import Dict, Any, List
from pathlib import Path

class ExportService:
    def __init__(self, output_dir: str = "exports"):
        """Initialize the export service with an output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Export analysis results to CSV format."""
        df = pd.DataFrame(self._flatten_dict(data))
        filepath = self.output_dir / f"{filename}.csv"
        df.to_csv(filepath, index=False)
        return str(filepath)

    def to_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export analysis results to JSON format."""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return str(filepath)

    def to_pdf(self, data: Dict[str, Any], filename: str) -> str:
        """Export analysis results to PDF format."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "Video Analysis Report", ln=True, align='C')
        pdf.ln(10)

        # Add content
        pdf.set_font("Arial", size=12)
        for section, content in data.items():
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, str(section), ln=True)
            pdf.set_font("Arial", size=12)
            
            if isinstance(content, (list, dict)):
                content_str = json.dumps(content, indent=2)
            else:
                content_str = str(content)
                
            pdf.multi_cell(0, 10, content_str)
            pdf.ln(5)

        filepath = self.output_dir / f"{filename}.pdf"
        pdf.output(str(filepath))
        return str(filepath)

    def send_email(self, 
                  to_email: str,
                  subject: str,
                  body: str,
                  attachments: List[str]) -> bool:
        """
        Send email with analysis results as attachments.
        
        Requires the following environment variables:
        - SMTP_SERVER: SMTP server address
        - SMTP_PORT: SMTP server port
        - SMTP_USERNAME: SMTP username
        - SMTP_PASSWORD: SMTP password
        - SENDER_EMAIL: Sender's email address
        """
        try:
            # Validate email
            validate_email(to_email)
        except EmailNotValidError:
            raise ValueError("Invalid recipient email address")

        # Get email configuration from environment variables
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        sender_email = os.getenv("SENDER_EMAIL")

        if not all([smtp_server, smtp_username, smtp_password, sender_email]):
            raise ValueError("Missing email configuration in environment variables")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Add attachments
        for filepath in attachments:
            with open(filepath, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(filepath))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
            msg.attach(part)

        # Send email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary for CSV export."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
