from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from db.DatabaseConnection import DatabaseConnection
from db.config import config
import os

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        session.pop('user', None) # clear session
        if request.form['password'] == 'password': # compare hash pass here instead

            ### NEED TO CHECK IF STUDENT OR INSTRUCTOR, and assign that to session variable  *******

            session['user'] = request.form['email']

            return redirect(url_for('dashboard'))
        
    if g.user: # if already signed in, then redirect user to dashboard
        return redirect(url_for('dashboard'))

    return render_template("sign-in.html")

@app.route('/sign-out')
def sign_out():
    if g.user:
        session.pop('user', None)

        flash('You have been successfully logged out')
    
    return redirect(url_for("sign_in"))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']
    
    return "Not logged in"

@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    
    return "Dropped"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.pop('user', None) # clear session
        
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            password = request.form['password']
         
            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()
                cursor.execute("INSERT INTO tms.student (first_name,last_name,email,password, team_name) VALUES (%s, %s, %s, %s, NULL)",(firstname,lastname,email,password))

                flash("Successfully registered user")
  
        except Exception as err:
            con.rollback()
            return f"{err.__class__.__name__}: {err}"
            # flash("Error in registering user")
        
        finally:
            con.close()
            #return render_template("register.html")


    if g.user: # if logged in, redirect to dashboard
        return redirect(url_for("dashboard"))

    return render_template("register.html") # otherwise, display register form


@app.route('/dashboard')
def dashboard():
    if g.user: ###### NEED TO CHECK USER TYPE --> REDIRECT TO STUDENT ONE FOR STUDENT, INSTR FOR INSTR ****** 

        # SO FAR JUST INSTRUCTOR REDIRECT
        return render_template("dashboardi.html")

    return redirect(url_for('sign_in'))

@app.route('/create-team')
def create_team():
    if g.user:
        return render_template("create-team.html")
    
    return redirect(url_for('sign_in'))

if __name__ == '__main__':
    app.run(debug=True)
