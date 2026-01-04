"""
Format Converters
Convert parsed email data to various formats (CSV, TXT, JSON, PDF)
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT
import pandas as pd


def convert_to_csv(emails: List[Dict[str, Any]], output_path: Path):
    """
    Convert emails to CSV format

    CSV columns: Date, From, To, CC, Subject, Body, Attachments
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'From', 'To', 'CC', 'Subject', 'Body', 'Attachments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for email in emails:
            # Format attachments as comma-separated list
            attachments = ', '.join(email.get('attachments', []))

            writer.writerow({
                'Date': email.get('date', ''),
                'From': email.get('from', ''),
                'To': email.get('to', ''),
                'CC': email.get('cc', ''),
                'Subject': email.get('subject', ''),
                'Body': email.get('body', '').replace('\n', ' ').replace('\r', ''),
                'Attachments': attachments
            })


def convert_to_txt(emails: List[Dict[str, Any]], output_path: Path):
    """
    Convert emails to plain text format

    Each email is formatted as a readable text block with clear separators
    """
    with open(output_path, 'w', encoding='utf-8') as txtfile:
        txtfile.write("=" * 80 + "\n")
        txtfile.write(f"EMAIL EXPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        txtfile.write(f"Total Emails: {len(emails)}\n")
        txtfile.write("=" * 80 + "\n\n")

        for idx, email in enumerate(emails, 1):
            txtfile.write(f"\n{'=' * 80}\n")
            txtfile.write(f"EMAIL #{idx}\n")
            txtfile.write(f"{'=' * 80}\n\n")

            txtfile.write(f"Date:    {email.get('date', 'N/A')}\n")
            txtfile.write(f"From:    {email.get('from', 'N/A')}\n")
            txtfile.write(f"To:      {email.get('to', 'N/A')}\n")

            if email.get('cc'):
                txtfile.write(f"CC:      {email.get('cc')}\n")

            txtfile.write(f"Subject: {email.get('subject', '(No Subject)')}\n")

            if email.get('attachments'):
                txtfile.write(f"Attachments: {', '.join(email.get('attachments'))}\n")

            txtfile.write(f"\n{'-' * 80}\n")
            txtfile.write("MESSAGE BODY:\n")
            txtfile.write(f"{'-' * 80}\n\n")

            body = email.get('body', '(No content)')
            txtfile.write(body)
            txtfile.write("\n\n")

        txtfile.write(f"\n{'=' * 80}\n")
        txtfile.write(f"END OF EXPORT - {len(emails)} emails processed\n")
        txtfile.write(f"{'=' * 80}\n")


def convert_to_json(emails: List[Dict[str, Any]], output_path: Path):
    """
    Convert emails to JSON format

    Creates a structured JSON with metadata and full email data
    """
    # Convert date objects to strings for JSON serialization
    emails_serializable = []
    for email in emails:
        email_copy = email.copy()
        if 'date_parsed' in email_copy and email_copy['date_parsed']:
            email_copy['date_parsed'] = email_copy['date_parsed'].isoformat()
        emails_serializable.append(email_copy)

    output = {
        'export_date': datetime.now().isoformat(),
        'total_emails': len(emails),
        'emails': emails_serializable
    }

    with open(output_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(output, jsonfile, indent=2, ensure_ascii=False)


def convert_to_pdf(emails: List[Dict[str, Any]], output_path: Path):
    """
    Convert emails to PDF format

    Creates a formatted PDF document with all emails
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.5*inch
    )

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#1a1a1a',
        spaceAfter=12
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#333333',
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor='#1a1a1a',
        alignment=TA_LEFT,
        spaceAfter=12
    )

    # Build PDF content
    story = []

    # Title page
    title = Paragraph(f"Email Export - {len(emails)} Messages", title_style)
    story.append(title)

    export_date = Paragraph(
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        header_style
    )
    story.append(export_date)
    story.append(Spacer(1, 0.25*inch))

    # Add each email
    for idx, email in enumerate(emails, 1):
        # Email header
        subject = email.get('subject', '(No Subject)')
        subject_text = f"<b>Email #{idx}: {_escape_html(subject)}</b>"
        story.append(Paragraph(subject_text, title_style))

        # Metadata
        metadata_lines = [
            f"<b>Date:</b> {_escape_html(email.get('date', 'N/A'))}",
            f"<b>From:</b> {_escape_html(email.get('from', 'N/A'))}",
            f"<b>To:</b> {_escape_html(email.get('to', 'N/A'))}"
        ]

        if email.get('cc'):
            metadata_lines.append(f"<b>CC:</b> {_escape_html(email.get('cc'))}")

        if email.get('attachments'):
            attachments_str = ', '.join(email.get('attachments'))
            metadata_lines.append(f"<b>Attachments:</b> {_escape_html(attachments_str)}")

        for line in metadata_lines:
            story.append(Paragraph(line, header_style))

        story.append(Spacer(1, 0.1*inch))

        # Email body
        body = email.get('body', '(No content)')
        # Truncate very long bodies and escape HTML
        if len(body) > 5000:
            body = body[:5000] + "\n\n[... Content truncated for PDF ...]"

        body_escaped = _escape_html(body)
        body_para = Paragraph(body_escaped.replace('\n', '<br/>'), body_style)
        story.append(body_para)

        # Add page break between emails (except last one)
        if idx < len(emails):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)


def _escape_html(text: str) -> str:
    """Escape HTML special characters"""
    if not text:
        return ""

    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')

    return text
