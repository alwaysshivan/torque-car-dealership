# Torque — start here

## Windows (recommended for your laptop)

1. Extract the entire ZIP. Do not run files from inside the ZIP.
2. Install Python 3.11+ with the Python Launcher enabled. Internet is needed the first time to download Python dependencies. The prebuilt React frontend is included, so Node.js is only needed if you edit/rebuild it.
3. Double-click **START-WINDOWS.bat**. Wait for `Application startup complete`.
4. Open **http://127.0.0.1:8000** in your browser. Keep the terminal window open.
5. For a regular customer account, click **Create an account**.

### Set up the administrator and sample cars

After the first launch, open PowerShell in the extracted `car-dealership` folder. Run these as two separate commands:

```powershell
.\.venv\Scripts\python.exe -m backend.cli create-admin --email admin@example.com --name "Showroom Admin"
.\.venv\Scripts\python.exe -m backend.cli seed
```

Choose your own password of at least 10 characters when prompted. Password typing is hidden; press Enter after typing, then confirm. There is no built-in admin password.

Sign in with `admin@example.com` and that password. If already signed in as a regular user, sign out first using the bottom-left icon. Refresh the page after seeding. You will see eight fictional vehicle listings, including a zero-stock vehicle to demonstrate disabled purchasing.

## What to try

1. Sign in as admin. Add a vehicle; search for it; edit its price; restock it.
2. Create a separate regular account. Search or filter the showroom and purchase a vehicle. The quantity drops and a receipt appears under **My purchases**.
3. Try the zero-stock vehicle: its Purchase button is disabled.
4. Sign in as admin again: only administrators can add, edit, delete, or restock vehicles.
5. Close and reopen the app. Users, stock, and receipts remain in `data/dealership.sqlite3`.

Purchasing is an inventory transaction. No money is collected, and no external order is placed. Prices and vehicle illustrations are demonstration content.

## Before submitting the assignment

- Read README.md and the test report in docs/TEST-REPORT.md.
- Use the supplied Git history; do not upload only a fresh single-commit copy if the evaluator checks TDD.
- Create an empty public Git repository, restore the included bundle, and push using the README instructions.
- PROMPTS.md contains verbatim visible development messages, not a complete export of tool events. Add your actual full chat export or public share link before final submission, as the assignment requests raw AI logs.
- Add dashboard/purchase screenshots from your local run. The included screenshots show the sign-in and registration screens; an integrated browser walkthrough was not available in the build environment.

The application is implemented and tested locally. A public repository and an optional live deployment have not been created for you.
