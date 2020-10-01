# %% 
import json

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px

# %%
this_week = pd.read_csv("data-by-modzcta.csv")
last_week = pd.read_csv("data-by-modzcta-last-week.csv")
this_week.columns = [c.lower() for c in this_week.columns]
last_week.columns = [c.lower() for c in last_week.columns]

# %%
nycmap = json.load(open("Geography-resources/MODZCTA_2010_WGS1984.geo.json"))

# %%
this_week["positive_check"] = ((this_week["covid_case_count"] / this_week["total_covid_tests"])* 100).round(2)
assert len(this_week[this_week.positive_check != this_week.percent_positive]) == 0

# %%
id_cols = ["modified_zcta", "neighborhood_name", "borough_group", "pop_denominator"]
cols_wanted = id_cols+["covid_case_count", "total_covid_tests"]
df = this_week[cols_wanted].merge(last_week[cols_wanted], how="left", on=id_cols, suffixes=["", "_last_week"])
# %%
df["Cases in the past week"] = df["covid_case_count"] - df["covid_case_count_last_week"]
# some places where total cases were higher past week than this week...
df["Cases in the past week"] = df["Cases in the past week"].clip(0, None)
df["Tests in the past week"] = df["total_covid_tests"] - df["total_covid_tests_last_week"]
df["Positivity Rate (%)"] = ((df["Cases in the past week"] / df["Tests in the past week"]) * 100).round(2)
df["Cases per 100,000 people"] = ((df["Cases in the past week"] / df["pop_denominator"]) * 100000).round()
df["Zip Code"] = df["modified_zcta"]
df["Neighborhood"] = df["neighborhood_name"].str.replace("/"," /<br>")

# %%
df["Positivity Rate (%)"].hist()

# %%
df["Cases per 100,000 people"].hist()

# %%
fig = px.choropleth_mapbox(df,
                           geojson=nycmap,
                           locations="Zip Code",
                           featureidkey="properties.MODZCTA",
                           color="Positivity Rate (%)",
                           color_continuous_scale="viridis",
                           mapbox_style="carto-positron",
                           zoom=9, 
                           center={"lat": 40.7, "lon": -73.9},
                           opacity=0.7,
                           hover_name="Neighborhood", 
                           hover_data={
                               "Cases in the past week", 
                               "Tests in the past week",
                               "Cases per 100,000 people"}
                           )
# %%
fig.write_html("nyc_positivity.html")
# %%
