# Make map of Covid-19 positivity rate in New York by neighborhood
import sys
import json
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px

nycmap = json.load(open("Geography-resources/MODZCTA_2010_WGS1984.geo.json"))
index_file = "index.md"
citywide_file = "trends/tests.csv"
map_name = "nyc-positivity.html"

def get_citywide_data(citywide_file, days_ago):
    """ 
    Get citywide tests data from date `days ago` days ago and format it
    """
    # workaround for new repo structure
    try: 
        citywide = pd.read_csv(citywide_file)
    except:
        citywide = pd.read_csv("tests.csv")
    citywide.columns = [c.lower() for c in citywide.columns]
    citywide = citywide.tail(20).reset_index(drop=True)
    for c in ["total_tests", "positive_tests", "total_tests_7days_avg", "positive_tests_7days_avg"]: 
        citywide[c] = citywide[c].astype(int).apply(lambda x : "{:,}".format(x))
    citywide["percent_positive_7days_avg"] = (citywide["percent_positive_7days_avg"] * 100).round(1)
    citywide["percent_positive"] = (citywide["percent_positive"] * 100).round(1)
    citywide["date"] = citywide["date"].map(lambda x: datetime.strptime(x, '%m/%d/%Y').strftime('%B %-d, %Y'))
    days_ago = (days_ago + 1) * -1
    citywide = citywide.iloc[days_ago]
    print(citywide)
    return citywide

def import_file(date_wanted):
    """ 
    Import neighborbood data
    """
    df = pd.read_csv(f"last7days-by-modzcta-{date_wanted}.csv")
    df.columns = [c.lower() for c in df.columns]
    df.columns = ["modified_zcta","neighborhood_name","percent_positive","total_covid_tests","covid_case_count",
    "median_daily_test_rate","adequately_tested","date_range"]
    return df

def merge_data(this_week, last_week):
    """ 
    Merge neighborhood case counts and covid tests from one week ago
    onto latest data available
    """
    # Check positivity rate calculation
    this_week["positive_check"] = ((this_week["covid_case_count"] / this_week["total_covid_tests"])* 100).round(2)
    assert len(this_week[this_week.positive_check != this_week.percent_positive]) == 0
    # Merge data sets
    id_cols = ["modified_zcta", "neighborhood_name"]
    cols_wanted = id_cols+["covid_case_count", "total_covid_tests", "date_range"]
    df = this_week[cols_wanted].merge(last_week[cols_wanted], how="left", on=id_cols, suffixes=["", "_last_week"])
    return df

def prep_stats(df):
    """
    Calculate cases and tests in last 7 days and positivity rate over 
    last 7 days. 
    Calculate the same for cases and tests in the week before last 7 days.
    """
    df = df.copy(deep=True)
    # %% Stats over the past week - today to 7 days ago
    df["cases_past_week"] = df["covid_case_count"]
    df["tests_past_week"] = df["total_covid_tests"]
    df["positivity_rate_past_week"] = ((df["cases_past_week"] / df["tests_past_week"]) * 100).round(1)

    # %% Stats over week before last - 7 days ago to 14 days ago
    df["positivity_rate_week_before_last"] = ((df["covid_case_count_last_week"] / df["total_covid_tests_last_week"]) * 100).round(1)

    return df

def produce_map(df, nycmap, map_name):
    """
    Make choropleth map showing positivity rate by neighborhood in New York.
    Show additional stats on hover.
    Save to file
    """
    # Formatting
    df["Positivity Rate (%)"] = df["positivity_rate_past_week"]
    df["neighborhood"] = df["neighborhood_name"].str.replace("/"," /<br>")
    # df["population"] = df["pop_denominator"].round().astype(int).apply(lambda x : "{:,}".format(x))
    df["tests_past_week"] = df["tests_past_week"].round().astype(int).apply(lambda x : "{:,}".format(x))

    # Make map
    fig = px.choropleth_mapbox(
        df,
        geojson=nycmap,
        locations="modified_zcta",
        featureidkey="properties.MODZCTA",
        color="Positivity Rate (%)",
        range_color=[0, 10],
        color_continuous_scale="Portland",
        mapbox_style="carto-positron",
        zoom=9, 
        center={"lat": 40.7, "lon": -73.98},
        opacity=0.7,
        custom_data=[
                "neighborhood", 
                "date_range",
                # "population", 
                "cases_past_week", 
                "tests_past_week",
                "positivity_rate_week_before_last", 
                # "case_rate_past_week",
                # "case_rate_week_before_last",  
        ],
        width=600, height=500
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{customdata[0]}</b>",
            "Zip code: %{location}",
            # "Population: %{customdata[1]}",
            "Date Range: %{customdata[1]}", 
            "Cases in the past week: %{customdata[2]}",
            "Tests in the past week: %{customdata[3]}",
            "Postivity rate (%)<br>    This week: %{z}",
            "    Last week: %{customdata[4]}",
            # "Average daily cases per 100,000 people<br>    This week: %{customdata[5]}",
            # "    Last week: %{customdata[6]}",
        ])
    )
    config = {'displaylogo': False}
    fig.write_html(map_name, config=config)
    return fig

def update_md_file(citywide, citywide_last_week, index_file):
    """
    Update main page of website with new information.
    Write to file.
    """

    # latest_date_long = datetime.strptime(latest_date, '%Y-%m-%d').strftime('%B %-d, %Y')

    md_str = f"""
## Positivity rate over the past week by neighborhood

This map displays the percentage of Covid-19 tests that were positive over the last seven days for each New York City zip code. 

{{% include_relative nyc-positivity.html%}}

### Citywide numbers as of {citywide["date"]}

New York is averaging {citywide["total_tests_7days_avg"]} tests and {citywide["positive_tests_7days_avg"]} new cases per day over the past week. 

Over the past seven days, {citywide["percent_positive_7days_avg"]} percent of tests were positive. 

In the week ending {citywide_last_week["date"]}, {citywide_last_week["positive_tests_7days_avg"]} out of {citywide_last_week["total_tests_7days_avg"]} tests per day were positive, a rate of {citywide_last_week["percent_positive_7days_avg"]} percent. 

Source: NYC Dept. of Health  
Repo: [https://github.com/jimmykaiser/coronavirus-data](https://github.com/jimmykaiser/coronavirus-data)
"""

    with open(index_file, 'w') as f:
        f.write(md_str)

    return md_str

def make_new_map(latest_date):
    """ Make new map of New York neighborhoods """
    citywide = get_citywide_data(citywide_file, 0)
    citywide_last_week = get_citywide_data(citywide_file, 7)
    this_week = import_file("today")
    last_week = import_file("last-week")
    # two_weeks_ago = import_file("two-weeks-ago")
    df = merge_data(this_week, last_week)
    df = prep_stats(df)
    fig = produce_map(df, nycmap, map_name)
    md_str = update_md_file(citywide, citywide_last_week, index_file)
    print(md_str)
    return

if __name__ == "__main__":
    # latest_date = sys.argv[1]
    latest_date = "2020-11-19"
    make_new_map(latest_date)
