# FMEA Studio — Mini Automotive FMEA Analyzer

A Streamlit prototype for editing a small automotive Failure Mode and Effects Analysis (FMEA) register.

## Features
- Editable failure register: edit all fields, add rows, and delete rows in the table
- Add blank failure rows or clear the register
- Live RPN calculation (Severity × Occurrence × Detection)
- Configurable illustrative review threshold
- Risk overview metrics, ranked failure modes, and interactive charts
- CSV export of analyzed records
- Example automotive failure modes for demonstration

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

## Important limitation
This is an educational prototype with illustrative examples. RPN is a prioritization aid, not an ASIL determination, safety case, or replacement for company-approved FMEA procedures, rating criteria, or ISO 26262 safety analysis. Example data is synthetic and must not be presented as validated vehicle data.
