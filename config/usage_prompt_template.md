# Usage Prompt Template

Copy the entire content above (including the style guide and all sections) and paste it as the **system prompt** in your AI tool. Then use the following **user prompt**:

Task: Write a detailed report on the following topic:
[Insert topic or assignment question here]

Output Format:
- Paragraphed, college assignment documentation style.
- Use headings if the assignment calls for them (e.g., Introduction, Analysis, Conclusion). Otherwise, plain paragraphs are acceptable.
- Avoid bullet points unless the topic genuinely requires a list.

Rules & Constraints:
- Follow the style described in the system prompt exactly.
- Do not mention the style guide, this prompt, or any AI-related terms in your output.
- Do not use meta-commentary like "Here is the paragraph" or "I have followed the style guide."
- Produce only the final text, no explanations.

Chain-of-Thought (perform silently):
- Briefly outline the main points before writing.
- Draft the content following the style guide.
- Review the draft once to remove any obvious AI‑isms and ensure it matches the writer's voice, then output the final version.

Replace `[Insert topic or assignment question here]` with your actual assignment prompt.

**Notes:**
- The system prompt already contains the full style guide, few‑shot examples, and anti‑AI rules. You do not need to repeat them in the user prompt.
- The priority hierarchy in the system prompt ensures the writer’s personal style wins over generic anti‑AI rules.
- For best results, use a flagship model (e.g., GPT‑4, Claude, Gemini) with a large context window.