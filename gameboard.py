import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import base64
# import patheffects for matplotlib
import matplotlib.patheffects as path_effects

def create_gameboard_map(geojson_path, yaml_data):
    # Read the GeoJSON file
    regions = gpd.read_file(geojson_path)

    # Define the color gradient
    green_color = "#00FF00"
    orange_color = "#FFA500"
    balanced_color = "#FAFAFA"
    color_range = 4
    color_gradient = [green_color, balanced_color, orange_color]
    color_map = mcolors.LinearSegmentedColormap.from_list(
        "balance_gradient", color_gradient, N=color_range * 2 + 1
    )

    region_data_dict = {region_data["region"]: region_data for region_data in yaml_data}

    # calcualte balance in region_data_dict, where balance is a str where, green_balance of +4 = "+4 green" and orange_balance of +4 = "+4 orange" if balanced, "0"
    for region_data in yaml_data:
        green_balance = region_data["green_balance"]
        orange_balance = region_data["orange_balance"]
        balance = green_balance - orange_balance
        region_data["balance"] = f"+{balance} green" if balance > 0 else f"+{balance*-1} orange" if balance < 0 else "0"

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
    fig, ax = plt.subplots(1, figsize=(16, 8))
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
        ax.annotate(
            f"{row['Region']}\n{region_data_dict[row['Region']]['votes']} votes\n{region_data_dict[row['Region']]['balance']}\n{region_data_dict[row['Region']]['agenda_str']}",
            xy=(center.x, center.y),
            xytext=(-25, -10),
            textcoords="offset points",
            fontsize=16,
            # stroke white
            path_effects=[path_effects.withStroke(linewidth=2, foreground="white")                          
                          ],
            # align centre
            horizontalalignment="center"
        )

    # Remove axis
    ax.axis("off")

    # Save the plot as an image
    img_data = io.BytesIO()
    plt.savefig(img_data, format="png", bbox_inches="tight", pad_inches=0.1)
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.getvalue()).decode("utf-8")

    return img_base64
