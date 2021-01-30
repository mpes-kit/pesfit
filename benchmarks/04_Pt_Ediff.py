#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pesfit as pf
import time
from hdfio import dict_io as io
import argparse
import multiprocessing as mp
import scipy.io as sio

n_cpu = mp.cpu_count()

fdir = r'E:\Diffraction\20190816_meas2_Lineouts_av_sorted.mat'
diffpat = sio.loadmat(fdir)

npk = 10
lp_prefixes = ['lp'+str(i)+'_' for i in range(1, npk+1)]

npks = [2, 5, 8, 10]
specwidths = [120, 250, 350, 380]
ctvals = np.array([60, 90, 160, 200, 220, 250, 290, 310, 330, 340])
# ctvals = ctvals[:8]
centers = pf.fitter.init_generator(lpnames=lp_prefixes, parname='center',
                                   varkeys=['value', 'min', 'max', 'vary'],
                                  parvals=[[ctvals[i], ctvals[i]-30, ctvals[i]+30, True] for i in range(npk)])
# amplitudes = pf.fitter.init_generator(lpnames=lp_prefixes, parname='amplitude',
#                                     varkeys=['value', 'min', 'max', 'vary'],
#                                     parvals=[[0.6, 0, 3, True] for i in range(npk)])
# sigmas = pf.fitter.init_generator(lpnames=lp_prefixes, parname='sigma',
#                                 varkeys=['value', 'min', 'max', 'vary'],
#                                 parvals=[[20, 2, 150, True] for i in range(npk)])
# gammas = pf.fitter.init_generator(lpnames=lp_prefixes, parname='gamma',
#                                 varkeys=['value', 'min', 'max', 'vary'],
#                                 parvals=[[5, 0, 20, True] for i in range(npk)])

decay = pf.fitter.init_generator(lpnames=['bg_'], parname='decay',
                                varkeys=['value', 'min', 'vary'],
                                parvals=[[50, 1, True]])

vardict = centers + decay

dts_seq = []
dts_para = []

# for npk, sw in zip(npks, specwidths):
#     dat = np.moveaxis(diffpat['Im_an'], 2, 0)[:, :, 100:sw+100].reshape((225, sw))
#     dat -= dat.min(axis=1)[:, None]
#     ctvals = ctvals[:npk]
    
#     # Time-stamping for the sequential fit
#     kfit = pf.fitter.PatchFitter(peaks={'Voigt':npk}, background='Exponential', xdata=np.arange(sw), ydata=dat)
#     kfit.set_inits(inits_dict=vardict, band_inits=None, offset=0)
#     t_start = time.perf_counter()
#     kfit.sequential_fit(jitter_init=False, varkeys=[], nspec=225, include_vary=False, pbar=True)
#     t_end = time.perf_counter()

#     dt = t_end - t_start
#     print(dt)
#     dts_seq.append(dt)

chunks = [50, 50, 30, 3]
for npk, sw, cs in zip(npks[3:], specwidths[3:], chunks[3:]):
    dat = np.moveaxis(diffpat['Im_an'], 2, 0)[:, :, 100:sw+100].reshape((225, sw))
    dat -= dat.min(axis=1)[:, None]
    ctvals = ctvals[:npk]

    # Time-stamping for the distributed fit
    if __name__ == '__main__':
        dfit = pf.fitter.DistributedFitter(peaks={'Voigt':npk}, background='Exponential', xdata=np.arange(sw), ydata=dat, nfitter=225)
        dfit.set_inits(inits_dict=vardict, band_inits=None, offset=0)
        t_start = time.perf_counter()
        dfit.parallel_fit(jitter_init=False, shifts=np.arange(-0.08, 0.09, 0.01),
                        backend='async', include_vary=False, chunksize=cs, pbar=True)
        t_end = time.perf_counter()
        
        dt = t_end - t_start
        print(dt)
        dts_para.append(dt)