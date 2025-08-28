# Job Alert Application 🚨

A lightweight Python watcher that polls a job board, **detects new postings in near-real time**, and **alerts you instantly** via email and an optional audible siren. Built for 24/7 monitoring so short-lived postings (often 2–5 minutes) don’t slip by.

---

## ✨ Highlights
- **Near-instant alerts**: Email + optional siren as soon as a matching job appears.
- **Session keep-alive**: Periodically refreshes the job site/session so results stay fresh.
- **Continuous monitoring**: Designed to run 24/7 (cron/systemd/Task Scheduler).
- **Proven impact**: Helped **8 friends** secure part-time roles by notifying them within seconds.

---

## 🧠 How It Works
1. **Keep-alive** — Pings a *refresh URL* every minute to maintain an active session.  
2. **Query** — Posts a GraphQL query to retrieve the latest job cards.  
3. **Filter & de-dupe** — Optionally filter by state/city/keywords; ignore job IDs you’ve already seen.  
4. **Notify** — On new matches, **play a siren** (optional) and **send an email** with job details.  

> ⚠️ **Use responsibly.** Respect the job site’s Terms of Service and rate limits. Tokens/cookies can expire and may require rotation.

---

## 📦 Requirements
- **Python** 3.10+
- **pip** for dependency management

`requirements.txt`:
```txt
requests==2.32.3
pygame==2.5.2
python-dotenv==1.0.1
```

Install:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🔐 Configuration
Create a file named **`.env`** in the project root:

```dotenv
# --- Job API / Session ---
JOB_GRAPHQL_URL=https://<your-appsync-endpoint>/graphql
JOB_REFRESH_URL=https://<the-site>/app#/jobSearch?query=&postal=&locale=en-CA

# Authorization or cookie headers (do not hardcode secrets in code)
AUTHORIZATION=Bearer <your-token-or-cookie>
USER_AGENT=Mozilla/5.0 ...
CONTENT_TYPE=application/json; charset=UTF-8

# --- Search parameters (tweak as needed) ---
LOCALE=en-CA
COUNTRY=Canada
KEYWORDS=
STATES_ALLOWED=ON,AB          # e.g., ON,QC,AB
CITIES_ALLOWED=               # optional: Laval,Montreal,Longueuil
POLL_INTERVAL_SECONDS=60

# --- Email (SMTP) ---
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=you@example.com
EMAIL_TO=you@example.com
EMAIL_PASSWORD=<app-password>  # Use a Gmail "App Password" with 2FA

# --- Siren (optional) ---
SIREN_SOUND_PATH=assets/siren.wav
ENABLE_SIREN=true
```

> ✅ **Gmail tip**: Enable 2-Step Verification → create an **App Password** → use it as `EMAIL_PASSWORD`. Do **not** use your normal Gmail password.

`.gitignore` additions:
```gitignore
.env
assets/*
!assets/.keep
```

---

## ▶️ Run Locally
```bash
# Activate venv if not active, then:
python job_alert.py
```

You’ll see logs like:
```text
Session refreshed successfully. Time now: 12:34:56
Found 3 jobs, 1 new.
[ALERT] New Job • ON • Toronto • FC Associate • $20–$23/hr • 7.2 km
Email sent to you@example.com
```

---

## 🛠️ Key Implementation Notes
```python
# Keep-alive
requests.get(JOB_REFRESH_URL, headers=headers)

# GraphQL query
requests.post(JOB_GRAPHQL_URL, json={"query": QUERY, "variables": variables}, headers=headers)

# De-duplication
seen_jobs: set[str] = set()
if job_id not in seen_jobs:
    seen_jobs.add(job_id)
    # notify...

# Email (TLS + app password)
with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()
    server.login(EMAIL_FROM, EMAIL_PASSWORD)
    server.send_message(msg)

# Optional siren
pygame.mixer.music.load(SIREN_SOUND_PATH)
pygame.mixer.music.play()
```

---

## 🖥️ Keep It Running 24/7

### Linux (systemd)
```ini
# /etc/systemd/system/job-alert.service
[Unit]
Description=Job Alert Monitor
After=network.target

[Service]
WorkingDirectory=/path/to/project
Environment="PYTHONPATH=/path/to/project"
ExecStart=/path/to/project/.venv/bin/python job_alert.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now job-alert
sudo journalctl -u job-alert -f
```

### macOS/Linux (cron)
```cron
* * * * * cd /path/to/project && /path/to/.venv/bin/python job_alert.py >> job.log 2>&1
```

### Windows (Task Scheduler)
```text
Create Task → Triggers: At startup / On a schedule
Action: Start a program → Program/script: python
Add arguments: C:\path\to\job_alert.py
Check: Run whether user is logged on or not
```

---

## 🧪 Troubleshooting
- **403 / Unauthorized** — Token/cookies expired or headers incomplete. Re-login in a browser, capture fresh headers, update `.env`.
- **SMTP auth fails** — Use an **App Password** (TLS on port 587). Ensure 2FA is enabled.
- **No sound / mixer error** — On headless servers set `ENABLE_SIREN=false` or `SDL_AUDIODRIVER=dummy`.
- **Empty results** — Loosen filters (`STATES_ALLOWED`, `CITIES_ALLOWED`, `KEYWORDS`) or verify GraphQL variables.

---

## ✅ Security Checklist
- Never commit `.env` or tokens.
- Rotate tokens periodically.
- Use a dedicated email + App Password.
- Respect site ToS and throttle requests as needed.

---

## 🗺️ Roadmap
- [ ] Persist `seen_jobs` across restarts (SQLite/JSON)
- [ ] Multi-channel alerts (Telegram/Slack/Discord, Twilio SMS)
- [ ] Advanced filters (pay range, distance, shift type)
- [ ] Exponential backoff + structured logging
- [ ] Docker image for one-command deployment

---

## 🙌 Acknowledgements
- `requests`, `pygame`, `python-dotenv`
- Real-world need: active jobs often vanish in **2–5 minutes**; this tool improved response time for our group.

