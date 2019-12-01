from flask import Flask, render_template, request, redirect, url_for, flash, g
from models.user import User
from models.team import Team

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')
app.secret_key = 'random string'

user = User('test', 'er', 'ere@ere.com')
user.user_type = 'Instructor'
teams = []
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
    app.run()
