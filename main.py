from flask import Flask, render_template, request, url_for, redirect
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

conn_str = "mysql://root:cset155@localhost/banking_website"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/', methods = ['GET'])
def register():
    return render_template("index.html")

@app.route('/', methods = ['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    ssn = request.form['ssn']
    address = request.form['address']
    phone_number = request.form['phone_number']
    role = request.form['role']

    sql = text("""
        INSERT INTO customer_info
        (Username, PasswordHash, FirstName, LastName, SSN, Address, Phone, role)
        VALUES
        (:Username, :PasswordHash, :FirstName, :LastName, :SSN, :Address, :Phone, :role)
    """)

    conn.execute(sql, {
        'Username': username,
        'PasswordHash': generate_password_hash(password),
        'FirstName': first_name,
        'LastName': last_name,
        'SSN': ssn,
        'Address': address,
        'Phone': phone_number,
        'role': role
    })
    conn.commit()

    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['login_username']
    password = request.form['login_password']

    sql = text("SELECT Username, PasswordHash, role FROM customer_info WHERE Username = :Username ")
    result = conn.execute(sql, {'Username': username}).fetchone()

    if result:
        stored_password = result['PasswordHash']
        role = result['role']

        if check_password_hash(stored_password, password):
            if role.lower() == 'admin':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('home'))
        else: 
            return "Incorrect password", 401
    else:
        return "Username not fround", 404
    
@app.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST': 
        approved_users = request.form.getlist('approve')

        if approved_users:
            sql = text("UPDATE customer_info SET approved = TRUE WHERE Username IN :usernames")
            conn.execute(sql, {'usernames': tuple(approved_users)})

        return redirect(url_for('admin_page'))
    
    sql = text("""
        SELECT Username, FirstName, LastName, Address, Phone, approved
        FROM customer_info
        ORDER BY approved IS NOT TRUE, Username
    """)
    users = conn.execute(sql).fetchall()

    return render_template('admin_page.html', users=users)

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/account')
def my_account():
    return render_template("my_account.html")

@app.route('/add_send')
def add_send():
    return render_template("add_send.html")

if __name__ == '__main__':
    app.run(debug=True)