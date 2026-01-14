# Development TODO List

---

# Queue

## Goal

- [ ] Make sure the use case works where I respond to Miguel via my AI
  - [x] Browse folders and find the folder
  - [x] Open doc and find miguel's email address from within it
  - [x] Find email from miguel
  - [x] Download attachment
  - [x] Edit attachment (maybe by converting to Google Docs, not sure)
    - [ ] Bug when updating the preferences / guidelines table - it overrides the agent's work and disrupts the agent from doing its thing.

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

- [ ] 

---

- [ ] 

---

## Backlog

- [ ] "Find the parent folder of X" is not in its toolset it seems
- [ ] not sure if the "learning" works, so when it edits my doc, if it actually learns about me and puts learnings into it's memory.

---

# Notes

## Guidelines Overrides Agent Bug
See 'llm_logs' row 464 and compare to https://drive.google.com/file/d/1t8DT3n0gZYqkUIiOvFT4uew3TFtccEZE/view?usp=drivesdk. In the image you see that I chatted with discord and said "I want to continue answering all the questions one by one. what's q3?", but the agent interpreted it as a guideline (which in itself isn't necessarily wrong), but the way the guideline process is implemented is wrong. We see in the table 'llm_logs' that the col "Original User Message" somehow was overridden by the guidelines update (screenshot: https://drive.google.com/file/d/1slkteqfwmCUzn818SHHy_GfnEZjbaDqQ/view?usp=drivesdk, text: "The user provided this feedback on the previous draft: I want to continue answering all the questions one by one. what's q3?. Please incorporate their feedback.") However the even weirder part is that in the response from AI, it provided this answer: "THOUGHT: Yusuf wants to proceed with answering the questions in the NIW Expansion Questionnaire one by one. I'll provide the details for Question 3.
FOCUS: Continuing with the NIW Expansion Questionnaire, moving to Question 3
FINAL_ANSWER: Let's move on to Question 3: "Explain how your work is in the national interest of the United States." Please share any thoughts or details you'd like to include, and I can help formulate an answer for this question.". This is not even the correct text from Question 3 so I don't know how it got this text.