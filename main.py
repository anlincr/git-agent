import json, os, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import git_manager, rag_processor, gemini_client

HERE = Path(__file__).parent


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def main():
    # Stage 1
    load_dotenv(HERE / ".env")
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not target.is_dir():
        sys.exit(f"Error: '{target}' is not a directory.")
    token, key = os.getenv("GITHUB_TOKEN"), os.getenv("GEMINI_API_KEY")
    if not token or not key:
        sys.exit("Error: set GITHUB_TOKEN and GEMINI_API_KEY in .env")
    config = json.loads((HERE / "config.json").read_text())
    log(f"Target: {target}")

    # Stage 2
    log("Publishing to GitHub...")
    repo_url = git_manager.publish(str(target), token, config)
    log(f"Repo: {repo_url}")

    # Stage 3
    log("Extracting project context...")
    ai_ctx, layman_ctx, stack = rag_processor.extract(str(target), config)

    # Stage 4
    log("Generating LinkedIn draft with Gemini...")
    post = gemini_client.generate_post(key, repo_url, ai_ctx, layman_ctx, stack, config)

    # Stage 5
    draft = target / "LINKEDIN_DRAFT.md"
    draft.write_text(post, encoding="utf-8")
    log(f"Draft saved: {draft}")
    code = shutil.which("code")
    if code:
        subprocess.run([code, "-r", str(draft)])
    else:
        log("'code' CLI not found. In VS Code: Cmd/Ctrl+Shift+P > 'Shell Command: Install code command in PATH'")
    print(f"\nDone! Review {draft.name}, edit, then paste into LinkedIn.\nRepo: {repo_url}")


if __name__ == "__main__":
    main()
