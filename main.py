from flask import Flask, render_template, redirect, url_for, request, session, json
from werkzeug.exceptions import HTTPException
import mysql.connector
import logging
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'the random string'

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Password1",
  database="rising_star_school"
)

mycursor = mydb.cursor()

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = mycursor.fetchone()
        print(account[0])
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # return 'Logged in successfully!'
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# http://localhost:5000/login/logout - this will be the logout page
@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = mycursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/')
def homepage():
    return render_template("schoolhome.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/url')
def my_method():
    try:
        call_method_that_raises_exception()
    except Exception as e:
	    render_template("500.html", error = str(e))

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e))
    return render_template('500.html'), 500

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        mycursor = mydb.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = mycursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            mycursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mydb.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# @app.route('/login/home')
# def home():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         return render_template('home.html', username=session['username'])
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))
@app.route('/login/record/',methods = ['POST', 'GET'])
def record():
    if 'loggedin' in session:
        # User is loggedin show them the record page
        return render_template('record.html', username=session['username'])
    elif request.method == 'POST':
        idStudent=request.form['idStudent']
        Student_Name=request.form['Student_Name']
        Student_Roll_No=request.form['Student_Roll_No']
        Student_Class=request.form['Student_Class']
        Date_of_Birth=request.form['Date_of_Birth']
        Mobile_No=request.form['Mobile_No']
        Address=request.form['Address']
        mycursor.execute("INSERT INTO student_record values (%s,%s,%s,%s,%s,%s,%s)",(idStudent, Student_Name, Student_Roll_No, Student_Class, Date_of_Birth,Mobile_No,Address))
        mydb.commit()
        return "successfully registered"

@app.route('/showrec/')
def showrec():
	mycursor.execute('SELECT * FROM student_record')
	data = mycursor.fetchall()

	list_of_dict = []
	
	for i in data:
		data_dict = {}
		data_dict['idStudent'] = i[0]
		data_dict['Student_Name'] = i[1]
		data_dict['Student_Roll_No'] = i[2]
		data_dict['Student_Class'] = i[3]
		data_dict['Date_of_Birth'] = i[4]
		data_dict['Mobile_No'] = i[5]
		data_dict['Address'] = i[6]
		list_of_dict.append(data_dict)
	return render_template('showrec.html', output_data = list_of_dict)

		


if __name__ == '__main__':
   app.run(debug = True)