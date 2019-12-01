from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from db.DatabaseConnection import DatabaseConnection
from db.config import config
import os
from werkzeug.security import generate_password_hash, check_password_hash

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

        email = request.form['email']
        password = request.form['password']

        try:
            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()
                cursor.execute("SELECT * FROM tms.student WHERE tms.student.email = (%s)",(email,))
                dbEmailResultStudent = cursor.fetchone()

                if (dbEmailResultStudent != None): # Student with email found
                    
                    dbHashedPass = dbEmailResultStudent[5]

                    userType = "student"

                else: # Check if instructor

                    cursor = con.cursor()
                    cursor.execute("SELECT * FROM tms.instructor WHERE tms.instructor.email = (%s)",(email,))
                    dbEmailResultInstructor = cursor.fetchone()

                    if (dbEmailResultInstructor != None): # instructor with email found
    
                        dbHashedPass = dbEmailResultInstructor[4]

                        userType = "instructor"

                    else:
                        flash("No user with such email exists.")
                        return redirect(url_for("sign_in"))

                if (check_password_hash(dbHashedPass, password)): # compare hash pass here instead

                    ### NEED TO CHECK IF STUDENT OR INSTRUCTOR, and assign that to session variable  *******
                    session['user'] = request.form['email']
                    session['userType'] = userType
                    
                    if (userType == "student"):
                        session['firstName'] = dbEmailResultStudent[1]
                        session['lastName'] = dbEmailResultStudent[2]
                        session['studentNumber'] = dbEmailResultStudent[3]
                        session['isLiaison'] = dbEmailResultStudent[6]
                        session["teamName"] = dbEmailResultStudent[7]
                    else:
                        session['firstName'] = dbEmailResultInstructor[1]
                        session['lastName'] = dbEmailResultInstructor[2]

                    flash("Login Successful")
                    return redirect(url_for('dashboard'))

                else:
                    flash("Invalid Password")
                    return redirect(url_for("sign_in"))

        except Exception as err:
            con.rollback()
            return f"{err.__class__.__name__}: {err}"
            # flash("Error in registering user")
        
        finally:
            con.close()
            #return render_template("register.html")
        
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
    g.user_type = None
    g.user_first_name = None
    g.user_last_name = None
    g.student_number = None
    g.student_is_liaison = None
    g.student_team_name = None

    if 'user' in session:
        g.user = session['user']
        g.user_type = session['userType']
        g.user_first_name = session['firstName']
        g.user_last_name = session['lastName']

    if g.user_type == "student":
        g.student_number = session['studentNumber']
        g.student_is_liaison = session['isLiaison']
        g.student_team_name = session["teamName"]

    userVals = ("EMAIL: " + str(g.user), "USER TYPE: " + str(g.user_type), "FIRSTNAME: " + str(g.user_first_name), "LAST NAME: " + str(g.user_last_name), "STUDENT NUM: " + str(g.student_number), "IS_LIAISON: " + str(g.student_is_liaison), "TEAM NAME: " + str(g.student_team_name))
    print("VALUES: " + str(userVals))

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
        
        if (request.form['password'] != request.form['confirm_password']):
            flash("Passwords don't match.")
            return redirect(url_for("register"))

        if (request.form['email'] != request.form['confirm_email']):
            flash("Emails don't match.")
            return redirect(url_for("register"))

        try:
            firstname = request.form['first_name']
            lastname = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            userType = request.form['user_type']
         
            hashedPass = generate_password_hash(password)

            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()
                
                if (userType == "student"): #if it's a student

                    cursor.execute("SELECT * FROM tms.student WHERE tms.student.email = (%s)",(email,))
                    dbEmailResult = cursor.fetchone()

                    if (dbEmailResult == None):
                    
                        studentNumber = request.form['student_number']
                        
                        cursor = con.cursor()
                        cursor.execute("INSERT INTO tms.student (first_name, last_name, student_number, email, password, team_name) VALUES (%s, %s, %s, %s, %s, NULL)",(firstname, lastname, studentNumber, email, hashedPass))
                
                        flash("Successfully registered user")

                    else:
                        flash("User with that email already exists.")

                else: #it's an instructor

                    cursor.execute("SELECT * FROM tms.instructor WHERE tms.instructor.email = (%s)",(email,))
                    dbEmailResult = cursor.fetchone()

                    if (dbEmailResult == None):

                        cursor = con.cursor()
                        cursor.execute("INSERT INTO tms.instructor (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",(firstname, lastname, email, hashedPass))
                        
                        flash("Successfully registered user")
                    
                    else:
                        flash("User with that email already exists.")
                
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
