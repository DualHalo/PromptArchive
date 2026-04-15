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
                subject_type TEXT NOT NULL DEFAULT 'Portrait',
                gender TEXT NOT NULL DEFAULT '',
                shot_type TEXT NOT NULL DEFAULT '',
                locale TEXT NOT NULL DEFAULT '',
                subject TEXT NOT NULL,
                lighting TEXT NOT NULL,
                camera TEXT NOT NULL,
                environment TEXT NOT NULL,
                time_of_day TEXT NOT NULL,
                eye_color TEXT NOT NULL DEFAULT '',
                expression TEXT NOT NULL DEFAULT '',
                hair_length TEXT NOT NULL,
                hair_style TEXT NOT NULL,
                hair_color TEXT NOT NULL,
                outfit_type TEXT NOT NULL,
                outfit_style TEXT NOT NULL,
                outfit_color TEXT NOT NULL,
                generated_prompt TEXT NOT NULL,
                negative_prompt TEXT NOT NULL DEFAULT '',
                is_favorite INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(prompts)").fetchall()
        }

        migrations = {
            "subject_type": "ALTER TABLE prompts ADD COLUMN subject_type TEXT NOT NULL DEFAULT 'Portrait'",
            "negative_prompt": "ALTER TABLE prompts ADD COLUMN negative_prompt TEXT NOT NULL DEFAULT ''",
            "gender": "ALTER TABLE prompts ADD COLUMN gender TEXT NOT NULL DEFAULT ''",
            "shot_type": "ALTER TABLE prompts ADD COLUMN shot_type TEXT NOT NULL DEFAULT ''",
            "locale": "ALTER TABLE prompts ADD COLUMN locale TEXT NOT NULL DEFAULT ''",
            "eye_color": "ALTER TABLE prompts ADD COLUMN eye_color TEXT NOT NULL DEFAULT ''",
            "expression": "ALTER TABLE prompts ADD COLUMN expression TEXT NOT NULL DEFAULT ''",
        }

        for column_name, sql in migrations.items():
            if column_name not in columns:
                conn.execute(sql)

        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def clean_value(value: str | None, fallback: str = "") -> str:
    return (value or fallback).strip()


def compose_hair(length: str, style: str, color: str) -> str:
    parts = [part for part in [length, style, color] if part]
    if not parts:
        return ""
    return " ".join(parts) + " hair"


def compose_outfit(outfit_type: str, outfit_style: str, outfit_color: str) -> str:
    parts = [part for part in [outfit_style, outfit_color, outfit_type] if part]
    if not parts:
        return ""

    article = "an" if parts[0][:1].lower() in "aeiou" else "a"
    return f"{article} " + " ".join(parts)


def compose_subject(subject: str, gender: str) -> str:
    if subject and gender:
        return f"{gender.lower()} {subject}"
    if subject:
        return subject
    if gender:
        return gender.lower()
    return ""


def build_prompt(data: dict[str, str]) -> str:
    subject = clean_value(data.get("subject"))
    subject_type = clean_value(data.get("subject_type"))
    gender = clean_value(data.get("gender"))
    shot_type = clean_value(data.get("shot_type"))
    locale = clean_value(data.get("locale"))
    lighting = clean_value(data.get("lighting"))
    camera = clean_value(data.get("camera"))
    environment = clean_value(data.get("environment"))
    time_of_day = clean_value(data.get("time_of_day"))

    eye_color = clean_value(data.get("eye_color"))
    expression = clean_value(data.get("expression"))

    hair_length = clean_value(data.get("hair_length"))
    hair_style = clean_value(data.get("hair_style"))
    hair_color = clean_value(data.get("hair_color"))

    outfit_type = clean_value(data.get("outfit_type"))
    outfit_style = clean_value(data.get("outfit_style"))
    outfit_color = clean_value(data.get("outfit_color"))

    if not any(
        [
            subject,
            subject_type,
            gender,
            shot_type,
            locale,
            lighting,
            camera,
            environment,
            time_of_day,
            eye_color,
            expression,
            hair_length,
            hair_style,
            hair_color,
            outfit_type,
            outfit_style,
            outfit_color,
        ]
    ):
        return ""

    subject_text = compose_subject(subject, gender)
    hair = compose_hair(hair_length, hair_style, hair_color)
    outfit = compose_outfit(outfit_type, outfit_style, outfit_color)

    prompt_parts: list[str] = []

    opening_bits = ["High-quality"]
    if shot_type:
        opening_bits.append(shot_type.lower())
    opening_bits.append("image")

    if subject_text:
        opening = " ".join(opening_bits) + f" of {subject_text}"
    else:
        opening = " ".join(opening_bits)

    prompt_parts.append(opening)

    if subject_type:
        prompt_parts.append(f"styled for a {subject_type.lower()} concept")

    if eye_color:
        prompt_parts.append(f"with {eye_color} eyes")

    if expression:
        prompt_parts.append(f"showing a {expression}")

    if outfit:
        prompt_parts.append(f"wearing {outfit}")

    if hair:
        prompt_parts.append(f"with {hair}")

    if environment:
        environment_text = environment
        if locale:
            environment_text = f"{environment} in {locale}"
        prompt_parts.append(f"in {environment_text}")
    elif locale:
        prompt_parts.append(f"set in {locale}")

    if time_of_day:
        prompt_parts.append(f"during {time_of_day}")

    if lighting:
        prompt_parts.append(f"lit with {lighting}")

    if camera:
        prompt_parts.append(f"captured using {camera}")

    prompt = ", ".join(prompt_parts)
    prompt += ", ultra-detailed, cohesive styling, polished composition."
    return prompt


def build_negative_prompt(data: dict[str, str]) -> str:
    subject = clean_value(data.get("subject")).lower()
    subject_type = clean_value(data.get("subject_type"))
    gender = clean_value(data.get("gender")).lower()
    shot_type = clean_value(data.get("shot_type")).lower()
    locale = clean_value(data.get("locale")).lower()
    eye_color = clean_value(data.get("eye_color")).lower()
    expression = clean_value(data.get("expression")).lower()

    other_values = [
        clean_value(data.get("lighting")),
        clean_value(data.get("camera")),
        clean_value(data.get("environment")),
        clean_value(data.get("time_of_day")),
        clean_value(data.get("hair_length")),
        clean_value(data.get("hair_style")),
        clean_value(data.get("hair_color")),
        clean_value(data.get("outfit_type")),
        clean_value(data.get("outfit_style")),
        clean_value(data.get("outfit_color")),
    ]

    if (
        not subject
        and not subject_type
        and not gender
        and not shot_type
        and not locale
        and not eye_color
        and not expression
        and not any(other_values)
    ):
        return ""

    base_negatives = [
        "blurry",
        "low quality",
        "low resolution",
        "pixelated",
        "distorted",
        "deformed",
        "bad anatomy",
        "bad proportions",
        "extra limbs",
        "extra fingers",
        "missing fingers",
        "poorly drawn hands",
        "poorly drawn face",
        "asymmetrical eyes",
        "duplicate features",
        "cropped",
        "out of frame",
        "watermark",
        "text",
        "logo",
        "jpeg artifacts",
    ]

    portrait_negatives = [
        "disfigured face",
        "cross-eyed",
        "bad eyes",
        "malformed mouth",
        "bad teeth",
        "unnatural skin",
        "waxy skin",
        "overly smooth skin",
        "bad facial symmetry",
    ]

    fashion_negatives = [
        "awkward pose",
        "unflattering angle",
        "poor styling",
        "wrinkled clothing",
        "mismatched outfit",
        "cheap-looking fabric",
        "bad draping",
        "clumsy composition",
    ]

    fantasy_negatives = [
        "broken costume",
        "floating accessories",
        "mismatched armor",
        "extra weapons",
        "inconsistent design",
        "bad fantasy details",
        "unfinished costume elements",
    ]

    lifestyle_negatives = [
        "stiff pose",
        "unnatural body position",
        "empty expression",
        "awkward candid framing",
        "flat lighting",
    ]

    group_negatives = [
        "merged bodies",
        "duplicated people",
        "fused limbs",
        "extra heads",
        "extra arms",
        "extra legs",
        "misaligned faces",
    ]

    headshot_negatives = [
        "cropped forehead",
        "cut-off chin",
        "bad facial crop",
        "off-center face",
    ]

    three_quarter_negatives = [
        "cropped legs",
        "awkward torso proportions",
        "broken arm positioning",
    ]

    full_body_negatives = [
        "cropped feet",
        "missing legs",
        "malformed shoes",
        "broken posture",
        "unnatural stance",
    ]

    locale_negatives = [
        "generic background",
        "inconsistent setting",
        "mismatched location details",
    ]

    expression_negatives = [
        "awkward expression",
        "unnatural facial expression",
        "emotionless face",
        "stiff face",
    ]

    gender_negatives = {
        "woman": [
            "masculine facial features",
            "masculine body proportions",
            "beard",
            "mustache",
            "masculine hairstyle",
        ],
        "man": [
            "feminine facial features",
            "feminine body proportions",
            "dress",
            "gown",
            "skirt",
            "high heels",
            "cleavage",
            "breasts",
            "feminine hairstyle",
        ],
        "non-binary": [],
    }

    keyword_map = {
        "portrait": portrait_negatives,
        "person": portrait_negatives,
        "woman": portrait_negatives,
        "man": portrait_negatives,
        "girl": portrait_negatives,
        "boy": portrait_negatives,
        "model": fashion_negatives,
        "fashion": fashion_negatives,
        "editorial": fashion_negatives,
        "glamour": fashion_negatives,
        "runway": fashion_negatives,
        "fantasy": fantasy_negatives,
        "warrior": fantasy_negatives,
        "mage": fantasy_negatives,
        "elf": fantasy_negatives,
        "knight": fantasy_negatives,
        "lifestyle": lifestyle_negatives,
        "group": group_negatives,
        "friends": group_negatives,
        "family": group_negatives,
        "headshot": headshot_negatives,
        "full body": full_body_negatives,
    }

    combined = list(base_negatives)

    type_map = {
        "Portrait": portrait_negatives,
        "Fashion": fashion_negatives,
        "Fantasy": fantasy_negatives,
        "Lifestyle": lifestyle_negatives,
        "Group": group_negatives,
        "Custom": [],
        "": [],
    }

    shot_map = {
        "Extreme close-up": headshot_negatives,
        "Headshot": headshot_negatives,
        "Tight portrait": portrait_negatives,
        "Chest-up": portrait_negatives,
        "Waist-up": three_quarter_negatives,
        "3/4 body": three_quarter_negatives,
        "3/4 Body": three_quarter_negatives,
        "Full body": full_body_negatives,
        "Full Body": full_body_negatives,
        "": [],
    }

    combined.extend(type_map.get(subject_type, []))
    combined.extend(shot_map.get(clean_value(data.get("shot_type")), []))
    combined.extend(gender_negatives.get(gender, []))

    if locale:
        combined.extend(locale_negatives)

    if expression:
        combined.extend(expression_negatives)

    for keyword, negatives in keyword_map.items():
        if keyword in subject:
            combined.extend(negatives)

    seen = set()
    ordered_unique = []
    for item in combined:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            ordered_unique.append(item)

    return ", ".join(ordered_unique)


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
    negative_prompt = build_negative_prompt(payload)
    return jsonify(
        {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
        }
    )


@app.post("/save")
def save_prompt():
    form_data = {
        "title": clean_value(request.form.get("title")),
        "subject_type": clean_value(request.form.get("subject_type")),
        "gender": clean_value(request.form.get("gender")),
        "shot_type": clean_value(request.form.get("shot_type")),
        "locale": clean_value(request.form.get("locale")),
        "subject": clean_value(request.form.get("subject")),
        "lighting": clean_value(request.form.get("lighting")),
        "camera": clean_value(request.form.get("camera")),
        "environment": clean_value(request.form.get("environment")),
        "time_of_day": clean_value(request.form.get("time_of_day")),
        "eye_color": clean_value(request.form.get("eye_color")),
        "expression": clean_value(request.form.get("expression")),
        "hair_length": clean_value(request.form.get("hair_length")),
        "hair_style": clean_value(request.form.get("hair_style")),
        "hair_color": clean_value(request.form.get("hair_color")),
        "outfit_type": clean_value(request.form.get("outfit_type")),
        "outfit_style": clean_value(request.form.get("outfit_style")),
        "outfit_color": clean_value(request.form.get("outfit_color")),
    }

    generated_prompt = build_prompt(form_data)
    negative_prompt = build_negative_prompt(form_data)

    if not form_data["title"]:
        form_data["title"] = f"Prompt - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO prompts (
                title,
                subject_type,
                gender,
                shot_type,
                locale,
                subject,
                lighting,
                camera,
                environment,
                time_of_day,
                eye_color,
                expression,
                hair_length,
                hair_style,
                hair_color,
                outfit_type,
                outfit_style,
                outfit_color,
                generated_prompt,
                negative_prompt,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form_data["title"],
                form_data["subject_type"],
                form_data["gender"],
                form_data["shot_type"],
                form_data["locale"],
                form_data["subject"],
                form_data["lighting"],
                form_data["camera"],
                form_data["environment"],
                form_data["time_of_day"],
                form_data["eye_color"],
                form_data["expression"],
                form_data["hair_length"],
                form_data["hair_style"],
                form_data["hair_color"],
                form_data["outfit_type"],
                form_data["outfit_style"],
                form_data["outfit_color"],
                generated_prompt,
                negative_prompt,
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