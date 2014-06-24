from __future__ import division
import numpy as np
from scipy.optimize import curve_fit


def _gaussian(x, A, variance, x0):
    return A*np.exp(-(x - x0)**2/(2*variance))


def Fstat(traj, lag, guess=None):
    """Return F statistic comparing variances of displacement distributions.

    Given trajectories for N particles, compute each particle's van Hove correlation
    function at over a given lag time. Fit those with Gaussians and compute the variance.
    Scale each variance by the number of independent degrees of freedom backing each
    particle's correlation function.

    Finally, consider the ratio of particles' scaled variances. These are F statistics.
    The results are given as an NxN array, where, for example, element [1, 2] is the
    F statistic comparing the variance of particles 1 and 2.

    Parameters
    ----------
    traj : DataFrame
        trajectories data, including columns 'frame' and 'particle'
    lag : time lag in frames
    guess : initial guess for nonlinear fit to Gaussian
        If None (default), infer a guess from the extremes of the data.

    Returns
    -------
    an NxN array comparing every particles' scaled variance to every other's

    Note
    ----
    This was implemented by Daniel B. Allan and the trackpy contributors, based on a
    method described by M.T. Valentine in Ref. 1, below. If it does not correctly
    represent that method, the fault lies with Dan.

    Reference
    ---------
    [1] M.T. Valentine et al., Phys. Rev. E, 061506 (2001)
    """
    pos = traj.set_index(['frame', 'particle'])['x'].unstack()
    vh = vanhove(pos, lag)
    if guess is None:
        guess = (vh.max().max(), vh.index.max()/2, 0.)
    lagtimes = vh.index.values.astype('float64')
    n = 1.5*traj.groupby('particle').size()/lag  # independent deg. of freedom
    # TODO Use more modern fitter? (Is it as fast?) Transform to log and fit parabola?
    fitter = lambda data: curve_fit(_gaussian, lagtimes, data, p0=guess)[0][1]
    variance = vh.apply(fitter)
    scaled_variance = variance/n
    f = scaled_variance.reshape(-1, 1) / scaled_variance.reshape(1, -1)
