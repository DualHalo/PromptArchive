from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "promptarchive.db"

app = Flask(__name__)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                lighting TEXT NOT NULL,
                camera TEXT NOT NULL,
                environment TEXT NOT NULL,
                time_of_day TEXT NOT NULL,
                hair_length TEXT NOT NULL,
                hair_style TEXT NOT NULL,
                hair_color TEXT NOT NULL,
                outfit_type TEXT NOT NULL,
                outfit_style TEXT NOT NULL,
                outfit_color TEXT NOT NULL,
                generated_prompt TEXT NOT NULL,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def clean_value(value: str | None, fallback: str = "") -> str:
    return (value or fallback).strip()


def compose_hair(length: str, style: str, color: str) -> str:
    parts = [part for part in [length, style, color] if part]
    if not parts:
        return "well-styled hair"
    return " ".join(parts) + " hair"


def compose_outfit(outfit_type: str, outfit_style: str, outfit_color: str) -> str:
    parts = [part for part in [outfit_style, outfit_color, outfit_type] if part]
    if not parts:
        return "a thoughtfully styled outfit"
    article = "an" if parts[0][:1].lower() in "aeiou" else "a"
    return f"{article} " + " ".join(parts)


def build_prompt(data: dict[str, str]) -> str:
    subject = clean_value(data.get("subject"), "stylish subject")
    lighting = clean_value(data.get("lighting"), "soft natural lighting")
    camera = clean_value(data.get("camera"), "85mm portrait lens")
    environment = clean_value(data.get("environment"), "cinematic setting")
    time_of_day = clean_value(data.get("time_of_day"), "golden hour")

    hair = compose_hair(
        clean_value(data.get("hair_length")),
        clean_value(data.get("hair_style")),
        clean_value(data.get("hair_color")),
    )
    outfit = compose_outfit(
        clean_value(data.get("outfit_type")),
        clean_value(data.get("outfit_style")),
        clean_value(data.get("outfit_color")),
    )

    return (
        f"High-quality image of {subject}, wearing {outfit}, with {hair}, "
        f"in {environment} during {time_of_day}, lit with {lighting}, "
        f"captured using {camera}, ultra-detailed, cohesive styling, polished composition."
    )


@app.route("/")
def index():
    with get_db_connection() as conn:
        prompts = conn.execute(
            """
            SELECT *
            FROM prompts
            ORDER BY is_favorite DESC, id DESC
            """
        ).fetchall()

    return render_template("index.html", prompts=prompts)


@app.post("/api/generate")
def api_generate():
    payload = request.get_json(silent=True) or {}
    prompt = build_prompt(payload)
    return jsonify({"prompt": prompt})


@app.post("/save")
def save_prompt():
    form_data = {
        "title": clean_value(request.form.get("title")),
        "subject": clean_value(request.form.get("subject")),
        "lighting": clean_value(request.form.get("lighting")),
        "camera": clean_value(request.form.get("camera")),
        "environment": clean_value(request.form.get("environment")),
        "time_of_day": clean_value(request.form.get("time_of_day")),
        "hair_length": clean_value(request.form.get("hair_length")),
        "hair_style": clean_value(request.form.get("hair_style")),
        "hair_color": clean_value(request.form.get("hair_color")),
        "outfit_type": clean_value(request.form.get("outfit_type")),
        "outfit_style": clean_value(request.form.get("outfit_style")),
        "outfit_color": clean_value(request.form.get("outfit_color")),
    }

    generated_prompt = build_prompt(form_data)

    if not form_data["title"]:
        form_data["title"] = f"Prompt - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO prompts (
                title,
                subject,
                lighting,
                camera,
                environment,
                time_of_day,
                hair_length,
                hair_style,
                hair_color,
                outfit_type,
                outfit_style,
                outfit_color,
                generated_prompt,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form_data["title"],
                form_data["subject"],
                form_data["lighting"],
                form_data["camera"],
                form_data["environment"],
                form_data["time_of_day"],
                form_data["hair_length"],
                form_data["hair_style"],
                form_data["hair_color"],
                form_data["outfit_type"],
                form_data["outfit_style"],
                form_data["outfit_color"],
                generated_prompt,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()

    return redirect(url_for("index"))


@app.post("/favorite/<int:prompt_id>")
def toggle_favorite(prompt_id: int):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT is_favorite FROM prompts WHERE id = ?",
            (prompt_id,),
        ).fetchone()

        if row is None:
            return jsonify({"ok": False, "error": "Prompt not found"}), 404

        new_value = 0 if row["is_favorite"] else 1
        conn.execute(
            "UPDATE prompts SET is_favorite = ? WHERE id = ?",
            (new_value, prompt_id),
        )
        conn.commit()

    return jsonify({"ok": True, "is_favorite": bool(new_value)})


@app.post("/delete/<int:prompt_id>")
def delete_prompt(prompt_id: int):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        conn.commit()

    return redirect(url_for("index"))


@app.get("/load/<int:prompt_id>")
def load_prompt(prompt_id: int):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,)).fetchone()

    if row is None:
        return jsonify({"ok": False, "error": "Prompt not found"}), 404

    return jsonify({"ok": True, "prompt": row_to_dict(row)})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5057)
