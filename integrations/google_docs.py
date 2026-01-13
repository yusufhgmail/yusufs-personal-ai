"""Google Docs API integration for editing documents."""

import os
import re
from typing import Optional, Tuple
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
    
    def _validate_document_id(self, document_id: str) -> bool:
        """Check if the provided string looks like a document ID (not a name)."""
        # Document IDs are alphanumeric with dashes/underscores, no spaces or parentheses
        if ' ' in document_id or '(' in document_id or ')' in document_id:
            return False
        return True
    
    def get_document(self, document_id: str) -> Optional[DocumentContent]:
        """
        Get document content with structure information including indices.
        
        Args:
            document_id: The Google Doc ID
            
        Returns:
            DocumentContent with text segments and their indices
        """
        if not self._validate_document_id(document_id):
            print(f"ERROR: '{document_id}' looks like a document name, not an ID. Use search_drive_files to get the actual document ID.")
            return None
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
            
            return DocumentContent(
                document_id=document_id,
                title=title,
                body_text=full_text,
                segments=segments,
                first_paragraph_index=first_paragraph_index,
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
            # Ensure minimum index is 1
            safe_index = max(1, index)
            
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
            
            self.service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            return True
        except Exception as e:
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
        try:
            doc = self.get_document(document_id)
            if not doc:
                return False
            
            # Use the first paragraph index for safe insertion
            return self.insert_text(document_id, text, doc.first_paragraph_index)
        except Exception as e:
            print(f"Error inserting at beginning: {e}")
            return False
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace: collapse all whitespace sequences to single space, trim."""
        # Replace all whitespace sequences with single space
        normalized = re.sub(r'\s+', ' ', text)
        # Trim leading/trailing whitespace
        return normalized.strip()
    
    def _find_text_with_variations(self, body_text: str, search_text: str) -> Optional[int]:
        """
        Try to find search_text in body_text using multiple strategies.
        
        Returns:
            Position in body_text where match is found, or None if not found
        """
        # Strategy 1: Exact match
        position = body_text.find(search_text)
        if position != -1:
            return position
        
        # Strategy 2: Normalized whitespace match
        normalized_search = self._normalize_whitespace(search_text)
        normalized_body = self._normalize_whitespace(body_text)
        
        if normalized_search and normalized_body:
            normalized_pos = normalized_body.find(normalized_search)
            if normalized_pos != -1:
                # Find the corresponding position in original text
                # Use a sliding window approach to find the best match
                # Search for a unique substring from the normalized match
                # For simplicity, try to find the core text (without leading/trailing whitespace)
                core_search = search_text.strip()
                if core_search:
                    # Try to find the core text in a reasonable region
                    # Estimate position based on normalized match
                    estimated_start = max(0, int(normalized_pos * len(body_text) / len(normalized_body)) - 100)
                    estimated_end = min(len(body_text), estimated_start + len(search_text) + 200)
                    search_region = body_text[estimated_start:estimated_end]
                    
                    # Try exact match of core text
                    core_pos = search_region.find(core_search)
                    if core_pos != -1:
                        return estimated_start + core_pos
                    
                    # Try with normalized core
                    normalized_core = self._normalize_whitespace(core_search)
                    if normalized_core:
                        normalized_region = self._normalize_whitespace(search_region)
                        normalized_core_pos = normalized_region.find(normalized_core)
                        if normalized_core_pos != -1:
                            # Map back approximately
                            return estimated_start + normalized_core_pos
        
        # Strategy 3: Without trailing whitespace
        search_no_trailing = search_text.rstrip()
        if search_no_trailing and search_no_trailing != search_text:
            position = body_text.find(search_no_trailing)
            if position != -1:
                return position
        
        # Strategy 4: Without leading whitespace
        search_no_leading = search_text.lstrip()
        if search_no_leading and search_no_leading != search_text:
            position = body_text.find(search_no_leading)
            if position != -1:
                return position
        
        # Strategy 5: Fully trimmed
        search_trimmed = search_text.strip()
        if search_trimmed and search_trimmed != search_text:
            position = body_text.find(search_trimmed)
            if position != -1:
                return position
        
        return None
    
    def _map_position_to_document_index(self, doc: DocumentContent, position: int, search_text_length: int) -> Optional[int]:
        """
        Map a character position in body_text to a document index.
        
        Args:
            doc: DocumentContent object
            position: Character position in body_text where search text starts
            search_text_length: Length of the search text
            
        Returns:
            Document index where search text ends (insertion point), or None if not found
        """
        # Calculate where search text ends in body_text
        end_position = position + search_text_length
        
        # Map end position in body_text to document index
        # This handles cases where formatting splits text across multiple segments
        cumulative_chars = 0
        for segment in doc.segments:
            segment_length = len(segment.text)
            segment_end = cumulative_chars + segment_length
            
            # Check if search text ends in this segment
            if cumulative_chars < end_position <= segment_end:
                # Calculate how many chars into this segment the end position is
                chars_into_segment = end_position - cumulative_chars
                # Document index where search text ends (insertion point)
                return segment.start_index + chars_into_segment
            
            cumulative_chars += segment_length
        
        return None
    
    def insert_after_text(self, document_id: str, search_text: str, text_to_insert: str) -> bool:
        """
        Insert text right after a specific text pattern in the document.
        This is useful for inserting answers after questions.
        
        Tries multiple search strategies to handle whitespace differences:
        1. Exact match (fast path)
        2. Normalized whitespace match
        3. Match without trailing whitespace
        
        Args:
            document_id: The Google Doc ID
            search_text: Text to search for (insert will happen after this)
            text_to_insert: Text to insert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = self.get_document(document_id)
            if not doc:
                return False
            
            body_text = doc.body_text
            
            # Try multiple search strategies
            position = self._find_text_with_variations(body_text, search_text)
            
            if position is not None:
                # Determine the actual search text length that was matched
                # Try to find which variant matched
                matched_length = len(search_text)
                
                # Check if it was an exact match
                if position + len(search_text) <= len(body_text) and body_text[position:position+len(search_text)] == search_text:
                    matched_length = len(search_text)
                else:
                    # Try to determine which variant matched
                    variants = [
                        (search_text.rstrip(), len(search_text.rstrip())),
                        (search_text.lstrip(), len(search_text.lstrip())),
                        (search_text.strip(), len(search_text.strip())),
                    ]
                    
                    for variant_text, variant_len in variants:
                        if variant_text and position + variant_len <= len(body_text) and body_text[position:position+variant_len] == variant_text:
                            matched_length = variant_len
                            break
                
                insert_index = self._map_position_to_document_index(doc, position, matched_length)
                if insert_index is not None:
                    return self.insert_text(document_id, text_to_insert, insert_index)
            
            # All strategies failed
            print(f"Could not find text after trying multiple strategies: {search_text[:100]}...")
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
