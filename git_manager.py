from pathlib import Path
from git import Repo
from github import Github, GithubException

DEFAULT_IGNORE = [".env", "venv/", "node_modules/", "__pycache__/", "build/", "dist/"]


def _ensure_gitignore(path: Path):
    """Make sure secrets are never committed (.env etc.) before 'git add .'."""
    gi = path / ".gitignore"
    existing = gi.read_text().splitlines() if gi.exists() else []
    missing = [p for p in DEFAULT_IGNORE if p not in existing]
    if missing:
        with gi.open("a") as f:
            f.write(("\n" if existing else "") + "\n".join(missing) + "\n")


def publish(target_dir: str, token: str, config: dict) -> str:
    path = Path(target_dir).resolve()
    branch = config["github_settings"]["default_branch"]
    private = config["github_settings"]["default_visibility"] != "public"

    # 1. local repo
    if (path / ".git").exists():
        repo = Repo(path)
    else:
        repo = Repo.init(path)
        repo.git.symbolic_ref("HEAD", f"refs/heads/{branch}")
    _ensure_gitignore(path)

    # 2-4. remote repo
    gh = Github(token)
    user = gh.get_user()
    name = path.name
    try:
        remote_repo = user.get_repo(name)
    except GithubException as e:
        if e.status != 404:
            raise
        remote_repo = user.create_repo(name, private=private)

    # 5. commit
    repo.git.add(".")
    if repo.is_dirty(untracked_files=True) or not repo.head.is_valid():
        repo.index.commit("Build: Automated release")

    # 6. push (token only used for this call; stored remote stays token-free)
    clean_url = remote_repo.clone_url
    authed_url = clean_url.replace("https://", f"https://{token}@")
    if "origin" in [r.name for r in repo.remotes]:
        repo.remote("origin").set_url(clean_url)
    else:
        repo.create_remote("origin", clean_url)
    repo.git.push(authed_url, f"{branch}:{branch}")
    return remote_repo.html_url
