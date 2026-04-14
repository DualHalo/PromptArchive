# PromptArchive v1

PromptArchive is a local Flask + SQLite app for building reusable image prompts with a structured, MadLibs-style UI.

## Features

- Live prompt generation
- Save prompts to SQLite
- Load saved prompts back into the builder
- Favorite prompts
- Delete prompts
- Surprise Me randomizer
- Windows batch setup helpers

## Project structure

```text
PromptArchive/
├── app.py
├── promptarchive.db
├── requirements.txt
├── README.md
├── build_promptarchive.bat
├── run_promptarchive.bat
├── init_github_backup.bat
├── templates/
│   └── index.html
└── static/
    ├── styles.css
    └── script.js
```

## Run locally

1. Double-click `build_promptarchive.bat`
2. Then double-click `run_promptarchive.bat`
3. Open the local URL shown in the terminal

## Notes

- The GitHub helper assumes your GitHub username is `DualHalo`
- If GitHub CLI (`gh`) is installed and authenticated, the backup helper can create the repo for you
- Otherwise it will initialize git locally and prompt you to create the remote repo manually
