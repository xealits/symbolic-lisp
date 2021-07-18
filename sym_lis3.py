# symbolic lisp 3: a lisp interpreter in Python

## based on Peter Norvig's [Lispy](http://norvig.com/lispy.html)

from __future__ import division
import math
import operator as op
import logging
import pdb
from os.path import isfile

import sys
from sys import exit

from sym_parse import List, Number, Int, String, Symbol, parse, lispstr


################ Environments

def source_file(env, filename):
    '''source_file(env, filename)

    env where the source in filename will be executed
    '''

    filename = str(filename)
    assert isfile(filename)
    assert isinstance(env, Env)

    with open(filename) as f:
        script = f.read()

        val = env.eval_str(script)
        if val is not None:
            print(lispstr(val))

def make_env(*keys_vals):
    if len(keys_vals) == 0:
        return Env()
    elif len(keys_vals) == 2:
        return Env(keys_vals[0], keys_vals[1])
    else:
        raise ValueError("wrong number of values to unpack for make_env (expected 0 or 1)")

def curry_func(func, *args):
    # TODO: this will not work for DIY env-based functions! make them callable?
    assert callable(func)
    return lambda *more_args: func(*(args + more_args))

def assert_check(var):
    assert var

def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    #env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        'exit': exit,
        '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>': op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        #'apply':   apply,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     lambda *x: List(map(*x)),
        'format':  lambda f, *x: f % x,
        'curry':   curry_func,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'callable?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'string?': lambda x: isinstance(x, String),
        'in?':     lambda e, x: x in e,
        'is?':     lambda x, y: x is y,
        'type?':   type,
        '_sys':    sys,
        '_getattr': lambda x, attr: getattr(x, attr),
        'print':   lambda *x: print(*x),
        'newlineit': lambda x: str(x).replace('\\n', '\n'),
        'debug':   lambda *x: logging.debug(*x),
        'None':    None,
        'str':     str,
        'join':    lambda d, l: d.join([str(x) for x in l]),
        'double_quote': '"',
        'single_quote': "'",
        'in':      lambda env, key: env[key],
        'out':     lambda env:      env.outer,
        'env':     make_env,
        'find':    lambda env, varname: env.find(varname),
        'find?':   lambda env, varname: env.find_env(varname) is not None,
        'nest':    lambda env_out, env_nested: env_nested.set_outer(env_out),
        'source':  source_file,
        'eval':    lambda env, var: lisp_eval(var, env), # for double-eval
        'assert':  lambda bool_val: assert_check(bool_val), # TODO: if not, print lisp stack?
    })
    return env

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, keys=(), vals=(), outer=None):
        self.update(zip(keys, vals))
        self.outer = outer

    def find_env(self, var, not_found_raises=False):
        "Find the innermost Env where var appears."

        if var in self:
            return self
        elif self.outer is None:
            if not_found_raises:
               raise NameError("Lisp could not find env with %s" % var)
            return None
        else:
            return self.outer.find_env(var)

    def find(self, name):
        "Find the name or handle not found case."

        var_env = self.find_env(name)

        if var_env is None:
            # not found name handler hook
            if "not_found" in self:
                return self["not_found"](name)

            # else - exception
            raise NameError("Lisp could not find %s" % name)

        else:
            return var_env[name]

    def set_outer(self, outer_env):
        self.outer = outer_env
        return self

class GlobalEnv(Env):

    def __init__(self, env=None):
        '''Initialize an independent global environment.

        env = None or Env class
            the initial state of the global environment
        '''

        # make an empty Env
        super().__init__()

        # populate it with defaults
        self.update(standard_env())
        # populate with root namespace
        self["root_env"] = self

    def eval(self, x):
        return lisp_eval(x, self)

    def eval_str(self, string):
        res = None
        exprs = parse(string)

        for i, expr in enumerate(exprs):
            try:
                # this will never work, because lisp_eval catches the exception
                # but it would be good to get it working
                # because this place has reference to the rest of the source code
                res = self.eval(expr)

            except Exception as e:
                # print the previous expressions in the string
                for prev_expr in exprs[:i]:
                    print(prev_expr, file=sys.stderr)

                # and the current one with some stack?
                print(expr, file=sys.stderr)

                raise e

        return res

################ Procedures

def call_env(env, args):
    return lisp_eval(env['_body'], Env(env['_args'], args, env))

class Procedure(Env):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        #self.parms, self.body, self.env = parms, body, env
        super().__init__(('_args', '_body'), (parms, body), env)
    def __call__(self, *args): 
        return lisp_eval(self['_body'], Env(self['_args'], args, self))

class Macro(Procedure):
    pass

################ eval

def lisp_eval(x, env=None):
    "Evaluate an expression in an environment."

    try:

        if isinstance(x, Symbol):      # variable reference
            if x == 'dyn_env':
                return env
            return env.find(x)

        elif not isinstance(x, List):  # constant literal
            return x                

        elif x[0] in ('quote', "'"):          # (quote exp)
            (_, exp) = x
            return exp

        elif x[0] == 'if':             # (if test conseq alt)
            (_, test, conseq, alt) = x
            exp = (conseq if lisp_eval(test, env) else alt)
            return lisp_eval(exp, env)

        elif x[0] == 'define':         # (define var exp)
            if len(x) == 3:
                (_, var_exp, exp) = x
                where_env = env
            elif len(x) == 4:
                (_, where_env_expr, var_exp, exp) = x
                where_env = lisp_eval(where_env_expr, env)
            else:
                raise ValueError("wrong number of values to unpack for define (expected 3 or 4)")

            var = lisp_eval(var_exp, env) # dynamic name
            where_env[var] = lisp_eval(exp, env)
            return where_env[var]

        elif x[0] == 'set!':           # (set! var exp)
            (_, var_exp, exp) = x
            var = lisp_eval(var_exp, env) # dynamic name
            var_env = env.find_env(var, not_found_raises=True)
            var_env[var] = lisp_eval(exp, env)
            return var_env[var]

        elif x[0] == 'lambda':         # (lambda (var...) body)
            (_, parms, body) = x
            return Procedure(parms, body, env)

        elif x[0] == 'macro':         # (lambda (var...) body)
            (_, parms, body) = x
            return Macro(parms, body, env)

        else:                          # (proc arg...)
            proc = lisp_eval(x[0], env)

            # do not eval the inputs for macro
            if isinstance(proc, Macro):
                args = x[1:]
            # eval for regular labdas
            else:
                args = [lisp_eval(exp, env) for exp in x[1:]]

            if isinstance(proc, Env) and "_args" in proc and "_body" in proc:
                return call_env(proc, args)
            return proc(*args)

    except Exception as e:
        # print the current call tree
        #print('---------- CURRENT CALL TREE ----------', file=sys.stderr)
        print(x, file=sys.stderr)

        #curr_env = env
        #nesting = 1
        #while curr_env is not None:

        #    print("  "*nesting + str(curr_env.keys()), file=sys.stderr)
        #    nesting += 1
        #    curr_env = curr_env.outer

        raise e
