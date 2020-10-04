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
citywide_file = "tests.csv"
map_name = "nyc-positivity.html"

def get_citywide_data(citywide_file):
    """ Get latest citywide tests data and format it """
    citywide = pd.read_csv(citywide_file)
    citywide.columns = [c.lower() for c in citywide.columns]
    citywide = citywide.tail(1).reset_index(drop=True)
    for c in ["total_tests", "positive_tests", "total_tests_7days_avg", "positive_tests_7days_avg"]: 
        citywide[c] = citywide[c].astype(int).apply(lambda x : "{:,}".format(x))
    citywide["percent_positive_7days_avg"] = (citywide["percent_positive_7days_avg"] * 100).round(1)
    citywide["percent_positive"] = (citywide["percent_positive"] * 100).round(1)
    citywide["date"] = citywide["date"].map(lambda x: datetime.strptime(x, '%m/%d/%Y').strftime('%B %d, %Y'))
    citywide = citywide.iloc[0]
    print(citywide)
    return citywide

def import_file(date_wanted):
    """ 
    Import neighborbood data from latest commit,
    one week before latest commit, and two weeks before latest commit 
    """
    df = pd.read_csv(f"data-by-modzcta-{date_wanted}.csv")
    df.columns = [c.lower() for c in df.columns]
    return df

def merge_data(this_week, last_week, two_weeks_ago):
    """ 
    Merge neighborhood case counts and covid tests from one week ago
    and two weeks ago onto latest data available
    """
    # Check positivity rate calculation
    this_week["positive_check"] = ((this_week["covid_case_count"] / this_week["total_covid_tests"])* 100).round(2)
    assert len(this_week[this_week.positive_check != this_week.percent_positive]) == 0
    # Merge data sets
    id_cols = ["modified_zcta", "neighborhood_name", "borough_group", "pop_denominator"]
    cols_wanted = id_cols+["covid_case_count", "total_covid_tests"]
    df = this_week[cols_wanted].merge(last_week[cols_wanted], how="left", on=id_cols, suffixes=["", "_last_week"])
    df = df.merge(two_weeks_ago[cols_wanted], how="left", on=id_cols, suffixes=["", "_two_weeks_ago"])
    return df

def prep_stats(df):
    """
    Calculate cases and tests in last 7 days, positivity rate over 
    last 7 days, and average daily cases per 100,000 people over 7 days.
    Calculate the same for cases and tests in the week before last 7 days.
    """
    df = df.copy(deep=True)
    # %% Stats over the past week - today to 7 days ago
    df["Cases in the past week"] = df["covid_case_count"] - df["covid_case_count_last_week"]
    # some places where total cases were higher past week than this week...
    df["Cases in the past week"] = df["Cases in the past week"].clip(0, None)
    df["Tests in the past week"] = df["total_covid_tests"] - df["total_covid_tests_last_week"]
    df["Positivity Rate (%)"] = ((df["Cases in the past week"] / df["Tests in the past week"]) * 100).round(2)
    df["Average daily cases per 100,000 people"] = (((df["Cases in the past week"] / df["pop_denominator"]) * 100000) / 7).round()

    # %% Stats over week before last - 7 days ago to 14 days ago
    df["Cases in the week before last"] = df["covid_case_count_last_week"] - df["covid_case_count_two_weeks_ago"]
    df["Cases in the week before last"] = df["Cases in the week before last"].clip(0, None)
    df["Tests in the week before last"] = df["total_covid_tests_last_week"] - df["total_covid_tests_two_weeks_ago"]
    df["Last week's positivity rate (%)"] = ((df["Cases in the week before last"] / df["Tests in the week before last"]) * 100).round(2)
    df["Last week's cases per 100,000 people"] = (((df["Cases in the week before last"] / df["pop_denominator"]) * 100000) / 7).round()

    return df

def produce_map(df, nycmap, map_name):
    """
    Make choropleth map showing positivity rate by neighborhood in New York.
    Show additional stats on hover.
    Save to file
    """
    # Formatting
    df["Zip Code"] = df["modified_zcta"]
    df["Neighborhood"] = df["neighborhood_name"].str.replace("/"," /<br>")
    df["Population"] = df["pop_denominator"].round()

    # Make map
    fig = px.choropleth_mapbox(
        df,
        geojson=nycmap,
        locations="Zip Code",
        featureidkey="properties.MODZCTA",
        color="Positivity Rate (%)",
        color_continuous_scale="Portland",
        mapbox_style="carto-positron",
        zoom=9, 
        center={"lat": 40.7, "lon": -74},
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
        width=600, height=600
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    config = {'displaylogo': False}
    fig.write_html(map_name, config=config)
    return fig

def update_md_file(citywide, latest_date, index_file):
    """
    Update main page of website with new information.
    Write to file.
    """

    latest_date_long = datetime.strptime(latest_date, '%Y-%m-%d').strftime('%B %d, %Y')

    md_str = f"""

    Last updated {latest_date_long}

    ## Citywide Positivity Rate in the Past Week

    As of {citywide["date"]}, New York performed an average of {citywide["total_tests_7days_avg"]} tests per day over the previous seven days. The city recorded {citywide["positive_tests_7days_avg"]} positive tests over the same period, a positivity rate of {citywide["percent_positive_7days_avg"]}%.

    ## Positivity Rate in the Past Week by Neighborhood

    {{% include_relative nyc-positivity.html%}}

    Map data as of {latest_date_long}

    Source: NYC Dept. of Health

    Repo: [https://github.com/jimmykaiser/coronavirus-data](https://github.com/jimmykaiser/coronavirus-data)"""

    with open(index_file, 'w') as f:
        f.write(md_str)

    return md_str

def make_new_map(latest_date):
    """ Make new map of New York neighborhoods """
    citywide = get_citywide_data(citywide_file)
    this_week = import_file("today")
    last_week = import_file("last-week")
    two_weeks_ago = import_file("two-weeks-ago")
    df = merge_data(this_week, last_week, two_weeks_ago)
    df = prep_stats(df)
    produce_map(df, nycmap, map_name)
    update_md_file(citywide, latest_date, index_file)
    return

if __name__ == "__main__":
    latest_date = sys.argv[1]
    make_new_map(latest_date)
