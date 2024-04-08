from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
import movie_operations

# Advised during testing
MINIMIZE_API_CALLS = True

if MINIMIZE_API_CALLS:
    length = 1
else:
    length = 10

app = Flask(__name__)
Bootstrap5(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        movie = eval(request.form["movie"])
        movie_operations.download_movie(movie["title"], movie["release_year"])
    return render_template("index.html", movies=movies)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    movies = movie_operations.get_movie_toplist(length=length)
    app.run(debug=True)

