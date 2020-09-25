#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import lineshape as ls, utils as u
import numpy as np
import pandas as pd
from functools import reduce
from lmfit import Minimizer, fit_report
import inspect
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import hdfio.dict_io as io

import yaml
yaml.warnings({'YAMLLoadWarning': False})


existing_models = dict(inspect.getmembers(ls.lmm, inspect.isclass))

####################
# Fitting routines #
####################

def init_generator(params=None, parname='center', varkeys=['value'], **kwds):
    """ Dictionary generator for initial fitting conditions.

    **Parameters**\n    
    params: instance of ``lmfit.parameter.Parameters``
        Existing model parameters.
    parname: str | 'center'
        Name of the parameter.
    varkeys: list/tuple | ['value']
        Keyword specified for the parameter ('value', 'min', 'max', 'vary').
    **kwds: keyword arguments
        lpnames: list/tuple | None
            Collection of namestrings (or prefixes) for lineshapes.
        parvals: list/tuple | None
            Collection of values for parameters.
    """

    if params is None:
        lpnames = kwds.pop('lpnames', None)
    else:
        lpnames = params.keys()

    parvals = kwds.pop('parvals', None)

    if parvals is not None:
        inits = []
        # As an example, dict(value=1) is equivalent to {'value':1}.
        # inits = dict((pn, {varkey:pv}) for pn, pv in zip(parnames, parvals))
        for ln, pvs in zip(lpnames, parvals):
            inits.append({ln: {parname: dict((vk, pv) for vk, pv in zip(varkeys, pvs))}})
    
        return inits


def model_generator(peaks={'Voigt':2}, background='None', **kwds):
    """ Simple multiband lineshape model generator with semantic parsing.

    **Parameters**\n
    peaks: dict | {'Voigt':2}
        Peak profile specified in a dictionary. All possible models see ``lmfit.models``.
    background: str | 'None'
        Background model name. All possible models see ``lmfit.models``.
    **kwds: keyword arguments
        Additional keyword arguments for ``pesfit.lineshape.MultipeakModel`` class.

    **Return**\n
    model: instance of ``pesfit.lineshape.MultipeakModel``
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
            model = ls.MultipeakModel(lineshape=pk_clsname, n=pkcount, background=bg_clsname(prefix='bg_'), **kwds)
        except:
            model = ls.MultipeakModel(lineshape=pk_clsname, n=pkcount, **kwds)

    return model


def random_varshift(fitres, model, params, shifts, yvals=None, xvals=None, parnames=[], verbose=True, **kwds):
    """ Recursively apply a random shift value to certain key variables to get a better fit. Execution of the function terminates when either (1) the fitting results are sufficiently good (measured by its chi-squared metric) or (2) the trials exhaust all choices of shift parameters.

    **Parameters**\n
    fitres: instance of ``lmfit.model.ModelResult``
        Current fitting result.
    model: instance of ``lmfit.model.Model`` or ``pesfit.lineshape.MultipeakModel``
        Lineshape model.
    params: instance of ``lmfit.parameter.Parameters``
        Lineshape model parameters.
    xvals, yvals: numpy array, numpy array | None, None
        Horizontal and vertical axis values for the lineshape fitting.
    parnames: list | []
        List of names of the parameters to update initial conditions.
    verbose: bool | True
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
        
        newfit = model.fit(yvals, params, x=xvals, **kwds)
        newshifts = np.delete(shifts, idx)
        
        return random_varshift(newfit, model, params, newshifts, yvals, xvals, parnames, verbose, **kwds)


def varsetter(params, inits={}, ret=False):
    """ Function to set the parameter constrains in multiparameter fitting.
    
    **Parameters**\n
    params: ``lmfit.parameter.Parameter`` or other subclass of dict
        Parameter dictionary.
    init: dict | {}
        Initialization value dictionary.
    ret: bool | False
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


def pointwise_fitting(xdata, ydata, model=None, peaks=None, background='None', params=None, inits=None, ynorm=True, method='leastsq', jitter_init=False, ret='result', modelkwds={}, **kwds):
    """ Pointwise fitting of a multiband line profile.

    **Parameters**\n
    xdata, ydata: 1D array, 1D array
        x and y axis data.
    model: instance of ``lmfit.model.Model`` or ``pesfit.lineshape.MultipeakModel`` | None
        A lineshape model for the fitting task.
    peaks, background: dict, str | None, 'None'
        Details see identical arguments for ``pesfit.fitter.model_generator()``
    params: instance of ``lmfit.paramter.Parameters`` | None
        Parameters of the model.
    inits: dict/list | None
        Fitting initial values and constraints (format see ``pesfit.fitter.varsetter()``).
    ynorm: bool | True
        Option to normalize each trace by its maximum before fitting.
    method: str | 'leastsq'
        Optimization method of choice (complete list see https://lmfit.github.io/lmfit-py/fitting.html).
    jitter_init: bool | False
        Option to introduct random perturbations (jittering) to the peak position in fitting. The values of jittering is supplied in ``shifts``.
    ret: str | 'result'
        Specification of return values.\n
        ``'result'``: returns the fitting result\n
        ``'all'``: returns the fitting result and evaluated lineshape components.
    **kwds: keyword arguments
        shifts: list/tuple/numpy array | np.arange(0.1, 1.1, 0.1)
            The choices of random shifts to apply to the peak position initialization (energy in eV unit). The shifts are only operational when ``jitter_init=True``.
        other arguments
            See details in ``pesfit.fitter.random_varshift()``.
    """
    
    # Initialize model
    if model is None:
        mod = model_generator(peaks=peaks, background=background, **modelkwds)
    else:
        mod = model
        if model is None:
            raise ValueError('The fitting requires a model to execute!')
    
    # Initialize parameters
    if params is None:
        pars = mod.make_params()
    else:
        pars = params

    sfts = kwds.pop('shifts', np.arange(0.1, 1.1, 0.1))
    
    # Initialization for each pointwise fitting
    if inits is not None:
        varsetter(pars, inits, ret=False)
    
    # Intensity normalization
    if ynorm:
        ydata /= ydata.max()
    
    fit_result = mod.fit(ydata, pars, x=xdata, **kwds)
    
    # Apply random shifts to initialization to find a better fit
    if jitter_init:
        fit_result = random_varshift(fit_result, model=mod, params=pars, yvals=ydata, xvals=xdata, shifts=sfts, method=method, **kwds)
    
    if ret == 'result':
        return fit_result
    elif ret == 'all':
        fit_comps = fit_result.eval_components(x=xdata)
        return fit_result, fit_comps


class PatchFitter(object):
    """ Class for fitting a patch of photoemission band mapping data.

    **Parameters**\n
    xdata: 1D array
        Energy coordinates for photoemission line spectrum fitting.
    ydata: numpy array
        Photoemission spectral data for fitting (2D or 3D).
    model: instance of ``lmfit.model.Model`` or ``pesfit.lineshape.MultipeakModel``
        Existing universal lineshape model for fitting (all spectra).
    peaks: dict | {'Voigt':2}
        Specification of constituent single-peak lineshape model.
    background: str | 'None'
        Specification of approximation function for approximating the signal background.
    """
    
    def __init__(self, xdata=None, ydata=None, model=None, modelkwds={}, **kwds):
        """ Initialize class.
        """
        
        self.xdata = xdata
        self.ydata = ydata

        if self.ydata is not None:
            self.patch_shape = self.ydata.shape
            self.patch_r, self.patch_c, self.elen = self.patch_shape
        
        if model is None:
            peaks = kwds.pop('peaks', {'Voigt':2})
            bg = kwds.pop('background', 'None')
            self.model = model_generator(peaks=peaks, background=bg, **modelkwds)
        else:
            self.model = model
        
        self.prefixes = self.model.prefixes
        self.fitres = None
    
    def load(self, attrname='', fdir='', fname='', ftype='h5', **kwds):
        """ Generic load function including attribute assignment.

        **Parameters**\n
        attrname: str | ''
            Attribute name to be assigned to.
        fdir, fname: str, str | '', ''
            Directory and name for file to load. The ull path is the string combination of the two).
        ftype: str | 'h5'
            File type to load.
        **kwds: keywords argument
            Additional arguments for ``pesfit.fitter.load_file()``.
        """
        
        cont = load_file(fdir=fdir, fname=fname, ftype=ftype, outtype='vals', **kwds)
        if len(cont) * len(attrname) > 0:
            setattr(self, attrname, cont[0])
    
    def load_spec_data(self, **kwds):
        """ Load line spectrum data patch as ``self.ydata``. Executes ``self.load()`` with ``attrname=ydata``.
        """
        
        self.load(attrname='ydata', **kwds)

        if self.ydata is not None:
            self.patch_shape = self.ydata.shape
            self.patch_r, self.patch_c, self.elen = self.patch_shape
    
    def load_band_inits(self, **kwds):
        """ Load band energy initialization as ``self.band_inits``. Executes ``self.load()`` with ``attrname=band_inits``.
        """
        
        self.load(attrname='band_inits', **kwds)

    def load_fitting(self, fdir=r'./', fname='', ftype='h5', **kwds):
        """ Load fitting outcome (for visualization).
        """

        path = fdir + fname
        if ftype == 'h5':
            self.df_fit = pd.read_hdf(path, **kwds)

    def set_inits(self, inits_dict=None, xdata=None, band_inits=None, drange=None):
        """ Set the persistent part of initialization parameters.

        **Parameters**\n
        inits_dict: dict | None
            Initialization parameters and constraints persistent throughout the fitting process.
        xdata: 1D array | None
            Calibrated energies for the energy axis
        band_inits: numpy array | None
            Initialization for the band energy values.
        drange: slice object | None
            Slice object corresponding to the energy range to select (None or slice(None, None) means selecting all values).
        """
        
        if inits_dict is not None:
            self.inits_persist = inits_dict
        else:
            self.inits_persist = {}

        self.drange = drange
        if xdata is None:
            self.xvals = self.xdata[drange]
        else:
            self.xvals = xdata
        self.ydata2D = u.partial_flatten(self.ydata[...,self.drange], axis=(0, 1))
        
        try:
            if band_inits is not None:
                self.band_inits = band_inits
            self.band_inits2D = u.partial_flatten(self.band_inits, axis=(1, 2))
        except:
            raise Exception('Cannot reshape the initialization!')
    
    @property
    def nspec(self):
        """ Total number of line spectra.
        """
        
        return self.patch_r * self.patch_c
    
    def sequential_fit(self, varkeys=['value', 'vary'], other_initvals=[True], pbar=False, pbenv='notebook', **kwds):
        """ Sequential line fitting of the data patch.

        **Parameters**\n
        varkeys: list/tuple | ['value', 'vary']
            Collection of parameter keys to set ('value', 'min', 'max', 'vary').
        other_initvals: list/tuple | [True]
            Initialization values for spectrum-dependent variables. Supply a list/tuple of size 1 or the same size as the number of spectra.
        pbar: bool | False
            Option to show a progress bar.
        pbenv: str | 'notebook'
            Progress bar environment ('notebook' for Jupyter notebook or 'classic' for command line).
        **kwds: keywords arguments
            nspec: int | ``self.nspec``
                Number of spectra for fitting.
            additional arguments:
                See ``pesfit.fitter.pointwise_fitting()``.
        """
        
        self.pars = self.model.make_params()
        # Setting the initialization parameters and constraints persistent throughout the fitting process
        try:
            varsetter(self.pars, self.inits_persist, ret=False)
        except:
            pass
        
        tqdm = u.tqdmenv(pbenv)

        # Fitting parameters for all line spectra in the data patch
        self.df_fit = pd.DataFrame(columns=self.pars.keys())
        # Number of spectrum to fit (for diagnostics)
        nspec = kwds.pop('nspec', self.nspec)
        
        # Construct the variable initialization parameters for all spectra
        # TODO: a better handling of nested dictionary generation
        varyvals = self.band_inits2D[:self.model.nlp, :nspec]
        if other_initvals is not None:
            other_size = np.asarray(other_initvals).size
            if (other_size != nspec) or ((other_size == 1) and (nspec == 1)):
                try:
                    othervals = np.ones((self.model.nlp, nspec))*other_initvals
                    inits_vary_vals = np.moveaxis(np.stack((varyvals, othervals)), 0, 1)
                except:
                    raise Exception('other_initvals has incorrect shape!')
            else:
                raise Exception('other_initvals has incorrect shape!')

        # Sequentially fit every line spectrum in the data patch
        for n in tqdm(range(nspec), disable=not(pbar)):

            # Setting the initialization parameters that vary for every line spectrum
            other_inits = inits_vary_vals[..., n]
            self.inits_vary = init_generator(parname='center', varkeys=varkeys, lpnames=self.prefixes, parvals=other_inits)
            varsetter(self.pars, self.inits_vary, ret=False)
            
            y = self.ydata2D[n, :] # Current energy distribution curve
            # Line fitting with all the initial guesses supplied
            out = pointwise_fitting(self.xvals, y, model=self.model, params=self.pars, ynorm=True, **kwds)

            dfout = u.df_collect(out.params, currdf=self.df_fit)
            self.df_fit = dfout
    
    # def parallel_fit(self, varkeys=['value', 'vary'], other_initvals=[True], **kwds):
    #     """ Parallel line fitting of the data patch.
    #     """

    #     nspec = kwds.pop('nspec', self.nspec)

    #     self.out = parallel_fitting(self.xvals, self.ydata2D, self.model, self.inits_persist, self.band_inits2D, nspec, self.prefixes,varkeys, other_initvals, **kwds)
    
    def save_data(self, fdir=r'./', fname='', ftype='h5', keyname='fitres', orient='dict', **kwds):
        """ Save the fitting outcome to a file.
        """
        
        path = fdir + fname
        if ftype == 'h5':
            self.df_fit.to_hdf(path, key=keyname, **kwds)
        elif ftype == 'json':
            self.df_fit.to_json(path, **kwds)
        elif ftype == 'mat':
            import scipy.io as scio
            outdict = self.df_fit.to_dict(orient=orient)
            scio.savemat(path, outdict, **kwds)
        else:
            raise NotImplementedError

    def fit_to_dict(self, shape, orient='dict'):
        """ Restructure the fitting outcome to dictionary.
        """

        outdict = self.df_fit.to_dict(orient=orient)
        for k, v in outdict:
            outdict[k] = v.reshape(shape)
        
        return outdict
    
    def view(self, fit_result=None, fit_df=None, xaxis=None, **kwds):
        """ Visualize selected fitting results.
        """
        
        if xaxis is None:
            xvals = self.xvals
        
        if fit_result is None:
            fres = self.fitres
        
        plot = plot_fit_result(fres, xvals, **kwds)
        
        return plot


import concurrent.futures as ccf
import multiprocessing as mp
import dask as dk

class ParallelPatchFitter(object):
    """ Parallelized fitting of line spectra in a photoemission data patch.
    """

    def __init__(self, xdata=None, ydata=None, model=None, modelkwds={}, **kwds):

        self.nspec = kwds.pop('nspec', 1)
        self.fitters = [PatchFitter(xdata, ydata, mode=model, modelkwds=modelkwds, **kwds) for _ in range(self.nspec)]
        self.models = [self.fitters[n].model for n in range(self.nspec)]
        self.prefixes = self.fitters[0].prefixes
        self.xdata = xdata
        self.ydata = ydata

    def set_inits(self, inits_dict=None, xdata=None, band_inits=None, drange=None):
        """ Set initialization for all constituent fitters.
        """
        
        for i in range(self.nspec):
            self.fitters[i].set_inits(inits_dict=inits_dict, band_inits=band_inits, drange=drange)
        if xdata is None:
            self.xvals = self.xdata[drange]
        else:
            self.xvals = xdata
        self.model = self.fitters[0].model
        self.ydata2D = self.fitters[0].ydata2D
        self.inits_persist = self.fitters[0].inits_persist
        self.band_inits2D = self.fitters[0].band_inits2D

    def parallel_fit(self, varkeys=['value', 'vary'], other_initvals=[True], compute_kwds={}, scheduler='processes', backend='concurrent', ret=False, **kwds):
        """ Parallel line fitting of the data patch.
        """

        nspec = kwds.pop('nspec', self.nspec)
        self.pars = [md.make_params() for md in self.models]
        # Setting the initialization parameters and constraints persistent throughout the fitting process
        try:
            for p in self.pars:
                varsetter(p, self.inits_persist, ret=False)
        except:
            pass

        # Fitting parameters for all line spectra in the data patch
        df_fit = pd.DataFrame(columns=self.pars[0].keys())

        varyvals = self.band_inits2D[:self.model.nlp, :nspec]
        if other_initvals is not None:
            other_size = np.asarray(other_initvals).size
            if (other_size != nspec) or ((other_size == 1) and (nspec == 1)):
                try:
                    othervals = np.ones((self.model.nlp, nspec))*other_initvals
                    self.other_inits = np.moveaxis(np.stack((varyvals, othervals)), 0, 1)
                except:
                    raise Exception('other_initvals has incorrect shape!')
            else:
                raise Exception('other_initvals has incorrect shape!')
            
        # Carry out parallelized fitting
        process_args = [(self.models[n], self.pars[n], self.xvals, self.ydata2D[n, :], n, self.prefixes,
        varkeys, self.other_inits[...,n]) for n in range(nspec)]
        
        if backend == 'dask':
            fit_tasks = [dk.delayed(self._single_fit)(*args) for args in process_args]
            fit_results = dk.compute(*fit_tasks, scheduler=scheduler, **compute_kwds)

        elif backend == 'concurrent':
            with ccf.ProcessPoolExecutor() as executor:
                fit_results = executor.map(self._single_fit, *zip(*process_args))

        elif backend == 'multiprocessing':
            nproc = kwds.pop('nproc', mp.cpu_count())
            pool = mp.Pool(processes=nproc)
            fit_results = pool.starmap(self._single_fit, process_args)
            pool.close()

        # Collect the results
        for fres in fit_results:
            dfout = u.df_collect(fres.params, currdf=df_fit)
            df_fit = dfout
            # print_fit_result(fres.params, printout=True)

        self.df_fit = df_fit

        if ret:
            return df_fit
    
    # @classmethod
    def _single_fit(self, model, pars, xvals, yspec, n, prefixes, varkeys, others, **kwds):
        """ Fit a single line spectrum with custom initializaton.
        """
        
        # Setting the initialization parameters that vary for every line spectrum
        inits_vary = init_generator(parname='center', varkeys=varkeys, lpnames=prefixes, parvals=others)
        varsetter(pars, inits_vary, ret=False)
        
        # Line fitting with all the initial guesses supplied
        out_single = pointwise_fitting(xvals, yspec, model=model, params=pars, ynorm=True, **kwds)

        return out_single

    def save_data(self, fdir=r'./', fname='', ftype='h5', keyname='fitres', orient='dict', **kwds):
        """ Save the fitting outcome to a file.
        """
        
        path = fdir + fname
        if ftype == 'h5':
            self.df_fit.to_hdf(path, key=keyname, **kwds)
        elif ftype == 'json':
            self.df_fit.to_json(path, **kwds)
        elif ftype == 'mat':
            import scipy.io as scio
            outdict = self.df_fit.to_dict(orient=orient)
            scio.savemat(path, outdict, **kwds)
        else:
            raise NotImplementedError

if __name__ == '__main__':
    pass


def load_file(fdir=r'./', fname='', ftype='h5', parts=None, **kwds):
    """ Load whole file or parts of the file.
    """
    
    path = fdir + fname
    if ftype == 'h5':
        if parts is None:
            content = io.h5_to_dict(path, **kwds)
        else:
            content = io.loadH5Parts(path, parts, **kwds)
    
    else:
        raise NotImplementedError
        
    return content


def print_fit_result(params, printout=False, fpath='', mode='a', **kwds):
    """ Pretty-print the fitting outcome.
    """

    fr = fit_report(params, **kwds)
    if printout:
        
        if fpath:
            with open(fpath, mode) as f:
                print(fr, file=f)
                print('\n')
        else:
            print(fr)

    return


##########################
# Visualization routines #
##########################

def plot_fit_result(fitres, x, plot_components=True, downsamp=1, ret=False, **kwds):
    """ Plot the fitting outcomes.

    **Parameters**\n
    fitres: instance of ``lmfit.model.ModelResult``
        Fitting result from the `lmfit` routine.
    x: numpy array
        Horizontal-axis values of the lineshape model.
    plot_components: bool | True
        Option to plot components of the multipeak lineshape.
    downsamp: int | 1
        Level of downsampling of the data (1 means no downsampling).
    **kwds: keyword arguments
        figsize: list/tuple | [8, 5]
            Default size of the figure.
    """
    
    figsz = kwds.pop('figsize', (8, 5))
    
    f, ax = plt.subplots(figsize=figsz)
    comps = fitres.eval_components(x=x)
    
    # Plot the spectral components
    if plot_components == True:
        for k, v in comps.items():
            ax.plot(x, v, '-', label=k[:-1])
    
    ax.plot(x, fitres.best_fit, '-r')
    ax.plot(x[::downsamp], fitres.data[::downsamp], '.k')

    if ret:
        return f, ax


def plot_bandpath(paths, ksymbols, erange=[], evals=None, path_inds=[], koverline=True, klines=False, ret=False, **kwds):
    """ Plot momentum-energy map from a segment of the band mapping data.

    **Parameters**\n
    paths: numpy array
        Momentum diagram data.
    ksymbols: list of strings
        Symbols of the high-symmetry points.
    erange: list | []
        Bounds of the electron energy, [lower, upper].
    evals: numpy array | None
        Energy values.
    path_inds: list | []
        Locations of the high-symmetry points along the momentum direction.
    koverline: bool | True
        Option to display momentum symbols with an overline.
    klines: bool | False
        Option to draw vertical lines at the specified high-symmetry points.
    ret: bool | False
        Option to return the graphical elements.
    **kwds: keyword arguments
        figsize: list/tuple | [10, 6]
            Default size of the figure.
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