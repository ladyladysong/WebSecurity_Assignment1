from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import jsonify
from flask import session
import json
import sqlite3
import hashlib
import bleach

app = Flask(__name__, static_folder='static', static_url_path='')

# Set the secret key for use by the session
app.secret_key = "7\x15\xc9\x0e\xd5\xed\xfba\xef4\xdd\xc9\x86\x00\xe2\r3cQKX%Z'"

# database connection variable
conn = None

# Home page function that responds to both GET and POST
@app.route('/', methods=['POST', 'GET'])
def searchmsg():
    # Connect to the database
    cursor=connect_to_db(True)

    # Get the query from the request - args for GET, form for POST
    search_term = None
    if request.method == 'POST':
        #VULN Client reflected XSS, sanitize input by using bleach 
        search_term = bleach.clean(request.form['query'])
    elif 'query' in request.args:
        #VULN Client reflected XSS, sanitize input by using bleach
        search_term = bleach.clean(request.args['query'])

    # If a search_term has been submitted run the query
    msgs = []
    if search_term is not None:
        #VULN unsafe input of SQL query
        sql = "SELECT *FROM messages WHERE category = ?"
        cursor.execute(sql,[search_term])
        msgs = cursor.fetchall()

    # Close the connection to the database
    close_db()

    # If we receivd a POST request return the results as JSON
    if request.method == 'POST':
        return jsonify(msgs)
    # Otherwise it is a GET page load and render the results on the server and return the complete page
    else:
        return render_template('home.html', messages=msgs, query=search_term)


# checks if a user id is currently in use
@app.route('/username', methods=['POST'])
def username():
    # get the request contents as JSON object
    req = request.get_json(force=True)

    cursor = connect_to_db()
    #VULN SQL injection for executing untrusted code directly input by client
    sql = "SELECT id FROM users WHERE id = ?"
    cursor.execute(sql, [req['username']])
    user = cursor.fetchone()

    close_db()

    # Check if user exists and return True or False
    if user is None:
        return jsonify(exists=False)
    else:
        return jsonify(exists=True)

# Log in to the page and show a post message screen
@app.route('/login', methods=['POST', 'GET'])
def login():
    # If this is a GET request it is a page load request and just return the template
    if request.method == 'GET':
        return render_template('login.html',user=session.get('user'))

    # connect to the database and set it to use the default JSON encoder to convert all results into a JSON array
    cursor = connect_to_db(True)
    #VULN SQL injection, untrusted code to execute directly(union query)
    sql = "SELECT  * FROM users WHERE id = ?"
    cursor.execute(sql,[request.form['id']])
    users = cursor.fetchall()

    close_db()

    # if no user found with given id
    if len(users) == 0:
        return render_template('login.html')

    # Check password is correct
    if users[0]['password'] == hashlib.md5(request.form['pwd'].encode()).hexdigest():
        # Add user to session
        session['user'] = users[0]
        # Password matches, treat the user as logged in
        return render_template('login.html', user=session.get('user'))
    else:
        # Password does not match, return to login page
        return render_template('login.html')

# Log out
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    # having cleared the session redirect to login page
    return redirect("./login")

# Simple registration function
@app.route('/register', methods=['POST', 'GET'])
def register():
    # If this is a GET request it is a page load request and just return the template
    if request.method == 'GET':
        return render_template('register.html')

    cursor = connect_to_db()
    #VULN Server Stored XSS, malicious code may be stored and run when be retrieved
    cursor.execute("INSERT into users (id, password, age) values (?, ?, ?)",
                   (bleach.clean(request.form['id']), hashlib.md5(request.form['pwd'].encode()).hexdigest(), -1))
    global conn
    conn.commit()
    close_db()

    # having inserted the user redirect to login page
    return redirect("./login")

# Post a message as the currently logged in user
@app.route('/postmessage', methods=['POST'])
def postmessage():
    cursor = connect_to_db()
    # VULN Server Stored XSS, retrieve data from database may not safe because of the malicious code
    cursor.execute("INSERT into messages (id, message, category) values (?, ?, ?)",
                   (session['user']['id'], bleach.clean(request.form['message']), bleach.clean(request.form['category'])))
    global conn
    conn.commit()
    close_db()
    return render_template("login.html", user=session.get('user'))


#===============================================================================
#                     Utility functions
#
# Code below here can be considered to be safe and is not part of the assignment.
#
#===============================================================================

# Utility function to convert database response into JSON compatiable array
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Utility function to connect to the database
def connect_to_db(jsonout=False):
    global conn
    conn = sqlite3.connect('assignment1.db')
    if jsonout:
        conn.row_factory = dict_factory
    cursor = conn.cursor()
    return cursor

# Utility function to close database connection
def close_db():
    global conn
    if conn is not None:
        conn.close()

# Utility function to reset database for testing purposes - also useful to see structure of DB
@app.route('/resetdatabase', methods=['GET'])
def resetdb():
    cursor=connect_to_db()

    # Remove any existing tables
    cursor.execute('''DROP TABLE IF EXISTS users''')
    cursor.execute('''DROP TABLE IF EXISTS messages''')

    # Create a new users table
    cursor.execute(
        '''CREATE TABLE users (id text PRIMARY KEY, password text, age integer)''')
    # Populate users table with example data
    cursor.execute("INSERT INTO users VALUES ('admin', '" + hashlib.md5('password'.encode()).hexdigest() + "', 26)")
    cursor.execute("INSERT INTO users VALUES ('JoeBloggs', '" + hashlib.md5('123456'.encode()).hexdigest() + "', 24)")
    cursor.execute("INSERT INTO users VALUES ('JohnDoe', '"+hashlib.md5('654321'.encode()).hexdigest() + "', 32)")

    # Create a new messages table
    cursor.execute(
        '''CREATE TABLE messages (id text, message text, category text)''')

    # Populate messages table with example data
    cursor.execute(
        "INSERT INTO messages VALUES ('JoeBloggs', 'Message 1 for joe', 'news')")
    cursor.execute(
        "INSERT INTO messages VALUES ('JoeBloggs', 'Message 2 for joe', 'weather')")
    cursor.execute(
        "INSERT INTO messages VALUES ('JohnDoe', 'Message for john', 'news')")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
    return jsonify(reset=True)
