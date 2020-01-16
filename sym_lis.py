# Symbolic Lisp
# (c) Alex Toldaiev, 2019
# https://github.com/xealits/symbolic-lisp

from __future__ import division
import math
import operator as op

from collections import OrderedDict, UserString

import importlib
import re
from sys import stdout, exit
import logging
import pdb
import traceback

################ Types

class List(list):
    """A Lisp List is implemented as a Python list"""

    pass

re_repetitions = re.compile(r"(/)\1{1,}", re.DOTALL)
class Symbol(UserString):

    def no_repeated_slashes(self):
        self.data = re_repetitions.sub(r"\1", self.data)

    def split(self, char):
        # just convert the output to Symbols again
        return [Symbol(s) for s in self.data.split(char)]

class Int(int):
    pass

#Number = (int, float) # A Lisp Number is implemented as a Python int or float

################ Parsing: parse, tokenize, and read_from_tokens

def parse(program):
    "Read a Scheme expression from a string."
    return read_all_from_tokens(tokenize(program))

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').split()

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

def read_all_from_tokens(tokens):
    '''Read all ()-closed expressions from tokens.'''

    all_expr = []
    while tokens:
        an_expr = read_from_tokens(tokens)
        # read_from_tokens pops the expression from tokens
        all_expr.append(an_expr)

    return all_expr

def read_from_tokens(tokens, nesting=0):
    """Read one expression from a sequence of tokens.

    An expression is either a List or an atom."""

    token = tokens.pop(0)
    # parse one nesting
    if '(' == token:
        L_one_expr = List()
        while tokens[0] != ')':
            L_one_expr.append(read_from_tokens(tokens, nesting+1))
        tokens.pop(0) # pop off ')'
        # TODO the rest of tokens could be used for literate documentation
        # for now would nice to just run them in sequence
        # but it breaks
        #if nesting==0 and tokens:
        #    #
        #    raise SyntaxError('unexpected continuation %s' % lispstr(tokens))
        return L_one_expr
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return Int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

################ Environments

def _note(note, obj):
    obj.note = note
    return obj

def standard_env():
    """An environment with some standard functional procedures.

    These procedures do not have the access to the dynamical environment of
    eval."""

    env = Env()
    #env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        #'apply':   apply, # no apply in python3
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        # list-ing the map objects in Python3
        'map':     lambda *x: list(map(*x)),
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'int?':    lambda x: isinstance(x, int),
        'float?':  lambda x: isinstance(x, float),
        'number?': lambda x: isinstance(x, (int, float)),
        'env?' :   lambda x: isinstance(x, Env),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'exit':    exit,
        'None':    lambda : None,
        'in?':     lambda nsp, y: y in nsp,
        'get':     lambda nsp, x: nsp(x),
        'get_default':     lambda nsp, x, d: nsp(x, default=d),
        'stdout': lambda *x: print(*x),
        '_note':  _note,
        'obj':   lambda x: x.note if 'note' in dir(x) else None,
        'par_l':  '(',
        'par_r':  ')',
        'join':   lambda *x: ''.join(str(i) for i in x),
    })
    return env

def standard_name_path_list(name_path):
    # a variable name
    assert isinstance(name_path, Symbol)

    name_path.no_repeated_slashes()
    if name_path[-1] == '/':
        name_path = name_path[:-1]
    return name_path.split('/')

def standard_missing_name_handler(varname):
    #raise NameError("name '%s' is not defined" %varname)
    #raise TypeError("name '%s' is not defined" %varname)
    return None

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

        # all global environments (anonymous are the same)
        # have the handler for missing names
        if self.outer is None:
            self['_missing_handler'] = standard_missing_name_handler

    def find_global_env(self):
        if self.outer is None:
            return self
        else:
            return self.outer.find_global_env()

    def bubble_find(self, var):
        "Find the outermost Env where var appears."
        if var in self:
            return self
        elif self.outer:
            return self.outer.bubble_find(var)
        else:
            # the case when there is no such variable
            # return self again
            # request of the missing key will call the programmable handler
            return self

    def __missing__(self, varname):
        return self['_missing_handler'](varname)

    def find(self, name_path):
        """Find the outermost Env where name_path appears and return the variable from the name_path.
        Return the global Env if not found."""

        #name_path = standard_name_path_list(name_path)
        # if the name path is empty
        if not name_path: return self

        # bubble the root part of the name up to the outermost
        start_name = name_path[0]

        if   start_name == '':
            start_env = self.find_global_env()
            # and remove the root name
            name_path = name_path[1:]
        elif start_name == '.':
            start_env = self
        elif start_name == '..':
            start_env = self # self.outer
        else:
            #return self if (var in self) else self.outer.bubble_find(var)
            start_env = self.bubble_find(start_name) #[start_name] # it must be another env
            # the path is not found
            if start_env is None: return None
            assert isinstance(start_env, Env)

        # nest down the name path
        for name in name_path[:-1]:
            if   name == '.':
                continue
            elif name == '..':
                start_env = start_env.outer
            else:
                start_env = start_env[name]

        # the final environment
        #return start_env if name_path[-1] in start_env else None # return None if no such name is defined
        #return start_env[name_path[-1]] # or crash
        return start_env

    def __call__(self, key, default=None):
        #return self[key] # TODO: now it is only the current namespace, expand?
        if not isinstance(key, Symbol):
            return self.get(key, default)

        name_path = standard_name_path_list(key)
        var_name = name_path[-1]
        path     = name_path
        located_var = self.find(path)

        # not found variable
        if var_name not in located_var:
            return default

        return located_var[var_name]

################ Procedures

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.outer = parms, body, env
    def __call__(self, *args): 
        return lisp_eval(self.body, Env(self.parms, args, outer=self.outer))

################ eval

def lisp_eval(x, env=None):
    """Evaluate an expression in an environment.

    If no environment is given, evaluate in a blank environment.
    """

    if env is None:
        env = standard_env()

    if isinstance(x, Symbol):      # variable reference
        # quote symbols
        if len(x) > 1 and x[0] == "'":
            return x[1:]

        # else it is a name path
        name_path = standard_name_path_list(x)
        var_name = name_path[-1]
        path     = name_path
        return env.find(path)[var_name]

    elif not isinstance(x, List):  # constant literal, like None
        return x                

    # in the rest x is List
    # first cases when x[0] is a keyword
    # they cannot be dynamically generated TODO: change it?
    # it seems this is the spot of the dynamic name scope
    # defined functions operate in their lexical scope
    # (they are defined into the lexical scope)
    # the keywords have access to the current namespace

    # same as look-up but with set at the end
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x

        name_path = standard_name_path_list(var)
        var_name = name_path[-1]
        path     = name_path
        env.find(path)[var_name] = lisp_eval(exp, env)

    elif x[0] == 'env':
        nsp = Env(outer=env)
        args = [lisp_eval(exp, env) for exp in x[1:]]
        nsp.update(args)
        return nsp

    elif x[0] == 'env_anonymous':
        nsp = Env()
        args = [lisp_eval(exp, env) for exp in x[1:]]
        nsp.update(args)
        return nsp

    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if lisp_eval(test, env) else alt)
        return lisp_eval(exp, env)

    elif x[0] == 'define':         # (define var exp)
        (_, name_path, exp) = x

        # dynamic names in define
        if isinstance(name_path, List):
            name_path = lisp_eval(name_path, env)

        name_path = standard_name_path_list(name_path)
        var_name = name_path[-1]
        path     = name_path[:-1]

        # nest down the path creating env-s
        nested_env = env
        for name in path:
            if   name == '':
                nested_env = nested_env.find_global_env()
            elif name in nested_env:
                assert isinstance(nested_env[name], Env)
                nested_env = nested_env[name]
            else:
                new_env = Env(outer=nested_env)
                nested_env[name] = new_env
                nested_env = new_env

        # but eval expr in the original Env of define!
        var = lisp_eval(exp, env)
        #var = lisp_eval(exp, nested_env)

        # the result is attached in the nested chain of env-s
        nested_env[var_name] = var
        # if the result is an env and it is not anonymous
        # set the outer to the nested chain of env-s
        attach_scope  = isinstance(var, Env) and var.outer is not None
        attach_scope |= isinstance(var, Procedure)
        if attach_scope:
            var.outer = nested_env

        return var

    elif x[0] == 'source':
        filenames = [lisp_eval(exp, env) for exp in x[1:]]
        results = []
        for fname in filenames:
            with open(fname.data) as f:
                file_program = f.read()
                res = lisp_eval_str(file_program, env)
                results.append(res)
        return results

    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = lisp_eval(x[0], env)
        if isinstance(proc, int):
            # convenience
            _, a_list = x
            args = lisp_eval(a_list, env)
            #pdb.set_trace()
            return args[proc]
        else:
            # proc must be a callable
            args = [lisp_eval(exp, env) for exp in x[1:]]
            return proc(*args)


def lisp_eval_str(string, env=None):
    res = None
    for expr in parse(string):
        res = lisp_eval(expr) if env is None else lisp_eval(expr, env)
    return res

class PythonPlugins(Env):
    '''Import external modules and call their contents.
    '''

    def __init__(self):
        '''Creates an empty global Env with 2 procedures: import and get.'''

        # make an empty Env
        super().__init__()

        self['import'] = self.imp
        self['get'] = self.get

    def imp(self, modname):
        assert isinstance(modname, Symbol)
        self[modname] = importlib.import_module(modname.data)

    def get(self, objpath):
        # DANGER: is there is a safer way to do it?
        assert isinstance(objpath, Symbol)
        return eval(objpath.data, globals(), self)


class GlobalEnv(Env):
    '''The behavior of a global environment.

    The important part is the global state.
    That is what needs to be encapsulated,
    lisp_eval is simply added to it with no reciprocal dependency.

    Hence, define the logic of the global state:
    the Env and the lisp eval methods attached.
    '''

    def __init__(self, env=None):
        '''Initialize an independent global environment.

        env = None or Env class
            the initial state of the global environment
        '''

        # make an empty Env
        super().__init__()

        # populate it with defaults
        if env is None:
            self.update(standard_env())
        elif isinstance(env, Env):
            self.update(env)
        else:
            raise TypeError("wrong content for GlobalEnv: %s" % repr(env))

        # also add the python plugins
        self['_Python'] = PythonPlugins()

    def eval(self, x):
        return lisp_eval(x, self)

    def eval_str(self, string):
        res = None
        for expr in parse(string):
            res = self.eval(expr)
        return res

