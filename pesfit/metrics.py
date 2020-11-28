#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


class GroupRMSE(object):
    """ Group-wise root-mean-square error calculator.
    """
    
    def __init__(self, fres, nband):
        self.fres = fres
        self.nband = nband
        
    @property
    def nfres(self):
        return len(self.fres)
        
    def load_data(self, file, varname, shape):
        """ Load a set of reconstruction data.
        """
        
        res = []
        for i in range(1, self.nband+1):
            fitres = pd.read_hdf(file)
            res.append(fitres['lp{}_{}'.format(i,varname)].values.reshape(shape))
        
        return np.array(res)
        
    def load_all_data(self, varname, shape):
        """ Load all reconstruction data.
        """
        
        self.res = list(map(lambda f: self.load_data(f, varname, shape), self.fres))
    
    def rmse(self, result, ground_truth):
        """ Calculate root-mean-square error.
        """
        
        rmserr = np.linalg.norm(result - ground_truth)
        return rmserr
    
    def group_rmse(self, ground_truth):
        """ Calculate group-wise root-mean-square error.
        """
                        
        rmserrs = list(map(lambda r: self.rmse(r, ground_truth), self.res))
        self.group_rmserr = np.array(rmserrs)