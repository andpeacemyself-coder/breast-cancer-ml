# Breast Cancer Prediction Web App

A small Flask + Tailwind CSS web application that predicts whether a breast
tumour is **Malignant (M)** or **Benign (B)** from 30 cell-measurement features,
using a scikit-learn `RandomForestClassifier` trained on the Wisconsin
Diagnostic Breast Cancer dataset.

> ⚠️ **Disclaimer:** This is a demonstration project trained on a public
> research dataset. It is **not** a medical device and must **not** be used for
> real diagnosis or clinical decisions.

---

## What's in the project

```
breast_cancer_app/
├── app.py               # Flask server: loads the model, serves the form, runs predictions
├── train_model.py       # Reproducible script that trains and saves cancer_model.pkl
├── cancer_model.pkl      # The trained model (regenerate with train_model.py if missing)
├── requirements.txt     # Pinned Python dependencies
├── templates/
│   └── index.html       # Tailwind CSS UI (30-field form + result banner)
└── venv/                # Local virtual environment (you create this yourself)
```

Tailwind CSS is loaded from a CDN inside `index.html`, so there is **no Node.js
or npm build step** — you only need Python.

---

## Prerequisites

### 1. Install Python (3.11 or newer; developed on 3.13.2)

**Windows**
1. Download the installer from <https://www.python.org/downloads/>.
2. Run it and — importantly — tick **"Add python.exe to PATH"** on the first screen.
3. Finish the install, then open a **new** PowerShell window and verify:

   ```powershell
   python --version
   ```

   You should see `Python 3.13.x` (or your installed 3.11+ version).

**macOS**

```bash
brew install python@3.13
```

**Linux (Debian/Ubuntu)**

```bash
sudo apt update && sudo apt install python3 python3-venv python3-pip
```

### 2. Git (only needed to clone the repo)

Download from <https://git-scm.com/downloads>, or install via your package
manager. Verify with `git --version`.

---

## Setup & Installation

Run these from a terminal, one step at a time.

### Step 1 — Get the code

```bash
git clone <your-repo-url>
cd breast_cancer_app
```

If you already have the folder, just `cd` into it.

### Step 2 — Create a virtual environment

A fresh `venv` keeps this project's dependencies isolated. **Create your own** —
don't rely on a `venv/` that came with a download, since it's tied to another
machine's paths.

```bash
python -m venv venv
```

### Step 3 — Activate the virtual environment

**Windows — PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows — Command Prompt (cmd)**

```bat
venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
source venv/bin/activate
```

Once active, your prompt shows `(venv)`. (See Troubleshooting if PowerShell
blocks the activation script.)

### Step 4 — Install the dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, joblib, numpy, and scikit-learn (plus their sub-dependencies).

---

## Make sure the model exists

The app needs `cancer_model.pkl` in the project root. If it's already there,
skip this. If it's missing (for example, it wasn't committed to the repo),
regenerate it — it takes a few seconds:

```bash
python train_model.py
```

Expected output ends with something like:

```
Hold-out test accuracy: 0.9649
Saved model to: ...\breast_cancer_app\cancer_model.pkl
```

---

## Run the app

With the virtual environment active:

```bash
python app.py
```

You'll see:

```
[startup] Loaded model from ...\cancer_model.pkl
 * Running on http://127.0.0.1:5001
```

Open **<http://127.0.0.1:5001>** in your browser.

> **Why 5001 and not 5000?** On many Windows 11 machines port 5000 is reserved
> by the system (Hyper-V / WSL2), which causes `WinError 10013`. The app
> defaults to **5001** to avoid this.

### Using a different port

Set the `PORT` environment variable — no code change needed:

**PowerShell**

```powershell
$env:PORT=8000; python app.py
```

**macOS / Linux**

```bash
PORT=8000 python app.py
```

---

## How to use it

1. Enter values for all **30 features** in the form (they map to the standard
   Wisconsin dataset measurements — `radius_mean`, `texture_mean`, … through
   `fractal_dimension_worst`).
2. Click **Run Prediction**.
3. A banner shows the result: **Malignant (M)** (red) or **Benign (B)** (green).

To stop the server, press `Ctrl + C` in the terminal.

---

## Troubleshooting

**`WinError 10013` / "socket ... forbidden by its access permissions"**
Port is reserved or in use. The app already uses 5001; if that's also taken,
pick another with `$env:PORT=8000; python app.py`.

**PowerShell: "running scripts is disabled on this system"** (activation blocked)
Allow local scripts for your user, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**"Error: model not loaded"** on the page
`cancer_model.pkl` is missing or unreadable. Regenerate it with
`python train_model.py` and restart the app.

**`ModuleNotFoundError` (e.g. No module named 'flask')**
The virtual environment isn't active, or dependencies aren't installed. Activate
`venv` (Step 3) and run `pip install -r requirements.txt` again.

**`python` is not recognized**
Python isn't on your PATH. Reinstall with "Add python.exe to PATH" ticked, or
try the `py` launcher on Windows (`py --version`, `py -m venv venv`, `py app.py`).

**Model unpickling warning about scikit-learn version**
The model was saved with the pinned versions in `requirements.txt`. If you
installed different versions, either match the pins or just retrain with
`python train_model.py`.

---

## Tech stack

- **Python** 3.13.2 (3.11+ supported)
- **Flask** 3.1.3 — web framework
- **scikit-learn** 1.9.0 — `RandomForestClassifier`
- **numpy** 2.5.1, **joblib** 1.5.3 — arrays & model persistence
- **Tailwind CSS** (CDN) — styling, no build step


