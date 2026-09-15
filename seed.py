def seed_database(db, User, Listing):
    if Listing.query.first(): return
    users = [User(name="Aarav Sharma", rating=4.9, contributions=18), User(name="Maya Iyer", rating=4.8, contributions=12), User(name="Kabir Singh", rating=4.7, contributions=9)]
    db.session.add_all(users); db.session.flush()
    rows = [
      ("Mountain Bicycle", "A well-maintained 21-speed bike, ideal for campus commutes.", "transportation", "lend", 150, "Koramangala", "Excellent", "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=80", 0),
      ("Engineering Books Bundle", "Core mechanical engineering textbooks with neat notes.", "books", "sell", 280, "Indiranagar", "Good", "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80", 1),
      ("Adjustable Laptop Stand", "Aluminium stand for a more comfortable desk setup.", "electronics", "sell", 450, "HSR Layout", "Like new", "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80", 2),
      ("Scientific Calculator", "Casio calculator, allowed for standard engineering exams.", "electronics", "lend", 50, "Koramangala", "Good", "https://images.unsplash.com/photo-1509223197845-458d87318791?auto=format&fit=crop&w=900&q=80", 0),
      ("Mirrorless Camera", "Sony mirrorless camera with kit lens for weekend projects.", "electronics", "lend", 600, "Indiranagar", "Excellent", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80", 1),
      ("Compact Study Table", "Foldable study table that fits a small room.", "furniture", "sell", 850, "HSR Layout", "Good", "https://images.unsplash.com/photo-1494438639946-1ebd1d20bf85?auto=format&fit=crop&w=900&q=80", 2),
      ("Graphic Design Service", "Posters, social posts and simple brand kits by a local designer.", "services", "service", 500, "Remote / Bengaluru", "Professional", "https://images.unsplash.com/photo-1561070791-2526d30994b5?auto=format&fit=crop&w=900&q=80", 1),
      ("Moving Help", "Two-person help for packing and moving within the neighbourhood.", "services", "service", 700, "Koramangala", "Professional", "https://images.unsplash.com/photo-1600518464441-9154a4dea21b?auto=format&fit=crop&w=900&q=80", 0),
      ("Cordless Power Drill", "Reliable drill with bits for a quick home repair.", "tools", "lend", 120, "Indiranagar", "Good", "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&w=900&q=80", 2),
      ("Badminton Set", "Two rackets, shuttlecocks and a carry cover.", "sports", "exchange", 300, "HSR Layout", "Good", "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=900&q=80", 0),
    ]
    db.session.add_all([Listing(title=a, description=b, category=c, listing_type=d, price=e, location=f, condition=g, image_url=h, owner=users[i]) for a,b,c,d,e,f,g,h,i in rows])
    db.session.commit()
