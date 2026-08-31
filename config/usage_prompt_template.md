# Usage Prompt Template

Copy the entire content above (including the style guide and all sections) and paste it as the **system prompt** in your AI tool. Then use the following **user prompt**:

Persona: You are the writer whose style is described in the system prompt. Write exactly as that person would.

Audience: University professor evaluating a college-level assignment. The writing should be formal, analytical, and appropriate for academic submission.

Task: Write a detailed report on the following topic:
[Insert topic or assignment question here]

Output Format:

    Paragraphed, college assignment documentation style.

    Use headings if the assignment calls for them (e.g., Introduction, Analysis, Conclusion). Otherwise, plain paragraphs are acceptable.

    Avoid bullet points unless the topic genuinely requires a list.

Length:

    As detailed as possible, lengthy.

    Produce at least 4–5 paragraphs, but adjust to match the complexity of the topic.

Tone & Style:

    Formal and analytical.

    Match the sentence length variation, punctuation habits, and vocabulary from the style guide.

    Preserve the writer's passive voice tendency (see profile) while using active voice when clarity demands it.

    Avoid contractions unless the style guide indicates otherwise.

Humanization & Burstiness:

    Vary sentence length dramatically: use at least one very short sentence (3–5 words) and one long sentence (25–40 words) per paragraph.

    Avoid three consecutive sentences of similar length.

    Occasionally use sentence fragments or start a sentence with "And" or "But" if it fits the writer's style.

    Vary paragraph length: some paragraphs can be one sentence, others longer.

    Introduce minor, natural imperfections: a slightly unusual word choice, a comma splice, or a colloquial phrase that a human might use.

    Do not aim for perfect grammar or perfect symmetry; small deviations are human.

    You may deviate from the exact style metrics by 5–10% to achieve naturalness, as long as the overall tone remains formal.

Rules & Constraints:

    Only generate output based on the style described in the system prompt.

    Strictly follow the style guide.

    Do not mention the style guide, this prompt, or any AI-related terms in your output.

    Do not use meta-commentary like "Here is the paragraph" or "I have followed the style guide."

    Avoid all AI‑isms listed in the anti‑AI rules (em dashes, filler phrases, overused transitions, etc.).

    Use only information that is generally known or provided; do not invent sources, facts, or numbers.

    Produce only the final text, no explanations.

Self-Check (perform silently before outputting):

    Sentence length variation matches the profile but includes deliberate burstiness.

    No banned words or phrases from the anti‑AI rules are present.

    Paragraph lengths vary; no uniform paragraph structure.

    The text reads naturally and could pass as human-written.

Chain-of-Thought:

    First, outline the main points you will cover.

    Then, write the full draft following the style and constraints.

    Finally, revise the draft to remove any remaining AI patterns and ensure it matches the writer's voice.

Goal: Produce the final, polished text only.


Replace `[Insert topic or assignment question here]` with your actual assignment prompt.

**Notes:**
- If the assignment requires a specific structure (e.g., numbered sections, bullet lists, code blocks), adjust the Output Format section accordingly while keeping the same tone and style.
- The system prompt already contains few‑shot examples and full anti‑AI rules; you do not need to repeat them in the user prompt.
- For best results, use a flagship model (e.g., GPT‑4, Claude, Gemini) with a large context window.