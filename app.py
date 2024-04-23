#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for
import yaml
from gameboard import create_gameboard_map, make_agenda_table
from chyron import generate_chyron_html
from expectedoutcomes import generate_expected_outcomes_html
import os
app = Flask(__name__)


@app.route("/")
def home():

    # parse turn as a get request in the route, otherwise it is 1
    turn = request.args.get("turn", default=1, type=int)

    #check if the turn directory exists, otherwise redirect to turn 1
    if not os.path.exists(f"data/{turn}"):
        return redirect(url_for('home', turn=1))


    geojson_path = "static/centralia.geojson"
    yaml_path = f"data/{turn}/gameboard.yaml"
    announcements_yaml_path = f"data/{turn}/announcements.yaml"

    with open(yaml_path, "r") as file:
        yaml_data = yaml.safe_load(file)

    if not yaml_data['active']:
        return redirect(url_for('home', turn=turn-1))

    with open(announcements_yaml_path, "r") as file:
        announce_yaml_data = yaml.safe_load(file)

    region_data_dict = {region_data["region"]: region_data for region_data in yaml_data["board"]}

    for key in region_data_dict:
        green_balance = region_data_dict[key]["green_balance"]
        orange_balance = region_data_dict[key]["orange_balance"]
        region_data_dict[key]["modifier"] = orange_balance - green_balance

    gameboard_map = create_gameboard_map(
        geojson_path, yaml_data["board"], region_data_dict
    )
    outcome_html = generate_expected_outcomes_html(region_data_dict)
    print(outcome_html)
    chyron_data = generate_chyron_html(
        announce_yaml_data["chyron"], turn=yaml_data["turn"], policies=announce_yaml_data.get("policies")
    )
    agenda_table = make_agenda_table(region_data_dict)
    return render_template(
        "index.html",
        gameboard_map=gameboard_map,
        turn=yaml_data["turn"],
        chyron_html=chyron_data,
        outcome_html=outcome_html,
        agenda_table=agenda_table,
    )


if __name__ == "__main__":
    app.run(debug=True)
