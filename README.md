# Python Scripts

A daily-growing collection of Python scripts, generated automatically by the [Gemini API](https://ai.google.dev/) and organized by category.

Every day a GitHub Action picks the next topic from [`topics.txt`](topics.txt), asks Gemini to write a complete, beginner-friendly script for it, saves it under the matching category folder, and updates the list below.

## How it works

1. `.github/workflows/daily.yml` runs on a daily schedule (and can be triggered manually).
2. `generator/generate_script.py` reads the next unused topic from `topics.txt`, builds a prompt from `prompts/python_prompt.txt`, and calls the Gemini API.
3. The generated script is saved as `<Category>/<date>_<topic>.py`.
4. The topic is recorded in `generator/used_topics.txt` so it's never repeated.
5. This README is updated automatically and the change is committed and pushed.

## Categories

`Automation` `API` `Web` `AI` `CLI` `Utilities` `File` `Image` `Networking` `Database` `Security` `DataScience` `Games` `Projects`

## Latest Scripts

<!-- LATEST_SCRIPTS_START -->
- 2026-08-04 — **Password Generator** (Security) — [2026-08-04_password_generator.py](Security/2026-08-04_password_generator.py)
<!-- LATEST_SCRIPTS_END -->
