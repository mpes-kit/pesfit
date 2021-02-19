#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import utils as u
import operator
from functools import reduce
from itertools import chain
from copy import deepcopy
from collections import OrderedDict
import lmfit.models as lmm
from lmfit import Model


def map_reduce_meth(meth, elems, op, init, **kwargs):
    """ Execute map-reduce on instance methods (callable).
    """

    return reduce(op, map(lambda elem: getattr(elem, meth)(**kwargs), elems), init)


def map_reduce_attr(attr, elems, op, **kwargs):
    """ Execute map-reduce on instance attributes (non-callable).
    """

    return reduce(op, map(lambda elem: getattr(elem, attr), elems), **kwargs)


def mr_dict_merge(meth, elems, op_dict=OrderedDict, **kwargs):
    """ Dictionary merging using map-reduce operations.
    """

    try: # Dictionary merging for Python 3.5 or above
        merged = map_reduce_meth(meth, elems, lambda x, y: {**x, **y}, {}, **kwargs)
    except: # Dictionary merging for other Python versions
        merged = map_reduce_meth(meth, elems, lambda x, y: chain(x.items(), y.items()), {}, **kwargs)

    return op_dict(merged)


def dict_merge(elems, init={}, op_dict=OrderedDict):
    """ Dictionary merging by reduce operation.
    """

    try:
        merged = reduce(lambda x, y: {**x, **y}, elems, init)
    except:
        merged = reduce(lambda x, y: chain(x.items(), y.items()), elems, init)

    return op_dict(merged)
    

class MultipeakModel(Model):
    """ Composite lineshape model consisting of multiple (sets of) identical peak profiles.

    **Parameters**\n
    model: instance of ``lmfit.model.Model`` | []
        An existing lineshape model.
    n, lineshape: int, ``lmfit.model.Model`` | 0, []
        Basis lineshape and the number of it. Their way of combination is defined by the ``op``.
    background: list/tuple or instance of ``lmfit.model.Model`` | []
        Functional model to approximate the signal background. If multiple operations are needed (e.g summation and multiplication), a precomposed background function should be supplied.
    op: func | ``operator.add``
        Operator used to combine lineshape components and between them and the signal background.
    preftext: str | 'lp'
        Prefix for the basis lineshape components. If it is set to ``'lp'``, the automatically generated lineshapes will be named as ``'lp1_'``, ``'lp2_'``, etc.
    **kws: keyword argument
        Additional keyword arguments passed to ``lmfit.Model`` class, including ``'independent_vars'`` and ``'missing'``.
    """
    
    _known_ops = {operator.add: '+', operator.mul: '*'}
    
    def __init__(self, model=[], n=0, lineshape=[], background=[], op=operator.add, preftext='lp', **kws):
        """ Initialize class.
        """
        
        self.components = []
        self.op = op
        self.preftext = preftext
        # Initialize the number of components
        self.nbg = 0 # number of background components
        self.nlp = 0 # number of line profiles
        
        # Introduce a background function
        if background:
            try:
                bg_comp = background.components
                if type(bg_comp) == list:
                    self.components += bg_comp
                    self.nbg = len(bg_comp)
            except:
                bg_comp = list(background)
                self.components += bg_comp
                self.nbg = len(bg_comp)
        
        # Construct the lineshape components
        if lineshape:
            self.components += [lineshape(prefix=preftext+str(i+1)+'_', **kws) for i in range(n)]
            self.nlp = n
        elif model:
            self.components += model.components
            self.nlp = len(model.components)

        if 'independent_vars' not in kws:
            try:
                kws['independent_vars'] = self.components[0].independent_vars
            except:
                pass
        
        if 'missing' not in kws:
            try:
                kws['missing'] = self.components[0].missing
            except:
                pass
            
        # def _tmp(self, *args, **kws):
        #     pass
        # Model.__init__(self, _tmp, **kws)
        Model.__init__(self, self._tmp, **kws)

        for side in self.components:
            prefix = side.prefix
            for basename, hint in side.param_hints.items():
                self.param_hints["%s%s" % (prefix, basename)] = hint

    def _tmp(self, *args, **kws):
        """ Dummy function (essential, don't delete!).
        """
        pass
            
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
        
        meth_reprs = [self.components[i]._reprstring for i in range(self.ncomp)]
        f_reprs = [meth_reprs[i](long=long) for i in range(self.ncomp)]
        op_reprs = [self._known_ops.get(self.op, self.op)]*self.ncomp
        mod_repr = u.riffle(f_reprs, op_reprs)[:-1].tolist()
        
        return mod_repr # Need pretty-printed format
            
    @property
    def param_names(self):
        """ All parameter names for a multipeak model.
        """
        
        return self.multi_retrieve('param_names', op=operator.add)

    #@property
    def components(self):
        """ All components for a multipeak model. Override the property constraint.
        """
        
        return self.components
    
    @property
    def ncomp(self):
        """ Number of components in a multipeak model.
        """
        
        return len(self.components)

    @property
    def prefixes(self):
        """ Collection of prefixes for all lineshape components.
        """

        prefs = [self.components[i].prefix for i in range(self.ncomp)]
        return prefs
    
    def eval(self, params=None, **kwargs):
        """ Evaluate the entire model.
        """
        # The commented-out line functions the same as the actual one
        return reduce(self.op, [comp.eval(params=params, **kwargs) for comp in self.components])
        # return map_reduce_meth('eval', self.components, self.op, init=0, params=params, **kwargs)

    def eval_components(self, **kwargs):
        """ Component-wise evaluation, which returns an OrderedDict of name, numerical results for each lineshape component.
        """
        
        comp_evals = [self.components[i].eval_components(**kwargs) for i in range(self.ncomp)]
        out = dict_merge(comp_evals, {}, op_dict=OrderedDict)
        # out = mr_dict_merge('eval_components', self.components, op_dict=OrderedDict, **kwargs)
    
        return out
    
    def _make_all_args(self, params=None, **kwargs):
        """ Generate **all** function arguments for all functions.
        """

        all_args = [self.components[i]._make_all_args(params=params, **kwargs) for i in range(self.ncomp)]
        out = dict_merge(all_args, {}, op_dict=OrderedDict)
        # out = mr_dict_merge('_make_all_args', self.components, op_dict=OrderedDict, params=params, **kwargs)

        return out
    
    def multi_eval(self, op, objs, fevs, *args, **kwargs):
        """ Evaluate multiple components with a defined operator using map-reduce operation, returns a list.

        **Parameters**\n
        op: func
            Functional operator used to reduce the terms.
        objs: iterable
            Collection of objects to evaluate on.
        fevs: iterable (list/tuple of functions)
            Collection of functions to map to objects.
        *args: arguments
            Additional arguments for the mapped function (every entry in ``fevs``).
        **kwargs: keyword arguments
            Additional keyword arguments for the mapped function (every entry in ``fevs``).
        """
        
        return reduce(op, map(lambda obj, fev: fev(obj, *args, **kwargs), objs, fevs))
 
    def multi_retrieve(self, prop, op=operator.add, init=[]):
        """ Retrieve the specified properties for all components in the multipeak model.

        **Parameters**\n
        prop: str
            Namestring of the property to retrieve.
        op: func | operator.add
            Functional operator used to reduce the terms.
        """

        return map_reduce_attr(prop, self.components, op, initializer=init)
        # return self.multi_eval(op, self.components, [getattr]*self.ncomp, prop)


class MultipeakModelPP(Model):
    """ Composite lineshape model consisting of multiple (sets of) identical peak profiles. This version has preserves the property type of model components (``self.components``), therefore called property-preserved (PP) version.
    """
    
    _known_ops = {operator.add: '+', operator.mul: '*'}
    
    def __init__(self, lineshape=None, n=1, model=[], background=[], op=operator.add, preftext='lp', **kws):
        """ Initialize class.
        """
        
        self.op = op
        self.lineshape = self._model_convert(lineshape)
        self.background = self._model_convert(background)
        self.model = model
        self.preftext = preftext
        # Initialize the number of components
        self.nbg = 0 # number of background components
        self.nlp = 0 # number of line profiles
            
        if 'independent_vars' not in kws:
            try:
                kws['independent_vars'] = self.components[0].independent_vars
            except:
                pass
        
        if 'missing' not in kws:
            try:
                kws['missing'] = self.components[0].missing
            except:
                pass
            
        def _tmp(self, *args, **kws):
            pass
        Model.__init__(self, _tmp, **kws)

        for side in self.components:
            prefix = side.prefix
            for basename, hint in side.param_hints.items():
                self.param_hints["%s%s" % (prefix, basename)] = hint


    def _model_convert(self, test_obj):
        """ Convert into an ``lmfit`` Model object.
        """

        if type(test_obj) != Model:
            
            try:
                return Model(test_obj)
            except:
                raise TypeError('Cannot convert to a model.')
        
        else:
            return test_obj
            
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
        """ All parameter names in a multipeak model.
        """
        
        return self.multi_retrieve('param_names', op=operator.add)

    @property
    def components(self):
        """ All components for a multipeak model.
        """
        
        if self.lineshape:
            components = [self.lineshape.func(prefix=self.preftext+str(i+1)+'_') for i in range(self.nlp)]
        elif self.model:
            components = self.model.components
            self.nlp = len(self.model.components)
        
        # Introduce a background function
        if self.background:
            try:
                components += self.background.components
                self.nbg = len(self.background.components)
            except:
                bg_comp = list(self.background)
                components += bg_comp
                self.nbg = len(bg_comp)
        
        return components
    
    @property
    def ncomp(self):
        """ Number of components for a multipeak model.
        """
        
        return len(self.components)

    @property
    def prefixes(self):
        """ Collection of prefixes for all lineshape components.
        """

        prefs = [self.components[i].prefix for i in range(self.ncomp)]
        return prefs
    
    def eval(self, params=None, **kwargs):
        """ Evaluate the entire model.
        """
        
        return reduce(self.op, [comp.eval(params=params, **kwargs) for comp in self.components])
        # return reduce(self.op, map(lambda comp: comp.eval(params=params, **kwargs), self.components, pm_parallel=True))

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
        """ Evaluate multiple components with a defined operator using map-reduce operation, returns a list.

        **Parameters**\n
        op: func
            Functional operator used to reduce the terms.
        objs: iterable
            Collection of objects to evaluate on.
        fevs: iterable (list/tuple of functions)
            Collection of functions to map to objects.
        *args: arguments
            Additional arguments for the mapped function (every entry in ``fevs``).
        **kwargs: keyword arguments
            Additional keyword arguments for the mapped function (every entry in ``fevs``).
        """
        
        return reduce(op, map(lambda obj, fev: fev(obj, *args, **kwargs), objs, fevs))
    
    def multi_retrieve(self, prop, op=operator.add):
        """ Retrieve the specified properties for all components in the multipeak model.

        **Parameters**\n
        prop: str
            Namestring of the property to retrieve.
        op: func | operator.add
            Functional operator used to reduce the terms.
        """
        
        return self.multi_eval(op, self.components, [getattr]*self.ncomp, prop)