from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from db.DatabaseConnection import DatabaseConnection
from db.config import config
import os
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
    return render_template("index.html")


@app.route('/sign-in')
def sign_in():
    return render_template("sign-in.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/create-team', methods=['GET', 'POST'])
def create_team():
    if request.method == 'POST':

        try:
            teamname = request.form['teamname']

            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()
                cursor.execute("INSERT INTO tms.team(team_name) VALUES (%s)", (teamname,))

                flash("Successfully created team")

        except:
            con.rollback()
            # return f"{err.__class__.__name__}: {err}"
            flash("Error in creating team")

        finally:
            con.close()
            return render_template("create-team.html")

    return render_template("create-team.html")


@app.route('/user/options')
def user_options():
    return render_template("user-options.html", user=user)


@app.route('/team/visualize')
def team_visualize():
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
        return redirect(url_for("user_options"))
    else:
        if user.user_type == 'Instructor':
            return render_template("set-team-parameters.html")
        else:
            return render_template("index.html")


if __name__ == '__main__':
    app.run()
