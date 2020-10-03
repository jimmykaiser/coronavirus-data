# %% 
import json

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px

from get_date import get_date

# %%
def import_file(date_wanted):
    df = pd.read_csv(f"data-by-modzcta-{date_wanted}.csv")
    df.columns = [c.lower() for c in df.columns]
    return df

today = get_date(0)
one_week_ago = get_date(7)
two_weeks_ago = get_date(14)

this_week = import_file(today)
last_week = import_file(one_week_ago)
week_before_last = import_file(two_weeks_ago)

# %%
nycmap = json.load(open("Geography-resources/MODZCTA_2010_WGS1984.geo.json"))

# %%
this_week["positive_check"] = ((this_week["covid_case_count"] / this_week["total_covid_tests"])* 100).round(2)
assert len(this_week[this_week.positive_check != this_week.percent_positive]) == 0

# %%
id_cols = ["modified_zcta", "neighborhood_name", "borough_group", "pop_denominator"]
cols_wanted = id_cols+["covid_case_count", "total_covid_tests"]
df = this_week[cols_wanted].merge(last_week[cols_wanted], how="left", on=id_cols, suffixes=["", "_last_week"])
df = df.merge(week_before_last[cols_wanted], how="left", on=id_cols, suffixes=["", "_two_weeks_ago"])
# %% Over the past week - today to 7 days ago
df["Cases in the past week"] = df["covid_case_count"] - df["covid_case_count_last_week"]
# some places where total cases were higher past week than this week...
df["Cases in the past week"] = df["Cases in the past week"].clip(0, None)
df["Tests in the past week"] = df["total_covid_tests"] - df["total_covid_tests_last_week"]
df["Positivity Rate (%)"] = ((df["Cases in the past week"] / df["Tests in the past week"]) * 100).round(2)
df["Average daily cases per 100,000 people"] = (((df["Cases in the past week"] / df["pop_denominator"]) * 100000) / 7).round()

# %% Week before last - 7 days ago to 14 days ago
df["Cases in the week before last"] = df["covid_case_count_last_week"] - df["covid_case_count_two_weeks_ago"]
df["Cases in the week before last"] = df["Cases in the week before last"].clip(0, None)
df["Tests in the week before last"] = df["total_covid_tests_last_week"] - df["total_covid_tests_two_weeks_ago"]
df["Last week's positivity rate (%)"] = ((df["Cases in the week before last"] / df["Tests in the week before last"]) * 100).round(2)
df["Last week's cases per 100,000 people"] = (((df["Cases in the week before last"] / df["pop_denominator"]) * 100000) / 7).round()

# %% Formatting
df["Zip Code"] = df["modified_zcta"]
df["Neighborhood"] = df["neighborhood_name"].str.replace("/"," /<br>")
df["Population"] = df["pop_denominator"].round()

# %%
df["Positivity Rate (%)"].hist()

# %%
df["Average daily cases per 100,000 people"].hist()

# %%
fig = px.choropleth_mapbox(df,
                           geojson=nycmap,
                           locations="Zip Code",
                           featureidkey="properties.MODZCTA",
                           color="Positivity Rate (%)",
                           color_continuous_scale="Portland",
                           mapbox_style="carto-positron",
                           zoom=9, 
                           center={"lat": 40.7, "lon": -73.9},
                           opacity=0.7,
                           hover_name="Neighborhood", 
                           hover_data={
                                "Population", 
                                "Cases in the past week", 
                                "Tests in the past week",
                                "Last week's cases per 100,000 people", 
                                "Average daily cases per 100,000 people",
                                "Last week's positivity rate (%)", 
                               },
                           width=900, height=700
                           )

# %%
# fig.update_traces(hovertemplate='Population: %{Population} <br>Cases: Test')
# %%
fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
config = {'displaylogo': False}
fig.write_html("nyc-positivity.html", config=config)

# %%
