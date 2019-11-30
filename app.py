from flask import Flask, render_template, request
from models.user import User

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')

user = User('test', 'er', 'ere@ere.com')
user.user_type = 'Instructor'
teams = []
are_team_parameters_set = False


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


@app.route('/team/parameters')
def team_parameters():
    if user.user_type == 'Instructor':
        return render_template("set-team-parameters.html")
    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run()
