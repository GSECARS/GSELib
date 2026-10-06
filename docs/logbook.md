# Logbook

The `logbook` module provides a beamline logbook backed by Google Docs. Entries are appended with timestamps and styled automatically; the document stays live and shareable in real time.

## Installation

```bash
pip install 'gselib[logbook]'
```

## Configuration

Authentication uses a Google service account. Place the JSON key file on disk and point to it via environment variables, either exported in the shell or in a `.env` file.

| Environment variable | Description |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT` | Path to the service account JSON key file (default: `service-account.json`) |
| `LOGBOOK_DOCUMENT_ID` | Google Doc ID to use when `--doc-id` is not passed |

Minimal `.env`:

```ini
GOOGLE_SERVICE_ACCOUNT=/path/to/service-account.json
LOGBOOK_DOCUMENT_ID=SomeDocumentID
```

The Doc ID is the long string in the document URL:
`https://docs.google.com/document/d/<DOCUMENT_ID>/edit`

## CLI

All commands are available under `gselib logbook`. Pass `--doc-id` to target a specific document, or set `LOGBOOK_DOCUMENT_ID` in your `.env`.

### Create a new logbook

```bash
gselib logbook create "13BMC Run 2026-3 Logbook"
```

Prints the new document ID. Share it with your team before starting the run.

### Append an entry

```bash
gselib logbook append "Collection started."
```

With an explicit document ID:

```bash
gselib logbook --doc-id YourDocumentID \
    append "Beam lost"
```

### Save a local copy

```bash
gselib logbook save /data/logs/logbook.pdf
```

Supported formats: `.pdf`, `.docx`, `.txt`, `.md`. Defaults to PDF for unknown extensions.

### Share the document

```bash
gselib logbook share user@example.com
gselib logbook share user@example.com --role viewer
gselib logbook share user@example.com --role commenter
```

Available roles: `editor` (default), `viewer`, `commenter`.

### Custom `.env` path

```bash
gselib logbook --env /beamline/config/.env append "Sample changed"
```

## Library

```python
from gselib.logbook import Logbook

# Open an existing logbook (reads LOGBOOK_DOCUMENT_ID from .env)
lb = Logbook()
lb.append("Collection started.")
lb.save("/data/logs/logbook.pdf")

# Explicit document ID
lb = Logbook(document_id="YourDocumentID")
lb.append("Beam lost")

# Custom .env location
lb = Logbook(env_file="/beamline/config/.env")

# Create a new logbook document programmatically
lb = Logbook(create_title="13BMC Run 2026-3 Logbook")
print(lb.document_id)  # save this for future sessions

# Share with a colleague
lb.share("colleague@example.com")  # editor by default
lb.share("observer@example.com", role="reader")  # read-only
```
