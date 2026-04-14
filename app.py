from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        quantity INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()
# BILLING SYSTEM
# BILLING SYSTEM (MULTI ITEM)
cart = []

@app.route('/billing', methods=['GET', 'POST'])
def billing():
    global cart

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if request.method == 'POST':
        product_id = request.form['product']
        quantity = int(request.form['quantity'])

        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()

        if product:
            name = product[1]
            price = product[2]
            stock = product[3]

            if quantity <= stock:
                total = price * quantity

                # ADD TO CART
                cart.append((name, quantity, price, total))

                # UPDATE STOCK
                new_stock = stock - quantity
                cursor.execute("UPDATE products SET quantity=? WHERE id=?",
                               (new_stock, product_id))
                conn.commit()

    conn.close()

    # CALCULATE GRAND TOTAL
    grand_total = sum(item[3] for item in cart)

    return render_template("billing.html",
                           products=products,
                           cart=cart,
                           grand_total=grand_total)


# CLEAR BILL
@app.route('/clear')
def clear():
    global cart
    cart = []
    return redirect('/billing')
# Dashboard
@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 5")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(price * quantity) FROM products")
    total_value = cursor.fetchone()[0] or 0

    conn.close()

    return render_template("index.html",
                           total=total,
                           low_stock=low_stock,
                           total_value=total_value)

# Add product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                       (name, price, quantity))
        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template("add_product.html")

# View + Search
@app.route('/view', methods=['GET', 'POST'])
def view_products():
    conn = get_db()
    cursor = conn.cursor()

    search = request.form.get('search')

    if search:
        cursor.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM products")

    data = cursor.fetchall()
    conn.close()

    return render_template("view_products.html", products=data)

# DELETE
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/view')

# EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        quantity = request.form['quantity']

        cursor.execute("UPDATE products SET name=?, price=?, quantity=? WHERE id=?",
                       (name, price, quantity, id))
        conn.commit()
        conn.close()
        return redirect('/view')

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()
    conn.close()

    return render_template("edit_product.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)