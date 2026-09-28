# Phase 2: Implementation

## Step 6: Try Building It

<!-- Describe the first implementation attempt. -->

## How the Work Started

I used an AI coding agent in VS Code with a detailed prompt to scaffold the backend with FastAPI, the frontend with HTML, Bootstrap, and JavaScript, and the documentation and tests. I then verified everything myself in the terminal.

## Project Structure

`backend/app` contains the FastAPI code, and `backend/tests` contains the pytest tests. `backend/app/data` contains `city_country.json`. The `frontend` folder contains `index.html`, `css`, and `js`. The `docs` folder contains documentation for each project phase. Secrets are kept in `backend/.env`, which Git ignores. `backend/.env.example` lists the variable names.

## What Was Built First

First, I built `GET /api/health`, which returns `{"status": "ok"}`, a frontend page that calls it when the page loads, and a pytest test for the endpoint. This confirmed that the backend, frontend, and tests work together before adding real features.

## Feature Development

<!-- Track the implementation of the project's features. -->

## Comparison: Original vs My Version

<!-- Compare the original application and this implementation. -->

| Aspect                              | Original | My Version |
| ----------------------------------- | -------- | ---------- |
| <!-- TODO: Add comparison rows. --> |          |            |

## Problems & Solutions

- **Problem:** The AI agent created the virtual environment in the project root instead of `backend/` as the prompt said. **Solution:** I checked the `.gitignore` rules and kept it in the root because it works the same there.
- **Problem:** Port 8000 was already in use because the agent had left a server running. **Solution:** I found the process with `lsof -i :8000` and stopped it with `kill`.
- **Problem:** Homebrew failed to reinstall a package while I was installing GitHub CLI because Xcode was outdated. **Solution:** I updated Xcode and reinstalled the package.
- **Problem:** The `.env` file could be committed with secrets. **Solution:** Before the first commit, I checked it with `git check-ignore -v backend/.env` and reviewed `git status`.
