"""Tool definitions for the agent."""

from typing import Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class Tool:
    """A tool the agent can use."""
    name: str
    description: str
    func: Callable[..., Any]
    parameters: dict  # JSON schema for parameters


class ToolRegistry:
    """Registry of available tools."""
    
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self._gmail_client = None
        self._drive_client = None
    
    def set_gmail_client(self, client):
        """Set the Gmail client for email tools."""
        self._gmail_client = client
    
    def set_drive_client(self, client):
        """Set the Google Drive client for file tools."""
        self._drive_client = client
    
    def register(self, tool: Tool):
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def execute(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with given arguments."""
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Unknown tool: {name}")
        return tool.func(**kwargs)
    
    def get_descriptions(self) -> str:
        """Get formatted descriptions of all tools."""
        lines = []
        for name, tool in self.tools.items():
            lines.append(f"- **{name}**: {tool.description}")
            if tool.parameters.get("properties"):
                lines.append("  Parameters:")
                for param_name, param_info in tool.parameters["properties"].items():
                    required = param_name in tool.parameters.get("required", [])
                    req_str = " (required)" if required else ""
                    lines.append(f"    - {param_name}: {param_info.get('description', '')}{req_str}")
        return "\n".join(lines)


# Create default tool registry
def create_default_registry(gmail_client=None, drive_client=None) -> ToolRegistry:
    """Create a tool registry with default tools."""
    registry = ToolRegistry()
    
    if gmail_client:
        registry.set_gmail_client(gmail_client)
    if drive_client:
        registry.set_drive_client(drive_client)
    
    # Gmail tools
    def search_emails(query: str, max_results: int = 5) -> str:
        """Search for emails matching the query."""
        if registry._gmail_client is None:
            return "[Gmail not configured] Would search for: " + query
        
        emails = registry._gmail_client.search_emails(query, max_results)
        if not emails:
            return "No emails found matching your query."
        
        result = f"Found {len(emails)} email(s):\n\n"
        for email in emails:
            result += f"- **ID**: {email.id}\n"
            result += f"  **From**: {email.sender}\n"
            result += f"  **Subject**: {email.subject}\n"
            result += f"  **Date**: {email.date}\n"
            result += f"  **Preview**: {email.snippet[:100]}...\n\n"
        return result
    
    def read_email(email_id: str) -> str:
        """Read the content of a specific email."""
        if registry._gmail_client is None:
            return f"[Gmail not configured] Would read email: {email_id}"
        
        email = registry._gmail_client.read_email(email_id)
        if not email:
            return f"Could not find email with ID: {email_id}"
        
        result = f"**From**: {email.sender}\n"
        result += f"**To**: {email.to}\n"
        result += f"**Subject**: {email.subject}\n"
        result += f"**Date**: {email.date}\n\n"
        result += f"**Body**:\n{email.body}\n"
        
        if email.attachments:
            result += f"\n**Attachments** ({len(email.attachments)}):\n"
            for att in email.attachments:
                result += f"- {att.filename} ({att.mime_type}, {att.size} bytes)\n"
        
        return result
    
    def create_email_draft(to: str, subject: str, body: str, reply_to: Optional[str] = None) -> str:
        """Create an email draft."""
        if registry._gmail_client is None:
            return f"[Gmail not configured] Would create draft to {to}: {subject}"
        
        draft_id = registry._gmail_client.create_draft(to, subject, body, reply_to)
        return f"Created draft with ID: {draft_id}"
    
    def send_draft(draft_id: str) -> str:
        """Send a previously created email draft."""
        if registry._gmail_client is None:
            return f"[Gmail not configured] Would send draft: {draft_id}"
        
        message_id = registry._gmail_client.send_draft(draft_id)
        return f"Email sent successfully! Message ID: {message_id}"
    
    def download_attachment(email_id: str, attachment_id: str, filename: str) -> str:
        """Download an email attachment and save to Drive."""
        if registry._gmail_client is None:
            return f"[Gmail not configured] Would download attachment from email: {email_id}"
        
        # Download the attachment
        data = registry._gmail_client.download_attachment(email_id, attachment_id)
        
        if registry._drive_client is None:
            return f"Downloaded attachment ({len(data)} bytes) but Drive not configured to save it"
        
        # Determine mime type from filename
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Upload to Drive
        result = registry._drive_client.upload_file(
            name=filename,
            content=data,
            mime_type=mime_type
        )
        
        if result:
            return f"Saved attachment to Drive:\n- Name: {result.name}\n- ID: {result.id}\n- Link: {result.web_view_link}"
        return "Failed to save attachment to Drive"
    
    # Register tools
    registry.register(Tool(
        name="search_emails",
        description="Search for emails matching a query (Gmail search syntax supported)",
        func=search_emails,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g., 'from:someone@example.com subject:meeting')"},
                "max_results": {"type": "integer", "description": "Maximum number of results", "default": 5}
            },
            "required": ["query"]
        }
    ))
    
    registry.register(Tool(
        name="read_email",
        description="Read the full content of a specific email including body and attachments",
        func=read_email,
        parameters={
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The ID of the email to read"}
            },
            "required": ["email_id"]
        }
    ))
    
    registry.register(Tool(
        name="create_email_draft",
        description="Create an email draft (does not send it). Returns draft ID for review.",
        func=create_email_draft,
        parameters={
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body": {"type": "string", "description": "Email body content"},
                "reply_to": {"type": "string", "description": "Optional: Message ID to reply to"}
            },
            "required": ["to", "subject", "body"]
        }
    ))
    
    registry.register(Tool(
        name="send_draft",
        description="Send a previously created email draft",
        func=send_draft,
        parameters={
            "type": "object",
            "properties": {
                "draft_id": {"type": "string", "description": "The ID of the draft to send"}
            },
            "required": ["draft_id"]
        }
    ))
    
    registry.register(Tool(
        name="download_attachment",
        description="Download an email attachment and save it to Google Drive",
        func=download_attachment,
        parameters={
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID containing the attachment"},
                "attachment_id": {"type": "string", "description": "The attachment ID"},
                "filename": {"type": "string", "description": "The filename to save as"}
            },
            "required": ["email_id", "attachment_id", "filename"]
        }
    ))
    
    # Google Drive tools
    def search_files(query: str, max_results: int = 10) -> str:
        """Search for files in Google Drive."""
        if registry._drive_client is None:
            return f"[Google Drive not configured] Would search for: {query}"
        
        files = registry._drive_client.search_files(query, max_results)
        if not files:
            return "No files found matching your query."
        
        result = f"Found {len(files)} file(s):\n\n"
        for f in files:
            result += f"- **{f.name}**\n"
            result += f"  ID: {f.id}\n"
            result += f"  Type: {f.mime_type}\n"
            if f.web_view_link:
                result += f"  Link: {f.web_view_link}\n"
            result += "\n"
        return result
    
    def read_drive_file(file_id: str) -> str:
        """Read the content of a file from Google Drive."""
        if registry._drive_client is None:
            return f"[Google Drive not configured] Would read file: {file_id}"
        
        file_info = registry._drive_client.get_file(file_id)
        if not file_info:
            return f"Could not find file with ID: {file_id}"
        
        # For Google Docs, export as plain text
        if file_info.mime_type == 'application/vnd.google-apps.document':
            content = registry._drive_client.export_google_doc(file_id, 'text/plain')
            if content:
                return f"**{file_info.name}** (Google Doc):\n\n{content}"
            return f"Could not read content of: {file_info.name}"
        
        # For other files, try to download
        content = registry._drive_client.download_file(file_id)
        if content:
            try:
                return f"**{file_info.name}**:\n\n{content.decode('utf-8')}"
            except UnicodeDecodeError:
                return f"**{file_info.name}** is a binary file ({len(content)} bytes)"
        
        return f"Could not read content of: {file_info.name}"
    
    def upload_to_drive(name: str, content: str, folder_id: Optional[str] = None) -> str:
        """Upload text content as a file to Google Drive."""
        if registry._drive_client is None:
            return f"[Google Drive not configured] Would upload: {name}"
        
        result = registry._drive_client.upload_file(
            name=name,
            content=content.encode('utf-8'),
            mime_type='text/plain',
            folder_id=folder_id
        )
        
        if result:
            return f"Uploaded file: {result.name}\nID: {result.id}\nLink: {result.web_view_link}"
        return "Failed to upload file"
    
    def create_google_doc(name: str, folder_id: Optional[str] = None) -> str:
        """Create a new Google Doc."""
        if registry._drive_client is None:
            return f"[Google Drive not configured] Would create doc: {name}"
        
        result = registry._drive_client.create_google_doc(name=name, folder_id=folder_id)
        
        if result:
            return f"Created Google Doc: {result.name}\nID: {result.id}\nLink: {result.web_view_link}"
        return "Failed to create Google Doc"
    
    def convert_to_google_doc(file_id: str) -> str:
        """Convert a file to Google Docs format."""
        if registry._drive_client is None:
            return f"[Google Drive not configured] Would convert file: {file_id}"
        
        result = registry._drive_client.convert_to_google_doc(file_id)
        
        if result:
            return f"Converted to Google Doc: {result.name}\nID: {result.id}\nLink: {result.web_view_link}"
        return "Failed to convert file to Google Doc"
    
    # Register Drive tools
    registry.register(Tool(
        name="search_drive_files",
        description="Search for files in Google Drive",
        func=search_files,
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (Drive API format, e.g., \"name contains 'report'\")"},
                "max_results": {"type": "integer", "description": "Maximum number of results", "default": 10}
            },
            "required": ["query"]
        }
    ))
    
    registry.register(Tool(
        name="read_drive_file",
        description="Read the content of a file from Google Drive",
        func=read_drive_file,
        parameters={
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "The ID of the file to read"}
            },
            "required": ["file_id"]
        }
    ))
    
    registry.register(Tool(
        name="upload_to_drive",
        description="Upload text content as a file to Google Drive",
        func=upload_to_drive,
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the file"},
                "content": {"type": "string", "description": "Text content to upload"},
                "folder_id": {"type": "string", "description": "Optional folder ID to upload to"}
            },
            "required": ["name", "content"]
        }
    ))
    
    registry.register(Tool(
        name="create_google_doc",
        description="Create a new empty Google Doc",
        func=create_google_doc,
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the document"},
                "folder_id": {"type": "string", "description": "Optional folder ID"}
            },
            "required": ["name"]
        }
    ))
    
    registry.register(Tool(
        name="convert_to_google_doc",
        description="Convert a file (e.g., Word doc) to Google Docs format",
        func=convert_to_google_doc,
        parameters={
            "type": "object",
            "properties": {
                "file_id": {"type": "string", "description": "The ID of the file to convert"}
            },
            "required": ["file_id"]
        }
    ))
    
    return registry

