#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from functools import reduce
from scipy.interpolate import RegularGridInterpolator as RGI
from tqdm import notebook as nbk
from tqdm import tqdm as tqdm_classic
import cloudpickle as cpk

def riffle(*arr):
    """
    Interleave multiple arrays of the same number of elements.

    **Parameter**

    *arr: array
        A number of arrays

    **Return**

    riffarr: 1D array
        An array with interleaving elements from each input array.
    """

    arr = (map(np.ravel, arr))
    arrlen = np.array(map(len, arr))

    try:
        unique_length = np.unique(arrlen).item()
        riffarr = np.vstack(arr).reshape((-1,), order='F')
        return riffarr
    except:
        raise ValueError('Input arrays need to have the same number of elements!')


def dictmerge(D, others):
    """
    Merge a dictionary with other dictionaries
 
    **Parameters**

    D: dict
        Main dictionary.
    others: list/tuple/dict
        Other dictionary or composite dictionarized elements.

    **Return**

    D: dict
        Merged dictionary.
    """

    if type(others) in (list, tuple): # Merge D with a list or tuple of dictionaries
        for oth in others:
            D = {**D, **oth}

    elif type(others) == dict: # Merge D with a single dictionary
        D = {**D, **others}

    return D


def dict_depth(dic, level=0): 
    """ Check the depth of a dictionary.
    
    **Parameters**

    dic: dict
        Instance of dictionary object or its subclass.
    level: int | 0
        Starting level of the depth counting.
    """
      
    if not isinstance(dic, dict) or not dic: 
        return level 
    return max(dict_depth(dic[key], level+1) for key in dic)


def df_collect(params, extra_params=None, currdf=None):
    """ Collect parameters from fitting outcome.
    
    **Parameters**\n    
    params: instance of ``lmfit.parameter.Parameters``.
        Collection of fitting parameters.
    extra_params: dict | None
        Extra parameters supplied as a dictionary
    currdf: instance of ``pandas.DataFrame`` | None
        An existing dataframe to append new data to.
        
    **Return**\n    
    df: instance of ``pandas.DataFrame``
        Fitting parameters reformatted as a dataframe (keeps only names and values).
    """

    # Convert parameters into a dataframe through a dictionary
    dfdict = {param.name:param.value for _, param in params.items()}
    if extra_params is not None:
        dfdict = dictmerge(dfdict, extra_params)
    df = pd.DataFrame.from_dict(dfdict, orient='index').T
    
    if currdf is not None:
        df = pd.concat([df, currdf], ignore_index=True, sort=True)
        
    return df


def partial_flatten(arr, axis):
    """ Partially flatten a multidimensional array.
    
    **Parameters**\n
    arr: numpy array
        Multidimensional array for partial flattening.
    axis: list/tuple
        Axes to flatten.
    
    **Return**\n
    arr_pf: numpy array
        Partially flattened array.
    """
    
    if type(axis) != list:
        axis = list(axis)
    nax = len(axis)
    axmin = min(axis)
    
    if nax < 2:
        raise Exception('The number of axes to flatten is at least 2!')
    else:
        shape = np.array(arr.shape, dtype='int') # Original shape of array
        flatsize = np.prod(shape[axis]) # Size of the flattened dimensions
        # Shape after partial flattening
        shape_flattened = np.insert(np.delete(shape, axis), axmin, flatsize)
        arr_pf = arr.reshape(tuple(shape_flattened))
        
        return arr_pf


def tqdmenv(env):
    """ Choose tqdm progress bar executing environment.
    
    **Parameter**\n
    env: str
        Name of the environment, 'classic' for ordinary environment,
        'notebook' for Jupyter notebook.
    """

    if env == 'classic':
        tqdm = tqdm_classic
    elif env == 'notebook':
        tqdm = nbk.tqdm

    return tqdm


def argpick(cliargs, argkey, defaults):
    """ Command-line input argument picker.

    **Parameters**\n
    cliargs: dict
        Command-line inputs
    argkey: str
        Argument key.
    defaults: any
        Default value for the argument if no input is found.
    """

    try:
        argval = getattr(cliargs, argkey)
        if argval is not None:
            a = argval
    except:
        a = defaults[argkey.upper()]
    
    return a


def intnz(num):
    """ Output an integer at least larger than 1.
    """

    num = abs(num)
    if num < 1:
        return 1
    else:
        return np.rint(num).astype('int')


def grid_indices(x, y, dtyp='float', ordering='rc', flatten=True):
    """ Construct grid indices.

    **Parameters**\n
    x, y: 1D array, 1D array
        Single-axis x and y coordinates.
    dtyp: str | 'float'
        Data type of the generated grid indices.
    ordering: str | 'rc'
        Ordering of the indices ('rc' for row-column ordering, 'xy' for x-y ordering).
    flatten: bool | True
        Option to flatten the grid indices.
    """
    
    nx, ny = len(x), len(y)

    if ordering == 'rc':
        grid = np.empty((ny, nx, 2), dtype=dtyp)
        grid[...,0] = y[:, None]
        grid[...,1] = x

    elif ordering == 'xy':
        grid = np.empty((x, y, 2), dtype=dtyp)
        grid[...,0] = x[:, None]
        grid[...,1] = y

    if flatten:
        grid = grid.reshape((nx*ny, 2))
        
    return grid


def grid_resample(data, coords_axes, coords_new=None, grid_scale=None, zoom_scale=None, interpolator=RGI, ret='scaled', **kwds):
    """ Resample data to new resolution.

    **Parameters**\n
    data: numpy.ndarray
        Data for resampling.
    coord_axes: list/tuple
        Current coordinates matching the dimensions of the input data
    coords_new: list/tuple | None
        New coordinates to resample the data with.
    grid_scale: list/tuple | None
        Scaling factors along every axis.
    zoom_scale: numeric | None
        Zooming-in factor.
    interpolator: func | ``scipy.interpolate.RegularGridInterpolator``
        Interpolation function.
    **kwds: keyword arguments
        Additional keyword arguments for the interpolation function.
    """
    
    nshape = list(map(len, coords_axes))
    interp = interpolator(coords_axes, data, **kwds)
    
    if grid_scale is not None:
        coords_scaled = []
        for ic, coo in enumerate(coords_axes):
            # If scaling factor is any real number, resample the axes coordinates.
            nax = len(coords_axes[ic])
            nstep_sc = int(np.rint(nax*grid_scale[ic]))
            coo_sc = np.linspace(coo[0], coo[-1], nstep_sc, endpoint=True)
            coords_scaled.append(coo_sc)
        coords_scaled = coords_scaled[::-1]
        nshape = list(map(len, coords_scaled))
        coords_new = grid_indices(*coords_scaled)
    
    elif (zoom_scale is not None) and (zoom_scale != 0):
        if (zoom_scale < -1) or (zoom_scale > 1):
            raise ValueError('Cannot interpolate beyond boundaries of original data!')
        else:
            coords_zoomed = [coo*zoom_scale for coo in coords_axes]
            coords_new = grid_indices(*coords_zoomed)
    
    elif coords_new is None:
        raise ValueError('Requires to specify coords_new or scale arguments.')
        
    resdata = interp(coords_new).reshape(nshape[::-1])

    if ret == 'scaled':
        return resdata
    elif ret == 'all':
        return resdata, coords_new


def merge_nested_dict(dicts):
    """ Merge nested dictionaries.

    **Parameter**\n
    dicts: list/tuple
        Collection of dictionaries
    """
    
    keys = [i.keys() for i in dicts]
    unique_keys = list(set([list(i)[0] for i in keys]))
    dict_merged = []
    
    for uk in unique_keys:
        # Look for duplicated keys
        repeats = [uk in k for k in keys]
        loc = np.where(repeats)

        if np.sum(repeats) == 1:
            dict_merged.append(np.array(dicts)[loc][0])
        elif np.sum(repeats) > 1:
            # Extract dictionaries with a shared key, uk
            shared_dicts = np.array(dicts)[loc]
            combined_vals = reduce(lambda x,y: {**x, **y}, [sd[uk] for sd in shared_dicts])
            combined_dict = {uk: combined_vals}
            dict_merged.append(combined_dict)
            
    return dict_merged


def pickle_obj(fname, obj):
    """ Pickle object.
    """
    
    f = open(fname, 'wb')
    cpk.dump(obj, f)
    f.close()


def load_pickle(fname):
    """ Load pickled object.
    """
    
    f = open(fname, 'rb')
    content = cpk.load(f)
    f.close()

    return content


def randomize(data, axis=0, seed=None):
    """ Randomize data along one axis.
    """
    
    if seed is not None:
        np.random.seed(seed)
    
    # Generate shuffled indices
    nchoice = data.shape(axis)
    choices = list(range(nchoice))
    np.random.shuffle(choices)
    
    data_rand = np.moveaxis(data, axis, 0)
    data_rand = data_rand[choices, ...]
    data_rand = np.moveaxis(data, 0, axis)
    
    return data_rand, choices


def index_gen(x):
    """Index generator.
    """ 
    
    indices = np.arange(*x, dtype='int').tolist()
    inditer = it.product(indices, indices)
    
    return inditer


def shape_gen(scale_vector):
    """ Generate a series of vector-related quantities.
    """

    length = len(range(*scale_vector))
    shape = (length, length)
    indices = index_gen(scale_vector)

    return length, shape, indices