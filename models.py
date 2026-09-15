from datetime import datetime, timezone
from extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Float, default=4.8, nullable=False)
    contributions = db.Column(db.Integer, default=0, nullable=False)
    listings = db.relationship("Listing", back_populates="owner", lazy=True)


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False)
    listing_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(80), nullable=False)
    image_url = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", back_populates="listings")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "category": self.category,
          "listing_type": self.listing_type, "price": self.price, "location": self.location, "condition": self.condition,
          "image_url": self.image_url, "created_at": self.created_at.isoformat(), "owner_name": self.owner.name,
          "owner_rating": self.owner.rating}
