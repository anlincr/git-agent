# ProjectPublisherAgent

A small Python CLI that publishes any local project folder to GitHub and drafts a LinkedIn post about it using Google Gemini. It never posts anything for you: it saves the draft as `LINKEDIN_DRAFT.md` and opens it in VS Code so you can review, edit and post it yourself.

## What it does

1. **CLI setup:** reads the target folder path (defaults to the current folder), loads `.env`, and checks the folder exists.
2. **Git automation:** initializes a git repo if missing, creates a GitHub repo named after the folder (if it doesn't exist), commits with `Build: Automated release`, and pushes to `main`.
3. **Context extraction:** reads the project's `README.md`, dependency files (`requirements.txt`, `package.json`, `pyproject.toml`), and the last 5 commit messages. Lines are sorted into "Technical/AI highlights" and "Features/workflow" using the keyword list in `config.json`.
4. **Draft generation:** sends that context to Gemini, which writes a LinkedIn post (hook, bullet points, tech stack, GitHub link, call to action, hashtags).
5. **Output:** writes `LINKEDIN_DRAFT.md` in the target folder and opens it with `code -r`.

## Project structure

```
main.py             # entry point, runs all stages
git_manager.py      # git + GitHub automation
rag_processor.py    # context extraction and keyword bucketing
gemini_client.py    # Gemini draft generation
config.json         # settings, hashtags, AI/ML keywords, model name
requirements.txt
.env.example
```

## Requirements

- Python 3.10+
- Git installed and available in PATH
- VS Code with the `code` command in PATH (optional; used to open the draft)
- A GitHub account
- A Google AI Studio API key

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```
GITHUB_TOKEN=your_github_classic_token
GEMINI_API_KEY=your_google_ai_studio_key
```

### Getting the keys

- **GitHub token:** Settings, Developer settings, Personal access tokens, **Tokens (classic)**, generate a new token and tick only the `repo` scope. Copy it immediately, since GitHub shows it once.
- **Gemini key:** create one at [Google AI Studio](https://aistudio.google.com).

## Usage

Run from the agent's own folder, passing the path of the project you want to publish:

```powershell
python main.py "C:\path\to\your\project"
```

With no argument, it publishes the current folder:

```powershell
python main.py
```

When it finishes, review `LINKEDIN_DRAFT.md` in the project folder, edit as needed, and paste it into LinkedIn yourself.

## Configuration (`config.json`)

| Key | Purpose |
| --- | --- |
| `github_settings.default_visibility` | `public` or `private` for new repos |
| `github_settings.default_branch` | Branch to push (default `main`) |
| `gemini_model` | Gemini model name; change it if you get a 404 |
| `content_strategy.tone` | Writing tone for the post |
| `content_strategy.hashtags` | Hashtags the post should use |
| `content_strategy.ai_ml_keywords` | Words that mark a line as AI/ML context |

## Safety notes

- Before staging files, the agent appends common patterns (`.env`, `venv/`, `node_modules/`, `__pycache__/`, `build/`, `dist/`) to the target project's `.gitignore`. Your own `.gitignore` entries are kept and respected.
- `.gitignore` does not remove files that were already committed. If a secret was committed before, remove it with `git rm --cached <file>` and rotate the key.
- Add any other virtual environment folder (such as `.venv/` or `env/`) and `LINKEDIN_DRAFT.md` to the project's `.gitignore` if you don't want them pushed.
- Your GitHub token is used only for the push command and is not stored in the repo's remote URL.
- If the target folder already has a different `origin` remote, the agent replaces it, so check first.
- Never commit your `.env` file.

## Troubleshooting

- **Gemini 404 (model not found):** set a model that works for your key in `config.json`.
- **Script hangs at "Generating LinkedIn draft":** usually a network issue (VPN, proxy, firewall) blocking `generativelanguage.googleapis.com`, or an unavailable model. Try another model name.
- **`code` command not found:** in VS Code, open the Command Palette and run "Shell Command: Install 'code' command in PATH".
- **429 error:** the free tier hit its rate limit; wait a minute and run again.
