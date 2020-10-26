``pesfit`` documentation
====================================
Multiband lineshape fitting routines and benchmarks for photoemission spectroscopy.

Rationale
############

Lineshape fitting is a universal task in photoemission spectroscopy and can be a tedious endeavor due to the increasing amount of data measured in modern instruments (e.g. angle-resolved hemispherical analyzer, time-of-flight electron momentum microscope). It extracts physically meaningful quantities directly related to the materials' electronic properties, which can be reproduced from theory calculations. However, the efficiency bottleneck in lineshape fitting puts constraints on the potential new physical insights obtainable within a meaningful time frame. We set up here examples of multiband photoemission spectra along with existing domain knowledge in the field. The routines and benchmarks featured here offer an open-source data and algorithm platform for continuous algorithm development to improve the computational efficiency of the lineshape fitting task, which, in the meantime, also paves the way towards the automation of materials characterization using photoemission spectroscopy.

The fitting part of the package builds and improves on the existing ``Model`` and ``CompositeModel`` classes in the ``lmfit`` `package <https://github.com/lmfit/lmfit-py/>`_ to include multiband lineshapes (involving an arbitrary number of bands) evaluated using map-reduce operations.


.. toctree::
   :caption: Instructions
   :maxdepth: 2
   
   I01_start
   I02_benchmark


.. toctree::
   :caption: API documentation
   :maxdepth: 2

   lineshape
   fitter
   utils

