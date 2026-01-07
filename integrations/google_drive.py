"""Google Drive API integration for the personal AI assistant."""

import os
import io
from typing import Optional
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

from config.settings import get_settings


# Drive API scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly'
]


@dataclass
class DriveFile:
    """Represents a file in Google Drive."""
    id: str
    name: str
    mime_type: str
    size: Optional[int] = None
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    web_view_link: Optional[str] = None


class GoogleDriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API using OAuth2."""
        creds = None
        token_path = "config/drive_token.json"
        
        # Load existing credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.settings.google_credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {self.settings.google_credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.settings.google_credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def search_files(self, query: str, max_results: int = 10) -> list[DriveFile]:
        """
        Search for files in Google Drive.
        
        Args:
            query: Search query (Drive API query format)
            max_results: Maximum number of results
            
        Returns:
            List of DriveFile objects
        """
        try:
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            return [
                DriveFile(
                    id=f['id'],
                    name=f['name'],
                    mime_type=f['mimeType'],
                    size=f.get('size'),
                    created_time=f.get('createdTime'),
                    modified_time=f.get('modifiedTime'),
                    web_view_link=f.get('webViewLink')
                )
                for f in files
            ]
        except Exception as e:
            print(f"Error searching files: {e}")
            return []
    
    def get_file(self, file_id: str) -> Optional[DriveFile]:
        """Get file metadata by ID."""
        try:
            f = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink"
            ).execute()
            
            return DriveFile(
                id=f['id'],
                name=f['name'],
                mime_type=f['mimeType'],
                size=f.get('size'),
                created_time=f.get('createdTime'),
                modified_time=f.get('modifiedTime'),
                web_view_link=f.get('webViewLink')
            )
        except Exception as e:
            print(f"Error getting file: {e}")
            return None
    
    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download a file's content.
        
        Args:
            file_id: The file ID
            
        Returns:
            File content as bytes, or None if failed
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return fh.getvalue()
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def export_google_doc(self, file_id: str, mime_type: str = 'text/plain') -> Optional[str]:
        """
        Export a Google Doc/Sheet/Slides to a specific format.
        
        Args:
            file_id: The file ID
            mime_type: The export format (e.g., 'text/plain', 'application/pdf')
            
        Returns:
            File content as string (for text formats) or None
        """
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=mime_type
            )
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = fh.getvalue()
            if mime_type.startswith('text/'):
                return content.decode('utf-8')
            return content
        except Exception as e:
            print(f"Error exporting file: {e}")
            return None
    
    def upload_file(self, name: str, content: bytes, mime_type: str, 
                    folder_id: Optional[str] = None) -> Optional[DriveFile]:
        """
        Upload a file to Google Drive.
        
        Args:
            name: File name
            content: File content as bytes
            mime_type: MIME type of the file
            folder_id: Optional folder ID to upload to
            
        Returns:
            DriveFile object for the uploaded file
        """
        try:
            file_metadata = {'name': name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaIoBaseUpload(
                io.BytesIO(content),
                mimetype=mime_type,
                resumable=True
            )
            
            f = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            
            return DriveFile(
                id=f['id'],
                name=f['name'],
                mime_type=f['mimeType'],
                web_view_link=f.get('webViewLink')
            )
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def create_google_doc(self, name: str, content: str = "",
                          folder_id: Optional[str] = None) -> Optional[DriveFile]:
        """
        Create a new Google Doc.
        
        Args:
            name: Document name
            content: Initial content (plain text)
            folder_id: Optional folder ID
            
        Returns:
            DriveFile object for the created doc
        """
        try:
            # Create the doc
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.document'
            }
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            f = self.service.files().create(
                body=file_metadata,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            
            # If content provided, update the doc
            if content:
                # Use the Docs API to insert content
                # For now, we'll just create an empty doc
                # Full content insertion requires the Docs API
                pass
            
            return DriveFile(
                id=f['id'],
                name=f['name'],
                mime_type=f['mimeType'],
                web_view_link=f.get('webViewLink')
            )
        except Exception as e:
            print(f"Error creating Google Doc: {e}")
            return None
    
    def convert_to_google_doc(self, file_id: str) -> Optional[DriveFile]:
        """
        Convert a file to Google Docs format.
        
        Args:
            file_id: The file ID to convert
            
        Returns:
            DriveFile object for the converted doc
        """
        try:
            # Get the original file metadata
            original = self.get_file(file_id)
            if not original:
                return None
            
            # Copy the file with Google Docs MIME type
            copy_metadata = {
                'name': original.name.rsplit('.', 1)[0] + ' (Google Doc)',
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            f = self.service.files().copy(
                fileId=file_id,
                body=copy_metadata,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            
            return DriveFile(
                id=f['id'],
                name=f['name'],
                mime_type=f['mimeType'],
                web_view_link=f.get('webViewLink')
            )
        except Exception as e:
            print(f"Error converting to Google Doc: {e}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_link(self, file_id: str) -> Optional[str]:
        """Get the web view link for a file."""
        file = self.get_file(file_id)
        return file.web_view_link if file else None

