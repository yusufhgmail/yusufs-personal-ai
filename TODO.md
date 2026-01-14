# Development TODO List

---

# Queue

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
  - [ ] Improve the fact remembering system. I have 2 branches. In one branch it's a more complex method, in the other it's a more simple. I've saved the complex method but will try the more simple method first to see if it works before I move on to the more complex one. If the simple works, I can discard the "complex method branch".
    - TEMP: The prompt I'm feeding AI to see if it auto-remembers it: "i'm going to build a company called FoundryVerse (we don't need to include the company's name in the questionnaire I think, unless you deem it useful) who will work on reskilling people who are being made unemployed by ai to reskill them into being able to provide value in the new economy. I will reskill them using an ai that will give them both the tools and the coaching and motivation and step by step process to find where they can provide the most value given their personal experiences and current skills and competencies and new skills they could learn that fits their personality, and reskill themselves to be able to provide value in the new economy that is being built. the new economy will require a lot of gig economy workers who can find their place in the new marketplace, and micro-entrepreneurs who build their own ventures. the impact will be big bease in the next coming years we'll see increased disruption in the marketplace with a lot of people being made redundant by ai, unless they can reskill and provide value in a new way required by the new economy. it will be hard for these people to transition without some help and guidance and tools, which is what we aim to provide. this will have a significant impact on the us economy because by making it easier for all these people to transition to the new economy, they will be able to provide much more value than they are capable of even today, and this is how we make the us economy boom - by making this transition as seamless and as effective as possible for as many people as possible." 

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

# Notes

## Remember_fact usage more proactively
Action: Improve the fact remembering system. I have 2 branches. In one branch it's a more complex method, in the other it's a more simple. I've saved the complex method but will try the more simple method first to see if it works before I move on to the more complex one. If the simple works, I can discard the "complex method branch".

TEMP: The prompt I'm feeding AI to see if it auto-remembers it: "i'm going to build a company called FoundryVerse (we don't need to include the company's name in the questionnaire I think, unless you deem it useful) who will work on reskilling people who are being made unemployed by ai to reskill them into being able to provide value in the new economy. I will reskill them using an ai that will give them both the tools and the coaching and motivation and step by step process to find where they can provide the most value given their personal experiences and current skills and competencies and new skills they could learn that fits their personality, and reskill themselves to be able to provide value in the new economy that is being built. the new economy will require a lot of gig economy workers who can find their place in the new marketplace, and micro-entrepreneurs who build their own ventures. the impact will be big bease in the next coming years we'll see increased disruption in the marketplace with a lot of people being made redundant by ai, unless they can reskill and provide value in a new way required by the new economy. it will be hard for these people to transition without some help and guidance and tools, which is what we aim to provide. this will have a significant impact on the us economy because by making it easier for all these people to transition to the new economy, they will be able to provide much more value than they are capable of even today, and this is how we make the us economy boom - by making this transition as seamless and as effective as possible for as many people as possible."

## 2026-01-14 Update: Works but needs to use it more frequently
In llm_logs 429-431 I have an example of where it didn't remember it automatically but did later when I prompted it explicitly to remember. Somehow the system prompt must be even more explicit. Or maybe we need to use another model.

TEST: Try to use another model to see if it works automatically.