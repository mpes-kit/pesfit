# pesfit
![License](https://img.shields.io/github/license/mpes-kit/pesfit) ![Downloads](https://pepy.tech/badge/pesfit) ![PyPI version](https://badge.fury.io/py/pesfit.svg)

Distributed multicomponent lineshape fitting routines and benchmarks for photoemission spectroscopy and spectral imaging

### Rationale

Lineshape fitting is a universal task in photoemission spectroscopy and can be a tedious endeavor due to the increasing amount of data measured in modern instruments (e.g. angle-resolved hemispherical analyzer, time-of-flight electron momentum microscope). It extracts physically meaningful quantities directly related to the materials' electronic properties, which can be reproduced from theory calculations. However, the efficiency bottleneck in lineshape fitting puts constraints on the potential new physical insights obtainable within a meaningful time frame. We set up here examples of multiband photoemission spectra along with existing domain knowledge in the field. The routines and benchmarks featured here offer an open-source data and algorithm platform for continuous algorithm development to improve the computational efficiency of the lineshape fitting task, which, in the meantime, also paves the way towards the automation of materials characterization using photoemission spectroscopy.

### Design and scope

The fitting part of the package builds and improves on the existing ``Model`` and ``CompositeModel`` classes in the widely-used ``lmfit`` [package](https://github.com/lmfit/lmfit-py/) to include multiband lineshapes (involving an arbitrary number of peaks) evaluated using map-reduce operations. Fitting of many intensity profiles (i.e. line spectra) can be carried out either in sequence or in parallel (built in using [dask](https://dask.org/) and [multiprocessing](https://docs.python.org/3/library/multiprocessing.html)).

The focus of the software and its benchmarks in on determining the momentum-dependent band positions in valence band photoemission data *at scale* (e.g. 10<sup>4</sup>-10<sup>5</sup> spectra with each containing 10+ bands), which meets the needs for a *global understanding* of these complex data with reasonable accuracy (not necessarily accounting for all photoemission physics) to yield empirical structural information (i.e. band structure parameters). For conventional data analysis of core-level photoemission spectroscopy that often exhibits a complex background, please consult software packages such as [lmfit](https://github.com/lmfit/lmfit-py/), [xps](https://gitlab.com/ddkn/xps), and [gxps](https://github.com/schachmett/gxps).

### Installation

1. Install from scratch
    <pre><code class="console"> pip install git+https://github.com/mpes-kit/pesfit.git </code></pre>

2. Upgrade or overwrite an existing installation
    <pre><code class="console"> pip install --upgrade git+https://github.com/mpes-kit/pesfit.git </code></pre>

3. Install from [PyPI](https://pypi.org/project/pesfit/)
    <pre><code class="console"> pip install pesfit </code></pre>

### Data source

Please download the data from [``mpes-kit/pesarxiv``](https://github.com/mpes-kit/pesarxiv). To run the examples and benchmarks, create a ``./data`` folder in the cloned repository and copy the downloaded data into it.

### Benchmarks and examples

Besides source code, the package comes with [examples](https://github.com/mpes-kit/pesfit/tree/master/examples) presented in Jupyter notebooks and [benchmarks](https://github.com/mpes-kit/pesfit/tree/master/benchmarks) for multiband dispersion fitting routines in scripts, using the data described above.

### Documentation

Online documentation is provided [here](https://mpes-kit.github.io/pesfit/).

### Reference

Please cite the following paper if you use the software:

R. Patrick Xian, R. Ernstorfer, Philipp M. Pelz, Scalable multicomponent spectral analysis for high-throughput data annotation, arXiv: [2102.05604](https://arxiv.org/abs/2102.05604).