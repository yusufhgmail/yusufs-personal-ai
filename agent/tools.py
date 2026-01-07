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
    
    return registry

