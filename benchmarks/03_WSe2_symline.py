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
parser.set_defaults(nband=2, nspectra=10, datasource='preprocessed', eoffset=0., operation='sequential', backend='multiprocessing', nworker=n_cpu, chunksize=0, timecount=True, persistent_init=True, varying_init='recon', jitter_init=False)
cli_args = parser.parse_args()