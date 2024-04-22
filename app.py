#!/usr/bin/env python3
from flask import Flask, render_template
import yaml
from gameboard import create_gameboard_map
from chyron import generate_chyron_html

app = Flask(__name__)


@app.route("/")
def home():
    geojson_path = "static/centralia.geojson"
    yaml_path = "data/gameboard.yaml"
    announcements_yaml_path = "data/announcements.yaml"

    with open(yaml_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    with open(announcements_yaml_path, "r") as file:
        announce_yaml_data = yaml.safe_load(file)

    gameboard_map = create_gameboard_map(geojson_path, yaml_data["board"])
    chyron_data = generate_chyron_html(announce_yaml_data["chyron"], turn=yaml_data["turn"])
    return render_template(
        "index.html",
        gameboard_map=gameboard_map,
        turn=yaml_data["turn"],
        chyron_html=chyron_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
