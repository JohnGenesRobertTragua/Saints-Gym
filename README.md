# Saints Gym Management System

Flask + SQLite gym management application with Windows local-network launcher files.

## Included
- Flask application and database module
- HTML templates and static CSS, JavaScript, and assets
- `gym.db`: a small database containing fictional demonstration records
- Python dependencies (`requirements.txt`)
- Waitress production server (`run_server.py`)
- Windows launcher scripts and startup page
- Placeholder environment configuration (`.env.example`)

## Local setup
1. Install Python 3.12 or a compatible supported Python version.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set a strong private `FLASK_SECRET_KEY`, `SAINTS_MASTER_USERNAME`, and `SAINTS_MASTER_PASSWORD`.
5. Confirm `SAINTS_DATABASE_PATH` points to this project's `gym.db`.
6. Start with `python run_server.py`, or use the Windows launcher.

## Demo database and privacy
`gym.db` is included intentionally so the repository can be previewed with sample records. The names and phone numbers in it are fictional demonstration data. Do not enter real customer information into a public demo copy. Before using Saints Gym for an actual business, create and configure a separate production database. Never commit `.env`, real credentials, client/member records, database backups, `.venv`, or Python cache files. `.env.example` contains placeholders only.

## Deployment
The launcher scripts are for a Windows local-network installation. The server computer must be running and connected to the gym network for other devices on that network to access the application. Do not use the public sample database as the client's live database.
