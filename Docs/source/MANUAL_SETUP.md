# FinSpark'26 — Manual Setup Checklist

These are the things **Claude Code can't (or shouldn't) do for you** — accounts, credentials, downloads that need your login, registration, and anything requiring a human decision. Do the ⭐ ones **before** you start Prompt 0, or Claude Code will stall waiting on data.

---

## A. Do these TODAY, before Prompt 0

### ⭐ 1. Register for Problem Statement 2
Register your team for **PS2 (AI-driven correlation of cybersecurity telemetry & transactional behaviour)** on the FinSpark'26 portal. The roadmap is clear: pick PS2, mention PS1 (privileged-access misuse) only verbally as a bonus the same engine gives you. Don't split the build.

### ⭐ 2. Install the base tools
| Tool | Why | Check |
|---|---|---|
| Python 3.11+ | ML + API | `python --version` |
| Node 18+ (20 LTS ideal) | React dashboard | `node --version` |
| Git | version control | `git --version` |
| Claude Code | the builder | `claude --version` |

### ⭐ 3. Set up the Kaggle API (needed for 3 of the 4 datasets)
1. Create/login to a Kaggle account.
2. Account → **Settings → API → Create New Token**. This downloads `kaggle.json`.
3. Place it at `~/.kaggle/kaggle.json` (Linux/Mac) or `C:\Users\<you>\.kaggle\kaggle.json` (Windows) and `chmod 600` it.
4. **Do not paste this token into Claude Code or share it.** Claude Code writes the download script; the token stays with you.

### ⭐ 4. Accept dataset rules, then let Claude Code download them
The Kaggle API only downloads a dataset **after you've clicked "accept rules" on its page while logged in.** Open each and accept:

| Dataset | Kaggle slug | Note |
|---|---|---|
| PaySim | `ealaxi/paysim1` | ~470 MB, 6.3M rows. Transaction backbone. |
| IEEE-CIS Fraud | `ieee-fraud-detection` | **Competition** dataset — you must also accept the *competition* rules to pull via API. Gives real device/identity features. |
| Elliptic Bitcoin | `ellipticco/elliptic-data-set` | Graph model (GraphSAGE). |

**UNSW-NB15** (the cyber-intrusion source): download from the UNSW ADFA site or a Kaggle mirror and drop the CSV into `/data/raw` manually — it's not always API-pullable. CICIDS2017 is an acceptable substitute.

> Downloads are large and slow. Kick them off first so they finish while you scaffold.

---

## B. Do before Day 2 (Prompt 3) — optional but nice

### 5. Neo4j Aura Free (only if you want the real graph store)
1. Create a free instance at Neo4j Aura.
2. Save the **connection URI**, **username**, and **generated password** — you only see the password once.
3. Put them in your local `.env` (which is gitignored):
   ```
   NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your-password
   ```
Claude Code's code auto-detects this and falls back to in-memory `networkx` if it's absent. **If Aura setup eats more than an hour, skip it** — the roadmap explicitly permits the networkx fallback.

### 6. Mentoring Session 2 — Sun 13 Jul, 7:00 PM
Show up with the three sharp questions:
1. Is a synthetic cyber-fraud correlation overlay acceptable as our evaluation harness?
2. Which compliance hook impresses the jury most — CERT-In auto-report or DPDP consent?
3. Finale: live demo or recorded?

Then ask what *they'd* want to see on stage.

---

## C. Do on Day 4–5 (Prompts 5–6)

### 7. Record the 3-minute demo video (your parachute)
Steady screen capture + voiceover of the killer demo (use `/docs/demo_script.md` that Claude Code generates). This is your safety net if the live run fails at COEP. Keep it queued during the finale.

### 8. Deployment accounts (optional polish — a public link raises perceived quality)
- **Vercel** for `/web`.
- **Render** or **Railway** for the FastAPI backend.
Create the accounts and run the deploy commands **yourself** — Claude Code prepares the config but should not log in or enter credentials on your behalf.

### 9. Fill the deck placeholders (human judgement)
Team name, repo link, demo-video link, and real screenshots (roadmap flags slides 1, 7, 15, 16). Add the **PS2 coverage checklist** slide from `/docs/ps2_coverage.md`.

### 10. Submit hours early on Jul 16
Deadline-day portals get congested. Submit with buffer.

---

## Quick "who does what" summary

| Task | You | Claude Code |
|---|---|---|
| Hackathon registration | ✅ | — |
| Kaggle token + accepting dataset rules | ✅ | — |
| Running the download script | — | ✅ (writes it; you run it once creds are set) |
| Fusion overlay, models, engine, API, UI | — | ✅ |
| Neo4j Aura account + password | ✅ | — |
| Mentoring session | ✅ | — |
| Demo video recording | ✅ | — |
| Deploy config | — | ✅ |
| Actually deploying (login) | ✅ | — |
| Deck placeholders + screenshots | ✅ | — |
| Final submission | ✅ | — |

---

## One-breath version of the whole plan
Set up data + tools today → let Claude Code build the fusion overlay (Prompt 1), then honest models (Prompt 2), then the graph + fusion engine by the 13th (Prompt 3) → dashboard + XAI on the 14th (Prompt 4) → quantum + CERT-In + the 90-second demo on the 15th (Prompt 5) → README, polish, submit early on the 16th (Prompt 6). Build the slice, describe the rest.
