# Development TODO List

---

## Goal

- [ ] Make sure the use case works where I respond to Miguel via my AI
  - [x] Browse folders and find the folder
  - [x] Open doc and find miguel's email address from within it
  - [x] Find email from miguel
  - [x] Download attachment
  - [ ] Edit attachment (maybe by converting to Google Docs, not sure)
    - [x] Make sure memory works (before I start editing the attachment - so it learns about me while I edit before I make the edits)
    - [x] Ability to edit google docs
    - [ ] Short-term memory so that it can remember context and instructions when doing longer tasks
      - [x] Ensure task brief injection works properly (it's now inserted into the system brief, and it seems to be created properly. I haven't checked if it updates and edits the task properly, or recreates a new task when i switch context completely.)

---

## Doing Queue

- [x] Bug fix: Making sure that the AI is able to access the document even in longer conversations (it doesn't store the doc ID it seems, just the doc name, and then it thinks it can't access the doc)
- [x] Bug fix: When using the "after_text" tool when inserting text into the doc, if the doc has bold text, then the "after_text" tool doesn't find the exact location 

---

## Queue Next

- [ ] 

---

- [ ] 

---

## Backlog

- [ ] "Find the parent folder of X" is not in its toolset it seems
- [ ] not sure if the "learning" works, so when it edits my doc, if it actually learns about me and puts learnings into it's memory.

---

## Notes
