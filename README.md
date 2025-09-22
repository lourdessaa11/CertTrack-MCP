## MCP Server Specification (CertTrack-MCP)
 
CertTrack-MCP is an MCP server (client-host-server model) built on JSON-RPC 2.0. For background on MCP architecture, see the official docs. 
 
**Transport/Protocol:** JSON-RPC 2.0 (per MCP).  
**Role in MCP:** This repo is the **server**; it exposes tools the host can call.  
**State/Context:** The server is stateless per request; persistence lives in Google Sheets (or CSV fallback).
 
References: MCP architecture & spec. 
- https://modelcontextprotocol.io/docs/concepts/architecture  
- https://modelcontextprotocol.io/specification/2025-06-18/architecture  
 
---

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/lourdessaa11/CertTrack-MCP.git
   cd CertTrack-MCP
   ```

2. Create and activate a virtual environment, then install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   # source .venv/bin/activate   # Mac/Linux
   pip install -r requirements.txt
   ```

3. Create a file `.env` in the project root. Minimum config:
   ```
   GOOGLE_SHEETS_MASTER_ID=<your_sheet_id>
   GOOGLE_SHEETS_TAB=Master
   MS_AUTH_MODE=user
   MS_CLIENT_ID=<your_azure_app_client_id>
   ```

4. Run the server:
   ```bash
   python server.py
   ```

The server will start and expose its tools. Use your MCP host to connect and call them.

---
 
## Tools
 
### 1) `health() -> object`
**Purpose:** Liveness check.  
**Inputs:** none  
**Output (JSON):**
```json
{ "ok": true, "server": "CertTrack-MCP" }
```
 
---
 
### 2) `list_my_certs(nombre: string) -> object`
**Purpose:** List certifications for a given person name.  
**Backend:** 
- **Google Sheets** (primary) via `spreadsheets.values.get` with A1 ranges. 
- **CSV fallback**: `certtrack_mcp/data/master.csv` (auto-created with sample rows).
**Inputs:**
- `nombre` (string) — Full name to match (case-insensitive).
**Output (JSON):**
```json
{
  "ok": true,
  "source": "sheets",         // or "csv"
  "count": 1,
  "certs": [
    {
      "certificacion": "DevOps III",
      "fecha": "2025-12-10",
      "vigencia_meses": 12,
      "proveedor": "Google",
      "tipo": "Tecnica",
      "costo": 185.0,
      "drive_file_id": "",
      "vence_el": "2026-12-10"
    }
  ]
}
```
**Notes (Sheets):** Uses the Google Sheets API. When appending/reading, user-entered parsing rules may apply if `USER_ENTERED` is used elsewhere (see Sheets docs). 

---

### 3) `sheets_append_cert(row: object) -> object`
**Purpose:** Append a new certification row to the master dataset.  
**Backend:** 
- **Google Sheets (primary):** `spreadsheets.values.append`  
  - `valueInputOption=USER_ENTERED` (values parsed as if typed by a user).  
- **CSV fallback** if Sheets isn’t configured.
**Required fields in `row`:** 
- `id`, `certificacion`, `nombre`, `fecha` (YYYY-MM-DD), `vigencia_meses`  
**Optional fields:** 
- `proveedor`, `tipo`, `costo`, `drive_file_id`
**Validation:** 
- Prevents duplicate `id`.  
- Validates date format `YYYY-MM-DD`.
**Output (JSON), examples:**
- CSV fallback:
```json
{ "status": "ok", "store": "csv", "inserted_at_row": 6 }
```
- Sheets (primary):
```json
{ "status": "ok", "store": "sheets" }
```
- Duplicate id:
```json
{ "status": "error: id duplicado: u4-dev-004" }
```
**Notes:** See Sheets `values.append` & `ValueInputOption`. 
 
---
 
### 4) `alerts_schedule_due(days?: number = 30) -> object`
**Purpose:** Compute certifications that will expire in the next X days, based on `fecha + vigencia_meses`.  
**Inputs:** 
- `days` (integer, optional; default 30).
**Output (JSON):** 
```json
{
  "ok": true,
  "source": "sheets",      // or "csv"
  "days": 30,
  "alerts": [
    {
      "nombre": "Laura Lopez",
      "certificacion": "DevOps I",
      "vence_el": "2026-10-01",
      "provider": "email-mock"     // or "graph_user" when coupled with outlook_send_email
    }
  ]
}
```
 
---

### 5) `outlook_send_email(to: string, subject: string, html: string) -> object`
**Purpose:** Send an email; prefers **Microsoft Graph (delegated, Device Code)** for Outlook.com personal accounts; falls back to **mock** if not configured.  
**Modes:**
- **User (delegated)**: `/me/sendMail` with scope **Mail.Send** via MSAL **Device Code** (tokens cached locally).  
- **Mock fallback**: prints message and returns a fake `message_id`.
**Inputs:**
- `to` (string; must contain `@`)  
- `subject` (string, non-empty)  
- `html` (string, non-empty)
**Output (JSON), examples:**
- Delegated Graph (user):
```json
{ "ok": true, "message_id": "graph-user-<hash>", "provider": "graph_user" }
```
- Mock fallback:
```json
{ "ok": true, "message_id": "mock-<hash>", "provider": "mock" }
```
**References (Graph):** `POST /me/sendMail` (delegated) and Mail.Send permission.

---

## Configuration quick-ref

**.env (server root)**
```
GOOGLE_SHEETS_MASTER_ID=<sheet_id>
GOOGLE_SHEETS_TAB=Master
MS_AUTH_MODE=user
MS_CLIENT_ID=<your_azure_app_client_id>
```
**Secrets/tokens (git-ignored):**
- `google_credentials.json` (OAuth client; Sheets).  
- `token.json` (Sheets user token).  
- `graph_user_cache.json` (MSAL device code cache).

---

## Example host commands (from your console host)

- Append:
  ```
  /add-cert id=u4-dev-006 certificacion="DevOps III" nombre="Carlos Ramirez" fecha=2025-12-10 vigencia_meses=12 proveedor=Google tipo=Tecnica costo=185
  ```
- Query by person:
  ```
  /mis-certs Carlos Ramirez
  ```
- Expiring soon:
  ```
  /vencen 30
  ```
- Email:
  ```
  /correo to=you@outlook.com subject="Test Graph User" html="<p>Hello</p>"
  ```
 
---

## Notes & References
- **Course requirement:** Provide the server specification (tools, params, examples) and keep the server in a **public, independent repo**. 
- MCP architecture/spec:
  - Architecture overview (MCP site)  
  - Architecture section (spec, 2025-06-18)
- Google Sheets API:
  - `spreadsheets.values.append`  
  - `ValueInputOption` (RAW vs USER_ENTERED)
- Microsoft Graph:
  - `POST /me/sendMail` (delegated)  
  - Permissions reference (`Mail.Send`, delegated)


