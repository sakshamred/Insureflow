# InsureFlow — Insurance Policy Management

A small DBMS mini-project using Streamlit, Python and SQLite.

## Features
- Add and view policyholders
- Create Life, Health and Vehicle policies
- Automatic premium calculation
- Register claims and approve/reject them
- Record payments
- Dashboard with summary cards and charts
- Sample data is inserted automatically on first run

## Premium formula

`Premium = Sum Insured × Base Rate × Risk Multiplier`

| Policy | Base rate |
|---|---:|
| Life | 1% |
| Vehicle | 1.5% |
| Health | 2% |

| Risk | Multiplier |
|---|---:|
| Low | 0.9 |
| Medium | 1.0 |
| High | 1.4 |

Example: Health + ₹5,00,000 + High risk = `500000 × 0.02 × 1.4 = ₹14,000`.

## Requirements
- Python 3.9+
- Internet for the first package installation

## Run on Windows
Open Command Prompt inside this folder and run:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Run on macOS / Linux
Open Terminal inside this folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Database
The SQLite database file `insurance.db` is created automatically beside `app.py`.
The app creates four tables: `policyholders`, `policies`, `claims`, and `payments`.

To reset all demo data: stop the app, delete `insurance.db`, then run the app again.

## DBMS concepts demonstrated
Primary keys, foreign keys, relational tables, CHECK constraints, CRUD operations, joins, aggregate functions, and premium calculation logic.

> This is an educational demonstration. Premium rates and risk multipliers are sample values, not real insurance pricing.
