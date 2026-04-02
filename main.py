from flask import Flask, render_template, request, url_for, redirect, session
from sqlalchemy import create_engine, text, bindparam
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)

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

    sql = text("""
        SELECT Username, PasswordHash, role, approved 
        FROM customer_info 
        WHERE Username = :Username 
    """)
    result = conn.execute(sql, {'Username': username}).mappings().fetchone()

    if result:
        stored_password = result['PasswordHash']
        role = result['role']
        approved = result['approved']

        if check_password_hash(stored_password, password):
            session['username'] = result['Username']
            session['role'] = role
            session['approved'] = approved

            if role.lower() == 'admin':
                return redirect(url_for('admin_page'))

            if approved is None:
                return "Account pending approval", 403
            
            if approved is False:
                return "Account rejected", 403
            
            return redirect(url_for('home'))
        else: 
            return "Incorrect password", 401
    else:
        return "Username not found", 404   

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('register'))

@app.route('/admin_page', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST': 
        approved_users = request.form.getlist('approve')
        rejected_users = request.form.getlist('reject')

        approved_set = set(approved_users)
        rejected_set = set(rejected_users)

        if approved_set & rejected_set:
            return "Error: Cannot approve and reject the same user", 400

        if approved_users:
            sql = text("""
                UPDATE customer_info 
                SET approved = TRUE 
                WHERE Username IN :usernames
            """).bindparams(bindparam("usernames", expanding=True))
            conn.execute(sql, {'usernames': tuple(approved_users)})

        if rejected_users:
            sql = text("""
                UPDATE customer_info
                SET approved = FALSE
                WHERE Username IN :usernames
            """).bindparams(bindparam("usernames", expanding=True))
            conn.execute(sql, {'usernames': tuple(rejected_users)})

        return redirect(url_for('admin_page'))
    
    sql_pending = text("""
        SELECT Username, FirstName, LastName, Address, Phone, approved, SSN
        FROM customer_info
        WHERE LOWER(role) != 'admin'
            AND approved IS NULL
        ORDER BY Username
    """)

    pending_users = conn.execute(sql_pending).mappings().fetchall()

    sql_approved = text("""
        SELECT Username, FirstName, LastName, Address, Phone, approved, SSN
        FROM customer_info
        WHERE LOWER(role) != 'admin'
            AND approved = TRUE
        ORDER BY Username
    """)
    approved_users = conn.execute(sql_approved).mappings().fetchall()

    sql_rejected = text("""
        SELECT Username, FirstName, LastName, Address, Phone, approved, SSN
        FROM customer_info
        WHERE LOWER(role) != 'admin'
            AND approved = FALSE
        ORDER BY Username
    """)
    rejected_users = conn.execute(sql_rejected).mappings().fetchall()
    
    conn.commit()
    return render_template('admin_page.html', pending_users=pending_users, approved_users=approved_users, rejected_users=rejected_users)

@app.route('/home')
def home():
    if not session.get('username'):
        return redirect(url_for('register'))
    
    sql = text("SELECT approved FROM customer_info WHERE Username = :Username")
    result = conn.execute(sql, {'Username': session['username']}).mappings().fetchone()

    if not result or result['approved'] !=1:
        return "Accounts not approved", 403
    
    return render_template("home.html")

@app.route('/account')
def my_account():
    if not session.get('username'):
        return redirect(url_for('register'))
    
    sql = text("SELECT approved FROM customer_info WHERE Username = :Username")
    result = conn.execute(sql, {'Username': session['username']}).mappings().fetchone()

    if not result or result['approved'] !=1:
        return "Accounts not approved", 403
    
    return render_template("my_account.html")

@app.route('/add_send')
def add_send():
    if not session.get('username'):
        return redirect(url_for('register'))
    
    sql = text("SELECT approved FROM customer_info WHERE Username = :Username")
    result = conn.execute(sql, {'Username': session['username']}).mappings().fetchone()

    if not result or result['approved'] !=1:
        return "Accounts not approved", 403
    
    return render_template("add_send.html")

if __name__ == '__main__':
    app.run(debug=True)