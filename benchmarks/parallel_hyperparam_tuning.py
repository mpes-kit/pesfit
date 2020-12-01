#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import pesfit as pf
import time
from hdfio import dict_io as io
import argparse
import parmap as pm
import multiprocessing as mp

n_cpu = mp.cpu_count()

def fitting_tasks(nband=2, nspectra=10, datasource='LDA_synth_14', eoffset=[0.], operation='parallel',
        backend='async', nworker=n_cpu, chunksize=1, timecount=True, persistent_init=True,
        varying_init='theory', jitter_init=False, **kwargs):

    """ Main fitting routine.
    """

    maxband = kwargs.pop('maxband', 14)
    # Sequential fitting of photoemission data patch around the K point of WSe2
    ## Number of bands to fit
    NBAND = nband
    if NBAND > maxband or NBAND < 1:
        raise ValueError('The number of bands to reconstruct is within [1, 14] for WSe2.')
    ## Data source used for band fitting, ('symmetrized', 'preprocessed')
    DATASOURCE = datasource
    ## Number of line spectra to fit
    NSPECTRA = nspectra
    ## Global energy offset for fitting initialization of each band
    argofs = list(map(float, eoffset))
    nargofs = len(argofs)
    if nargofs == 1:
        argofs = argofs*NBAND
        allofs = argofs + [0]*(maxband-NBAND)
    elif nargofs == NBAND:
        allofs = argofs + [0]*(maxband-NBAND)
    EOFFSET = np.asarray([allofs]).T
    ## Option for computing method ('sequential' or 'parallel')
    OPERATION = operation
    ## Backend software package for execution
    BACKEND = backend
    ## Number of workers to use in running the benchmark
    NWORKER = nworker
    ## Number of tasks assigned to each worker
    CHUNKSIZE = chunksize
    ## Option to enable code profiling
    TIMECOUNT = timecount
    ## Option to introduce persistent initial conditions
    PERSISTENT_INIT = persistent_init
    ## Specification of spectrum-dependent initial conditions ('theory' or 'recon')
    VARYING_INIT = varying_init
    ## Option to apply jittering to initializations to obtain better fitting results
    JITTER_INIT = jitter_init
    # print(cli_args)

    # Photoemission band mapping data
    data_dir = r'../data/WSe2'
    # pes_fname = r'/pes/kpoint/kpoint_{}.h5'.format(DATASOURCE)
    pes_fname = r'/synth/kpoint/kpoint_{}.h5'.format(DATASOURCE)
    pes_path = data_dir + pes_fname
    pes_data = io.h5_to_dict(pes_path)
    print(pes_data['V'].shape)

    if VARYING_INIT == 'theory':
        # Theoretical calculations interpolated to the same momentum grid (as one type of initialization)
        # theo_fname = r'/theory/kpoint/kpoint_LDA.h5'
        theo_fname = r'/theory/kpoint/kpoint_PBE.h5'
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
        vardict['02'] = [{'lp1_':{'amplitude':dict(value=0.5, min=0, max=2, vary=True),
                                'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                                'gamma':dict(value=0.05, min=0, max=2, vary=True),
                                'center':dict(vary=True)}},
                
                        {'lp2_':{'amplitude':dict(value=0.5, min=0, max=2, vary=True),
                                'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                                'gamma':dict(value=0.05, min=0, max=2, vary=True),
                                'center':dict(vary=True)}}]

        ## Case of 4 bands near K point
        vardict['04'] = [{'lp3_':{'amplitude':dict(value=0.5, min=0, max=2, vary=True),
                                'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                                'gamma':dict(value=0.05, min=0, max=2, vary=True)}},
            
                        {'lp4_':{'amplitude':dict(value=0.5, min=0, max=2, vary=True),
                                'sigma':dict(value=0.1, min=0.05, max=2, vary=False),
                                'gamma':dict(value=0.05, min=0, max=2, vary=True)}}]
        vardict['04'] = vardict['02'] + vardict['04']

        ## Case of 8 bands near K point
        amplitudes = pf.fitter.init_generator(lpnames=lp_prefixes[4:8], parname='amplitude',
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
        amplitudes = pf.fitter.init_generator(lpnames=lp_prefixes[4:14], parname='amplitude',
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

    # print(inits_persist)
    ## Select energy axis data range used for fitting
    if NBAND == 2:
        en_range = slice(10, 100)
    elif NBAND == 4:
        en_range = slice(10, 220)
    elif NBAND == 8:
        en_range = slice(10, 280)
    elif NBAND == 14:
        en_range = slice(10, 490)
    else:
        en_range = slice(10, 490)

    ## Run the fitting benchmark
    pesdata_shape = pes_data['V'].shape
    maxspectra = pesdata_shape[0] * pesdata_shape[1]
    nspec = min([NSPECTRA, maxspectra])

    if OPERATION == 'sequential':    
        kfit = pf.fitter.PatchFitter(peaks={'Voigt':NBAND}, xdata=pes_data['E'], ydata=pes_data['V'], preftext=preftext)

        kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=en_range)

        tstart = time.perf_counter()
        kfit.sequential_fit(pbar=True, pbenv='classic', jitter_init=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nspec=nspec)
        tstop = time.perf_counter()

        print(kfit.df_fit)

        if TIMECOUNT:
            tdiff =  tstop - tstart
            print('Fitting took {} seconds'.format(tdiff))

        ## Save the fitting outcome
        out_dir = kwargs.pop('outdir', r'../data/WSe2/benchmark')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        kfit.save_data(fdir=out_dir, fname='/kpoint_{}_seqfit_nband={}_ofs={}_{}.h5'.format(DATASOURCE, NBAND, argofs, VARYING_INIT))

    elif OPERATION == 'parallel':
        print("I'm here")
        kfit = pf.fitter.DistributedFitter(peaks={'Voigt':NBAND}, xdata=pes_data['E'], ydata=pes_data['V'], drange=en_range, nfitter=nspec)

        kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, offset=EOFFSET)

        if CHUNKSIZE > 0:
            tstart = time.perf_counter()
            kfit.parallel_fit(jitter_init=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nfitter=nspec, backend=BACKEND, scheduler='processes', num_workers=NWORKER, chunksize=CHUNKSIZE, pbar=True)
        else:
            tstart = time.perf_counter()
            kfit.parallel_fit(jitter_init=JITTER_INIT, shifts=np.arange(-0.08, 0.09, 0.01), nfitter=nspec, backend=BACKEND, scheduler='processes', num_workers=NWORKER, pbar=True)
        tstop = time.perf_counter()

        if TIMECOUNT:
            tdiff =  tstop - tstart
            print('Fitting took {} seconds'.format(tdiff))

        print(kfit.df_fit)

        ## Save the fitting outcome
        out_dir = r'../data/WSe2/benchmark'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        kfit.save_data(fdir=out_dir, fname='/kpoint_{}_parafit_nband={}_ofs={}_{}.h5'.format(DATASOURCE, NBAND, argofs, VARYING_INIT))
    
        return kfit.df_fit

    else:
        raise NotImplementedError


def main(shifts):

    tuning_args = [[2, 900, 'LDA_synth_14', [shifts[i]], 'parallel', 'async', 4, 300] for i in range(3)]
    # nband=2, nspectra=10, datasource='LDA_synth_14', eoffset=0., operation='parallel', backend='async', nworker=n_cpu, chunksize=1
    tuning_procs = pm.starmap_async(fitting_tasks, tuning_args, pm_processes=3)
    try:
        pm.parmap._do_pbar(tuning_procs, num_tasks=3, chunksize=1)
    finally:
        tuning_results = tuning_procs.get()
    # print(tuning_results)
    print('Tuning completed!')


if __name__ == '__main__':

    shifts = [0.22, 0.26, 0.34] # Candidate hyperparameter values
    main(shifts)