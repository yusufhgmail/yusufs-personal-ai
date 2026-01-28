# Development TODO List

---

# Queue

## Goal


---

## Doing Queue

- [x] Bug fix: Making sure that the AI is able to access the document even in longer conversations (it doesn't store the doc ID it seems, just the doc name, and then it thinks it can't access the doc)
- [x] Bug fix: When using the "after_text" tool when inserting text into the doc, if the doc has bold text, then the "after_text" tool doesn't find the exact location
- [x] Make sure memory works (before I start editing the attachment - so it learns about me while I edit before I make the edits)
- [x] Ability to edit google docs
- [x] Short-term memory so that it can remember context and instructions when doing longer tasks
- [x] Ensure task brief injection works properly (it's now inserted into the system brief, and it seems to be created properly. I haven't checked if it updates and edits the task properly, or recreates a new task when i switch context completely.)
- [x] Improve the fact remembering system.

---

## Queue Next

### Core
- [ ] Make the workflow more automated and conversational - when asked to do something, the AI should proactively ask clarifying questions and gather more information like a real person would, rather than just blindly executing tasks without thinking. It should engage in a dialogue to understand the full context and requirements before proceeding.

### Side track
- [ ] Compare to Clawdbot's code and see how they've implemented vs. how I've implemented.

---

- [ ] Fix so auth is persistent or easy to reauth

---

## Backlog

- [ ] "Find the parent folder of X" is not in its toolset it seems
- [ ] not sure if the "learning" works, so when it edits my doc, if it actually learns about me and puts learnings into it's memory.

---

# Temp Notes

# Done Milestones
- [x] 2026-01-12: Fix the use case when I can email a response to Miguel: Find email, download doc, convert to docs, move to folder, fill in, respond in email with link to it