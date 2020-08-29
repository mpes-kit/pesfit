#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import lineshape as ls, utils as u
import matplotlib.pyplot as plt
from functools import reduce


####################
# Fitting routines #
####################

def init_generator():

    pass


def model_generator():

    pass


def random_shift():

    pass


def varsetter(params, inits={}, ret=False):
    """ Variable setter for multiparameter fitting.
    
    :Parameters:
        params : `lmfit.parameter.Parameter` or other subclass of dict
            Parameter dictionary.
        init : dict | {}
            Initialization value dictionary.
        ret : bool | False
            Option for returning outcome.
    """
    
    if not issubclass(type(params), dict):
        raise TypeError('The params argument needs to be a dictionary or one of its subclasses.')
        
    else:
        if inits:

            # Merge entries if inits are provided as a list of dictionaries
            if len(inits) > 1:
                inits = reduce(u.dictmerge, inits)

            # Unpack the dictionary at the component level
            for kcomp, vcomp in inits.items():
                # Unpack the dictionary at the parameter level
                for kparam, vparam in vcomp.items():
                    params[kcomp+kparam].set(**vparam)
    
    if ret:
        return params


##########################
# Visualization routines #
##########################

def plot_fit_result(fitres, x, plot_components=True, downsamp=1, **kwds):
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


def plot_bandpath(paths, ksymbols, erange=[], evals=None, path_inds=[], koverline=True, klines=False, ret=False, **kwds):
    """ Plot momentum-energy map from a segment of the band mapping data.
    """
    
    fsize = kwds.pop('figsize', (10, 6))
    f, ax = plt.subplots(figsize=fsize)
    
    maxind = paths.shape[1]
    
    try:
        elo, ehi = erange
    except:
        elo, ehi = evals[0], evals[-1]
    plt.imshow(pathDiagram[:450, :], cmap='Blues', aspect=9.3, extent=[0, maxind, elo, ehi], vmin=0, vmax=0.5)
    
    # Momentum high-symmetry point annotation
    if koverline:
        klabels = ['$\overline{' + ksb +'}$' for ksb in ksymbols]
    else:
        klabels = ['$' + ksb + '$' for ksb in ksymbols]
    
    ax.set_xticks(path_inds)
    ax.set_xticklabels(klabels, fontsize=15)
    
    # Draw vertical lines to label momentum high-symmetry points
    if len(path_inds) * klines:
        for p in path_inds[:-1]:
            ax.axvline(x=p, c='r', ls='--', lw=2, dashes=[4, 2])

    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.set_ylabel('Energy (eV)', fontsize=15, rotation=-90, labelpad=20)
    ax.tick_params(axis='x', length=0, pad=6)
    ax.tick_params(which='both', axis='y', length=8, width=2, labelsize=15)
    
    if ret:
        return f, ax