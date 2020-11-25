import os
import numpy as np
import pesfit as pf
import time
from hdfio import dict_io as io
import argparse
import multiprocessing as mp

n_cpu = mp.cpu_count()

# Definitions of command line interaction
parser = argparse.ArgumentParser(description='Input arguments')
parser.add_argument('-nb', '--nband', metavar='nband', nargs='?', type=int, help='Number of bands in fitting model, needs an integer between 1 and 14')
parser.add_argument('-ns', '--nspectra', metavar='nspectra', nargs='?', type=int, help='Number of spectra to fit, needs an integer larger than 1')
parser.add_argument('-ds', '--datasource', metavar='datasource', nargs='?', type=str, help='Name of the data source for band fitting')
parser.add_argument('-ofs', '--eoffset', metavar='eoffset', nargs='?', type=float, help='Global energy offset')
parser.add_argument('-op', '--operation', metavar='operation', nargs='?', type=str, help='What computing method to run the benchmark program with')
parser.add_argument('-bk', '--backend', metavar='backend', nargs='?', type=str, help='Backend software package used for execution (in paralleli or in sequence)')
parser.add_argument('-nw', '--nworker', metavar='nworker', nargs='?', type=int, help='Number of workers to spawn')
parser.add_argument('-cs', '--chunksize', metavar='chunksize', nargs='?', type=int, help='Chunk size of tasks assigned to each worker')
parser.add_argument('-tc', '--timecount', metavar='timcount', nargs='?', type=bool, help='Whether to include time profiling')
parser.add_argument('-persin', '--persistent_init', metavar='persistent_init', nargs='?', type=bool, help='Initialization include persistent settings')
parser.add_argument('-varin', '--varying_init', metavar='varying_init', nargs='?', type=str, help='Initialization including varying settings')
parser.add_argument('-jittin', '--jitter_init', metavar='jitter_init', nargs='?', type=bool, help='Add jitter to initialization for better fits')
parser.set_defaults(nband=2, nspectra=10, datasource='preprocessed', eoffset=0., operation='sequential', backend='multiprocessing', nworker=n_cpu, chunksize=1, timecount=True, persistent_init=True, varying_init='recon', jitter_init=False)
cli_args = parser.parse_args()

# Sequential fitting of photoemission data patch around the K point of WSe2
## Number of bands to fit
NBAND = cli_args.nband
if NBAND > 14 or NBAND < 1:
    raise ValueError('The number of bands to reconstruct is within [1, 14] for WSe2.')
## Data source used for band fitting, ('symmetrized', 'preprocessed')
DATASOURCE = cli_args.datasource
## Number of line spectra to fit
NSPECTRA = cli_args.nspectra
## Global energy offset for band fitting initialization
EOFFSET = cli_args.eoffset
## Option for computing method ('sequential' or 'parallel')
OPERATION = cli_args.operation
## Backend software package for execution
BACKEND = cli_args.backend
## Number of workers to use in running the benchmark
NWORKER = cli_args.nworker
## Number of tasks assigned to each worker
CHUNKSIZE = cli_args.chunksize
## Option to enable code profiling
TIMECOUNT = cli_args.timecount
## Option to introduce persistent initial conditions
PERSISTENT_INIT = cli_args.persistent_init
## Specification of spectrum-dependent initial conditions ('theory' or 'recon')
VARYING_INIT = cli_args.varying_init
## Option to apply jittering to initializations to obtain better fitting results
JITTER_INIT = cli_args.jitter_init
# print(cli_args)

# Photoemission band mapping data
data_dir = r'../data/WSe2'
pes_fname = r'/pes/symline/hsymline_{}.h5'.format(DATASOURCE)
pes_path = data_dir + pes_fname
pes_data = io.h5_to_dict(pes_path)

if VARYING_INIT == 'theory':
    # Theoretical calculations interpolated to the same momentum grid (as one type of initialization)
    theo_fname = r'/theory/symline/hsymline_LDA.h5'
    theo_path = data_dir + theo_fname
    theo_data = io.h5_to_dict(theo_path)['data']['kimage']
    inits_vary = theo_data

elif VARYING_INIT == 'recon':
    # Reconstructed photoemission band dispersion (as another type of initialization)
    recon_fname = r'/recon/symline/hsymline_LDA_recon.h5'
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
        # print(lp_exclude)
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
pesdata_shape = pes_data['data']['kimage'].shape
maxspectra = pesdata_shape[0] * pesdata_shape[1]
nspec = min([NSPECTRA, maxspectra])

if OPERATION == 'sequential':    
    kfit = pf.fitter.PatchFitter(peaks={'Voigt':NBAND}, xdata=pes_data['data']['E'], ydata=pes_data['data']['kimage'], preftext=preftext)

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

    kfit.save_data(fdir=out_dir, fname='/hsymline_{}_seqfit_nband={}_ofs={}_{}.h5'.format(DATASOURCE,NBAND,EOFFSET,VARYING_INIT))

elif OPERATION == 'parallel':
    if __name__ == '__main__':
        kfit = pf.fitter.DistributedFitter(peaks={'Voigt':NBAND}, xdata=pes_data['data']['E'], ydata=pes_data['data']['kimage'], nfitter=nspec)

        kfit.set_inits(inits_dict=inits_persist, band_inits=inits_vary, drange=en_range, offset=EOFFSET)
        print(EOFFSET)

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

        ## Save the fitting outcome
        out_dir = r'../data/WSe2/benchmark'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        kfit.save_data(fdir=out_dir, fname='/hsymline_{}_parafit_nband={}_ofs={}_{}.h5'.format(DATASOURCE,NBAND,EOFFSET,VARYING_INIT))

else:
    raise NotImplementedError