from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from db.DatabaseConnection import DatabaseConnection
from db.config import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.team import Team

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')
app.secret_key = os.urandom(24)

user = User('test', 'er', 'ere@ere.com')
user.user_type = 'Instructor'

with app.app_context():
    db = DatabaseConnection()

    with db.get_connection().cursor() as cursor:
        cursor.execute("SELECT * FROM tms.team_parameters")
        team_parameters = cursor.fetchone()
        g.are_team_parameters_set = team_parameters[3]

    db.get_connection().close()

    print(g.are_team_parameters_set)


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

                    
                    session['user'] = request.form['email']
                    session['userType'] = userType
                    
                    if (userType == "student"): # Student
                        session['firstName'] = dbEmailResultStudent[1]
                        session['lastName'] = dbEmailResultStudent[2]
                        session['studentNumber'] = dbEmailResultStudent[3]
                        session['isLiaison'] = dbEmailResultStudent[6]
                        session["teamName"] = dbEmailResultStudent[7]
                    else: # Instructor
                        session['firstName'] = dbEmailResultInstructor[1]
                        session['lastName'] = dbEmailResultInstructor[2]

                    flash("Login Successful")
                    return redirect(url_for('dashboard'))

                else:
                    flash("Invalid Password")
                    return redirect(url_for("sign_in"))

        except:
            con.rollback()
            #return f"{err.__class__.__name__}: {err}"
            flash("Error in registering user")
        
        finally:
            con.close()
        
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
                        cursor.execute("INSERT INTO tms.student (first_name, last_name, student_number, email, password, is_liason, team_name) VALUES (%s, %s, %s, %s, %s, %s, NULL)",(firstname, lastname, studentNumber, email, hashedPass, False))
                
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
                
        except:
            con.rollback()
            #return f"{err.__class__.__name__}: {err}"
            flash("Error in registering user")
        
        finally:
            con.close()

    if g.user: # if logged in, redirect to dashboard
        return redirect(url_for("dashboard"))

    return render_template("register.html") # otherwise, display register form


@app.route('/dashboard')
def dashboard():

    if g.user: 

        return render_template("dashboardi.html")

    return redirect(url_for('sign_in'))

@app.route('/team/join', methods=['GET', 'POST'])
def join_team():

    if request.method == 'POST':

        try:

            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()

                cursor.execute("SELECT * FROM tms.team") # Check if teams exist
                teams_sql = cursor.fetchone()

                if (teams_sql != None):

                    teamToJoin = request.form['team_to_join']
                    cursor.execute("SELECT * FROM tms.team_request WHERE team_name=(%s) AND student_email=(%s)",(teamToJoin, g.user))
                    joinRequestResult = cursor.fetchone()

                    if (joinRequestResult == None):

                        studentFullName = g.user_first_name + " " + g.user_last_name
                        cursor.execute("INSERT INTO tms.team_request (team_name, student_email, request_status, student_name) VALUES (%s, %s, %s, %s)", (teamToJoin, g.user, "pending", studentFullName))
                        flash("Successfully sent request to join team: " + teamToJoin)

                    else:

                        flash("Already sent a request to join team: " + teamToJoin)
                else:
                    flash("No teams currently exist")


        except Exception as err:
            con.rollback()
            return f"{err.__class__.__name__}: {err}"
            #flash("Error in sending request to join team")

        finally:
            con.close()

    # GET Request

    # If it's a student that's not in a team
    if ((g.user_type == "student") and (g.student_team_name == None)):

        teams_sql = []
        team_names = []
        db = DatabaseConnection()

        with db.get_connection().cursor() as cursor:
            cursor.execute("SELECT * FROM tms.team")
            teams_sql = cursor.fetchall()

            for team_sql in teams_sql:
                team_names.append(team_sql[1])

            print("Teams: " + str(teams_sql))

        return render_template("join-team.html", teams=team_names)

    elif ((g.user_type == "student") and (g.student_team_name != None)):
        flash("You are already part of a team!")
        return redirect(url_for("dashboard")) # student is already in team, redirect

    else:
        return redirect(url_for("dashboard")) # user is not signed in or is instructor


@app.route('/team/create', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':
        try:
            teamName = request.form['team_name']

            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()

                cursor.execute("SELECT * FROM tms.team_parameters")
                team_parameters = cursor.fetchone()
                areTeamParametersSet = team_parameters[3]
                print("ARE PARAMETERS SET: " + str(areTeamParametersSet))
                
                if (areTeamParametersSet):

                    # Create the team in DB and initialize team_size as 1
                    cursor.execute("INSERT INTO tms.team(team_name, team_size) VALUES (%s, %s)", (teamName, 1))

                    # Update the values of student's is_liaison and team name
                    cursor.execute("UPDATE tms.student SET is_liason=(%s), team_name=(%s) WHERE email=(%s)", (True, teamName, g.user))

                    # Update request status to accepted
                    cursor.execute("UPDATE tms.team_request SET request_status=(%s) WHERE student_email=(%s)", ("accepted", g.user))

                    session['isLiaison'] = True # Set the session variables so that changes take effect this session
                    session["teamName"] = teamName

                    flash("Successfully created team")
                
                else:
                    flash("Instructor has not yet set the team parameters")

        except:
            con.rollback()
            # return f"{err.__class__.__name__}: {err}"
            flash("Error in creating team")

        finally:
            con.close()
            return redirect(url_for("dashboard"))

    # GET Request

    if ((g.user_type == "student") and (g.student_team_name == None)):
        return render_template("create-team.html") # Student with no team

    elif ((g.user_type == "student") and (g.student_team_name != None)):
        flash("You are already part of a team!")
        return redirect(url_for("dashboard")) # Student already in team, redirect

    else:
        return redirect(url_for("dashboard")) # user is instructor or not logged in

@app.route('/team/requests', methods=['GET', 'POST'])
def team_requests():

    if request.method == 'POST':

        try:
            studentRequestEmail = request.form['student_request_email'] # Get the email of the student trying to join the team
            studentRequestName = request.form['student_request_name'] # Get the email of the student trying to join the team

            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()

                cursor.execute("SELECT * FROM tms.team_parameters")
                team_parameters = cursor.fetchone()
                maxTeamSize = team_parameters[1] # Get Max team size

                cursor.execute("SELECT * FROM tms.team where team_name=(%s)", (g.student_team_name,))
                current_team = cursor.fetchone()
                currentTeamSize = current_team[4] # Get current size of the team

                if (currentTeamSize < maxTeamSize): # If team capacity has not been reached

                    incrementTeamSize = currentTeamSize + 1
                    # Update student's team name
                    cursor.execute("UPDATE tms.student SET team_name=(%s) WHERE email=(%s)", (g.student_team_name, studentRequestEmail))

                    # Increment team size
                    cursor.execute("UPDATE tms.team SET team_size=(%s) WHERE team_name=(%s)", (incrementTeamSize, g.student_team_name))

                    print("GOT HERE")
                    # Update request status to accepted
                    cursor.execute("UPDATE tms.team_request SET request_status=(%s) WHERE student_email=(%s)", ("accepted", studentRequestEmail))

                    flash("Added " + studentRequestName + " to the team!")

                else:
                    flash("Team Capacity of " + str(maxTeamSize) + " has already been reached!")

        except:
            con.rollback()
            #return f"{err.__class__.__name__}: {err}"
            flash("Error in accepting team member")

        finally:
            con.close()
            return redirect(url_for("team_requests"))

    # GET Request

    # If it's a student that is a liaison
    if ((g.user_type == "student") and (g.student_is_liaison == True)):

        student_requests_sql = []
        array_student_request_data = []

        db = DatabaseConnection()

        with db.get_connection().cursor() as cursor:
            
            cursor.execute("SELECT * FROM tms.team_request WHERE team_name=(%s) AND request_status=(%s)",(g.student_team_name, "pending"))
            student_requests_sql = cursor.fetchall()

            for student_request in student_requests_sql:
                student_request_data = []
                student_request_data.append(student_request[2]) # Append email of student
                student_request_data.append(student_request[4]) # Append full name of student
                array_student_request_data.append(student_request_data) # Append that list to the larger list

            print("Student Requests: " + str(student_requests_sql))
            print("-----------------")
            print("Student Request Emails: " + str(array_student_request_data))

        return render_template("accept-students.html", studentRequests=array_student_request_data)

    else:
        return redirect(url_for("dashboard")) # user is not signed in or is instructor



@app.route('/team/visualize')
def team_visualize():

    if g.user_type == "instructor":
        teams = []
        teams_sql = []

        db = DatabaseConnection()

        with db.get_connection().cursor() as cursor:
            cursor.execute("SELECT * FROM tms.team")
            teams_sql = cursor.fetchall()
        db.get_connection().close()

        for team_sql in teams_sql:
            team = Team(team_sql[1])
            team.team_number = team_sql[0]
            team.set_max_team_size(team_sql[2])
            team.set_min_team_size(team_sql[3])
            team.num_team_members = team_sql[4]
            teams.append(team)

        return render_template("visualize-teams.html", teams=teams)

    return redirect(url_for("dashboard"))


@app.route('/team/parameters', methods=['POST', 'GET'])
def team_parameters():
    if request.method == 'POST':
        if request.form['min_size'] == '' or request.form['min_size'] == '':
            error = 'Invalid parameters - empty parameters'
            return render_template("set-team-parameters.html", error=error)
        else:
            Team.default_min_size = int(request.form['min_size'])
            Team.default_max_size = int(request.form['max_size'])

            if Team.default_min_size > Team.default_max_size:
                error = 'Invalid parameters - minimum team size can\'t be larger than maximum team size'
                return render_template("set-team-parameters.html", error=error)

        db = DatabaseConnection()

        with db.get_connection().cursor() as cursor:
            cursor.execute("UPDATE tms.team_parameters SET max_team_size =(%s), min_team_size=(%s), are_parameters_Set=(%s)",
                           (Team.default_max_size, Team.default_min_size, True))

        db.get_connection().close()

        flash('Parameters successfully set')
        g.are_team_parameters_set = True
        return redirect(url_for("dashboard"))

    # GET Request 
    else:
        if g.user_type == 'instructor':
            return render_template("set-team-parameters.html")
        else:
            return redirect(url_for("dashboard"))


if __name__ == '__main__':
    
    app.run(debug=True)