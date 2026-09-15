import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from services.ai_service import AIServiceError, enhance_listing, parse_search_query
from services.matching import rank_listings
from extensions import db

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
CATEGORIES = ["books", "electronics", "furniture", "transportation", "tools", "sports", "services", "home"]
LISTING_TYPES = ["sell", "buy", "borrow", "lend", "exchange", "service"]


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{BASE_DIR / 'community_market.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", ""),
        GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    from models import Listing, User

    @app.get("/")
    def home():
        return render_template("index.html", categories=CATEGORIES)

    @app.get("/add-listing")
    def add_listing_page():
        return render_template("add_listing.html", categories=CATEGORIES, listing_types=LISTING_TYPES)

    @app.get("/listing/<int:listing_id>")
    def listing_detail_page(listing_id):
        return render_template("detail.html", listing_id=listing_id)

    @app.get("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.get("/api/listings")
    def get_listings():
        query = Listing.query
        category = request.args.get("category", "").lower()
        listing_type = request.args.get("type", "").lower()
        location = request.args.get("location", "").strip()
        search = request.args.get("search", "").strip()
        max_price = request.args.get("max_price", type=float)
        if category in CATEGORIES: query = query.filter_by(category=category)
        if listing_type in LISTING_TYPES: query = query.filter_by(listing_type=listing_type)
        if location: query = query.filter(Listing.location.ilike(f"%{location}%"))
        if max_price is not None and max_price >= 0: query = query.filter(Listing.price <= max_price)
        if search:
            pattern = f"%{search}%"
            query = query.filter(or_(Listing.title.ilike(pattern), Listing.description.ilike(pattern)))
        return jsonify({"listings": [listing.to_dict() for listing in query.order_by(Listing.created_at.desc()).all()]})

    @app.get("/api/listings/<int:listing_id>")
    def get_listing(listing_id):
        listing = db.session.get(Listing, listing_id)
        if not listing: return jsonify({"error": "Listing not found."}), 404
        return jsonify({"listing": listing.to_dict()})

    @app.post("/api/listings")
    def create_listing():
        data = request.get_json(silent=True) or {}
        required = ["title", "description", "listing_type", "category", "price", "location", "condition"]
        missing = [field for field in required if data.get(field) in (None, "")]
        if missing: return jsonify({"error": f"Please provide: {', '.join(missing)}."}), 400
        if data["listing_type"] not in LISTING_TYPES or data["category"] not in CATEGORIES:
            return jsonify({"error": "Please choose a valid category and listing type."}), 400
        try:
            price = float(data["price"])
            if price < 0: raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a non-negative number."}), 400
        try:
            user = User.query.first()
            listing = Listing(title=data["title"].strip()[:120], description=data["description"].strip()[:2000],
                listing_type=data["listing_type"], category=data["category"], price=price,
                location=data["location"].strip()[:100], condition=data["condition"].strip()[:80],
                image_url=data.get("image_url", "").strip()[:500], owner=user)
            db.session.add(listing); db.session.commit()
            return jsonify({"listing": listing.to_dict(), "message": "Listing created."}), 201
        except SQLAlchemyError:
            db.session.rollback(); return jsonify({"error": "We couldn't save that listing. Please try again."}), 500

    @app.post("/api/ai/enhance")
    def ai_enhance():
        description = (request.get_json(silent=True) or {}).get("description", "").strip()
        if len(description) < 12: return jsonify({"error": "Add a little more detail before enhancing (at least 12 characters)."}), 400
        try: return jsonify({"enhancement": enhance_listing(description, app.config)})
        except AIServiceError as error: return jsonify({"error": str(error)}), 502

    @app.post("/api/ai/search")
    def ai_search():
        user_query = (request.get_json(silent=True) or {}).get("query", "").strip()
        if not user_query: return jsonify({"error": "Tell us what you are looking for."}), 400
        try: parsed = parse_search_query(user_query, app.config)
        except AIServiceError as error: return jsonify({"error": str(error)}), 502
        candidates = Listing.query.all()  # AI only returns data; matching remains safe application logic.
        matches = rank_listings(candidates, parsed)
        return jsonify({"interpretation": parsed, "matches": matches, "note": "AI Match is a transparent relevance score, not a probability."})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Resource not found."}) if request.path.startswith("/api/") else (render_template("404.html"), 404)

    with app.app_context():
        db.create_all()
        from seed import seed_database
        seed_database(db, User, Listing)
    return app


app = create_app()
if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
