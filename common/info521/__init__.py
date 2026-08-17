"""info521 - plumbing for INFO 521 projects.

This package provides *mechanics only*: data loading, plotting helpers, and
value-based self-check fixtures. It deliberately contains NO machine-learning
estimators. Fitting a model (least squares, MLE, posterior, SVM, k-means, PCA)
is the student's job and must be implemented from scratch in NumPy/SciPy, per
the course's depth-over-breadth, no-off-the-shelf-solvers policy.

If you find yourself wanting to add a function that *solves* for parameters,
that belongs in a student notebook, not here.
"""

from . import data, plotting, checks

__all__ = ["data", "plotting", "checks"]
__version__ = "0.1.0"
