"""Statistical plots"""

from pathlib import Path
import pandas as pd
import numpy as np
import os

import plotly.graph_objects as go
from narwhals import DataFrame
from plotly.subplots import make_subplots

def box_all(data:DataFrame, x:str, y:str, desired_order:list[str], points:str="all"):
    # make algorithm column categorical and in the order of best performing.
    data[x] = pd.Categorical(data[x], categories=desired_order, ordered=True)

    # Make the plot
    fig = go.Figure()
    fig.add_trace(go.Box(y=data[y], x=data[x], marker_color='#ed1b2f', boxpoints=points, boxmean=True))

    fig.update_layout(xaxis=dict(title=dict(text=x),),
                      yaxis=dict(title=dict(text=y),),
                      font=dict(size=24),
                      boxmode='group', height=750,
                      template="plotly_white"
                      )

    # Explicitly set the x-axis for the plot
    fig.update_xaxes(categoryorder="array", categoryarray=desired_order)
    fig.show()
    return fig

    # fig.write_image(".png")


def box_segmented(df:DataFrame, dim1:str, x:str, y:str, desired_order:list[str], points:str="all"):
    df[dim1] = pd.Categorical(df[dim1], categories=desired_order, ordered=True)
    fig = make_subplots(rows=1, cols=1, )
    for walk_mode in df["condition"].unique():
        filtered_df = df[df["condition"] == walk_mode]
        filtered_df["algorithm"] = pd.Categorical(filtered_df["algorithm"], categories=desired_order, ordered=True)
        fig.add_trace(go.Box(y=filtered_df["accuracy"], x=filtered_df["algorithm"],
                             name=walk_mode), row=1, col=1)

    fig.update_layout(xaxis_title="Algorithm",
                      yaxis_title="accuracy",
                      font=dict(size=24),
                      boxmode='group', height=750,
                      # plot_bgcolor='rgba(0, 0, 0, 0)',
                      # paper_bgcolor='rgba(0, 0, 0, 0)',
                      template='plotly_white',
                      )

    xaxis = dict(
        linecolor="#BCCCDC",  # Sets color of X-axis line
        showgrid=False,  # Removes X-axis grid lines
        zeroline=False,  # thick line at x=0
        showline=False,  # removes X-axis line
        showticklabels=True,  # axis ticklabels
        visible=True,  # numbers below

        showspikes=True,  # shows vertical line on hover
        spikemode='toaxis+across',  # shows vertical line on hover
        spikesnap='cursor',

        spikedash='solid',  # shows vertical line on hover
        spikecolor="#000000",
        spikethickness=1,

        categoryorder='array',
        categoryarray=desired_order

    )
    fig.update_xaxes(xaxis)
    fig.show()
    return fig
