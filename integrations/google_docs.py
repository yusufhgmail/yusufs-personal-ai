"""Google Docs API integration for editing documents."""

import os
from typing import Optional
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config.settings import get_settings

# Use same scopes as Drive (includes documents scope)
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents'
]


@dataclass
class TextSegment:
    """Represents a segment of text in a document with its position."""
    text: str
    start_index: int
    end_index: int


@dataclass 
class DocumentContent:
    """Represents the content of a Google Doc with structure info."""
    document_id: str
    title: str
    body_text: str
    segments: list[TextSegment]
    end_index: int  # Last valid index for insertions


class GoogleDocsClient:
    """Client for interacting with Google Docs API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Docs API using OAuth2."""
        creds = None
        # Use same token as Drive since we share scopes
        token_path = self.settings.get_token_path("drive_token.json", self.settings.drive_token_base64)
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds_path = self.settings.get_google_credentials_path()
                if not os.path.exists(creds_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {creds_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('docs', 'v1', credentials=creds)
    
    def get_document(self, document_id: str) -> Optional[DocumentContent]:
        """
        Get document content with structure information including indices.
        
        Args:
            document_id: The Google Doc ID
            
        Returns:
            DocumentContent with text segments and their indices
        """
        try:
            doc = self.service.documents().get(documentId=document_id).execute()
            
            title = doc.get('title', 'Untitled')
            body = doc.get('body', {})
            content = body.get('content', [])
            
            segments = []
            full_text = ""
            end_index = 1  # Documents start at index 1
            
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    para_elements = paragraph.get('elements', [])
                    
                    for para_element in para_elements:
                        if 'textRun' in para_element:
                            text_run = para_element['textRun']
                            text = text_run.get('content', '')
                            start_idx = para_element.get('startIndex', 0)
                            end_idx = para_element.get('endIndex', start_idx + len(text))
                            
                            segments.append(TextSegment(
                                text=text,
                                start_index=start_idx,
                                end_index=end_idx
                            ))
                            full_text += text
                            end_index = max(end_index, end_idx)
            
            return DocumentContent(
                document_id=document_id,
                title=title,
                body_text=full_text,
                segments=segments,
                end_index=end_index
            )
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def insert_text(self, document_id: str, text: str, index: int) -> bool:
        """
        Insert text at a specific index in the document.
        
        Args:
            document_id: The Google Doc ID
            text: Text to insert
            index: Position to insert at (1-based, as per Docs API)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': index
                        },
                        'text': text
                    }
                }
            ]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error inserting text: {e}")
            return False
    
    def delete_range(self, document_id: str, start_index: int, end_index: int) -> bool:
        """
        Delete text between two indices.
        
        Args:
            document_id: The Google Doc ID
            start_index: Start of range to delete (inclusive)
            end_index: End of range to delete (exclusive)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            requests = [
                {
                    'deleteContentRange': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index
                        }
                    }
                }
            ]
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error deleting range: {e}")
            return False
    
    def replace_all_text(self, document_id: str, find_text: str, replace_text: str) -> int:
        """
        Find and replace all occurrences of text in the document.
        
        Args:
            document_id: The Google Doc ID
            find_text: Text to find
            replace_text: Text to replace with
            
        Returns:
            Number of replacements made, or -1 on error
        """
        try:
            requests = [
                {
                    'replaceAllText': {
                        'containsText': {
                            'text': find_text,
                            'matchCase': True
                        },
                        'replaceText': replace_text
                    }
                }
            ]
            
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # Get the number of occurrences replaced
            replies = result.get('replies', [])
            if replies and 'replaceAllText' in replies[0]:
                return replies[0]['replaceAllText'].get('occurrencesChanged', 0)
            return 0
        except Exception as e:
            print(f"Error replacing text: {e}")
            return -1
    
    def append_text(self, document_id: str, text: str) -> bool:
        """
        Append text to the end of the document.
        
        Args:
            document_id: The Google Doc ID
            text: Text to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the document to find the end index
            doc = self.get_document(document_id)
            if not doc:
                return False
            
            # Insert at the end (before the final newline if present)
            # The end_index points to right after the last character
            insert_index = doc.end_index - 1 if doc.end_index > 1 else 1
            
            return self.insert_text(document_id, text, insert_index)
        except Exception as e:
            print(f"Error appending text: {e}")
            return False

