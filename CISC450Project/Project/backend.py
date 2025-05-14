from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import os
#TEST
app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "restaurants.db"

# Connect to DB
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        need_init = not os.path.exists(DATABASE)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        if need_init:
            with open("restaurants.sql") as f:
                db.executescript(f.read())
    return db

def reset_database():
    db = get_db()
    with open("restaurants.sql") as f:
        db.executescript(f.read())
    db.commit()

@app.route("/reset_db", methods=["GET","POST"])
def reset_db():
    if "user_id" not in session:
        return redirect("/login")
    reset_database()
    return "Database reset."


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#  ROUTES

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()

        if user:
            # Check password
            if user["password"] == password:
                session["user_id"] = user["userID"]
                session["username"] = user["username"]
                return redirect("/home")
            else:
                return render_template("login.html", error="Incorrect password.")
        else:
            # Auto-register new user
            db.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (username, "", password))
            db.commit()
            new_user = db.execute("SELECT * FROM Users WHERE username = ?", (username,)).fetchone()
            session["user_id"] = new_user["userID"]
            session["username"] = new_user["username"]
            return redirect("/home")

    return render_template("login.html")


@app.route("/home")
def home():
    
   # Homepage for logged-in users. Redirects to login page if not logged in.
    
    if "user_id" not in session:
        return redirect("/login")
    return render_template("home.html", username=session["username"])

@app.route("/add_restaurant_form", methods=["GET", "POST"])
def add_restaurant_form():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        db = get_db()

         # Check if the restaurant already exists
        existing = db.execute(
            "SELECT * FROM Restaurants WHERE name = ? AND location = ?",
            (name, location)
        ).fetchone()

        if existing:
            # error message if restaurant already exists
            return render_template("add_restaurant.html", error="Restaurant already exists.")

        db.execute("INSERT INTO Restaurants (name, location) VALUES (?, ?)", (name, location))
        db.commit()
        return redirect("/home")
    return render_template("add_restaurant.html")

@app.route("/add_meal_form", methods=["GET", "POST"])
def add_meal_form():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    if request.method == "POST":
        restaurantID = request.form["restaurantID"]
        name = request.form["dish_name"]
        description = request.form["description"]
        db.execute("INSERT INTO Dishes (restaurantID, name, description) VALUES (?, ?, ?)", (restaurantID, name, description))
        db.commit()
        return redirect("/home")
    restaurants = db.execute("SELECT * FROM Restaurants").fetchall()
    return render_template("add_meal.html", restaurants=restaurants)

@app.route("/add_rating_form", methods=["GET", "POST"])
def add_rating_form():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    if request.method == "POST":
        userID = session["user_id"]
        restaurantID = request.form["restaurantID"]
        dishID = request.form["dishID"]
        rating = int(request.form["rating"])
        comment = request.form["comment"]
        db.execute("""
            INSERT INTO Ratings (userID, restaurantID, dishID, comment, rating)
            VALUES (?, ?, ?, ?, ?)""", (userID, restaurantID, dishID, comment, rating))
        db.commit()
        return redirect("/home")
    restaurants = db.execute("SELECT * FROM Restaurants").fetchall()
    dishes = db.execute("SELECT * FROM Dishes").fetchall()
    return render_template("add_rating.html", restaurants=restaurants, dishes=dishes)

@app.route("/visited_restaurants")
def visited_restaurants():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    rows = db.execute("""
        SELECT DISTINCT R.name, R.location
        FROM Restaurants R
        JOIN Ratings Ra ON R.restaurantID = Ra.restaurantID
        WHERE Ra.userID = ?
    """, (session["user_id"],)).fetchall()

    if rows == []:
        return render_template("visited.html", error="You have not rated any restaurants.")
    
    
    return render_template("visited.html", restaurants=rows)

@app.route("/favorite_restaurants")
def favorite_restaurants():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    rows = db.execute("""
        SELECT R.name, AVG(Ra.rating) as avg_rating
        FROM Restaurants R
        JOIN Ratings Ra ON R.restaurantID = Ra.restaurantID
        WHERE Ra.userID = ?
        GROUP BY R.restaurantID
        ORDER BY avg_rating DESC
        LIMIT 5
    """, (session["user_id"],)).fetchall()
    return render_template("favorites.html", favorites=rows)

@app.route("/suggestions", methods=["GET", "POST"])
def suggestions():
    if "user_id" not in session:
        return redirect("/login")
    db = get_db()
    restaurants = db.execute("SELECT * FROM Restaurants").fetchall()
    top_meal = None
    if request.method == "POST":
        restaurantID = request.form["restaurantID"]
        top_meal = db.execute("""
            SELECT D.name, AVG(R.rating) as avg_rating
            FROM Dishes D
            JOIN Ratings R ON D.dishID = R.dishID
            WHERE R.restaurantID = ?
            GROUP BY D.dishID
            ORDER BY avg_rating DESC
            LIMIT 1
        """, (restaurantID,)).fetchone()
    return render_template("suggestions.html", restaurants=restaurants, top_meal=top_meal)


@app.route("/logout")
def logout():
    print("logout route hit")
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)




