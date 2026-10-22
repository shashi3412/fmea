# FMEA Studio — Automotive FMEA Analyzer

A Streamlit application for editing an automotive Failure Mode and Effects Analysis (FMEA) register.

## Features
- Editable failure register: edit fields, add rows, and delete rows
- Live RPN calculation (Severity × Occurrence × Detection)
- Configurable review threshold
- Risk overview metrics, ranked failure modes, and interactive charts
- CSV export
- Starter automotive failure modes that can be replaced

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows:
```bat
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install and run:
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy online
1. Upload `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository.
3. Set the main file path to `app.py` and deploy.

## Engineering note
RPN is a prioritization aid and should not be the sole basis for accepting risk. Review high-severity failure modes independently and follow applicable organizational procedures for formal engineering decisions.
