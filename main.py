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
        (Username, PasswordHash, FirstName, LastName, SSN, Address, Phone,role)
        VALUES
        (:username, :password, :first_name, :last_name, :ssn, :address, :phone_number, :role)
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

    sql = text("SELECT Username, PasswordHash FROM customer_info WHERE Username = :Username ")
    result = conn.execute(sql, {'Username': username}).fetchone()

    if result:
        stored_password = result[1]

        if check_password_hash(stored_password, password):
            return redirect(url_for('home'))
        else: 
            return "Incorrect password"
    else:
        return "Username not fround"

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