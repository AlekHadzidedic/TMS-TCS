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
teams = []
    
with app.app_context():
    g.are_team_parameters_set = False

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/sign-in')
def sign_in():
    return render_template("sign-in.html")


@app.route('/register')
def register():
    return render_template("register.html")



@app.route('/create-team', methods=['GET','POST'])
def create_team():
    if request.method == 'POST':
      
            try:
                team_name = request.form['team_name']
                    
                
                db = DatabaseConnection()

                with db.get_connection() as con:

                    cursor = con.cursor()
                    cursor.execute("INSERT INTO tms.team(team_name) VALUES (%s)",(team_name,))

                    flash("Successfully created team")
        
            except:
                con.rollback()
                return f"{err.__class__.__name__}: {err}"
                #flash("Error in creating team")
                
            finally:
                con.close()
                return render_template("create-team.html")
       

    return render_template("create-team.html")


@app.route('/user/options')
def user_options():
    return render_template("user-options.html", user=user)


@app.route('/team')
def team_options():
    return render_template("create-team.html")


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

        flash('Parameters successfully set')
        g.are_team_parameters_set = True
        return redirect(url_for("user_options"))
    else:
        if user.user_type == 'Instructor':
            return render_template("set-team-parameters.html")
        else:
            return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    app.run()
