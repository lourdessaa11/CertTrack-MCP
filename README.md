# CertTrack-MCP (Server Only)
 
CertTrack-MCP is a custom Model Context Protocol (MCP) server for managing certifications.
It supports Google Sheets for storage, Outlook.com personal accounts for sending emails, with fallbacks.
 
## Features
- List certifications by person.
- Add new certifications (validates duplicates, date format).
- Compute upcoming expirations (alerts).
- Send email via Microsoft Graph (user delegated) or mock if not configured.
 
## Requirements
- Python 3.10+  
- Packages: listed in `requirements.txt` (including google API, msal, requests)
 
## Installation
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```
 
## Configuration
- Copy or create `.env` file (don’t commit it).  
- Required variables:
  ```
  GOOGLE_SHEETS_MASTER_ID=<your_sheet_id>
  GOOGLE_SHEETS_TAB=Master
  MS_AUTH_MODE=user
  MS_CLIENT_ID=<your_app_client_id>
  ```
- Optional: application mode (if you want to use app credentials).
 
## Running
- Start the server:
  ```bash
  python server.py
  ```
- The server waits for MCP host commands (e.g. `/add-cert`, `/list-my-certs`, `/vencen`, `/correo`)
 
## .gitignore
```
.env
google_credentials.json
token.json
graph_user_cache.json
logs/
__pycache__/
```
 
## Usage
- `/add-cert`, `/mis-certs`, `/vencen`, `/correo` are available tools.
- Email sending uses Graph user mode first; falls back to mock if not configured.
 
## Security
- Never commit credentials or tokens.
- Use `.env` and ensure secrets are ignored.
