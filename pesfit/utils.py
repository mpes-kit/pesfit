#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from tqdm import notebook as nbk
from tqdm import tqdm as tqdm_classic

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


def df_collect(params, currdf=None):
    """ Collect parameters from fitting outcome.
    
    **Parameters**\n    
    params: instance of ``lmfit.parameter.Parameters``.
        Collection of fitting parameters.
    currdf: instance of ``pandas.DataFrame`` | None
        An existing dataframe to append new data to.
        
    **Return**\n    
    df: instance of ``pandas.DataFrame``
        Fitting parameters reformatted as a dataframe (keeps only names and values).
    """

    dfdict = {param.name:param.value for _, param in params.items()}  
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