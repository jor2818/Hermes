from flask import Blueprint, render_template


views = Blueprint("views",__name__)

@views.route("/")
@views.route("/home")
def home():
    return render_template('home.html', name="HOME")

@views.route("/form")
def form():
    return render_template('form.html', name="FORM")


@views.route("/about")
def about():
    return render_template('about.html',name="ABOUT")

