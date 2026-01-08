# VISION

## Vision Statement

This is a **Personal AI Assistant** that performs real work tasks while continuously learning from user feedback to become better at working with its specific user. The vision is an assistant that understands your preferences, communication style, and work patterns through observation and adaptation—becoming more useful and accurate over time without manual configuration.

## Envisioned Use Cases

### Email Management Workflows

The assistant should handle complete email workflows:

1. **Natural Language Email Queries**
   - "Find emails from John about the project"
   - "Show me unread emails from last week"
   - "What did Sarah say about the meeting?"

2. **Email Composition & Review**
   - "Draft a response to the email about the deadline"
   - "Reply to John's email, make it professional but friendly"
   - "Create a follow-up email for the client meeting"

3. **Email Actions**
   - "Send that draft after I review it"
   - "Save the attachment from that email to Drive"
   - "Archive all emails about the old project"

### Google Drive Workflows

The assistant should manage files and documents:

1. **File Discovery**
   - "Find the document about the Q4 budget"
   - "Show me all Google Docs I created last month"
   - "What files do I have related to the marketing campaign?"

2. **Document Management**
   - "Read the project proposal and summarize it"
   - "Create a new Google Doc with the meeting notes"
   - "Convert that PDF to a Google Doc"
   - "Upload this file to my Drive"

3. **Content Creation**
   - "Create a document with the email template"
   - "Draft a document based on our conversation"

### Learning & Adaptation

The assistant should learn from every interaction:

1. **Style Learning**
   - Observes when you edit drafts and learns your writing style
   - Adapts tone (formal/casual) based on your corrections
   - Learns your preferred email length and structure

2. **Preference Learning**
   - Remembers how you like to organize information
   - Learns your communication patterns
   - Adapts to your work habits over time

3. **Context Learning**
   - Understands relationships between tasks
   - Remembers previous conversations and decisions
   - Builds context about your projects and contacts

## Vision for Success

The system achieves its vision when:

1. **Seamless Workflow**: You can delegate email and document tasks naturally through conversation
2. **Continuous Improvement**: The assistant gets better at your specific tasks without you teaching it explicitly
3. **Reduced Friction**: Over time, drafts require fewer edits because the assistant learned your preferences
4. **Transparency**: You can see what the assistant learned and why it made certain decisions
5. **Trust**: You feel confident delegating tasks because you maintain control and can see the learning process
6. **Efficiency**: Tasks that used to take multiple iterations now work on the first or second try

## Core Values

These values guide all design decisions:

1. **User Agency**: You always have final control over actions—nothing happens without your approval
2. **Continuous Improvement**: The system gets better through use, not through manual configuration
3. **Simplicity**: Architecture and workflows remain simple and understandable
4. **Privacy**: Your data stays in your control (Supabase, your Google account)
5. **Transparency**: You can see what was learned, why decisions were made, and how guidelines evolved

## Design Principles

When making decisions, the system should:

1. **Prioritize Learning**: Every feature should either enable learning or benefit from learned patterns
2. **Maintain Simplicity**: Avoid complexity that obscures how the system works
3. **Respect User Control**: Never take irreversible actions without explicit approval
4. **Stay Focused**: Concentrate on email, Drive, and learning—avoid scope creep
5. **Be Transparent**: Make the learning process visible and understandable

## Architecture Vision

The system should maintain:

1. **Single Agent Design**
   - ReAct-style (Reasoning + Acting) agent pattern
   - Simple loop: think → act → observe → repeat
   - No complex multi-agent orchestration

2. **Learning-Centered Architecture**
   - Every interaction is a potential learning opportunity
   - Learning happens automatically through observation
   - Guidelines are the single source of truth for user preferences

3. **User Control at Every Step**
   - All drafts require explicit user approval
   - User can edit drafts directly
   - User can provide feedback that gets learned
   - Guidelines are readable and manually editable

4. **Simple & Accessible Interface**
   - Discord as the primary interface (simple, accessible, always available)
   - Supabase for persistent storage (guidelines, conversations)
   - Optional Google API integrations (works without them)

## Design Constraints

To maintain focus and simplicity:

- **Interface**: Discord (not web UI, not CLI-only)
- **Storage**: Supabase (not local files, not other databases)
- **LLM**: OpenAI or Anthropic (configurable, but not other providers without good reason)
- **Scope**: Email and Drive management (not calendar, not other Google services unless they serve email/Drive workflows)
- **Learning**: Pattern-based learning from edits/feedback (not machine learning model training)
- **User Model**: Personal assistant for a single user (not multi-user or team collaboration)

## Decision-Making Principles

When considering new features or changes, ask:

1. Does this serve the vision of a personal assistant that learns?
2. Does this maintain simplicity, or does it add unnecessary complexity?
3. Does this respect user control and privacy?
4. Does this fit within the existing architecture (Discord → Agent → Tools → Learning)?
5. Will this feature help the system learn better, or is it just "nice to have"?

If the answer to any of these is "no", reconsider the feature or redesign it to align with the vision.

