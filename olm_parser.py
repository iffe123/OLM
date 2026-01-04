"""
OLM File Parser
Extracts email data from Outlook for Mac (.olm) files
"""
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser
import base64
import chardet


class OLMParser:
    """Parser for OLM (Outlook for Mac) files"""

    def __init__(self, olm_path: Path):
        self.olm_path = Path(olm_path)
        self.temp_dir = None
        self.emails = []

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parse OLM file and extract all emails

        Returns:
            List of email dictionaries with metadata and content
        """
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()

        try:
            # OLM files are actually ZIP archives
            self._extract_olm()

            # Find and parse email files
            self._parse_emails()

            return self.emails

        except Exception as e:
            raise Exception(f"Error parsing OLM file: {str(e)}")

    def _extract_olm(self):
        """Extract OLM file contents"""
        try:
            with zipfile.ZipFile(self.olm_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
        except zipfile.BadZipFile:
            # Some OLM files might be directories, not zipped
            if self.olm_path.is_dir():
                shutil.copytree(self.olm_path, self.temp_dir, dirs_exist_ok=True)
            else:
                raise Exception("Invalid OLM file format")

    def _parse_emails(self):
        """Parse all email files in the extracted OLM structure"""
        temp_path = Path(self.temp_dir)

        # OLM structure typically contains .eml files or message XML files
        # Look for .eml files (standard email format)
        eml_files = list(temp_path.rglob("*.eml"))

        for eml_file in eml_files:
            try:
                email_data = self._parse_eml_file(eml_file)
                if email_data:
                    self.emails.append(email_data)
            except Exception as e:
                # Skip problematic emails but continue processing
                print(f"Warning: Failed to parse {eml_file}: {str(e)}")
                continue

        # Also look for .xml message files (alternative OLM format)
        xml_files = list(temp_path.rglob("*.xml"))
        for xml_file in xml_files:
            if "message" in xml_file.name.lower():
                try:
                    email_data = self._parse_xml_message(xml_file)
                    if email_data:
                        self.emails.append(email_data)
                except Exception as e:
                    print(f"Warning: Failed to parse {xml_file}: {str(e)}")
                    continue

        # If no emails found, try alternative parsing methods
        if not self.emails:
            self._parse_alternative_formats()

    def _parse_eml_file(self, eml_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a .eml (RFC 822) email file"""
        with open(eml_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        # Extract email data
        email_data = {
            'subject': msg.get('Subject', '(No Subject)'),
            'from': msg.get('From', ''),
            'to': msg.get('To', ''),
            'cc': msg.get('Cc', ''),
            'date': msg.get('Date', ''),
            'body': '',
            'attachments': []
        }

        # Parse date
        try:
            if email_data['date']:
                email_data['date_parsed'] = email.utils.parsedate_to_datetime(email_data['date'])
            else:
                email_data['date_parsed'] = None
        except:
            email_data['date_parsed'] = None

        # Extract body
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Get email body
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            # Detect encoding
                            detected = chardet.detect(body)
                            encoding = detected['encoding'] or 'utf-8'
                            email_data['body'] = body.decode(encoding, errors='ignore')
                    except:
                        pass

                # Track attachments
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        email_data['attachments'].append(filename)
        else:
            try:
                body = msg.get_payload(decode=True)
                if body:
                    detected = chardet.detect(body)
                    encoding = detected['encoding'] or 'utf-8'
                    email_data['body'] = body.decode(encoding, errors='ignore')
            except:
                email_data['body'] = str(msg.get_payload())

        return email_data

    def _parse_xml_message(self, xml_path: Path) -> Optional[Dict[str, Any]]:
        """Parse XML-formatted message file"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            email_data = {
                'subject': '',
                'from': '',
                'to': '',
                'cc': '',
                'date': '',
                'body': '',
                'attachments': []
            }

            # Extract data from XML (structure varies)
            for elem in root.iter():
                tag_lower = elem.tag.lower()
                if 'subject' in tag_lower and elem.text:
                    email_data['subject'] = elem.text
                elif 'from' in tag_lower and elem.text:
                    email_data['from'] = elem.text
                elif 'to' in tag_lower and elem.text:
                    email_data['to'] = elem.text
                elif 'date' in tag_lower and elem.text:
                    email_data['date'] = elem.text
                elif 'body' in tag_lower and elem.text:
                    email_data['body'] = elem.text

            return email_data if email_data['subject'] or email_data['body'] else None

        except:
            return None

    def _parse_alternative_formats(self):
        """Try alternative parsing methods for different OLM formats"""
        temp_path = Path(self.temp_dir)

        # Look for any text files that might contain email data
        for text_file in temp_path.rglob("*.txt"):
            try:
                with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 50:  # Reasonable email length
                        self.emails.append({
                            'subject': f'Message from {text_file.name}',
                            'from': '',
                            'to': '',
                            'cc': '',
                            'date': '',
                            'body': content,
                            'attachments': []
                        })
            except:
                continue

    def cleanup(self):
        """Remove temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
