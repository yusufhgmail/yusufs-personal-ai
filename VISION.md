# VISION
Below is a high level description of what the system should accomplish. 

I want to build a personal AI that can do work for me.

It should have a connection to my google drive, my gmail, and my other assets - then be able to actually perform work for me.

## Three types of memories
The AI system will have three types of memories about Yusuf so that it can perform tasks as efficiently as possible and improve itself constantly:
- Preferences
- System improvements 
- Facts

### Inference and self improvement
Every time Yusuf discusses something with AI, the AI should infer based on Yusuf's messages whether it can improve its three memory systems to make itself perform more efficiently.

The AI should:
- Infer from Yusuf's messages whether Yusuf is happy or unhappy with the output, and based on that infer how it can improve its preferences or add system improvement opportunities (for example new tools it might need) to become more efficient in the future.
- If it infers that something is strongly positive or negative, but needs clarification, the AI should explicitly bring this up with Yusuf and ask him about potential improvements.
- The AI might store information about which tasks it has performed historically, or use cases it has been used for, along with the information above, to give itself examples of how it should behave to make Yusuf happy or unhappy.

System improvements might also include inferences about how the AI itself is designed (i.e. introspection), and suggestions for how it can be redesigned to do things that it infers that Yusuf might want done, but which are not possible or efficient today based on how it currently is architected or designed. **This includes improvements on how the AI system can become better at introspection itself.**

The system should, when it deems appropriate or when Yusuf asks it, discuss with Yusuf how Yusuf can improve the system itself (by developing it further, giving it more tools and features, or change its prompts and architecture or otherwise) to make the system more capable of accomplishing tasks Yusuf is likely to give it in the future.

### Facts
The aim of the Facts memory is that the AI should be able to know everything it needs to know about Yusuf to accomplish tasks without needing to ask him. To accompish this, facts are for example information about Yusuf, such as:
- Pure facts about Yusuf's life, circumstances, friends, goals, accomplishments, and anything else good to know *about* Yusuf to perform tasks without needing to ask Yusuf in the future.
- Historic events, so that there is a store about what has happened to Yusuf and what Yusuf has done over time.

This facts bank should be large and detailed, updated anytime something important is learned or updated about Yusuf, store dates when those memories were updated (because more recent memories take preference over older memories in case of conflicts), and be searchable in a database (implemented in a way that makes it efficient for AI to search the memory bank for relevant facts whenever it needs to accomplish a task for Yusuf).

## Grand vision
The goal is to have a self-improving (and improving by Yusuf developing it further, through introspection and discussion with Yusuf) personal assisstant that becomes more and more aligned with Yusuf at accomplishing tasks effectively and efficiently. In the end, Yusuf wants an assistant that can "be him" and do things as if it was Yusuf himself, with minimal intervention or management.