"""Gmail API integration for the personal AI assistant."""

import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config.settings import get_settings


# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]


@dataclass
class Email:
    """Represents an email message."""
    id: str
    thread_id: str
    subject: str
    sender: str
    to: str
    date: str
    snippet: str
    body: Optional[str] = None
    attachments: list = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


@dataclass
class Attachment:
    """Represents an email attachment."""
    id: str  # attachmentId (may be empty for inline attachments)
    filename: str
    mime_type: str
    size: int
    inline_data: Optional[str] = None  # base64 data if inline attachment


class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        # Get token path, creating from base64 if needed
        token_path = self.settings.get_token_path("gmail_token.json", self.settings.gmail_token_base64)
        
        # Load existing credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds_path = self.settings.get_google_credentials_path()
                if not os.path.exists(creds_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {creds_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console or set GOOGLE_CREDENTIALS_BASE64."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def search_emails(self, query: str, max_results: int = 10) -> list[Email]:
        """
        Search for emails matching a query.
        
        Args:
            query: Gmail search query (e.g., "from:someone@example.com subject:meeting")
            max_results: Maximum number of results to return
            
        Returns:
            List of Email objects
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email = self._get_email_metadata(msg['id'])
                if email:
                    emails.append(email)
            
            return emails
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def _get_email_metadata(self, message_id: str) -> Optional[Email]:
        """Get email metadata (without full body)."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'To', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            return Email(
                id=message['id'],
                thread_id=message['threadId'],
                subject=headers.get('Subject', '(No Subject)'),
                sender=headers.get('From', ''),
                to=headers.get('To', ''),
                date=headers.get('Date', ''),
                snippet=message.get('snippet', '')
            )
        except Exception as e:
            print(f"Error getting email metadata: {e}")
            return None
    
    def read_email(self, message_id: str) -> Optional[Email]:
        """
        Read the full content of an email.
        
        Args:
            message_id: The Gmail message ID
            
        Returns:
            Email object with full body, or None if not found
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            # Extract body
            body = self._extract_body(message.get('payload', {}))
            
            # Extract attachments info
            attachments = self._extract_attachments(message.get('payload', {}))
            
            return Email(
                id=message['id'],
                thread_id=message['threadId'],
                subject=headers.get('Subject', '(No Subject)'),
                sender=headers.get('From', ''),
                to=headers.get('To', ''),
                date=headers.get('Date', ''),
                snippet=message.get('snippet', ''),
                body=body,
                attachments=attachments
            )
        except Exception as e:
            print(f"Error reading email: {e}")
            return None
    
    def _extract_body(self, payload: dict) -> str:
        """Extract the email body from the payload."""
        body = ""
        
        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if part['body'].get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    body = self._extract_body(part)
                    if body:
                        break
        
        return body
    
    def _extract_attachments(self, payload: dict) -> list[Attachment]:
        """Extract attachment information from the payload."""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append(Attachment(
                        id=part['body'].get('attachmentId', ''),
                        filename=part['filename'],
                        mime_type=part['mimeType'],
                        size=part['body'].get('size', 0),
                        inline_data=part['body'].get('data')  # Capture inline data if present
                    ))
                if 'parts' in part:
                    attachments.extend(self._extract_attachments(part))
        
        return attachments
    
    def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """
        Download an attachment by attachment ID.
        
        Args:
            message_id: The Gmail message ID
            attachment_id: The attachment ID
            
        Returns:
            The attachment data as bytes
        """
        attachment = self.service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
        
        return base64.urlsafe_b64decode(attachment['data'])
    
    def get_attachment_data(self, message_id: str, filename: str) -> tuple[bytes, str]:
        """
        Download attachment data by filename.
        Handles both regular attachments (via API) and inline attachments (embedded data).
        
        Args:
            message_id: The Gmail message ID
            filename: The filename of the attachment to download
            
        Returns:
            Tuple of (attachment data as bytes, mime_type)
            
        Raises:
            ValueError: If email or attachment not found, or if attachment has no data
        """
        # Fetch the full email
        email = self.read_email(message_id)
        if not email:
            raise ValueError(f"Email not found: {message_id}")
        
        # Find attachment by filename
        attachment = None
        for att in email.attachments:
            if att.filename == filename:
                attachment = att
                break
        
        if not attachment:
            # List available attachments for better error message
            available = [att.filename for att in email.attachments]
            raise ValueError(f"Attachment not found: '{filename}'. Available attachments: {available}")
        
        # Try inline data first (if present)
        if attachment.inline_data:
            return base64.urlsafe_b64decode(attachment.inline_data), attachment.mime_type
        
        # Otherwise use API call (validate ID first)
        if not attachment.id:
            raise ValueError(f"Attachment has no ID or inline data: '{filename}'")
        
        data = self.download_attachment(message_id, attachment.id)
        return data, attachment.mime_type
    
    def create_draft(self, to: str, subject: str, body: str, 
                     reply_to_message_id: Optional[str] = None) -> str:
        """
        Create an email draft.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            reply_to_message_id: Optional message ID to reply to
            
        Returns:
            The draft ID
        """
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft_body = {'message': {'raw': raw}}
        
        if reply_to_message_id:
            # Get the thread ID for the reply
            original = self.service.users().messages().get(
                userId='me', id=reply_to_message_id
            ).execute()
            draft_body['message']['threadId'] = original['threadId']
        
        draft = self.service.users().drafts().create(
            userId='me',
            body=draft_body
        ).execute()
        
        return draft['id']
    
    def send_draft(self, draft_id: str) -> str:
        """
        Send a draft email.
        
        Args:
            draft_id: The draft ID to send
            
        Returns:
            The sent message ID
        """
        sent = self.service.users().drafts().send(
            userId='me',
            body={'id': draft_id}
        ).execute()
        
        return sent['id']
    
    def send_email(self, to: str, subject: str, body: str,
                   reply_to_message_id: Optional[str] = None) -> str:
        """
        Send an email directly (without creating a draft first).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            reply_to_message_id: Optional message ID to reply to
            
        Returns:
            The sent message ID
        """
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        send_body = {'raw': raw}
        
        if reply_to_message_id:
            original = self.service.users().messages().get(
                userId='me', id=reply_to_message_id
            ).execute()
            send_body['threadId'] = original['threadId']
        
        sent = self.service.users().messages().send(
            userId='me',
            body=send_body
        ).execute()
        
        return sent['id']
    
    def get_draft(self, draft_id: str) -> Optional[dict]:
        """Get a draft by ID."""
        try:
            draft = self.service.users().drafts().get(
                userId='me',
                id=draft_id
            ).execute()
            return draft
        except Exception as e:
            print(f"Error getting draft: {e}")
            return None
    
    def update_draft(self, draft_id: str, to: str, subject: str, body: str) -> str:
        """
        Update an existing draft.
        
        Args:
            draft_id: The draft ID to update
            to: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            The updated draft ID
        """
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        updated = self.service.users().drafts().update(
            userId='me',
            id=draft_id,
            body={'message': {'raw': raw}}
        ).execute()
        
        return updated['id']
    
    def delete_draft(self, draft_id: str):
        """Delete a draft."""
        self.service.users().drafts().delete(
            userId='me',
            id=draft_id
        ).execute()

