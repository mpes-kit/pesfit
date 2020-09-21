#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pesfit as pf
import time
from hdfio import dict_io as io

# Sequential fitting of photoemission data patch around the K point of WSe2
# Option to introduce persistent initial conditions
PERSISTENT_INIT = True
# Number of bands to fit
NBAND = 2
# Option to enable code profiling
TIMECOUNT = True
# Specification of spectrum-dependent initial conditions ('theory' or 'recon')
VARYING_INIT = 'recon'
# The preprocessing needed before fitting ('symmetrized', 'mclahe', 'mclahe_smooth')
PREPROC = 'symmetrized'

# Photoemission band mapping data
data_dir = r'./data/WSe2'
pes_fname = r'/pes/kpoint/kpoint_symmetrized.h5'
pes_path = data_dir + pes_fname
pes_data = io.h5_to_dict(pes_path)

# Theoretical calculations interpolated to the same momentum grid (as one type of initialization)
theo_fname = r'/theory/kpoint/kpoint_LDA.h5'
theo_path = data_dir + theo_fname
theo_data = io.h5_to_dict(theo_path)

# Reconstructed photoemission band dispersion (as another type of initialization)
recon_fname = r'/recon/kpoint/kpoint_LDA_recon.h5'
recon_path = data_dir + recon_fname
recon_data = io.h5_to_dict(recon_path)

# Setting initial conditions persistent throughout the fitting. These fixed constraints are tested for fitting the band dispersion nearby the K point of WSe2 and are required to make the fitting relatively stable!
if PERSISTENT_INIT:
    vardict = {}

    ## Case of 2 bands near K point
    vardict['02'] = [{'lp1_':{'amplitude':dict(value=0.2, min=0, max=2, vary=1.),
                    'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                    'gamma':dict(value=0.02, min=0, max=2, vary=True),
                    'center':dict(vary=True)}},
            
                {'lp2_':{'amplitude':dict(value=0.2, min=0, max=2, vary=True),
                    'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                    'gamma':dict(value=0.02, min=0, max=2, vary=True),
                    'center':dict(vary=True)}}]

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

# Run fitting routine
kfit = pf.fitter.PatchFitter(xdata=pes_data['E'], ydata=pes_data['V'])
if PERSISTENT_INIT:
    inits_persist = vardict[str(int(NBAND)).zfill(2)]
else:
    inits_persist = None

if VARYING_INIT == 'theory':
    inits_vary = theo_data
elif VARYING_INIT == 'recon':
    inits_vary = recon_data

kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=slice(20,100))
kfit.sequential_fit(pbar=False, jitter_inits=True, shifts=np.arange(-0.08, 0.09, 0.01), nspec=900)

if TIMECOUNT:
    tstop = time.perf_counter()
    tdiff =  tstop - tstart

# Save fitting outcome
kfit.save_data()
