################ Lispy: Scheme Interpreter in Python

## (c) Peter Norvig, 2010-16; See http://norvig.com/lispy.html

from __future__ import division
import math
import operator as op

import re
from sys import stdout, exit
import argparse
import logging
import pdb

################ Types

Symbol = str          # A Lisp Symbol is implemented as a Python str
List   = list         # A Lisp List is implemented as a Python list
#Number = (int, float) # A Lisp Number is implemented as a Python int or float

################ Parsing: parse, tokenize, and read_from_tokens

def parse(program):
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').split()

def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

################ Environments

def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
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
        'map':     map,
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
    })
    return env

re_repetitions = re.compile(r"(/)\1{1,}", re.DOTALL)
def no_repeated_slashes(string):
    return re_repetitions.sub(r"\1", string)

def standard_name_path_list(name_path):
    # a literal
    if not isinstance(name_path, Symbol):
        return name_path

    # a variable name
    name_path = no_repeated_slashes(name_path)
    if name_path[-1] == '/':
        name_path = name_path[:-1]
    return name_path.split('/')

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def bubble_find(self, var):
        "Find the outermost Env where var appears."
        return self if (var in self) else (self.outer.bubble_find(var) if self.outer is not None else None)

    def find(self, name_path):
        """Find the outermost Env where name_path appears and return the variable from the name_path."""

        #name_path = standard_name_path_list(name_path)
        # if the name path is empty
        if not name_path: return self

        # bubble the root part of the name up to the outermost
        start_name = name_path[0]

        if   start_name == '':
            start_env = global_env
        elif start_name == '.':
            start_env = self
        elif start_name == '..':
            start_env = self.outer
        else:
            #return self if (var in self) else self.outer.bubble_find(var)
            start_env = self.bubble_find(start_name) #[start_name] # it must be another env
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
        return start_env if name_path[-1] in start_env else None

    def nest(self, name_path):
        """Nest env-s from the current env or its outer. 
        """

        name_path = standard_name_path_list(name_path)
        start_name = name_path[0]

        # the starting env, no bubbling up to the outermost
        if   start_name == '':
            start_env = global_env
        elif start_name == '.':
            start_env = self
        elif start_name == '..':
            start_env = self.outer

    def __call__(self, key, default=None):
        #return self[key] # TODO: now it is only the current namespace, expand?
        if not isinstance(key, Symbol):
            return self[key]

        name_path = standard_name_path_list(key)
        var_name = name_path[-1]
        path     = name_path
        return self.find(path)[key] if key in self.find(path) else default

global_env = standard_env()

################ Interaction: A REPL

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None: 
            print(lispstr(val))

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

################ Procedures

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, outer=self.env))

################ eval

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        # quote symbols
        if len(x) > 1 and x[0] == "'":
            return x[1:]

        # else it is a name path
        name_path = standard_name_path_list(x)
        var_name = name_path[-1]
        path     = name_path #[:-1]
        return env.find(path)[var_name]

    elif not isinstance(x, List):  # constant literal, like None
        return x                

    # in the rest x is List

    # same as look-up but with set at the end
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x

        name_path = standard_name_path_list(name_path)
        var_name = name_path[-1]
        path     = name_path #[:-1]
        env.find(path)[var_name] = eval(exp, env)

    elif isinstance(x[0], int):       # convenience
        return x[x[0]]

    elif isinstance(x[0], Env):
        nsp, key = x
        #return nsp[key] # TODO: get absolute or relative name!
        name_path = standard_name_path_list(key)
        var_name = name_path[-1]
        path     = name_path
        return nsp.find(path)[var_name]

    elif x[0] == 'env':
        #nsp = Env(outer=env)
        nsp = Env() # TODO: it is a completely anonymous env now, should it be like that or should it attach in the lexical structure?
        args = [eval(exp, env) for exp in x[1:]]
        nsp.update(args)
        return nsp

    elif x[0] == 'env_attached':
        nsp = Env(outer=env)
        #nsp = Env() # TODO: it is a completely anonymous env now, should it be like that or should it attach in the lexical structure?
        args = [eval(exp, env) for exp in x[1:]]
        nsp.update(args)
        return nsp

    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)

    elif x[0] == 'define':         # (define var exp)
        (_, name_path, exp) = x

        # dynamic names in define
        if isinstance(name_path, List):
            name_path = eval(name_path, env)

        name_path = standard_name_path_list(name_path)
        var_name = name_path[-1]
        path     = name_path[:-1]

        # nest down the path
        for name in path:
            if   name == '':
                env = global_env
            elif name in env:
                assert isinstance(env[name], Env)
                env = env[name]
            else:
                new_env = Env(outer=env)
                env[name] = new_env
                env = new_env

        env[var_name] = eval(exp, env) # TODO: define at an absolute or relative name!

    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)


passed_tests = [
'(+ 1 2)',
'(+ (+ 11 28) 2)',
'(+ (+ 11 28) (* 1 2))',
'(+ (list 1 2 3) (list 34 3 2))',
'(define foo (lambda (x y) (+ 2 (+ x y))))',
'(foo 4 2)',
'(+ (quote foo) (quote _bar))',
'(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))',
'(foo_bar 4 2)',
]

test_string_quote = [
'(define foo (lambda (x y) (+ 2 (+ x y))))',
"foo",
"'foo",
"(define (+ 'foo '_bar) (lambda (x y) (+ 2 (+ x y))))",
'(foo_bar 4 2)',
]

tests_iterations = [
"(1 'foo 'bar 77)",
"(3 'foo 'bar 77)",
"(5 'foo 'bar 77)",
]

tests_namespaces = [
"(quote (env (quote 'foo 5) (quote 3 7)))",
"(env (quote ('foo 5)) (quote (3 7)))",
"(env? (env (quote ('foo 5)) (quote (3 7))))",
"((env (quote ('foo 5)) (quote (3 7))) 3)",
]

tests_namespaces_nested = [
"(env (quote ('foo 5)) (quote (3 7)))",
"(define foo (env (quote ('foo 5)) (quote (3 7))))",
"foo",
"/foo",
"/./foo",
"./foo",
"././foo",
"(define foo/bar/baz 55)",
"foo",
"(foo 'bar)",
"foo/bar",
"foo/bar/",
"((foo 'bar) 'baz)",
"foo/bar/baz",
"(+ foo/bar/baz 33)",
]

tests = tests_namespaces_attached = [
"None",
"(None)",
"(define foo  (env (quote ('foo 5)) (quote (3 7))))",
"(define foo2 (env (quote  (foo 5)) (quote (3 7))))",
"(define bar (env_attached (quote ('foo 5)) (quote (3 7))))",
"(define bar/baz (env_attached (quote ('foo 5)) (quote (3 7))))",
"(define globalvar 55)",
"foo",
"bar",
"(foo 3)",
"(bar 3)",
"(bar 'globalvar)",
"(bar 'baz)",
"((bar 'baz) 'globalvar)",
"(in? (quote (3 7)) 3)",
"(in? (quote (4 7)) 3)",
"(in? foo  3)",
"(in? foo  'foo)",
"(in? foo2 'foo)",
"(get_default foo 'globalvar 1)",
"(get foo 'globalvar)",
"(get foo 3)",
"(foo 'globalvar)",
]


def test(eval_proc=eval):
    for t in tests:
        stdout.write("%40s " % t)
        val = eval_proc(parse(t))
        if val is not None: 
            print("= %s" % lispstr(val))
        else:
            print("  None")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "run tests and start repl",
        epilog = """Example:\nrlwrap python lis_sym.py\nrlwrap python lis_sym.py --debug"""
        )

    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")
    parser.add_argument("--test",   action='store_true', help="just run tests")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.test:
        test()
    else:
        repl()
        #sym_repl()

