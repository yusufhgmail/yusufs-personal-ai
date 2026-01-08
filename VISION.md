# VISION
Below is a high level description of what the system should accomplish. 

I want to build a personal AI that can do work for me.

It should have a connection to my google drive, my gmail, and my other assets - then be able to actually perform work for me.

# Scope of this document
The scope of exactly the type of work the AI should do and the channels and UI will be defined in specific development requests with Cursor and do not need to be specified in this document. The purpose of this document is to give Cursor general guidelines when accommodating such requests.

# Memory and self improvement capabilities
## Three types of memories
The AI system will have three types of memories so that it can perform tasks as efficiently as possible and improve itself constantly:
- **Facts about Yusuf:** Objective information about Yusuf and his world (who his friends are, what he's done, his circumstances) - i.e. information **about** him.
- **Preferences by Yusuf:** How Yusuf wants things done (communication style, output format, decision-making tendencies) - i.e. how the system should **perform and work** when doing tasks for Yusuf.
- **System Improvements:** Meta-level suggestions about the AI's architecture, tools, and capabilities - i.e. how the **system itself can be improved** to accomplish its goals better.

## Inference and self-improvement
Every time Yusuf discusses something with AI, the AI should infer based on Yusuf's messages whether it should update its three memory systems to make itself perform more efficiently.

The AI should:
- Infer from Yusuf's messages whether Yusuf is happy or unhappy with the output, and based on that infer how it can improve its preferences or add system improvement opportunities (for example new tools it might need) to become more efficient in the future.
- If it infers that something is strongly positive or negative, but needs clarification, the AI should explicitly bring this up with Yusuf and ask him about potential improvements.
- The AI might store information about which tasks it has performed historically, or use cases it has been used for, along with the information above, to give itself examples of how it should behave to make Yusuf happy or unhappy.

### Facts
The aim of the Facts memory is that the AI should be able to know everything it needs to know about Yusuf to accomplish tasks without needing to ask him. To accomplish this, facts are for example information about Yusuf, such as:
- Pure facts about Yusuf's life, circumstances, friends, goals, accomplishments, and anything else good to know *about* Yusuf to perform tasks without needing to ask Yusuf in the future.
- Historic events, so that there is a store about what has happened to Yusuf and what Yusuf has done over time.

This facts bank should be large and detailed, updated anytime something important is learned or updated about Yusuf, store dates when those memories were updated (because more recent memories take preference over older memories in case of conflicts), and be searchable in a database (implemented in a way that makes it efficient for AI to search the memory bank for relevant facts whenever it needs to accomplish a task for Yusuf).

### Preferences
Preferences should be stored in such a way that the AI system should be able to search for the relevant preferences any time it will do a task for Yusuf. When a task is requested, the AI should start by loading the relevant preferences into its context so that the task can be done according to Yusuf's preferences. The goal is for the AI to always behave in a way that is aligned with Yusuf's wishes.

Preferences need not necessarily be stored historically, but rather when a new preference is surfaced that seems to contradict an existing preference, the preferences memory is updated to reflect the current most recent state.

### System Improvements
System improvements might also include inferences about how the AI itself is designed (i.e. introspection), and suggestions for how it can be redesigned to do things that it infers that Yusuf might want done, but which are not possible or efficient today based on how it currently is architected or designed. **This includes improvements on how the AI system can become better at introspection itself.**.

Such improvements are meant to be considered by Yusuf when he develops the system itself, for example giving it more tools and features, change its prompts, redesign its architecture, or otherwise. The aim of the system is to help Yusuf make it more capable of accomplishing tasks Yusuf is likely to give it in the future.

The system improvements should be surfaced when Yusuf explicitly asks the AI about how the system itself can be improved (for example when he intends to improve the system), or proactively by the AI when the AI is performing a task, if the AI detects a possible significant improvement that would make it able to perform the task significantly better (or not fail at it). As such, the AI should be able to temporarily mention or switch into a "meta discussion" with Yusuf about how it can be improved to perform its current and future duties better.

# Grand vision
The goal is to have a self-improving (and improving by Yusuf developing it further, through introspection and discussion with Yusuf) personal assistant that becomes more and more aligned with Yusuf at accomplishing tasks effectively and efficiently. In the end, Yusuf wants an assistant that can "be him" and do things as if it was Yusuf himself, with minimal intervention or management.