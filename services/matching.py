def rank_listings(listings, parsed):
    results = []
    for listing in listings:
        score, reasons = 0, []
        text = f"{listing.title} {listing.description}".lower()
        if parsed.get("category") == listing.category:
            score += 40; reasons.append("requested category")
        if parsed.get("listing_type") and parsed["listing_type"] == listing.listing_type:
            score += 30; reasons.append("requested preference")
        keyword_hits = [word for word in parsed.get("keywords", []) if word in text]
        if keyword_hits:
            score += 20; reasons.append("matching keywords")
        budget = parsed.get("budget_max")
        if budget is not None and listing.price <= budget:
            score += 10; reasons.append("budget")
        if score:
            data = listing.to_dict(); data["match_score"] = min(100, score); data["match_reason"] = "Matches your " + " and ".join(reasons) + "."
            results.append(data)
    return sorted(results, key=lambda result: result["match_score"], reverse=True)
