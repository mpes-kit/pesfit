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
parser.add_argument('persistent_init', metavar='pi', nargs='?', type=bool, help='initialization include persistent settings')
parser.add_argument('varying_init', metavar='vi', nargs='?', type=str, help='initialization including varying settings')
parser.add_argument('jitter_init', metavar='ji', nargs='?', type=bool, help='add jitter to initialization for better fits')
parser.add_argument('preproc', metavar='pp', nargs='?', type=str, help='the stage of preprocessing used for fitting')
parser.set_defaults(nband=2, timecount=True, persistent_init=True, varying_init='recon',
                    jitter_init=False, preproc='symmetrized')
cli_args = parser.parse_args()

# Sequential fitting of photoemission data patch around the K point of WSe2
# Option to introduce persistent initial conditions
PERSISTENT_INIT = cli_args.persistent_init
# Number of bands to fit
NBAND = cli_args.nband
# Option to enable code profiling
TIMECOUNT = cli_args.timecount
# Specification of spectrum-dependent initial conditions ('theory' or 'recon')
VARYING_INIT = cli_args.varying_init
# The preprocessing needed before fitting ('symmetrized', 'mclahe', 'mclahe_smooth')
PREPROC = cli_args.preproc
# Option to apply jittering to initializations to obtain better fitting results
JITTER_INIT = cli_args.jitter_init

# Photoemission band mapping data
data_dir = r'./data/WSe2'
pes_fname = r'/pes/mpoint/mpoint_symmetrized.h5'
pes_path = data_dir + pes_fname
pes_data = io.h5_to_dict(pes_path)

# Theoretical calculations interpolated to the same momentum grid (as one type of initialization)
theo_fname = r'/theory/mpoint/mpoint_LDA.h5'
theo_path = data_dir + theo_fname
theo_data = io.h5_to_dict(theo_path)

# Reconstructed photoemission band dispersion (as another type of initialization)
recon_fname = r'/recon/mpoint/mpoint_LDA_recon.h5'
recon_path = data_dir + recon_fname
recon_data = io.h5_to_dict(recon_path)

# Setting initial conditions persistent throughout the fitting. These fixed constraints are tested for fitting the band dispersion nearby the M' point of WSe2 and are required to make the fitting relatively stable!
if PERSISTENT_INIT:
    vardict = {}

    ## Case of 2 bands near K point
    vardict['02'] = [{'lp1_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                    'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                    'gamma':dict(value=0.02, min=0, max=2, vary=True)}},
            
                    {'lp2_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                        'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                        'gamma':dict(value=0.02, min=0, max=2, vary=True)}}]

    ## Case of 4 bands near K point
    vardict['04'] = [{'lp3_':{'amplitude':dict(value=0.2, min=0, max=2, vary=1.),
                    'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                    'gamma':dict(value=0.02, min=0, max=2, vary=True),
                    'center':dict(vary=True)}},
            
                {'lp4_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                    'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                    'gamma':dict(value=0.02, min=0, max=2, vary=True),
                    'center':dict(vary=True)}}]
    vardict['04'] = vardict['02'] + vardict['04']

    ## Case of 8 bands near K point
    vardict['08'] = []
    vardict['08'] = vardict['04'] + vardict['08']

    ## Case of 14 bands near K point
    vardict['14'] = []
    vardict['14'] = vardict['08'] + vardict['14']

if TIMECOUNT:
    tstart = time.perf_counter()

# Set up and run the fitting routine
## Fitting model initialization
mfit = pf.fitter.PatchFitter(peaks={'Voigt':NBAND}, xdata=pes_data['E'], ydata=pes_data['V'], preftext=preftext)

## Specify the set of initialization to apply to the fitting
if PERSISTENT_INIT:
    inits_persist = vardict[str(int(NBAND)).zfill(2)]
else:
    inits_persist = None

if VARYING_INIT == 'theory':
    inits_vary = theo_data
elif VARYING_INIT == 'recon':
    inits_vary = recon_data

## Select energy axis data range used for fitting
if NBAND == 2:
    en_range = slice(20, 100)
elif NBAND == 4:
    en_range = slice(20, 220)
elif NBAND == 8:
    en_range = slice(20, 320)
elif NBAND == 14:
    en_range = slice(20, None)

mfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=en_range)
mfit.sequential_fit(pbar=False, jitter_inits=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nspec=900)

if TIMECOUNT:
    tstop = time.perf_counter()
    tdiff =  tstop - tstart

# Save the fitting outcome
out_dir = r'../data/WSe2/benchmark'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

mfit.save_data(fdir=out_dir, fname='/mpoint_symmetrized_fit_nband={}.h5'.format(NBAND))