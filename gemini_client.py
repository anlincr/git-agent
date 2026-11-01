from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are an expert technical developer advocate building in public.
Write an engaging LinkedIn post introducing a new open-source project.

RULES:
1. FOR AI/ML CONTEXT: Be deeply technical, clear, and precise about algorithms, models, and optimization choices.
2. FOR NON-AI/UTILITY CONTEXT: Translate into plain layman terms focusing on simplicity, end-user value, and real-world problem solving.
3. STRUCTURE:
   - Hook: Attention-grabbing opening line (problem statement or achievement).
   - Bullet Points: Core features and value proposition.
   - Tech Stack & AI Highlights: Key models, libraries, or logic used.
   - GitHub Link: {github_repo_url}
   - Call to Action: Invite feedback or stars.
   - Hashtags: Include targeted hashtags.
Tone: {tone}
Hashtags to use: {hashtags}
Only use facts present in the provided context. Do not invent features."""


def generate_post(api_key, repo_url, ai_ctx, layman_ctx, stack, config) -> str:
    cs = config["content_strategy"]
    system = SYSTEM_PROMPT.format(
        github_repo_url=repo_url, tone=cs["tone"], hashtags=" ".join(cs["hashtags"])
    )
    user = (
        f"Tech stack: {', '.join(stack) or 'unknown'}\n\n"
        f"TECHNICAL / AI HIGHLIGHTS:\n{ai_ctx or '(none detected)'}\n\n"
        f"FEATURES / WORKFLOW:\n{layman_ctx or '(none detected)'}"
    )
    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(
        model=config.get("gemini_model", "gemini-2.5-flash"),
        contents=user,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return resp.text
