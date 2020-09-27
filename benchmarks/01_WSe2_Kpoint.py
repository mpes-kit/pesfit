#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pesfit as pf
import time
from hdfio import dict_io as io
import argparse

# Definitions of command line interaction
parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('nband', metavar='nb', nargs='?', type=int, help='integer between 1 and 14')
parser.add_argument('timecount', metavar='t', nargs='?', type=bool, help='whether to include time profiling')
parser.add_argument('operation', metavar='op', nargs='?', type=str, help='what computing method to run the benchmark program with')
parser.add_argument('persistent_init', metavar='pi', nargs='?', type=bool, help='initialization include persistent settings')
parser.add_argument('varying_init', metavar='vi', nargs='?', type=str, help='initialization including varying settings')
parser.add_argument('jitter_init', metavar='ji', nargs='?', type=bool, help='add jitter to initialization for better fits')
parser.add_argument('preproc', metavar='pp', nargs='?', type=str, help='the stage of preprocessing used for fitting')
parser.set_defaults(nband=2, timecount=True, operation='sequential', persistent_init=True, varying_init='recon', jitter_init=False, preproc='symmetrized')
cli_args = parser.parse_args()

# Sequential fitting of photoemission data patch around the K point of WSe2
## Option to introduce persistent initial conditions
PERSISTENT_INIT = cli_args.persistent_init
## Number of bands to fit
NBAND = cli_args.nband
if NBAND > 14 or NBAND < 1:
    raise ValueError('The number of bands to reconstruct is within [1, 14] for WSe2.')
## Option to enable code profiling
TIMECOUNT = cli_args.timecount
## Option for computing method ('sequential' or 'parallel')
OPERATION = cli_args.operation
## Specification of spectrum-dependent initial conditions ('theory' or 'recon')
VARYING_INIT = cli_args.varying_init
## The preprocessing needed before fitting ('symmetrized', 'mclahe', 'mclahe_smooth')
PREPROC = cli_args.preproc
## Option to apply jittering to initializations to obtain better fitting results
JITTER_INIT = cli_args.jitter_init
# print(cli_args)

# Photoemission band mapping data
data_dir = r'../data/WSe2'
pes_fname = r'/pes/kpoint/kpoint_symmetrized.h5'
pes_path = data_dir + pes_fname
pes_data = io.h5_to_dict(pes_path)

if VARYING_INIT == 'theory':
    # Theoretical calculations interpolated to the same momentum grid (as one type of initialization)
    theo_fname = r'/theory/kpoint/kpoint_LDA.h5'
    theo_path = data_dir + theo_fname
    theo_data = io.h5_to_dict(theo_path)['bands']
    inits_vary = theo_data

elif VARYING_INIT == 'recon':
    # Reconstructed photoemission band dispersion (as another type of initialization)
    recon_fname = r'/recon/kpoint/kpoint_LDA_recon.h5'
    recon_path = data_dir + recon_fname
    recon_data = io.h5_to_dict(recon_path)['recon']
    inits_vary = recon_data

# Setting initial conditions persistent throughout the fitting. These fixed constraints are tested for fitting
# the band dispersion nearby the K point of WSe2 and are required to make the fitting relatively stable!
if PERSISTENT_INIT:
    vardict = {}
    preftext = 'lp'
    lp_prefixes = [preftext+str(i)+'_' for i in range(1, NBAND+1)]

    ## Case of 2 bands near K point
    vardict['02'] = [{'lp1_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                            'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                            'gamma':dict(value=0.02, min=0, max=2, vary=True),
                            'center':dict(vary=True)}},
            
                    {'lp2_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                            'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                            'gamma':dict(value=0.02, min=0, max=2, vary=True),
                            'center':dict(vary=True)}}]

    ## Case of 4 bands near K point
    vardict['04'] = [{'lp3_':{'amplitude':dict(value=0.5, min=0, max=2, vary=True),
                            'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                            'gamma':dict(value=0.05, min=0, max=2, vary=True)}},
          
                    {'lp4_':{'amplitude':dict(value=0.6, min=0, max=2, vary=True),
                            'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                            'gamma':dict(value=0.05, min=0, max=2, vary=True)}}]
    vardict['04'] = vardict['02'] + vardict['04']

    ## Case of 8 bands near K point
    amplitudes = pf.fitter.init_generator(lpnames=lp_prefixes[4:8], parname='sigma',
                                        varkeys=['value', 'min', 'max', 'vary'],
                                        parvals=[[0.5, 0, 2, True] for i in range(8-4)])
    sigmas = pf.fitter.init_generator(lpnames=lp_prefixes[4:8], parname='sigma',
                                    varkeys=['value', 'min', 'max', 'vary'],
                                    parvals=[[0.1, 0.05, 0.2, False] for i in range(8-4)])
    gammas = pf.fitter.init_generator(lpnames=lp_prefixes[4:8], parname='gamma',
                                    varkeys=['value', 'min', 'max', 'vary'],
                                    parvals=[[0.05, 0, 2, True] for i in range(8-4)])
    vardict['08'] = amplitudes + sigmas + gammas
    vardict['08'] = vardict['04'] + vardict['08']

    ## Case of 14 bands near K point
    amplitudes = pf.fitter.init_generator(lpnames=lp_prefixes[4:14], parname='sigma',
                                        varkeys=['value', 'min', 'max', 'vary'],
                                        parvals=[[0.5, 0, 2, True] for i in range(14-4)])
    sigmas = pf.fitter.init_generator(lpnames=lp_prefixes[4:14], parname='sigma',
                                    varkeys=['value', 'min', 'max', 'vary'],
                                    parvals=[[0.1, 0.05, 0.2, False] for i in range(14-4)])
    gammas = pf.fitter.init_generator(lpnames=lp_prefixes[4:14], parname='gamma', 
                                    varkeys=['value', 'min', 'max', 'vary'],
                                    parvals=[[0.05, 0, 2, True] for i in range(14-4)])
    vardict['14'] = amplitudes + sigmas + gammas
    vardict['14'] = vardict['04'] + vardict['14']

    ## Other number of bands
    if NBAND not in [2, 4, 8, 14]:
        vals = vardict['14']
        vardict_other = {}
        lp_exclude = [preftext+str(i)+'_' for i in range(NBAND+1, 15)]
        print(lp_exclude)
        for inits in vardict['14']:
            for lpn, lpv in inits.items():
                if lpn in lp_exclude:
                    vals.pop(lpn)
        vardict_other[str(NBAND).zfill(2)] = vals

# Set up and run the fitting routine
## Specify the sets of initialization to apply to the fitting
if PERSISTENT_INIT:
    bandkey = str(int(NBAND)).zfill(2)
    try:
        inits_persist = vardict[bandkey]
    except:
        inits_persist = vardict_other[bandkey]
else:
    inits_persist = None

## Select energy axis data range used for fitting
if NBAND == 2:
    en_range = slice(20, 100)
elif NBAND == 4:
    en_range = slice(20, 220)
elif NBAND == 8:
    en_range = slice(20, 320)
elif NBAND == 14:
    en_range = slice(20, 470)
else:
    en_range = slice(20, 400)

## Run the fitting benchmark
nspec = 900

if OPERATION == 'sequential':    
    kfit = pf.fitter.PatchFitter(peaks={'Voigt':NBAND}, xdata=pes_data['E'], ydata=pes_data['V'], preftext=preftext)

    kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=en_range)

    tstart = time.perf_counter()
    kfit.sequential_fit(pbar=True, pbenv='classic', jitter_init=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nspec=nspec)
    tstop = time.perf_counter()

    if TIMECOUNT:
        tdiff =  tstop - tstart
        print('Fitting took {} seconds'.format(tdiff))

    ## Save the fitting outcome
    out_dir = r'../data/WSe2/benchmark'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    kfit.save_data(fdir=out_dir, fname='/kpoint_symmetrized_seqfit_nband={}.h5'.format(NBAND))

elif OPERATION == 'parallel':
    if __name__ == '__main__':
        kfit = pf.fitter.ParallelPatchFitter(peaks={'Voigt':NBAND}, xdata=pes_data['E'], ydata=pes_data['V'], nfitter=nspec)
        
        kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=en_range)

        tstart = time.perf_counter()
        kfit.parallel_fit(jitter_init=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nfitter=nspec, backend='multiprocessing', scheduler='processes')
        tstop = time.perf_counter()

        if TIMECOUNT:
            tdiff =  tstop - tstart
            print('Fitting took {} seconds'.format(tdiff))

        ## Save the fitting outcome
        out_dir = r'../data/WSe2/benchmark'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        kfit.save_data(fdir=out_dir, fname='/kpoint_symmetrized_parafit_nband={}.h5'.format(NBAND))

else:
    raise NotImplementedError
