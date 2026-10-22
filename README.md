# Mini FMEA Analyzer

An interactive, learning-oriented Failure Mode and Effects Analysis (FMEA) prototype for exploring automotive-style failure modes with synthetic data.

## Features

- Editable failure-mode register
- Severity, Occurrence, and Detection ratings (1–10)
- RPN calculation: `RPN = Severity × Occurrence × Detection`
- Ranked results and an interactive bar chart
- Illustrative high-RPN threshold
- CSV export
- Example ECU/sensor/communication failure modes

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Deploy free with Streamlit Community Cloud

1. Create a public GitHub repository named `mini-fmea-analyzer`.
2. Upload `app.py`, `requirements.txt`, and this `README.md`.
3. Sign in to Streamlit Community Cloud and create an app from that repository.
4. Set the main file path to `app.py` and deploy.
5. Test the public app link in a private/incognito window before sharing it.

## Method and limitations

This tool is a small educational prototype. The sample data is synthetic and is not an assessment of any real vehicle or ECU.

RPN is calculated as Severity × Occurrence × Detection using 1–10 ratings. The rating definitions and high-RPN threshold are illustrative and should be tailored to a documented process. RPN is a prioritization aid, not a substitute for engineering judgment, safety analysis, or an ISO 26262 ASIL determination. A low RPN should not automatically dismiss a high-severity failure.

## Suggested next improvements

- Add configurable rating-scale definitions
- Add action owner, due date, and residual-risk fields
- Add before/after action RPN comparison
- Add unit tests for calculations and input validation
- Add a controlled report template and revision history
