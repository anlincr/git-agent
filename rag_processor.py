import json
from pathlib import Path
from git import Repo, InvalidGitRepositoryError

EXCLUDE = {".git", "node_modules", "venv", "__pycache__", "build", "dist", ".env"}
MAX_CHARS = 6000


def _read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")[:MAX_CHARS]
    except OSError:
        return ""


def _readme_text(root: Path) -> str:
    readme = next((p for p in root.iterdir() if p.name.lower() == "readme.md"), None)
    text = _read(readme) if readme else ""
    if len(text) < 200:  # fallback: list top-level files
        files = [p.name for p in root.iterdir() if p.name not in EXCLUDE]
        text += "\nTop-level files: " + ", ".join(sorted(files))
    return text


def _tech_stack(root: Path) -> list[str]:
    stack = set()
    req = root / "requirements.txt"
    if req.exists():
        for line in _read(req).splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                for sep in "=<>~[;":
                    line = line.split(sep)[0]
                stack.add(line.strip())
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(_read(pkg))
            stack |= set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))
        except json.JSONDecodeError:
            pass
    pyp = root / "pyproject.toml"
    if pyp.exists():
        stack.add("pyproject.toml (Python)")
    return sorted(stack)


def _commits(root: Path) -> list[str]:
    try:
        return Repo(root).git.log("-n", "5", "--oneline").splitlines()
    except (InvalidGitRepositoryError, Exception):
        return []


def extract(target_dir: str, config: dict):
    root = Path(target_dir).resolve()
    keywords = [k.lower() for k in config["content_strategy"]["ai_ml_keywords"]]

    readme = _readme_text(root)
    stack = _tech_stack(root)
    commits = _commits(root)

    ai_lines, layman_lines = [], []
    # bucket README lines, stack entries and commits by keyword match
    candidates = [l.strip() for l in readme.splitlines() if l.strip()]
    candidates += [f"Dependency: {s}" for s in stack]
    candidates += [f"Commit: {c}" for c in commits]
    for line in candidates:
        (ai_lines if any(k in line.lower() for k in keywords) else layman_lines).append(line)

    return "\n".join(ai_lines), "\n".join(layman_lines), stack
