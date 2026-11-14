SAINTS GYM — LOCAL DEPLOYMENT PACKAGE

This folder contains the Saints Gym application for local use on a Windows
computer. The application code, templates, static assets, startup scripts, and
SQLite database with fictional demonstration records are included. This file replaces older developer notes.

SETUP ON THE COMPUTER THAT WILL RUN SAINTS GYM
1. Copy the entire Saints_Gym_Final_Deployment folder to a permanent location
   on that computer. Do not run the application directly from the USB drive.
2. Install Python if it is not already installed. Python 3.12 is the preferred
   version for the tested setup.
3. Run INSTALL_DEPENDENCIES.bat. An internet connection is needed while Python
   packages are downloaded. Wait for the script to finish successfully.
4. If .env does not exist, copy .env.example to .env.
5. Edit .env and set a unique FLASK_SECRET_KEY (at least 32 characters),
   SAINTS_MASTER_USERNAME, and a strong SAINTS_MASTER_PASSWORD (at least 8
   characters). Keep .env private; never upload it publicly or share its values.
6. Ensure SAINTS_DATABASE_PATH points to this folder's gym.db. This repository's
   gym.db contains fictional demo records; do not use it for real customer data.
   Create a separate production database for an actual gym installation.
7. Create a desktop shortcut to LAUNCH_SAINTS_GYM.bat and use that shortcut to
   start Saints Gym and open the browser.

WHILE RUNNING
- Keep the minimized Saints Gym server console open. Closing it stops the app.
- The computer must remain powered on and the server running while in use.
- In this local setup, phones need to be on the same Wi-Fi network to access
  Saints Gym using its local network address or QR code.
- To stop the server, bring its console forward and press Ctrl+C.

DATABASE AND BACKUPS
- The included gym.db contains fictional demonstration records for previewing
  the application. It is not the client's live database.
- Use a separate database for a real gym installation; never mix demo records
  with actual customer records.
- Keep a separate backup before maintenance or database changes.
- After configuration, verify staff login and the main workflows before handover.
