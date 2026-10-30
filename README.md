# QuestLearn: Shadows of the Machine 🖥️👻

> **An interactive retro CRT terminal RPG for narrative debugging and Socratic algorithmic learning powered by open-weight Google Gemma.**  
> Built for the **Hacktoberfest 2026 Open-Source AI Challenge** (*Week 4: Ghost in the Machine*).  
> 🌐 **Live Web Demo:** [https://questlearn-jy52.onrender.com/](https://questlearn-jy52.onrender.com/)

---

## 1. Executive Summary & Theme Resonance

**QuestLearn: Shadows of the Machine** immerses learners inside **AetherOS**, an abandoned 1980s mainframe corrupted by an autonomous execution daemon. To restore system integrity, the player must identify and repair algorithmic bugs in corrupted memory sectors.

### Theme Articulation: *Ghost in the Machine & Día de los Muertos*
In the cultural spirit of **Día de los Muertos**, memory is not merely dead storage—it is an altar. The learner communes with the digitized spirits of computer science pioneers residing in the machine's legacy registers:
* **Sector 0x01 (Recursion & Base Cases):** Guided by **Alan Turing** (*The Recursive Void / The Unending Spiral*).
* **Sector 0x02 (Array Bounds & Off-by-One):** Guided by **Grace Hopper** (*The Moth in the Relays*).
* **Sector 0x03 (Data Structures & Key Accumulation):** Guided by **Ada Lovelace** (*The Weaving Engine*).

The AI core is powered by open-weight **Google Gemma** models, functioning under strict Socratic policies that forbid giving raw code solutions, steering students through algorithmic inquiry instead.

---

## 2. Key Features

- **Retro Cathode Ray Tube (CRT) Interface:** Scanlines, phosphor bloom, curvature shaders, flicker effects, and selectable phosphor palettes (Green, Amber, Cyan).
- **Web Audio 8-Bit Synthesizer:** Real-time synthesized keystroke clicks, modem chirps, error buzzes, and victory arpeggios via the Web Audio API.
- **Socratic Open-Weight AI Core:** Powered by Google Gemma (`gemma-2-9b-it` or `gemma:2b`). Enforces strict negative prompt policies to prevent direct code leakage and encourage critical thinking.
- **AST-Verified Isolated Sandbox:** Multi-tier code execution harness with AST validation and a hard **2.0-second timeout** to protect against runaway recursion and infinite while-loops.
- **Dual-Tier Data Persistence:** Production MongoDB Atlas async driver (`motor`) with an automatic, zero-config local SQLite fallback (`aiosqlite`).
- **Interactive In-Terminal Code Editor:** Full modal code editor with syntax formatting and one-click patch submission via `Ctrl+Enter`.
- **System Integrity & Exorcism Report:** Comprehensive diagnostic and mastery report downloadable as `.txt` upon restoring system integrity to 100%.

---

## 3. System Architecture

```
QuestLearn (AetherOS)
├── [Presentation Layer]  -> Retro CRT Canvas, Web Audio Synthesizer, Vanilla JS Terminal
├── [Orchestration Layer] -> FastAPI, Session Lifecycle, Sector Progression
├── [Sandbox Layer]       -> AST Safety Filter, Isolated Python Subprocess (<= 2.0s timeout)
├── [Intelligence Layer]  -> Open-Weight Google Gemma (Groq / Ollama / HuggingFace)
└── [Persistence Layer]   -> MongoDB Atlas Async Client (motor) + SQLite Fallback (aiosqlite)
```

---

## 4. Quickstart & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.15)
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/questlearn.git
cd questlearn
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key settings:
```env
PORT=8000
GEMMA_API_BASE=https://api.groq.com/openai/v1
GEMMA_API_KEY=your_api_key_here
GEMMA_MODEL=gemma2-9b-it
MONGO_URI=your_mongodb_connection_string
```
*Note: QuestLearn includes an intelligent offline Socratic fallback engine. If no API key or MongoDB URI is provided, the game automatically runs offline with SQLite and localized persona heuristics!*

### 4. Launch AetherOS
```bash
uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000` in your browser.

---

## 5. Terminal Command Reference

| Command | Arguments | Description |
|---|---|---|
| `scan` | None | Scans current memory sector, prints buggy code, stack trace, and lore |
| `commune` | `<query>` | Consults the sector's historical spirit guide for Socratic hints |
| `patch` | `[code]` | Submits Python code to the sandbox harness (or opens editor) |
| `edit` | None | Opens the retro in-terminal visual code patch editor |
| `inspect` | None | Prints hardware registers, call stack depth, and heap telemetry |
| `status` | None | Displays overall integrity percentage and solved sectors |
| `sectors` | None | Lists all sectors in AetherOS and clearance status |
| `switch` | `<sector_id>` | Swaps focus between sectors (e.g., `switch 0x02`) |
| `report` | None | Compiles and downloads the official System Exorcism Report |
| `theme` | `[green\|amber\|cyan]` | Switches CRT phosphor color palette |
| `audio` | `[on\|off]` | Toggles 8-bit sound effects |
| `crt` | `[on\|off]` | Toggles CRT scanlines and screen flicker |
| `reset` | None | Resets session memory and restarts the challenge |
| `clear` | None | Clears visible terminal output |

---

## 6. Socratic Pedagogical Model & Quest Sectors

### Sector 0x01: The Unending Spiral
- **Topic:** Recursion and Base Cases (Stack Overflow).
- **Guiding Spirit:** Alan Turing.
- **Pedagogy:** Leads the learner to realize that every recursive call requires a non-recursive terminating condition ($n \le 1$).

### Sector 0x02: The Moth in the Relays
- **Topic:** Off-by-one errors and array bounds checking.
- **Guiding Spirit:** Grace Hopper.
- **Pedagogy:** Emphasizes zero-indexing and index comparison operators (`<=` vs `<`).

### Sector 0x03: The Weaving Engine
- **Topic:** Dictionary key accumulation and uninitialized access.
- **Guiding Spirit:** Ada Lovelace.
- **Pedagogy:** Illustrates key initialization patterns (`if key in dict` or `dict.get(key, 0)`).

---

## 7. Security & Sandboxing

1. **AST Pre-Execution Validation:** Prohibits hazardous imports (`os`, `sys`, `subprocess`, `socket`, `shutil`) and execution primitives (`eval`, `exec`, `open`).
2. **Subprocess Isolation:** Candidate patches are executed in a fresh isolated Python subprocess using the `-I` isolated mode flag.
3. **Hard 2.0s Timeouts:** Infinite loops and runaway recursion are automatically halted after 2 seconds.

---

## 8. Deployment Blueprint (Render)

This repository includes a production-ready `render.yaml` blueprint:
```yaml
services:
  - type: web
    name: questlearn-shadows
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 🌐 Community Wisdom & Proven Patterns

In developing **QuestLearn: Shadows of the Machine**, architectural decisions were informed by established patterns within the software and developer community:

1. **Subprocess Code Sandboxing & Defense-in-Depth:**
   - As emphasized across engineering and vulnerability research discussions on [dev.to](https://dev.to) regarding Python execution sandboxes, pure in-language restricted namespaces (`__builtins__ = {}` or `exec`) are notoriously prone to namespace traversal exploits. True isolation requires OS-level process boundaries, AST rejection of dangerous imports, and strict execution timeouts. QuestLearn utilizes isolated subprocess flags (`python -I`) coupled with AST safety filters.
2. **Socratic Prompt Engineering for Pedagogical AI:**
   - Research and practitioner guides on [dev.to/mchomsky](https://dev.to) and the broader LLM developer community demonstrate that direct code synthesis hinders student retention ("AI plagiarism" and shallow pattern imitation). By enforcing negative system prompts ("under no circumstances provide verbatim code") and scaffolding hints across successive student attempts, the LLM functions as an authentic Socratic tutor rather than a passive code generator.

---

## 9. License

Distributed under the **Apache 2.0 License**. Created with ❤️ for the Hacktoberfest 2026 Open-Source AI Challenge.
