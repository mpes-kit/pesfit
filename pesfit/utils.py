#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


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