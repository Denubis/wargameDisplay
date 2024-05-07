from collections import defaultdict
from pprint import pprint
import tabulate
from gameboard import *

dice_prob = {
    2: 1 / 36,
    3: 2 / 36,
    4: 3 / 36,
    5: 4 / 36,
    6: 5 / 36,
    7: 6 / 36,
    8: 5 / 36,
    9: 4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
}


def calculate_adjusted_outcomes(regions, adjustment=0):
    """
        regions = {
        'Island': {'votes': 3, 'modifier': 0},
        'WestCoast': {'votes': 4, 'modifier': +2},
        'MidWest': {'votes': 11, 'modifier': -3},
        'EastCoast': {'votes': 10, 'modifier': 0},
        'SouthWest': {'votes': 8, 'modifier': 0},
        'DeepSouth': {'votes': 5, 'modifier': -2},
        'SunState': {'votes': 12, 'modifier': +2}
    }
    """
    # pprint(regions)
    adjusted_results = {}
    for region, info in regions.items():
        # Apply the adjustment to the modifier
        adjusted_modifier = info["modifier"] + adjustment
        orange_wins = 0
        green_wins = 0
        undecided = 0
        for sum_dice, prob in dice_prob.items():
            adjusted_sum = sum_dice + adjusted_modifier
            if adjusted_sum < 7:
                green_wins += prob
            elif adjusted_sum > 7:
                orange_wins += prob
            else:
                undecided += prob
        adjusted_results[region] = {
            "orange_wins": round(orange_wins * info["votes"], 2),
            "green_wins": round(green_wins * info["votes"], 2),
            "undecided_votes": round(undecided * info["votes"], 2),
        }
    # aggregate all regions to get total
    total_orange_wins = sum([info["orange_wins"] for info in adjusted_results.values()])
    total_green_wins = sum([info["green_wins"] for info in adjusted_results.values()])
    total_undecided = sum(
        [info["undecided_votes"] for info in adjusted_results.values()]
    )
    adjusted_results["Total"] = {
        "orange_wins": round(total_orange_wins, 2),
        "green_wins": round(total_green_wins, 2),
        "undecided_votes": round(total_undecided, 2),
    }
    return adjusted_results


def generate_expected_outcomes_html(regions):
    pprint(regions)
    # make out_regions a list ordered by votes
    out_regions = []
    output = calculate_adjusted_outcomes(regions)
    for region, values in output.items():
        out_regions.append(
            [
                region,
                values["orange_wins"],
                values["green_wins"],
                values["undecided_votes"],
            ]
        )

    out_html = "<table><tr><th>Region</th><th style='padding-left:5px'>Orange</th><th style='padding-left:5px'>Green</th><th style='padding-left:5px'>Centre</th></tr>"

    for region, orange, green, undecided in out_regions:
        
        print(balance_colors)
        if region != "Total":
            background = balance_colors[regions[region]['modifier']+4]
            text_color = "#000000"
        else:            
            background = "#000000"                    
            text_color = "#fff"


        out_html += f"<tr style='background:{background};color:{text_color}'><td>{region}</td><td class='center'>{'+' if orange < 10 else ''}{orange:.2f}</td><td class='center'>{'+' if green < 10  else ''}{green:.2f}</td><td class='center'>{'+' if undecided < 10  else ''}{undecided:.2f}</td></tr>"

    out_html += "</table>"
    return out_html
