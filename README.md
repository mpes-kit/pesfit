# pesfit
![License](https://img.shields.io/github/license/mpes-kit/pesfit)

Multiband lineshape fitting routines and benchmarks for photoemission spectroscopy

### Rationale
Lineshape fitting is a universal task in photoemission spectroscopy and can be a tedious endeavor due to the increasing amount of data measured in modern instruments (e.g. angle-resolved hemispherical analyzer, time-of-flight electron momentum microscope). It extracts physically meaningful quantities directly related to the materials' electronic properties, which can be reproduced from theory calculations. However, the efficiency bottleneck in lineshape fitting puts constraints on the potential new physical insights obtainable within a meaningful time frame. We set up here examples of multiband photoemission spectra along with existing domain knowledge in the field. The routines and benchmarks featured here offer an open-source data and algorithm platform for continuous algorithm development to improve the computational efficiency of the lineshape fitting task, which, in the meantime, also paves the way towards the automation of materials characterization using photoemission spectroscopy.

The fitting part of the package builds and improves on the existing ``Model`` and ``CompositeModel`` classes in the widely-used ``lmfit`` [package](https://github.com/lmfit/lmfit-py/) to include multiband lineshapes (involving an arbitrary number of peaks) evaluated using map-reduce operations. Fitting of multiple intensity profiles can be carried out either in sequence or in parallel.

### Installation

1. Install from scratch
    <pre><code class="console"> pip install git+https://github.com/mpes-kit/pesfit.git </code></pre>

2. Upgrade or override an existing installation

    <pre><code class="console"> pip install --upgrade git+https://github.com/mpes-kit/pesfit.git </code></pre>

### Data source

Please download the data from [``mpes-kit/pesarxiv``](https://github.com/mpes-kit/pesarxiv). To run the examples and benchmarks, create a ``./data`` folder in the cloned repository and copy the downloaded data into it.

### Benchmarks

The benchmarks for multiband dispersion fitting routines are provided [here](https://github.com/mpes-kit/pesfit/tree/master/benchmarks).

### Documentation

Documentation is provided [here](https://mpes-kit.github.io/pesfit/).