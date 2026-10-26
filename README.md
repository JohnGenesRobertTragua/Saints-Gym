# Saints Gym Management System

A Flask and SQLite-based gym management application created as a software portfolio project.

## Features

- Staff login and administrative dashboard
- Member registration and member management
- Member and guest check-in/check-out workflows
- Attendance history and dashboard reporting
- Staff account recovery/settings workflows
- Responsive pages and phone-oriented styling
- SQLite database integration

## Technology Stack

- Python
- Flask
- SQLite
- HTML, CSS, and JavaScript
- Waitress for local serving; Gunicorn configuration is included for supported hosting environments

## Run locally

1. Install Python 3.10 or newer.
2. Clone or download this repository.
3. Open a terminal in this folder and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate it on Windows:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   Or in Command Prompt:

   ```bat
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env` and replace every placeholder with private values. Use a unique random `FLASK_SECRET_KEY` at least 32 characters long, a private master username, and a strong master password of at least 8 characters. Never commit `.env`.
7. Start the local server:

   ```bash
   python run_server.py
   ```

8. Open `http://127.0.0.1:5000` in your browser.

The app creates/uses its SQLite database at the configured `SAINTS_DATABASE_PATH`; when not set, it uses `gym.db` in the project directory. The database file is intentionally excluded from this public portfolio package.

## Environment configuration

See `.env.example` for configuration variable names. It contains placeholders only. Do not publish real credentials, secret keys, customer data, database files, backups, or production environment files.

## Portfolio and privacy note

This repository is a public demonstration copy. It does not include the operational SQLite database or a real `.env` file. Use your own test data and private credentials for local testing. Before publishing, confirm you have permission to share the application code and any included branding/assets. This project has not been represented as a full independent security audit.

## License

No license is specified. Add a license only after deciding what reuse permissions you want to grant.
