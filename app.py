from flask import Flask, render_template, request, session, redirect, url_for, g, flash
from db.DatabaseConnection import DatabaseConnection
from db.config import config
import os

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')
app.secret_key = os.urandom(24)

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
            teamname = request.form['teamname']
				
			 
            db = DatabaseConnection()

            with db.get_connection() as con:

                cursor = con.cursor()
                cursor.execute("INSERT INTO tms.team(team_name) VALUES (%s)",(teamname,))

                flash("Successfully created team")
	  
        except:
            con.rollback()
            #return f"{err.__class__.__name__}: {err}"
            flash("Error in creating team")
			
        finally:
            con.close()
            return render_template("create-team.html")

    return render_template("create-team.html")


if __name__ == '__main__':
    app.run()
