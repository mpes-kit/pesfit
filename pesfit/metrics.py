#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


class GroupMetrics(object):
    """ Group-wise evaluation metrics calculator.
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

    def instability(self, result, ground_truth):
        """ Calculate reconstruction instability.
        """
        
        diff = result - ground_truth
        instab = np.var(diff)
        return instab
        
    def group_instability(self, ground_truth):
        """ Calculate the group-wise reconstruction instability.
        """
        
        instabs = list(map(lambda r: self.instability(r, ground_truth), self.res))
        self.group_instab = np.array(instabs)