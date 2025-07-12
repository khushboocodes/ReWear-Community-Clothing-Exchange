from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this with a strong secret key in production

DB_NAME = 'users.db'

# Function to initialize the database
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Create users table
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                address TEXT NOT NULL
            )
        ''')
        
        # ✅ Create items table
        c.execute('''
            CREATE TABLE items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                image_url TEXT
            )
        ''')

        conn.commit()
        conn.close()


# Route: Index Page
@app.route('/index')
def index():
    return render_template('index.html')

# Route: Home (Redirect to index if logged in, else to Sign In)
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('signin'))



# Route: Sign In
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]  # Store first_name in session
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('signin'))
    
    return render_template('signin.html')

# Route: Sign Up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            data = (
                request.form['first_name'],
                request.form['last_name'],
                request.form['email'],
                request.form['phone'],
                request.form['password'],
                request.form['address']
            )

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (first_name, last_name, email, phone, password, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()
            conn.close()

            flash('Registration successful! Please sign in.')
            return redirect(url_for('signin'))

        except sqlite3.IntegrityError:
            flash('An account with that email already exists.')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('signin'))

    user = session['user']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT item_name, category, description, image_url FROM items WHERE user=?", (user,))
    items = c.fetchall()
    conn.close()

    return render_template('dashboard.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'user' not in session:
        return redirect(url_for('signin'))

    item_name = request.form['item_name']
    category = request.form['category']
    description = request.form['description']
    image_url = request.form['image_url']
    user = session['user']

    # Save item in the database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO items (user, item_name, category, description, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (user, item_name, category, description, image_url))
    conn.commit()
    conn.close()

    flash("Item added successfully!", "success")
    return redirect(url_for('dashboard'))

    
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.")
    return redirect(url_for('signin'))

@app.route("/shop")
def shop():
    return render_template("shop.html")

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search')
def search():
    return render_template('search.html')




# Main
if __name__ == '__main__':
    init_db()  # Ensure database is created before running
    app.run(debug=True, port=5050)

