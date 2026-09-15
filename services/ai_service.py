import json
import os
import re


class AIServiceError(Exception): pass

VALID_TYPES = {"sell", "buy", "borrow", "lend", "exchange", "service"}
VALID_CATEGORIES = {"books", "electronics", "furniture", "transportation", "tools", "sports", "services", "home"}

def _validate(data, enhancement=False):
    if not isinstance(data, dict): raise AIServiceError("AI returned an unexpected response. Please try again.")
    if enhancement:
        required = {"title", "description", "category", "listing_type", "keywords"}
        if not required.issubset(data) or not isinstance(data["keywords"], list): raise AIServiceError("AI returned incomplete listing suggestions. Please try again.")
        data["improved_title"] = str(data.pop("title"))[:120]
        data["improved_description"] = str(data.pop("description"))[:2000]
    else:
        required = {"intent", "category", "keywords", "budget_max", "duration", "location"}
        if not required.issubset(data) or not isinstance(data["keywords"], list): raise AIServiceError("AI returned an incomplete search interpretation. Please try again.")
        data["listing_type"] = data.pop("intent")
    if data["listing_type"] not in VALID_TYPES: data["listing_type"] = None
    if data["category"] not in VALID_CATEGORIES: data["category"] = None
    data["keywords"] = [str(word).lower()[:50] for word in data["keywords"][:8] if str(word).strip()]
    if data.get("budget_max") is not None:
        try: data["budget_max"] = float(data["budget_max"])
        except (ValueError, TypeError): data["budget_max"] = None
    return data

def _fallback_search(query):
    q = query.lower()
    intent = next((x for x in VALID_TYPES if x in q), None)
    if not intent: intent = "borrow" if any(x in q for x in ["need", "rent", "for 2 days", "for 3 days"]) else None
    category_map = {"bicycle": "transportation", "bike": "transportation", "book": "books", "laptop": "electronics", "camera": "electronics", "calculator": "electronics", "drill": "tools", "table": "furniture", "moving": "services", "design": "services", "sport": "sports"}
    category = next((v for k, v in category_map.items() if k in q), None)
    amount = re.search(r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)|under\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)", q)
    budget = float(next(v for v in amount.groups() if v)) if amount else None
    duration = re.search(r"\b\d+\s*(?:day|days|week|weeks|hour|hours)\b", q)
    keywords = [word for word in re.findall(r"[a-z]{3,}", q) if word not in {"need", "looking", "under", "near", "college", "want", "borrow", "lend", "sell", "buy", "days", "for"}]
    return _validate({"intent": intent, "category": category, "keywords": keywords, "budget_max": budget, "duration": duration.group(0) if duration else None, "location": None})

def _gemini_json(prompt, config):
    api_key = config.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key: return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=config.get("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt,
            config={"response_mime_type": "application/json", "temperature": 0.2})
        return json.loads(response.text)
    except Exception as exc:
        raise AIServiceError("AI is temporarily unavailable. Please try again in a moment.") from exc

def parse_search_query(query, config):
    prompt = f'''Return only JSON for this marketplace request: {query!r}. Schema: {{"intent":"sell|buy|borrow|lend|exchange|service|null","category":"books|electronics|furniture|transportation|tools|sports|services|home|null","keywords":["..."],"budget_max":number|null,"duration":string|null,"location":string|null}}. Do not invent details.'''
    data = _gemini_json(prompt, config)
    return _validate(data) if data is not None else _fallback_search(query)

def enhance_listing(description, config):
    prompt = f'''Return only JSON that improves this community marketplace listing: {description!r}. Schema: {{"title":"...","description":"...","category":"books|electronics|furniture|transportation|tools|sports|services|home","listing_type":"sell|buy|borrow|lend|exchange|service","keywords":["..."]}}. Keep it factual and concise.'''
    data = _gemini_json(prompt, config)
    if data is None:
        parsed = _fallback_search(description)
        data = {"title": description.split(".")[0][:70].title(), "description": description.strip(), "category": parsed["category"] or "home", "listing_type": parsed["listing_type"] or "sell", "keywords": parsed["keywords"]}
    return _validate(data, enhancement=True)
