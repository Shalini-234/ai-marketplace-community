# AI Community Marketplace

CommunityMarket is a local resource-sharing marketplace for buying, selling, borrowing, lending, exchanging items, and finding neighbourhood services. Its AI search turns a natural-language request into safe, structured filters, then ranks local listings with an explainable score.

## Problem and solution

Useful things often sit idle while someone nearby needs them. CommunityMarket makes those resources discoverable without forcing people to learn rigid filters: a request such as “I need a bicycle for college for 3 days under ₹500” becomes a borrowing, transportation, budget-aware search.

## Features

- Polished responsive vanilla HTML/CSS/JavaScript interface
- Seeded SQLite marketplace with 10 realistic demo listings
- Browse search plus category, type, location, and price filtering
- Add-listing flow with reviewable AI suggestions
- Gemini natural-language search, with validated JSON output
- Safe application-side database filtering and transparent match scoring
- Detail and demo profile pages, plus loading, empty, and error states

## Architecture

`Browser → Flask routes/API → AI service (Gemini) → validation → SQLAlchemy/SQLite → matching service → JSON/UI`

Gemini never executes SQL or receives database credentials. The backend validates its limited structured response and performs all database access using SQLAlchemy.

## Tech stack

Python 3, Flask, SQLAlchemy, SQLite, python-dotenv, the official `google-genai` Python SDK, and vanilla HTML/CSS/JavaScript.

## Folder structure

```text
ai-community-marketplace/
├── app.py                 # Flask routes and API
├── extensions.py           # Shared Flask extension instances
├── models.py              # User and Listing models
├── seed.py                # Initial demo data
├── services/
│   ├── ai_service.py      # Gemini + validated local fallback
│   └── matching.py        # Explainable relevance ranking
├── templates/             # Server-rendered pages
├── static/css/style.css   # Responsive design system
├── static/js/app.js       # Client interactions
├── requirements.txt
├── .env.example
└── .gitignore
```

## Install and run

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open `http://127.0.0.1:5000`. On first launch, `community_market.db` is automatically created and seeded. Delete only that database file if you intentionally want to recreate the demo data.

## Environment variables

Set these in `.env` (which is ignored by Git):

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
FLASK_DEBUG=true
```

`GEMINI_MODEL` is configurable for future model changes. Without a Gemini key, the app still runs and uses a clearly limited rule-based local interpretation so the demo remains usable; add a key for Gemini-powered extraction/enhancement.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/listings` | List/search/filter listings |
| GET | `/api/listings/<id>` | Get one listing |
| POST | `/api/listings` | Create a listing |
| POST | `/api/ai/enhance` | Improve listing copy from `description` |
| POST | `/api/ai/search` | Parse `query` and return ranked matches |

Example AI search request:

```json
{"query":"I need a bicycle for college for 3 days under ₹500."}
```

## Matching algorithm

The relevance score is intentionally simple and visible:

- +40 category match
- +30 listing-type/intent match
- +20 one or more keyword matches
- +10 listing price fits the supplied budget

The resulting “AI Match” is a relevance score, never a probability or guarantee.

## Test instructions

```bash
python -m py_compile app.py models.py seed.py services/ai_service.py services/matching.py
python app.py
```

In another terminal, test `GET /api/listings`, `GET /api/listings/1`, and post the JSON above to `/api/ai/search`. Also test an empty AI query, an unknown listing ID, and a new listing in the browser.

## Demo queries

- `I need a bicycle for college for 3 days under ₹500.`
- `Looking for engineering books under ₹300.`
- `I want to borrow a camera near Indiranagar.`
- `Need a power drill for a quick repair.`

## Known limitations and next steps

This MVP has mock identity/contact actions, remote image URLs, basic keyword/location matching, no image upload, and no authentication, messaging, availability calendar, payments, or geospatial distance search. Natural-language fallback is intentionally narrower than Gemini. Future work could add authenticated profiles, moderation, availability and booking flows, notifications, image storage, maps, semantic embeddings, saved searches, and automated tests/CI.

## Screenshots
<img width="1856" height="765" alt="image" src="https://github.com/user-attachments/assets/7d7f3b07-cae7-4a5b-9032-1a0ccf293f23" />

<img width="1856" height="765" alt="image" src="https://github.com/user-attachments/assets/0ee055fa-a266-4f1e-8e05-71de75aa4c24" />

<img width="1908" height="906" alt="image" src="https://github.com/user-attachments/assets/f23e87ec-3dec-4fc1-9b82-9ddebeb776c1" />

_Add screenshots of the homepage, AI search results, and add-listing flow here._
