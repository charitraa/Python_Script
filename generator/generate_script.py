"""
Daily script generator.

Reads the next unused topic from topics.txt, asks Gemini to write a Python
script for it, saves the result under its category folder, records the topic
as used, and updates README.md with a link to the new script.

Run manually with:
    GEMINI_API_KEY=... python generator/generate_script.py
"""

import datetime
import os
import re
import sys

from google import genai

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS_FILE = os.path.join(REPO_ROOT, "topics.txt")
USED_TOPICS_FILE = os.path.join(REPO_ROOT, "generator", "used_topics.txt")
PROMPT_FILE = os.path.join(REPO_ROOT, "prompts", "python_prompt.txt")
README_FILE = os.path.join(REPO_ROOT, "README.md")

README_START = "<!-- LATEST_SCRIPTS_START -->"
README_END = "<!-- LATEST_SCRIPTS_END -->"

DEFAULT_MODEL = "gemini-2.5-flash"


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def load_used_topics():
    return set(read_lines(USED_TOPICS_FILE))


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug


def pick_next_topic(client, model):
    used = load_used_topics()
    for line in read_lines(TOPICS_FILE):
        if line in used:
            continue
        category, _, topic = line.partition("|")
        if not topic:
            continue
        return category.strip(), topic.strip(), line

    # topics.txt exhausted: ask Gemini to invent a fresh, unused idea
    used_titles = "\n".join(sorted(used)) or "(none yet)"
    brainstorm_prompt = (
        "Suggest ONE new beginner-friendly, practical Python script idea that is "
        "NOT already in this list of previously generated topics:\n"
        f"{used_titles}\n\n"
        "Reply with exactly one line in the format: Category|Topic Name\n"
        "Category must be one of: Automation, API, Web, AI, CLI, Utilities, File, "
        "Image, Networking, Database, Security, DataScience, Games, Projects.\n"
        "No extra text."
    )
    response = client.models.generate_content(model=model, contents=brainstorm_prompt)
    line = response.text.strip().splitlines()[0].strip()
    category, _, topic = line.partition("|")
    if not topic:
        category, topic = "Projects", line
    return category.strip(), topic.strip(), f"{category.strip()}|{topic.strip()}"


def strip_code_fences(text):
    text = text.strip()
    text = re.sub(r"^```(?:python)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    return text.strip() + "\n"


def generate_code(client, model, topic):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        template = f.read()
    prompt = template.format(topic=topic)
    response = client.models.generate_content(model=model, contents=prompt)
    return strip_code_fences(response.text)


def save_script(category, topic, code, today):
    category_dir = os.path.join(REPO_ROOT, category)
    os.makedirs(category_dir, exist_ok=True)
    filename = f"{today}_{slugify(topic)}.py"
    path = os.path.join(category_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return os.path.join(category, filename)


def mark_topic_used(topic_line):
    os.makedirs(os.path.dirname(USED_TOPICS_FILE), exist_ok=True)
    with open(USED_TOPICS_FILE, "a", encoding="utf-8") as f:
        f.write(topic_line + "\n")


def update_readme(today, category, topic, rel_path):
    entry = f"- {today} — **{topic}** ({category}) — [{os.path.basename(rel_path)}]({rel_path})"

    if not os.path.exists(README_FILE):
        content = (
            "# Python Scripts\n\n"
            "A daily-growing collection of Python scripts generated with the Gemini API.\n\n"
            "## Latest Scripts\n\n"
            f"{README_START}\n{README_END}\n"
        )
    else:
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if README_START not in content:
            content += f"\n## Latest Scripts\n\n{README_START}\n{README_END}\n"

    start_idx = content.index(README_START) + len(README_START)
    end_idx = content.index(README_END)
    existing_entries = content[start_idx:end_idx].strip("\n")
    new_block = entry if not existing_entries else f"{entry}\n{existing_entries}"
    content = content[:start_idx] + "\n" + new_block + "\n" + content[end_idx:]

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    client = genai.Client(api_key=api_key)

    category, topic, topic_line = pick_next_topic(client, model)
    print(f"Selected topic: {category} | {topic}")

    code = generate_code(client, model, topic)
    today = datetime.date.today().isoformat()
    rel_path = save_script(category, topic, code, today)
    mark_topic_used(topic_line)
    update_readme(today, category, topic, rel_path)

    print(f"Saved {rel_path}")


if __name__ == "__main__":
    main()
