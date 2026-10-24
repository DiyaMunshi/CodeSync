# CodeSync ⚡

**Automatically save your accepted LeetCode solutions locally and sync them with your GitHub repository.**

CodeSync is a lightweight browser extension and Python Flask application designed to simplify LeetCode solution management. It helps you save accepted coding solutions directly to your local machine, organize them by problem and programming language, and maintain a separate GitHub repository for your coding practice.

Instead of manually copying code, creating files, and committing each solution, CodeSync streamlines the workflow.

## ✨ Features

- **One-click saving:** Save accepted LeetCode solutions using a button injected into the LeetCode page.
- **Acceptance confirmation:** Confirm that a solution has been accepted before saving.
- **Automatic file creation:** Generate solution files with appropriate extensions for supported programming languages.
- **Organized solutions:** Store solutions in a dedicated directory with descriptive filenames and problem numbers when available.
- **Submission history:** Maintain a JSON record containing problem details, code, language, timestamps, and synchronization status.
- **Duplicate prevention:** Avoid saving the same problem and language combination repeatedly.
- **GitHub integration:** Keep coding solutions in a separate Git repository and automate synchronization where configured.
- **Local-first workflow:** Save solutions locally without requiring a separate cloud database.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Browser extension | JavaScript |
| Backend API | Python, Flask |
| Data storage | JSON |
| Version control | Git |
| Repository hosting | GitHub |

## 📁 Project Structure

```text
CodeSync/
├── extension/
│   ├── background.js
│   ├── content.js
│   └── manifest.json
├── server/
│   ├── app.py
│   └── requirements.txt
├── data/
│   └── submissions.json
├── solutions/
│   └── Your saved solutions
├── config.json
├── .gitignore
└── README.md
```

The `solutions/` directory is intended to be managed as a separate Git repository if you want your LeetCode solutions to be published independently of the CodeSync application.

## ⚙️ Prerequisites

Before setting up CodeSync, ensure you have:

- Python 3 installed
- Google Chrome or a Chromium-based browser
- Git installed and configured
- A GitHub account
- A GitHub repository for your LeetCode solutions (optional)

## 🚀 Installation and Setup

### 1. Clone the CodeSync repository

```bash
git clone https://github.com/<your-username>/CodeSync.git
cd CodeSync
```

Replace `<your-username>` with your GitHub username.

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r server/requirements.txt
```

### 4. Start the Flask backend

From the root directory, run:

```bash
python server/app.py
```

The local API should be available at:

```text
http://127.0.0.1:5050
```

You can check whether the backend is running by opening:

```text
http://127.0.0.1:5050/health
```

A successful response should indicate that the service is running.

**Note:** The Flask backend must be running for the current local-saving workflow to work. The browser extension communicates with this backend to store solutions on your computer.

### 5. Load the browser extension

1. Open Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension/` directory inside CodeSync.
6. Open a LeetCode problem and verify that the extension is available.

### 6. Configure the solutions repository

If you want to sync your solutions to a separate GitHub repository:

1. Create a dedicated repository on GitHub for your LeetCode solutions.
2. Configure the Git remote and branch as required by the backend.
3. Ensure Git authentication is configured on your machine.
4. Verify that the `solutions/` directory is a Git repository.
5. Test synchronization with a single accepted solution before relying on automated pushes.

Keep the CodeSync application repository separate from the solutions repository.

## 💻 Usage

1. Start the Flask backend.
2. Open a LeetCode problem in your browser.
3. Solve the problem and submit your solution.
4. Once LeetCode reports **Accepted**, use the CodeSync save button.
5. Confirm the acceptance prompt.
6. CodeSync sends the solution details to the local backend.
7. The backend saves the source file and updates `data/submissions.json`.
8. If Git synchronization is configured, the solution can subsequently be committed and pushed to your separate repository.

## 🗃️ Supported Programming Languages

The backend currently supports the following language mappings:

- Python / Python 3
- C
- C++
- Java
- JavaScript
- TypeScript
- C#
- Go
- Rust
- Kotlin
- Swift
- Ruby
- PHP
- SQL

The exact language detected by the extension should match one of the supported mappings.

## 🔌 API Overview

### Health Check

`GET /health`

Checks whether the Flask service is running.

Example response:

```json
{
  "status": "running",
  "service": "CodeSync"
}
```

### Save Solution

`POST /solution`

Accepts solution details from the browser extension.

Example request:

```json
{
  "title": "Two Sum",
  "problemNumber": "1",
  "problemSlug": "two-sum",
  "language": "python",
  "url": "https://leetcode.com/problems/two-sum/",
  "code": "class Solution:\n    pass",
  "status": "accepted"
}
```

The backend validates the submission, saves the solution file, and records its metadata in the local JSON history.

## 🔒 Privacy and Security

- Solutions are stored locally by default.
- GitHub synchronization is optional and requires repository configuration.
- Do not commit API keys, access tokens, passwords, or other credentials.
- Keep virtual environments and generated runtime files out of the application repository.
- Review your `.gitignore` before pushing the project.
- Do not expose the local Flask service publicly without appropriate security controls.

## 🗺️ Future Improvements

Potential improvements include:

- Running the backend automatically when the browser starts.
- Better synchronization status indicators.
- Retry handling for failed Git operations.
- Support for additional coding platforms.
- A dashboard for browsing saved solutions.
- Statistics for tracking coding practice and problem-solving progress.
- More robust duplicate detection and error handling.

## 🎯 Motivation

CodeSync was created to make coding practice more organized and less repetitive. By combining a browser extension, a local backend, and GitHub integration, it provides a simple workflow for maintaining a personal coding portfolio.
