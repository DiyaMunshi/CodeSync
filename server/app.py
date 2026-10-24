
from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime
import json
import re
import subprocess

app = Flask(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
SOLUTIONS_DIR = BASE_DIR / "solutions"
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "submissions.json"

# GitHub repository lives INSIDE the solutions folder.
GIT_BRANCH = "main"
GIT_REMOTE = "origin"

SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")


EXTENSIONS = {
    "python": ".py",
    "python3": ".py",
    "c": ".c",
    "cpp": ".cpp",
    "c++": ".cpp",
    "java": ".java",
    "javascript": ".js",
    "typescript": ".ts",
    "csharp": ".cs",
    "c#": ".cs",
    "go": ".go",
    "rust": ".rs",
    "kotlin": ".kt",
    "swift": ".swift",
    "ruby": ".rb",
    "php": ".php",
    "sql": ".sql",
}


def load_history():
    try:
        history = json.loads(
            HISTORY_FILE.read_text(encoding="utf-8")
        )
        return history if isinstance(history, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def safe_filename(title):
    name = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower())
    return name.strip("-") or "untitled-solution"


def run_git(*args):
    """Run a Git command inside the solutions repository."""
    return subprocess.run(
        ["git", "-C", str(SOLUTIONS_DIR), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def sync_solution_to_github(filename, title):
    """
    Commit and push only the specified solution file.
    Other project files are not added to the commit.
    """
    try:
        # Stage only this solution file.
        result = run_git("add", "--", filename)

        if result.returncode != 0:
            return False, result.stderr.strip() or "Git add failed"

        # Check whether this file has staged changes.
        result = run_git(
            "diff", "--cached", "--quiet", "--", filename
        )

        if result.returncode == 1:
            # File is new or has changed.
            commit = run_git(
                "commit",
                "-m",
                f"Add/update LeetCode solution: {title}",
                "--",
                filename,
            )

            if commit.returncode != 0:
                return (
                    False,
                    commit.stderr.strip() or "Git commit failed",
                )

        elif result.returncode != 0:
            return False, result.stderr.strip() or "Git diff failed"

        # Push to the existing LeetCode GitHub repository.
        push = run_git("push", GIT_REMOTE, GIT_BRANCH)

        if push.returncode != 0:
            return (
                False,
                push.stderr.strip() or "Git push failed",
            )

        return True, "Pushed to GitHub successfully"

    except subprocess.TimeoutExpired:
        return False, "Git operation timed out"
    except OSError as exc:
        return False, str(exc)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "service": "CodeSync",
    })


@app.route("/solution", methods=["POST"])
def save_solution():
    data = request.get_json(silent=True) or {}

    title = data.get("title", "")
    code = data.get("code", "")
    language = data.get("language", "python")
    url = data.get("url", "")
    status = data.get("status", "")

    # Validate incoming data types before processing.
    if not all(
        isinstance(value, str)
        for value in (title, code, language, url, status)
    ):
        return jsonify({"error": "Invalid data types"}), 400

    title = title.strip()
    language = language.strip().lower()
    url = url.strip()
    status = status.strip().lower()

    problem_number = str(
        data.get("problemNumber", "")
    ).strip()

    problem_slug = str(
        data.get("problemSlug", "")
    ).strip().lower()

    # Extract the problem slug from the LeetCode URL if needed.
    if not problem_slug and url:
        match = re.search(r"/problems/([^/]+)", url)
        if match:
            problem_slug = match.group(1).lower()

    if not title or not code.strip():
        return jsonify({
            "error": "Title and code are required"
        }), 400

    if status != "accepted":
        return jsonify({
            "error": "Only accepted solutions can be saved"
        }), 400

    if not re.fullmatch(r"[a-z0-9+#.-]{1,30}", language):
        return jsonify({"error": "Invalid language"}), 400

    extension = EXTENSIONS.get(language)

    if extension is None:
        return jsonify({
            "error": f"Unsupported language: {language}"
        }), 400

    history = load_history()

    # Find a previously saved solution for this problem/language.
    existing_index = None

    for index, item in enumerate(history):
        same_language = (
            item.get("language", "").lower() == language
        )

        saved_slug = item.get("problem_slug", "").lower()

        same_problem = (
            bool(problem_slug) and saved_slug == problem_slug
        )

        # Backward compatibility with older history records.
        if not saved_slug and item.get("title") == title:
            same_problem = True

        if same_problem and same_language:
            existing_index = index
            break

    # Reuse the existing filename when updating a saved solution.
    if existing_index is not None:
        existing_filename = Path(
            history[existing_index].get("filename", "")
        ).name

        if existing_filename.endswith(extension):
            filename = existing_filename
        else:
            filename = None
    else:
        filename = None

    # Otherwise, create a numbered filename.
    if not filename:
        prefix = (
            f"{int(problem_number):04d}-"
            if problem_number.isdigit()
            else ""
        )

        filename = f"{prefix}{safe_filename(title)}{extension}"

    solution_path = SOLUTIONS_DIR / filename

    # Do not overwrite an unrelated existing file.
    if existing_index is None and solution_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        solution_path = SOLUTIONS_DIR / (
            f"{solution_path.stem}-{timestamp}"
            f"{solution_path.suffix}"
        )
        filename = solution_path.name

    # Save the solution locally first.
    solution_path.write_text(code, encoding="utf-8")

    # Push this solution file to GitHub.
    synced, sync_message = sync_solution_to_github(
        filename, title
    )

    record = {
        "title": title,
        "problem_number": problem_number,
        "problem_slug": problem_slug,
        "language": language,
        "url": url,
        "filename": filename,
        "code": code,
        "saved_at": datetime.now().astimezone().isoformat(),
        "synced": synced,
    }

    if existing_index is not None:
        history[existing_index] = record
        message = "Existing solution updated locally"
    else:
        history.append(record)
        message = "Solution saved locally"

    # Keep history updated even if GitHub syncing fails.
    save_history(history)

    if synced:
        message += " and pushed to GitHub"
    else:
        message += ", but GitHub sync failed"

    return jsonify({
        "message": message,
        "filename": filename,
        "synced": synced,
        "sync_message": sync_message,
    }), 201 if existing_index is None else 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5050,
        debug=False,
    )
