#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import utils as u
import operator
from functools import reduce
from copy import deepcopy
from collections import OrderedDict
import lmfit.models as lmm
from lmfit import Model


class MultipeakModel(Model):
    """ Composite lineshape model consisting of multiple identical peak profiles.
    """
    
    _known_ops = {operator.add: '+', operator.mul: '*'}
    
    def __init__(self, model=None, n=1, lineshape=None, background=None, op=operator.add, **kws):
        
        self.components = []
        self.op = op
        
        # Introduce a background function
        if background is not None:
            try:
                self.components += background.components
            except:
                self.components += list(background)
        
        if model is None:
            self.components = [lineshape(prefix="lp"+str(i+1)+"_", **kws) for i in range(n)]
        else:
            self.ls = model
            self.components = model.components

        if 'independent_vars' not in kws:
            kws['independent_vars'] = self.components[0].independent_vars
        if 'missing' not in kws:
            kws['missing'] = self.components[0].missing
            
        def _tmp(self, *args, **kws):
            pass
        Model.__init__(self, _tmp, **kws)

        for side in self.components:
            prefix = side.prefix
            for basename, hint in side.param_hints.items():
                self.param_hints["%s%s" % (prefix, basename)] = hint
            
    def _parse_params(self):
        """ Parsing and merging parameters from constituent models.
        """
        self._func_haskeywords = reduce(operator.or_, [self.components[i]._func_haskeywords for i in range(self.ncomp)])
        self._func_allargs = reduce(operator.add, [self.components[i]._func_allargs for i in range(self.ncomp)])
        
        self.def_vals = deepcopy(self.components[0].def_vals)
        self.opts = deepcopy(self.components[0].opts)
        if self.ncomp > 1:
            for i in range(self.ncomp-1):
                self.def_vals.update(self.components[i+1].def_vals)
                self.opts.update(self.components[i+1].opts)
            
    def _reprstring(self, long=False):
        """ Representation string for the multipeak model.
        """
        
        meth_reprs = list(map(lambda obj: getattr(obj, '_reprstring'), self.components))
        f_reprs = [meth_reprs[i](long=long) for i in range(self.ncomp)]
        op_reprs = [self._known_ops.get(self.op, self.op)]*self.ncomp
        mod_repr = u.riffle(f_reprs, op_reprs)[:-1].tolist()
        
        return mod_repr # Need pretty-printed format
            
    @property
    def param_names(self):
        """ All parameter names for a multipeak model.
        """
        
        return self.multi_retrieve('param_names', op=operator.add)

    # #@property
    # def components(self):
    #     """ All components for a multipeak model.
    #     """
        
    #     return self.components
    
    @property
    def ncomp(self):
        """ Number of components in a multipeak model.
        """
        
        return len(self.components)
    
    def eval(self, params=None, **kwargs):
        """ Evaluate the entire model.
        """
        
        return reduce(self.op, [comp.eval(params=params, **kwargs) for comp in self.components])

    def eval_components(self, **kwargs):
        """ Return OrderedDict of name, results for each component.
        """
        out = OrderedDict(self.components[0].eval_components(**kwargs))
        if self.ncomp > 1:
            for i in range(self.ncomp-1):
                out.update(self.components[i+1].eval_components(**kwargs))
        
        return out
    
    def _make_all_args(self, params=None, **kwargs):
        """ Generate **all** function arguments for all functions.
        """
        
        out = self.components[0]._make_all_args(params=params, **kwargs)
        if self.ncomp > 1:
            for i in range(self.ncomp-1):
                out.update(self.components[i+1]._make_all_args(params=params, **kwargs))
        
        return out
    
    def multi_eval(self, op, objs, fevs, *args, **kwargs):
        """ Evaluate multiple components with a defined operator, returns a list.
        """
        
        return reduce(op, map(lambda obj, fev: fev(obj, *args, **kwargs), objs, fevs))
    
    def multi_retrieve(self, prop, op=operator.add):
        """ Retrieve the specified properties for all components in the multipeak model.
        """
        
        return self.multi_eval(op, self.components, [getattr]*self.ncomp, prop)