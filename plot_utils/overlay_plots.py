""" Custom plots that consist of 2 or more plots overlayed
"""
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from typing import Any, Dict, List


def dot_line_overlay(
    x: str,
    y: str,
    hue: str,
    split: bool,
    data: pd.DataFrame,
    dot_plot=sns.swarmplot,
    ax: Any = None,
    hue_order: List = None,
    show_mean: bool = True,
    linewidth: float = 2.0,
    **kwargs
) -> Any:
    if ax is None:
        _, ax = plt.subplots()
    if hue_order is None:
        hue_order = data[hue].unique()
    dot_plot(
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        split=split,
        data=data,
        ax=ax,
        zorder=0,
        **kwargs
    )
    medianprops = dict(
        linewidth=0,
        color='black',
        linestyle='solid'
    )
    meanprops = dict(
        linestyle='solid',
        linewidth=linewidth,
        color='black'
    )
    if not show_mean:
        print('Line is Median')
        medianprops['linewidth'] = linewidth
        meanprops['linewidth'] = 0

    sns.boxplot(
        x=x,
        y=y,
        hue=hue,
        hue_order=hue_order,
        data=data,
        ax=ax,
        fliersize=0,
        showbox=False,
        whiskerprops={
            "alpha": 0
        },
        showcaps=False,
        showmeans=True,
        meanline=True,
        meanprops=meanprops,
        medianprops=medianprops,
        zorder=1,
    )
