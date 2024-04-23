import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import base64
# import patheffects for matplotlib
import matplotlib.patheffects as path_effects
from matplotlib.colors import to_hex
import matplotlib.colors as mcolors

import tabulate
import textwrap


# Define the color gradient
green_color = "#00FF00"
orange_color = "#FFA500"
balanced_color = "#FAFAFA"
color_range = 4
color_gradient = [green_color, balanced_color, orange_color]
color_map = mcolors.LinearSegmentedColormap.from_list(
    "balance_gradient", color_gradient, N=color_range * 2 + 1
)
balance_colors = [mcolors.rgb2hex(color_map(i)) for i in range(color_range * 2 + 1)]

def create_gameboard_map(geojson_path, yaml_data, region_data_dict):
    # Read the GeoJSON file
    regions = gpd.read_file(geojson_path)

    
    
    # calcualte balance in region_data_dict, where balance is a str where, green_balance of +4 = "+4 green" and orange_balance of +4 = "+4 orange" if balanced, "0"
    for region_data in yaml_data:
        green_balance = region_data["green_balance"]
        orange_balance = region_data["orange_balance"]
        balance = green_balance - orange_balance
        region_data["balance_str"] = f"+{balance} green" if balance > 0 else f"+{balance*-1} orange" if balance < 0 else "0"

        # make a str for agenda
        region_data["agenda_str"] = '\n'.join(region_data['agenda'])

    # print(region_data_dict)

    # Update the regions data with YAML data
    for region_data in yaml_data:
        # print(region_data)
        region_name = region_data["region"]
        region = regions[regions["Region"] == region_name]
        if not region.empty:
            region.loc[:, "votes"] = region_data["votes"]
            region.loc[:, "green_balance"] = region_data["green_balance"]
            region.loc[:, "orange_balance"] = region_data["orange_balance"]
            # print(region)
        

    # Create a plot
    fig, ax = plt.subplots(1, figsize=(17, 11))
    regions.plot(ax=ax, edgecolor="black", linewidth=0.25, color="gray")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove plot margin
    # Tight layout
    fig.tight_layout()

    # Customize the fill color based on balance
    for _, row in regions.iterrows():
        region_name = row["Region"]
        if region_name in region_data_dict:
            region_data = region_data_dict[region_name]
            green_balance = region_data["green_balance"]
            orange_balance = region_data["orange_balance"]
            balance = orange_balance- green_balance
            fill_color = color_map((balance + color_range) / (color_range * 2))
            if row.geometry.geom_type == "MultiPolygon":
                for polygon in row.geometry.geoms:
                    ax.fill(
                        polygon.exterior.xy[0],
                        polygon.exterior.xy[1],
                        color=fill_color,
                        edgecolor="gray",
                    )
            else:
                ax.fill(
                    row.geometry.exterior.xy[0],
                    row.geometry.exterior.xy[1],
                    color=fill_color,
                    edgecolor="gray",
                )

    # Add region names as labels
    for _, row in regions.iterrows():
        center = row.geometry.centroid
        # {region_data_dict[row['Region']]['votes']} votes\n
        ax.annotate(
            f"""{row['Region']}\n{region_data_dict[row['Region']]['balance_str']}""",
            xy=(center.x, center.y),
            xytext=(-5, -5),
            textcoords="offset points",
            fontsize=16,
            # stroke white
            path_effects=[path_effects.withStroke(linewidth=2, foreground="white")                          
                          ],
            # align centre
            horizontalalignment="center"
        )
        # ax.annotate(
        #     f"""{region_data_dict[row['Region']]['agenda_str']}""",
        #     xy=(center.x, center.y),
        #     xytext=(-25, -60),
        #     textcoords="offset points",
        #     fontsize=12,
        #     # stroke white
        #     path_effects=[path_effects.withStroke(linewidth=2, foreground="white")                          
        #                   ],
        #     # align centre
        #     horizontalalignment="center"
        # )

    # Remove axis
    ax.axis("off")

    # Save the plot as an image
    img_data = io.BytesIO()
    plt.savefig(img_data, format="png", bbox_inches="tight", pad_inches=0.1)
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.getvalue()).decode("utf-8")

    return img_base64


def make_agenda_table(region_data_dict):
    """Make a tabulate table of region and votes, colour the region by balance"""

    agendas = []
    
    print(balance_colors)
    for region, data in region_data_dict.items():
        agenda_inner_html = "<ul>"
        for agenda in data["agenda"]:
            agenda_inner_html += f"<li>{agenda}</li>"
        agenda_inner_html += "</ul>"

        balance = data['balance_str']
        votes = data['votes']
        agendas.append([region, agenda_inner_html, votes])
    
    # reorder agendas by votes
    # agendas = sorted(agendas, key=lambda x: x[2], reverse=False)

    agenda_html = f"""
<table id="agenda"><tr><th>Region</th><th>Agenda</th><th>Votes</th></tr>
    """
    for region, agenda, votes in agendas:
        background = balance_colors[region_data_dict[region]['modifier']+4]
        agenda_html += f"<tr style='background:{background}'><td class='region'>{region}</td><td class='agenda'>{agenda}</td><td class='pad'>{votes}</td></tr>"


    return agenda_html