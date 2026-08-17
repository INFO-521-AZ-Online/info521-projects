"""Plotting plumbing: colorblind-safe palette and reusable panels.

Helpers draw *given* quantities (a fit line, an error band, a credible band).
They never compute the fit, the variance, or the posterior -- the student passes
those in.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# Okabe-Ito colorblind-safe palette (course standard).
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "skyblue": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}


def use_course_style():
    """Apply a clean, accessible default style. Call once at notebook top."""
    plt.rcParams.update({
        "figure.figsize": (7, 4.5),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "font.size": 11,
        "axes.prop_cycle": plt.cycler(color=list(OKABE_ITO.values())),
    })


def scatter(x, y, ax=None, label="data", **kw):
    ax = ax or plt.gca()
    ax.scatter(x, y, s=18, alpha=0.6, color=OKABE_ITO["black"], label=label, **kw)
    return ax


def fit_line(x_grid, y_hat, ax=None, label="fit", color=None, **kw):
    """Overlay a predicted curve the student computed."""
    ax = ax or plt.gca()
    ax.plot(x_grid, y_hat, lw=2, color=color or OKABE_ITO["blue"], label=label, **kw)
    return ax


def error_band(x_grid, y_hat, sd, ax=None, k=2.0, label=None, color=None):
    """Shade y_hat +/- k*sd. Use for predictive (frequentist) uncertainty in 1.2.

    The student supplies y_hat and sd; this only shades.
    """
    ax = ax or plt.gca()
    c = color or OKABE_ITO["orange"]
    ax.fill_between(x_grid, y_hat - k * sd, y_hat + k * sd, alpha=0.25, color=c,
                    label=label or f"+/- {k:g} sd")
    return ax


def credible_band(x_grid, lower, upper, ax=None, label=None, color=None):
    """Shade an interval [lower, upper] the student computed. Use for Bayesian
    posterior-predictive credible intervals in 1.3."""
    ax = ax or plt.gca()
    c = color or OKABE_ITO["green"]
    ax.fill_between(x_grid, lower, upper, alpha=0.25, color=c,
                    label=label or "credible interval")
    return ax


def cv_curve(orders, train_err, val_err, ax=None):
    """Plot training vs validation error against model complexity (1.1)."""
    ax = ax or plt.gca()
    ax.plot(orders, train_err, marker="o", color=OKABE_ITO["skyblue"], label="train")
    ax.plot(orders, val_err, marker="s", color=OKABE_ITO["vermillion"], label="validation")
    ax.set_xlabel("polynomial order")
    ax.set_ylabel("error")
    ax.legend()
    return ax
