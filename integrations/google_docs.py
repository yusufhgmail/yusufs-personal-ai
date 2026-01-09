"""Google Docs API integration for editing documents."""

import os
import json
import time
from typing import Optional
from dataclasses import dataclass

# #region agent log
DEBUG_LOG_PATH = r"c:\Users\yusuf\code\yusufsPersonalAIAssistant\.cursor\debug.log"
def _debug_log(hypothesis_id: str, location: str, message: str, data: dict):
    try:
        with open(DEBUG_LOG_PATH, 'a') as f:
            f.write(json.dumps({"hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(time.time() * 1000), "sessionId": "debug-session"}) + "\n")
    except: pass
# #endregion

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
    first_paragraph_index: int  # First valid index for insertions (start of first paragraph)
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
            first_paragraph_index = 1  # Default to 1
            found_first_paragraph = False
            
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    # Get the paragraph's start index from the element itself
                    para_start = element.get('startIndex', 1)
                    
                    # Track the first paragraph's starting position
                    if not found_first_paragraph:
                        first_paragraph_index = para_start
                        found_first_paragraph = True
                    
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
            
            # #region agent log
            _debug_log("B", "google_docs.py:get_document", "Document structure retrieved", {"doc_id": document_id, "first_paragraph_index": first_paragraph_index, "end_index": end_index, "num_segments": len(segments), "found_first_paragraph": found_first_paragraph})
            # #endregion
            return DocumentContent(
                document_id=document_id,
                title=title,
                body_text=full_text,
                segments=segments,
                first_paragraph_index=first_paragraph_index,
                end_index=end_index
            )
        except Exception as e:
            # #region agent log
            _debug_log("D", "google_docs.py:get_document:error", "Error getting document", {"doc_id": document_id, "error": str(e)})
            # #endregion
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
            # Ensure minimum index is 1
            safe_index = max(1, index)
            # #region agent log
            _debug_log("A,B,C", "google_docs.py:insert_text:before", "About to call batchUpdate", {"doc_id": document_id, "original_index": index, "safe_index": safe_index, "text_length": len(text), "text_preview": text[:50]})
            # #endregion
            
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': safe_index
                        },
                        'text': text
                    }
                }
            ]
            
            result = self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # #region agent log
            _debug_log("A,C", "google_docs.py:insert_text:after", "batchUpdate completed", {"doc_id": document_id, "safe_index": safe_index, "result_keys": list(result.keys()) if result else None})
            # #endregion
            return True
        except Exception as e:
            # #region agent log
            _debug_log("A", "google_docs.py:insert_text:error", "Exception in insert_text", {"doc_id": document_id, "index": index, "error": str(e)})
            # #endregion
            print(f"Error inserting text: {e}")
            return False
    
    def insert_at_beginning(self, document_id: str, text: str) -> bool:
        """
        Insert text at the beginning of the document (first paragraph).
        
        Args:
            document_id: The Google Doc ID
            text: Text to insert
            
        Returns:
            True if successful, False otherwise
        """
        # #region agent log
        _debug_log("A,B", "google_docs.py:insert_at_beginning:entry", "Called insert_at_beginning", {"doc_id": document_id, "text_preview": text[:50]})
        # #endregion
        try:
            doc = self.get_document(document_id)
            if not doc:
                # #region agent log
                _debug_log("D", "google_docs.py:insert_at_beginning:no_doc", "get_document returned None", {"doc_id": document_id})
                # #endregion
                return False
            
            # #region agent log
            _debug_log("B", "google_docs.py:insert_at_beginning:before_insert", "About to call insert_text", {"doc_id": document_id, "first_paragraph_index": doc.first_paragraph_index})
            # #endregion
            # Use the first paragraph index for safe insertion
            result = self.insert_text(document_id, text, doc.first_paragraph_index)
            # #region agent log
            _debug_log("A", "google_docs.py:insert_at_beginning:after_insert", "insert_text returned", {"doc_id": document_id, "result": result})
            # #endregion
            return result
        except Exception as e:
            # #region agent log
            _debug_log("A", "google_docs.py:insert_at_beginning:error", "Exception", {"error": str(e)})
            # #endregion
            print(f"Error inserting at beginning: {e}")
            return False
    
    def insert_after_text(self, document_id: str, search_text: str, text_to_insert: str) -> bool:
        """
        Insert text right after a specific text pattern in the document.
        This is useful for inserting answers after questions.
        
        Args:
            document_id: The Google Doc ID
            search_text: Text to search for (insert will happen after this)
            text_to_insert: Text to insert
            
        Returns:
            True if successful, False otherwise
        """
        # #region agent log
        _debug_log("E", "google_docs.py:insert_after_text:entry", "Called insert_after_text", {"doc_id": document_id, "search_text_preview": search_text[:50] if search_text else None, "insert_text_preview": text_to_insert[:50] if text_to_insert else None})
        # #endregion
        try:
            doc = self.get_document(document_id)
            if not doc:
                # #region agent log
                _debug_log("E", "google_docs.py:insert_after_text:no_doc", "get_document returned None", {"doc_id": document_id})
                # #endregion
                return False
            
            # Find the search text in the document
            body_text = doc.body_text
            position = body_text.find(search_text)
            # #region agent log
            _debug_log("E", "google_docs.py:insert_after_text:search", "Searched for text", {"found_position": position, "body_text_length": len(body_text)})
            # #endregion
            
            if position == -1:
                print(f"Could not find text: {search_text}")
                return False
            
            # Calculate the insertion index
            # We need to find which segment contains this text and get the actual index
            cumulative_length = 0
            for segment in doc.segments:
                segment_text = segment.text
                if search_text in segment_text:
                    # Found it in this segment
                    local_pos = segment_text.find(search_text)
                    # Insert after the search text
                    insert_index = segment.start_index + local_pos + len(search_text)
                    return self.insert_text(document_id, text_to_insert, insert_index)
                cumulative_length += len(segment_text)
            
            return False
        except Exception as e:
            print(f"Error inserting after text: {e}")
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

