from flask import Flask, render_template, request

# app = Flask(__name__)
app = Flask(__name__, static_folder='./static')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/sign-in')
def sign_in():
    return render_template("sign-in.html")


@app.route('/register')
def register():
    return render_template("register.html")


@app.route('/create-team')
def create_team():
    return render_template("create-team.html")


if __name__ == '__main__':
    app.run()
