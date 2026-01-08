# VISION

---
# Temp
I want to build a personal AI that can do work for me.

It should have a connection to my google drive, my gmail, and my other assets - then be able to actually perform work for me.

It needs to have a memory that works like this:
- When I tell it something, it should always analyze my message and try to extract my "general guidelines for how it should work", then compare it with its current understanding of how it wants me to work (saved in its internal memory as text), and improve that understanding. There is an "intention interpreter agent" that does this continuously in parallel to the executor agent who actually executes my requests.
- Every time I ask it to do something, this "intention interpreter agent" will compare what I asked to this saved memory state and ask itself "is Yusuf happy with my work? If not, how can I improve my work so that he becomes more happy?" If he can't figure out what that is, he can ask me by mentioning that he feels that I'm not happy, and having a discussion with me about how he can improve the way he works to make me more happy.
- The intention interpreter ai should list the following things in the document:
  - Tools he lacks but could have to make me even happier (only if significant). he should save those tools in his internal "general guidelines" document for discussion with me later.
  - memories he should save to make me happier
  - looking at the input (my words + the info he gathers through the tools) and the output that is produced, and trying to infer what can be improved in the ai system itself to make me happier, and again saving those in its "general guidelines" db or doc.
- When I ask it for how we can improve our collab or improve the system itself, the "intention interpreter agent" (or another agent responsible for "discussing with yusuf to improve the system itself", let's call it "system improver agent" should take over and have a discussion with yusuf.

Over time I'm planning to give this tool tasks, and every time I give it a task, I want to also look at the results, and discuss with it how we can improve it (or by doing it myself without discussing with it). I envision that doing this repeatedly, over time, I'll have an amazing "general agent" who can do anything for me.

## Project Vision & Goals

This project aims to build a **personal AI assistant that can actually perform work** and continuously improve through learning.

### Core Vision

The assistant should be able to:
- **Perform real work** - Execute tasks end-to-end (starting with email responses with attachments)
- **Connect to your assets** - Access Google Drive, Gmail, and other services to work with your actual data
- **Learn continuously** - Improve its understanding of how you want things done through every interaction
- **Adapt and improve** - Become better at working with you over time through feedback and iterative refinement.

### Key Learning Mechanism

An agent can do almost anything given the right prompts and tools. The differentiator is not capability - it's **personalization**:

- Continuously monitors all conversations and document edits (not just initial instructions)
- Extracts general guidelines from your feedback, corrections, and edits
- Learns your preferences, writing style, and working patterns
- Saves improvement suggestions for discussion
- Cannot determine what needs improvement from initial instructions alone - it learns primarily from:
  - Your edits to drafts/suggestions
  - Your feedback during discussions (e.g., "you did something wrong")
  - Document diffs showing how you changed things
  - Learning how YOU work, YOUR style, YOUR preferences
- Understanding YOUR specific data, workflows, and needs
- Improving its work FOR YOU through YOUR feedback

### Architecture Philosophy
The value comes from making the agent better at working with you specifically.

### The Learning Loop (Core of the System)
```
1. You give a task
2. Agent executes, produces draft/result
3. You edit the draft OR give feedback
4. Learning Observer extracts pattern:
   - WHAT changed (diff analysis)
   - WHY it changed (infer from context)
   - GUIDELINE to add (structured rule)
5. Guidelines document updated
6. Next similar task uses updated guidelines
7. MEASURE: Did this task require fewer edits?
```

This loop is THE core of the system. Everything else serves this loop.

```
┌─────────────────────────────────────────────────────────┐
│                     Discord Interface                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Single Agent                          │
│  (ReAct-style: reasons, plans, and executes inline)     │
│  - Loads guidelines into context                         │
│  - Uses tools to perform actions                         │
│  - Produces drafts for approval                          │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│   Tool Registry      │    │   Learning Observer          │
│   - Gmail            │    │   - Monitors all interactions│
│   - Google Drive     │    │   - Analyzes edits/feedback  │
│   - Discord          │    │   - Updates guidelines       │
└──────────────────────┘    └──────────────────────────────┘
                                          │
                                          ▼
                            ┌──────────────────────────────┐
                            │   Guidelines Document        │
                            │   (THE centerpiece)          │
                            │   - Structured rules         │
                            │   - Version history          │
                            │   - Injected into prompts    │
                            └──────────────────────────────┘
                                          │
                                          ▼
                            ┌──────────────────────────────┐
                            │   Supabase                   │
                            │   - guidelines (with history)│
                            │   - interactions (context)   │
                            └──────────────────────────────┘
```



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


- Uses ReAct pattern: Reason → Act → Observe → Repeat
- Loads relevant guidelines into context before each action
- Has access to all tools (Gmail, Drive, Discord)
- Produces drafts for approval when needed
- Can handle any task - no specialized agents

**What it learns from**:
- Your edits to drafts (diff analysis)
- Your feedback during conversation ("you did this wrong", "I prefer X")
- Your corrections and clarifications

**What it produces**:
- New guidelines to add
- Updates to existing guidelines
- Suggestions for discussion (stored for later review)

## Decision-Making Principles

When considering new features or changes, ask:

1. Does this serve the vision of a personal assistant that learns?
2. Does this maintain simplicity, or does it add unnecessary complexity?
3. Does this respect user control and privacy?
4. Does this fit within the existing architecture (Discord → Agent → Tools → Learning)?
5. Will this feature help the system learn better, or is it just "nice to have"?

If the answer to any of these is "no", reconsider the feature or redesign it to align with the vision.

