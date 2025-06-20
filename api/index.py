from flask import Flask, request, jsonify
from .scraper import get_all_movie_links  # relative import

app = Flask(__name__)

@app.route("/", methods=["GET"])
def search():
    movie_name = request.args.get("name", "").strip()

    if not movie_name:
        return jsonify({"error": "Missing or empty 'name' parameter"}), 400

    # Ensure a trailing space if not already present
    if not movie_name.endswith(" "):
        movie_name += " "

    results = get_all_movie_links(movie_name)

    if not results:
        return jsonify({"message": "No results found"}), 404

    return jsonify({"data": results})
