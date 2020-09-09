#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import lineshape as ls, utils as u
import numpy as np
from functools import reduce
import inspect
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


existing_models = dict(inspect.getmembers(ls.lmm, inspect.isclass))

####################
# Fitting routines #
####################

def init_generator(params=None, varkey='value', **kwds):
    """ Dictionary generator for initial fitting conditions.

    :Parameters:
        params : instance of ``lmfit.parameter.Parameters``
            Existing model parameters.
        varkey : str | 'value'
            Keyword specified for the parameter ('value', 'min', 'max', 'vary').
        **kwds : keyword arguments
    """

    if params is None:
        parnames = kwds.pop('parnames', [])
    else:
        parnames = params.keys()

    parvals = kwds.pop('parvals', [])

    if parvals:
        # As an example, dict(value=1) is equivalent to {'value':1}.
        inits = dict((pn, {varkey:pv}) for pn, pv in zip(parnames, parvals))
    
        return inits


def model_generator(peaks={'Voigt':2}, background='None'):
    """ Simple multiband lineshape model generator with semantic parsing.

    :Parameters:
        peaks : dict | {'Voigt':2}
            Peak profile specified in a dictionary. All possible models see ``lmfit.models``.
        background : str | 'None'
            Background model name. All possible models see ``lmfit.models``.

    :Return:
        model : instance of ``pesfit.lineshape.MultipeakModel``
            Lineshape model created from the specified components.
    """

    bg_modname = background + 'Model'
    if bg_modname in existing_models.keys():
        bg_clsname = existing_models[bg_modname]
    
    # Currently only support a single type of lineshape for arbitrary number of peaks.
    for pk, pkcount in peaks.items():
        pk_modname = pk + 'Model'
        if pk_modname in existing_models.keys():
            pk_clsname = existing_models[pk_modname]
        
        try:
            model = ls.MultipeakModel(lineshape=pk_clsname, n=pkcount, background=bg_clsname(prefix='bg_'))
        except:
            model = ls.MultipeakModel(lineshape=pk_clsname, n=pkcount)

    return model


def random_varshift(fitres, model, params, shifts, yvals=None, xvals=None, parnames=[], verbose=True):
    """ Randomly and recursively apply a shift value to certain key variables to get a better fit. Execution of the function terminates when either (1) the fitting results are sufficiently good (measured by its chi-squared metric) or (2) the trials exhaust all choices of shift parameters.

    :Parameters:
        fitres : instance of ``lmfit.model.ModelResult``
            Current fitting result.
        model : instance of ``lmfit.model.Model`` or its subclass
            Lineshape model.
        params : instance of ``lmfit.parameter.Parameters``
            Lineshape model parameters.
        xvals, yvals : numpy array, numpy array | None, None
            Horizontal and vertical axis values for the lineshape fitting.
        parnames : list | []
            List of names of the parameters to update initial conditions.
        verbose : bool | True
            Option for printout of the chi-squared value.
    """

    # Check goodness-of-fit criterion
    if fitres.chisqr < 0.8:
        return fitres
    
    else:
        if verbose:
            print('csq = {}'.format(fitres.chisqr))
        
        idx = np.random.choice(range(len(shifts)), 1)[0]
        sft = shifts[idx]
        if parnames:
            pardict = dict((p, params[p].value+sft) for p in parnames)
            varsetter(params, pardict)
        
        newfit = model.fit(yvals, params, x=xvals)
        newshifts = np.delete(shifts, idx)
        
        return random_varshift(newfit, model, params, yvals, xvals, newshifts)


def varsetter(params, inits={}, ret=False):
    """ Variable setter for multiparameter fitting.
    
    :Parameters:
        params : ``lmfit.parameter.Parameter`` or other subclass of dict
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

            # Merge entries if inits are provided as a list of dictionaries.
            # Merging doesn't change the depth of the dictionary.
            if len(inits) > 1:
                inits = reduce(u.dictmerge, inits)
            
            dd = u.dict_depth(inits, level=0)
            
            if dd == 3:
                # Unpack the dictionary at the component level
                for kcomp, vcomp in inits.items():
                    # Unpack the dictionary at the parameter level
                    for kparam, vparam in vcomp.items():
                        params[kcomp+kparam].set(**vparam)
            
            elif dd == 2:
                # Unpack the dictionary at the parameter level
                for kparam, vparam in inits.items():
                    params[kparam].set(**vparam)
    
    if ret:
        return params


##########################
# Visualization routines #
##########################

def plot_fit_result(fitres, x, plot_components=True, downsamp=1, **kwds):
    """ Plot the fitting outcomes.

    :Parameters:
        fitres : instance of ``lmfit.model.ModelResult``
            Fitting result from the `lmfit` routine.
        x : numpy array
            Horizontal-axis values of the lineshape model.
        plot_components : bool | True
            Option to plot components of the multipeak lineshape.
        downsamp : int | 1
            Level of downsampling of the data (1 means no downsampling).
        **kwds : keyword arguments
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

    :Parameters:
        paths : numpy array
            Momentum diagram data.
        ksymbols : list of strings
            Symbols of the high-symmetry points.
        erange : list | []
            Bounds of the electron energy, [lower, upper].
        evals : numpy array | None
        path_inds : list | []
        koverline : bool | True
            Option to display momentum symbols with an overline.
        klines : bool | False
            Option to draw vertical lines at the specified high-symmetry points.
        ret : bool | False
            Option to return the graphical elements.
        **kwds : keyword arguments
    """
    
    fsize = kwds.pop('figsize', (10, 6))
    f, ax = plt.subplots(figsize=fsize)
    
    maxind = paths.shape[1]
    
    try:
        elo, ehi = erange
    except:
        elo, ehi = evals[0], evals[-1]
    plt.imshow(paths, cmap='Blues', aspect=9.3, extent=[0, maxind, elo, ehi], vmin=0, vmax=0.5)
    
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