#! /usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt


def fit_plot(fitres, x, plot_components=True, downsamp=1, **kwds):
    """ Plot the fitting outcomes.
    """
    
    figsz = kwds.pop('figsize', (8, 5))
    
    plt.figure(figsize=figsz)
    comps = fitres.eval_components(x=x)
    
    # Plot the spectral components
    if plot_components == True:
        for k, v in comps.items():
            plt.plot(x, v, '-', label=k[:-1])
    
    plt.plot(x, fitres.best_fit, '-r')
    plt.plot(x[::downsamp], fitres.data[::downsamp], '.k')