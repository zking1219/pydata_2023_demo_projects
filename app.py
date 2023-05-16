# Example of using plotly via shinywidgets

import numpy as np
import plotly.graph_objs as go
from shiny import App, reactive, ui, render
from shinywidgets import output_widget, register_widget
from sklearn.linear_model import LinearRegression

import datetime
import pandas as pd

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("rate", "Annual rate of power bill increase", 0, 10, 4.5, step=.1),
        ),
        ui.panel_main(
            output_widget("time_series"),
        ),
    ),
)

def generate_bills_df(avg_bill, rate):
    """
    Requires more input params to be truly useful, just vary avg starting
    bill and rate of Dominion's annual bill increases for now.
    """
    # Get list of months to plot
    datelist = pd.date_range(datetime.datetime(2023,5,1), periods=int(26.8*12), freq='M').tolist()
    bills = []
    start_year = int(datelist[0].year)
    for dt in datelist:
        # Apply annual increases - perturb rates later to be more realistic
        years_from_today = dt.year - start_year
        base_bill = avg_bill*((1+rate)**years_from_today)
        
        # Add noise to monthly bill - get kwH used from mlforecast later and convert to a bill amount
        bills.append(base_bill + np.random.normal(0,30*((1+rate)**years_from_today)))
        
    bills_df = pd.DataFrame({"date" : datelist, "power_bill" : bills})
    bills_df['rolling6'] = bills_df['power_bill'].rolling(window=6, min_periods=1, center=True).mean()
    return bills_df

def server(input, output, session):
    # Create some fake utility bill data from now until 2050
    avg_bill = 170 # 2023 pre July rate hike of 10%
    init_rate = 0.045
    
    bills_df = generate_bills_df(avg_bill, init_rate)
    
    scatterplot = go.FigureWidget(
        data=[
            go.Scattergl(
                x=bills_df['date'],
                y=bills_df['power_bill'],
                mode="markers",
                marker=dict(color="blue", size=3),
                name="Monthly Bills"
            ),
            go.Scattergl(
                x=bills_df['date'],
                y=bills_df['rolling6'],
                mode="lines",
                marker=dict(color="red", size=3),
                name="6 Month Avg."
            )
        ],
        layout={
            "showlegend": True,
            "title" : f"Simulated Power Bills assuming {init_rate*100:.1f}% APR",
            "yaxis" : {"title" : "USD"},
            "xaxis" : {"title" : "billing date"}
        },
    )

    register_widget("time_series", scatterplot)

    @reactive.Effect
    def _():
        bills_df = generate_bills_df(avg_bill, float(input.rate())*.01)
        scatterplot.data[0].y = bills_df['power_bill']
        scatterplot.data[1].y = bills_df['rolling6']
        scatterplot.layout.title = f"Simulated Power Bills assuming {input.rate():.1f}% APR"


app = App(app_ui, server)
