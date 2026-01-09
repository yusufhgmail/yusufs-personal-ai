"""Tool definitions for the agent."""

from typing import Callable, Any, Optional
from dataclasses import dataclass

from storage.facts_store import FactsStore


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
        self._docs_client = None
        self._facts_store = None
    
    def set_gmail_client(self, client):
        """Set the Gmail client for email tools."""
        self._gmail_client = client
    
    def set_drive_client(self, client):
        """Set the Google Drive client for file tools."""
        self._drive_client = client
    
    def set_docs_client(self, client):
        """Set the Google Docs client for document editing tools."""
        self._docs_client = client
    
    def set_facts_store(self, store: FactsStore):
        """Set the facts store for memory tools."""
        self._facts_store = store
    
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
def create_default_registry(gmail_client=None, drive_client=None, docs_client=None, facts_store=None) -> ToolRegistry:
    """Create a tool registry with default tools."""
    registry = ToolRegistry()
    
    if gmail_client:
        registry.set_gmail_client(gmail_client)
    if drive_client:
        registry.set_drive_client(drive_client)
    if docs_client:
        registry.set_docs_client(docs_client)
    
    # Initialize facts store (create one if not provided)
    if facts_store is None:
        facts_store = FactsStore()
    registry.set_facts_store(facts_store)
    
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
    
    def download_attachment(email_id: str, filename: str, folder_id: Optional[str] = None) -> str:
        """Download an email attachment by filename and save to Google Drive."""
        if registry._gmail_client is None:
            return f"[Gmail not configured] Would download attachment from email: {email_id}"
        
        if registry._drive_client is None:
            return f"[Google Drive not configured] Cannot save attachment"
        
        try:
            # Download the attachment using filename-based lookup
            # This handles both regular and inline attachments internally
            data, mime_type = registry._gmail_client.get_attachment_data(email_id, filename)
        except ValueError as e:
            return f"Error downloading attachment: {str(e)}"
        except Exception as e:
            return f"Unexpected error downloading attachment: {str(e)}"
        
        # Upload to Drive (with optional folder)
        result = registry._drive_client.upload_file(
            name=filename,
            content=data,
            mime_type=mime_type,
            folder_id=folder_id
        )
        
        if result:
            folder_info = f" (in folder)" if folder_id else ""
            return f"Saved attachment to Drive{folder_info}:\n- Name: {result.name}\n- ID: {result.id}\n- Link: {result.web_view_link}"
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
        description="Download an email attachment by filename and save it to Google Drive. Use the exact filename shown when reading the email.",
        func=download_attachment,
        parameters={
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID containing the attachment"},
                "filename": {"type": "string", "description": "The exact filename of the attachment to download"},
                "folder_id": {"type": "string", "description": "Optional: Google Drive folder ID to save the file to. Use list_drive_folders to find folder IDs."}
            },
            "required": ["email_id", "filename"]
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
    
    def list_drive_folders(parent_folder_id: Optional[str] = None) -> str:
        """List folders in Google Drive to help find the right destination for files."""
        if registry._drive_client is None:
            return "[Google Drive not configured]"
        
        folders = registry._drive_client.list_folders(parent_id=parent_folder_id)
        
        if not folders:
            if parent_folder_id:
                return "No subfolders found in the specified folder."
            return "No folders found in Google Drive."
        
        location = "in the specified folder" if parent_folder_id else "in Google Drive"
        result = f"Found {len(folders)} folder(s) {location}:\n\n"
        for folder in folders:
            result += f"- **{folder.name}**\n"
            result += f"  ID: {folder.id}\n"
            if folder.web_view_link:
                result += f"  Link: {folder.web_view_link}\n"
            result += "\n"
        return result
    
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
    
    registry.register(Tool(
        name="list_drive_folders",
        description="List folders in Google Drive. Use this to find folder IDs for saving attachments or files to specific locations.",
        func=list_drive_folders,
        parameters={
            "type": "object",
            "properties": {
                "parent_folder_id": {"type": "string", "description": "Optional: ID of a parent folder to list subfolders of. If not provided, lists top-level accessible folders."}
            },
            "required": []
        }
    ))
    
    # Google Docs editing tools
    def get_doc_structure(document_id: str) -> str:
        """Get the document structure with character indices for precise editing."""
        if registry._docs_client is None:
            return f"[Google Docs not configured] Would get structure of: {document_id}"
        
        doc = registry._docs_client.get_document(document_id)
        if not doc:
            return f"Could not find document with ID: {document_id}"
        
        result = f"**{doc.title}** (Document ID: {doc.document_id})\n\n"
        result += f"**First paragraph index**: {doc.first_paragraph_index} (use for inserting at beginning)\n"
        result += f"**End index**: {doc.end_index} (use for appending)\n\n"
        result += "**Content with indices** (use these indices for editing):\n\n"
        
        for segment in doc.segments:
            # Show the text with its index range
            text_preview = segment.text.replace('\n', '\\n')
            result += f"[{segment.start_index}-{segment.end_index}] \"{text_preview}\"\n"
        
        return result
    
    def edit_google_doc(document_id: str, action: str, text: Optional[str] = None, 
                        index: Optional[int] = None, start_index: Optional[int] = None, 
                        end_index: Optional[int] = None, find_text: Optional[str] = None, 
                        replace_text: Optional[str] = None, after_text: Optional[str] = None) -> str:
        """Edit a Google Doc using various actions."""
        if registry._docs_client is None:
            return f"[Google Docs not configured] Would edit document: {document_id}"
        
        if action == "insert":
            if text is None or index is None:
                return "Error: 'insert' action requires 'text' and 'index' parameters"
            success = registry._docs_client.insert_text(document_id, text, index)
            if success:
                return f"Successfully inserted text at index {index}"
            return "Failed to insert text. Make sure the index is within a paragraph (use get_doc_structure to find valid indices)."
        
        elif action == "insert_beginning":
            if text is None:
                return "Error: 'insert_beginning' action requires 'text' parameter"
            success = registry._docs_client.insert_at_beginning(document_id, text)
            if success:
                return "Successfully inserted text at the beginning of the document"
            return "Failed to insert text at beginning"
        
        elif action == "insert_after":
            if text is None or after_text is None:
                return "Error: 'insert_after' action requires 'text' and 'after_text' parameters"
            success = registry._docs_client.insert_after_text(document_id, after_text, text)
            if success:
                return f"Successfully inserted text after '{after_text[:50]}...'" if len(after_text) > 50 else f"Successfully inserted text after '{after_text}'"
            return f"Failed to insert text. Could not find '{after_text[:50]}...' in the document" if len(after_text) > 50 else f"Failed to insert text. Could not find '{after_text}' in the document"
        
        elif action == "delete":
            if start_index is None or end_index is None:
                return "Error: 'delete' action requires 'start_index' and 'end_index' parameters"
            success = registry._docs_client.delete_range(document_id, start_index, end_index)
            if success:
                return f"Successfully deleted content from index {start_index} to {end_index}"
            return "Failed to delete content"
        
        elif action == "replace":
            if find_text is None or replace_text is None:
                return "Error: 'replace' action requires 'find_text' and 'replace_text' parameters"
            count = registry._docs_client.replace_all_text(document_id, find_text, replace_text)
            if count >= 0:
                return f"Replaced {count} occurrence(s) of '{find_text}' with '{replace_text}'"
            return "Failed to replace text"
        
        elif action == "append":
            if text is None:
                return "Error: 'append' action requires 'text' parameter"
            success = registry._docs_client.append_text(document_id, text)
            if success:
                return "Successfully appended text to the document"
            return "Failed to append text"
        
        else:
            return f"Unknown action: {action}. Valid actions are: insert, insert_beginning, insert_after, delete, replace, append"
    
    # Register Google Docs tools
    registry.register(Tool(
        name="get_doc_structure",
        description="Get a Google Doc's content with character indices. Use this before editing to find the exact positions where you want to insert, delete, or modify text.",
        func=get_doc_structure,
        parameters={
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "The Google Doc ID (e.g. '1AH-mD6oY...' - get this from search_drive_files, NOT the document name)"}
            },
            "required": ["document_id"]
        }
    ))
    
    registry.register(Tool(
        name="edit_google_doc",
        description="Edit a Google Doc. Actions: insert (at index), insert_beginning (at start), insert_after (after specific text), delete (range), replace (find/replace all), append (at end). For Q&A docs, use insert_after with the question text to add an answer right after it.",
        func=edit_google_doc,
        parameters={
            "type": "object",
            "properties": {
                "document_id": {"type": "string", "description": "The Google Doc ID (e.g. '1AH-mD6oY...' - get this from search_drive_files, NOT the document name)"},
                "action": {"type": "string", "description": "Action: 'insert', 'insert_beginning', 'insert_after', 'delete', 'replace', or 'append'"},
                "text": {"type": "string", "description": "Text to insert or append (for insert/insert_beginning/insert_after/append actions)"},
                "index": {"type": "integer", "description": "Position to insert text at (for insert action). Use get_doc_structure to find indices."},
                "after_text": {"type": "string", "description": "Text to search for and insert after (for insert_after action). The new text will be added right after this text."},
                "start_index": {"type": "integer", "description": "Start of range to delete (for delete action, inclusive)"},
                "end_index": {"type": "integer", "description": "End of range to delete (for delete action, exclusive)"},
                "find_text": {"type": "string", "description": "Text to find (for replace action)"},
                "replace_text": {"type": "string", "description": "Text to replace with (for replace action)"}
            },
            "required": ["document_id", "action"]
        }
    ))
    
    # Memory tools - for storing facts about Yusuf
    def remember_fact(fact: str) -> str:
        """Store a fact about Yusuf in memory."""
        if registry._facts_store is None:
            return "[Facts store not configured] Would remember: " + fact
        
        try:
            stored_fact = registry._facts_store.add_fact(fact)
            return f"Remembered: {fact}"
        except Exception as e:
            return f"Failed to store fact: {str(e)}"
    
    def list_facts() -> str:
        """List all stored facts about Yusuf."""
        if registry._facts_store is None:
            return "[Facts store not configured]"
        
        facts = registry._facts_store.get_all_facts()
        if not facts:
            return "No facts stored yet."
        
        result = f"Stored facts about Yusuf ({len(facts)}):\n\n"
        for fact in facts:
            date_str = fact.created_at.strftime("%Y-%m-%d")
            result += f"- [{date_str}] {fact.content}\n"
        return result
    
    def forget_fact(fact_id: int) -> str:
        """Delete a fact from memory."""
        if registry._facts_store is None:
            return "[Facts store not configured]"
        
        if registry._facts_store.delete_fact(fact_id):
            return f"Deleted fact with ID: {fact_id}"
        return f"Could not find fact with ID: {fact_id}"
    
    # Register memory tools
    registry.register(Tool(
        name="remember_fact",
        description="Store a fact about Yusuf in memory. Use this when Yusuf shares important information about himself, his life, people he knows, events, goals, or circumstances. Facts should be objective information, not preferences.",
        func=remember_fact,
        parameters={
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "The fact to remember (e.g., 'Miguel is a friend who works at Google' or 'Yusuf started his company in 2020')"}
            },
            "required": ["fact"]
        }
    ))
    
    registry.register(Tool(
        name="list_facts",
        description="List all stored facts about Yusuf from memory.",
        func=list_facts,
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    ))
    
    registry.register(Tool(
        name="forget_fact",
        description="Delete a fact from memory by its ID. Use list_facts first to find the ID.",
        func=forget_fact,
        parameters={
            "type": "object",
            "properties": {
                "fact_id": {"type": "integer", "description": "The ID of the fact to delete"}
            },
            "required": ["fact_id"]
        }
    ))
    
    return registry

