import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt

# Load the GeoJSON data
url = (
    "https://github.com/PublicaMundi/MappingAPI/raw/master/data/geojson/us-states.json"
)
states = gpd.read_file(url)

# Define the regions and their corresponding state names
# regions = {
#     "WestCoast": ["Washington", "Oregon", "California"],
#     "MidWest": [
#         "Ohio",
#         "Indiana",
#         "Michigan",
#         "Illinois",
#         "Wisconsin",
#         "Minnesota",
#         "Iowa",
#         "Missouri",
#         "North Dakota",
#         "South Dakota",
#         "Nebraska",
#         "Kansas",
#     ],
#     "EastCoast": [
#         "Maine",
#         "New Hampshire",
#         "Vermont",
#         "Massachusetts",
#         "Rhode Island",
#         "Connecticut",
#         "New York",
#         "New Jersey",
#         "Pennsylvania",
#         "Delaware",
#         "Maryland",
#         "Virginia",
#         "West Virginia",
#     ],
#     "Island": ["Alaska", "Hawaii"],
#     "SouthWest": [
#         "Colorado",
#         "New Mexico",
#         "Arizona",
#         "Utah",
#         "Nevada",
#         "Montana",
#         "Idaho",
#         "Wyoming",
#     ],
#     "DeepSouth": [
#         "Kentucky",
#         "Tennessee",
#         "Alabama",
#         "Mississippi",
#         "Arkansas",
#         "Louisiana",
#         "Oklahoma",
#         "Texas",
#     ],
#     "SunState": ["North Carolina", "South Carolina", "Georgia", "Florida"],
# }

regions = {
    "WestCoast": [
        # "Maine",
        # "New Hampshire",
        # "Vermont",
        "Massachusetts",
        "Rhode Island",
        "Connecticut",
        "New York",
        "New Jersey",
        "Pennsylvania",
        "Delaware",
        "Maryland",
        "Virginia",
        "North Carolina",
        "South Carolina",
        "West Virginia",
        "Ohio",
        "Kentucky",
        "Tennessee",
        # "Florida",
    ],
    "MidWest": [
        "Georgia",
        "Arkansas",
        "Alabama",
        "Mississippi",
        "Oklahoma",
        "Louisiana",
        "Texas",
    ],
    "EastCoast": [
        "New Mexico",
        "California",
        "Nevada",
        "Arizona",
        "Utah",
    ],
    "Island": ["Alaska", "Hawaii"],
    "DeepSouth": [
        "Kansas",
        "Colorado",
        "Nebraska",
        "South Dakota",
        "North Dakota",
    ],
    "SouthWest": [
        "Missouri",
        "Indiana",
        "Illinois",
        # "Michigan",
        "Wisconsin",
        "Minnesota",
        "Iowa",
    ],
    "SunState": [
        "Wyoming",
        "Montana",
        "Oregon",
        "Idaho",
        "Washington",
    ],
}


# Create a new column 'Region' based on the state name
states["Region"] = states["name"].map(
    lambda x: next((k for k, v in regions.items() if x in v), "Unknown")
)

# Group states by region and create MultiPolygon geometries
regions_gdf = states.dissolve(by="Region")


# remove the "Island" region from regions_gdf
# regions_gdf = regions_gdf[regions_gdf.index != "Island"]

# Also remove anything that isn't in a region
regions_gdf = regions_gdf[regions_gdf.index != "Unknown"]


# Reset the index
regions_gdf = regions_gdf.reset_index()


# Flip the map by skewing the x-axis
regions_gdf["geometry"] =  regions_gdf["geometry"].rotate(180, origin=(0, 0))

# Separate Alaska and Hawaii from the 'Island' region
alaska = states[states["name"] == "Alaska"]
hawaii = states[states["name"] == "Hawaii"]

# Translate and scale Alaska and Hawaii
alaska_scaled = (
    alaska.scale(0.2, 0.4, origin=(0, 0)).translate(-45, 5).rotate(180, origin=(0, 0))
)
hawaii_scaled = (
    hawaii.scale(1.5, 2, origin=(0, 0)).translate(162, -6).rotate(180, origin=(0, 0))
)


island_geometry = unary_union([alaska_scaled.item(), hawaii_scaled.item()])

# # Update the geometry of the 'Island' region in the GeoDataFrame
regions_gdf.loc[regions_gdf["Region"] == "Island", "geometry"] = island_geometry

# Simplify the geometries to smooth the map
tolerance = 0.1  # Adjust the tolerance value as needed
regions_gdf["geometry"] = regions_gdf["geometry"].simplify(tolerance)


regions_gdf["votes"] = 0
regions_gdf["green_balance"] = 0
regions_gdf["orange_balance"] = 0

# Plot the map
fig, ax = plt.subplots(1, figsize=(10, 6))
regions_gdf.plot(column="Region", cmap="tab10", linewidth=0.8, ax=ax, edgecolor="0.8")

#Add region names to the regions
for x, y, label in zip(regions_gdf.geometry.centroid.x, regions_gdf.geometry.centroid.y, regions_gdf["Region"]):
    ax.text(x, y, label, fontsize=8, ha='center', va='center')

# add states to a geodf, rotate the map 180, then plot over the same figure
states = states[states["Region"] != "Unknown"]
# remove HI and AK from states
states = states[states["name"] != "Alaska"]
states = states[states["name"] != "Hawaii"]
states["geometry"] = states["geometry"].rotate(180, origin=(0, 0))
states.plot(ax=ax, edgecolor="black", linewidth=0.25, color="none")
# label each state
for x, y, label in zip(states.geometry.centroid.x, states.geometry.centroid.y, states["name"]):
    ax.text(x, y, label, fontsize=6, ha='center', va='center')




# Save the combined GeoDataFrame to a GeoJSON file
output_file = "./static/centralia.geojson"
regions_gdf.to_file(output_file, driver="GeoJSON")

# Customize the plot
ax.axis("off")
ax.set_title("US Regions")

# Display the plot
plt.show()
