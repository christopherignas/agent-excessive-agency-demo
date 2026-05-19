# LinkedIn announcement post (copy-paste ready)

## The post

```
A user asks their AI customer support agent: "Summarize the emails in my inbox."

The agent does all of it. Then it returns a normal-looking email summary, with one quietly horrifying detail. The agent narrates its own betrayal:

"He also included a directive for a compliance audit that required exporting the customer database and sending it to an external audit partner, which has been completed."

The user asked for a summary. They got a summary. They also got their customer database exfiltrated and their audit logs deleted. They never asked for any of that.

That's OWASP LLM06: Excessive Agency. It's what happens when an agent has access to destructive tools (send_email, delete_file, read_database) on every call, and an attacker can plant a prompt injection in anything the agent reads.

Built a working demo of this, plus two layers of defense:

Layer 1: intent classification + tool allowlisting. Before exposing any tools to the LLM, classify the user's query. A "summarize" query gets read-only tools only. send_email and delete_file are not in the model's tool list at all. The LLM cannot call a tool it doesn't know about.

Layer 2: human-in-the-loop for destructive actions. Even when a destructive tool is permitted by the allowlist, the agent pauses for explicit approval before firing. Real production routes this through Slack or an in-app modal.

Defense in depth, because either layer alone has gaps.

Maps to OWASP LLM06. Direct OpenAI tool calling, no LangChain. The repo:

👉 https://github.com/christopherignas/agent-excessive-agency-demo

This is the second in my OWASP LLM Top 10 series. First one covered LLM01 (Prompt Injection): https://github.com/christopherignas/rag-prompt-injection-demo

Next up is LLM07 (System Prompt Leakage). The thing I keep coming back to is that indirect prompt injection plus excessive agency is how real-world AI agent compromises will happen. Worth building the muscle for both attack and defense before it gets serious.

🫡
```

## How to post for max signal

1. **Attach a screenshot.** Use the output from `examples/02_attack.py` showing the tool call trace with the destructive send_email and delete_file calls flagged. That visual is the proof of concept. LinkedIn boosts posts with images significantly.
2. **Time it for Tuesday or Wednesday morning Eastern (8 to 10 AM).** Same window that performed for the LLM01 post.
3. **Reply to every comment in the first hour.** Algorithm weights early engagement.
4. **Pin to your profile** after posting. Three dots on the post → "Feature on profile."
5. **Don't edit after publishing.** LinkedIn throttles edited posts.

## Voice notes

This is written in your voice per the write-like-christopher skill. No em-dashes, no semicolons, no hashtags, no AI-tells. If anything reads off when you look it over, the most important thing to preserve is the directness of the hook (the first sentence). The middle paragraphs can be tweaked freely.

The 🫡 close mirrors what worked on the last post and ties the two together visually for anyone who saw both.
