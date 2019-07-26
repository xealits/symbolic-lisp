################ Lispy: Scheme Interpreter in Python

## (c) Peter Norvig, 2010-16; See http://norvig.com/lispy.html

from __future__ import division
import math
import operator as op
from sys import stderr

import argparse
import logging
import pdb

################ Types

Symbol = str          # A Lisp Symbol is implemented as a Python str
List   = list         # A Lisp List is implemented as a Python list
Number = (int, float) # A Lisp Number is implemented as a Python int or float

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

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        # TODO: make a hook for top-most names to embed into shell or python
        if (var in self):
            return self
        elif self.outer is None:
            return None
        else:
            return self.outer.find(var)

global_env = Env()
################ Interaction: A REPL

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        user_inp = raw_input(prompt)
        if not user_inp:
            continue

        # run eval on user's program
        #val = eval(parse(user_inp))
        val = basic_eval(parse(user_inp))
        if val is not None: 
            print(lispstr(val))

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

################ Procedures

class SymbolicProcedure(object):
    "A user-defined procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
        '''
        here env is the lexical environment where this procedure is defined
        body is a list (proc a b c)
        can be (begin (foo a b c) ...)
        '''

    def __call__(self, callerenv_n_args): 
        '''
        body is evaluated in the lexical env extended with defined local parameters
        here I need
        1) a caller env
        2) pass it to the body as some arg __caller_env
        3) be able to run eval of arguments in the __caller_env

        for 3) eval must go into the language and envs must get names?
        must envs get structure and dict go into the language too?
        or there is some hack to avoid all of this and sneek in caller env?

        like double body -- one is perfomed in caller's env, the other is in lexical

        (caller_env, args) = callerenv_n_args
        eval(self.body_caller, Env(self.parms, args, caller_env)) # <-- here
        # something is made in this env, evaluated etc, bound to parameters
        # which are passed to the next step
        return eval(self.body_lexical, Env(self.parms, args, self.env))

        -- weird

        so I need Env with 1 special parameter, a link to callers env, which is used only in eval
        maybe lets make "eval_at_caller"?

        yeah... eval itself must be configurable...
        and define with produced env-s...
        '''

        (caller_env, args) = callerenv_n_args
        # make a function which runs eval at caller_env
        # and pass it as an additional argument
        return eval(self.body, Env(self.parms, args, self.env))

class Procedure(object):
    "A user-defined Scheme^WSymbolic procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, args): 
        #return eval(self.body, Env(self.parms, args, self.env))
        return basic_eval(self.body, Env(self.parms, args, self.env))

################ eval

def var_name(var):
    assert isinstance(var, Symbol)
    return var.split('/')[-1]

def basic_eval(x, env=global_env):
    "Find a symbol in an environment or the first symbol of a list."

    logging.debug('x: %s' % repr(x))

    # constants
    #if isinstance(x, Symbol):      # symbol is considered a literal
    #    return x
    #elif not isinstance(x, List):  # constant literal
    #    return x                
    # actually, not lists are constants

    # TODO: there is a confusion with refering to variables
    # I made passing symbols first-class
    # but now `eval` does not `get` the variables
    if isinstance(x, Symbol):
        if env.find(x):
            return env.find(x)[var_name(x)]
        else:
            logging.debug('Symbol %s not found' % repr(x))
            return x

    elif not isinstance(x, List):  # constant literal
        return x
    elif isinstance(x, List) and len(x) == 0:
        return x

    # if, execution branching
    #elif x[0] == 'if':             # (if test conseq alt)
    # if assumes execution of the test expression
    # here just check for truth
    elif x[0] == 'True?':          # (True? test conseq alt)
        if bool(x[1]):
            return basic_eval(x[2])
        else:
            return basic_eval(x[3])

    # TODO: there is a confusion with passing parameters or lists
    # (basic_eval 1 2 3) =? (basic_eval [1 2 3])?
    # here is to resolve it quickly:
    # basic_eval takes only 1 argument!
    elif x[0] == 'basic_eval':
        return basic_eval(x[1], env)
    # eval evaluates each part of the list in current env
    # and launches the first symbol with the results
    # also, it must do it in recursion for the whole call tree...
    # and it stops at evaluating arguments, which contain the call tree...
    elif x[0] == 'eval':
        # eval also has only 1 argument
        #first_symbol = x[1]
        #args = x[]
        ##pdb.set_trace()
        #for arg in x[2:]:
        #    evaluated_arg = basic_eval(arg, env)
        #    args.append(evaluated_arg)
        #    #args.append(eval(arg, env))
        #evaluated_call = [first_symbol] + args
        if isinstance(x[1], List):
            args = [basic_eval(exp, env) for exp in x[1]]
        else:
            args = x[1]
        # eval x translates to basic_eval x
        logging.debug("eval call: %s" % repr(args))
        return basic_eval(args, env)

    # namespace manipulation
    elif x[0] == 'get':      # variable reference
        var = basic_eval(x[1])
        if isinstance(var, Symbol):
            return env.find(var)[var_name(var)]
        #     variable can be /absolute/name/space/name
        else:
            #print("not supported object for variable reference: %s" % repr(x[1]), file=stderr)
            print("not supported object for variable reference: %s" % repr(x[1]))
        # TODO x[1] can be not a symbol
    elif x[0] == 'set!':
        # (set! var exp)
        # var is either in current namespace,
        # or an absolute name /global/name/space/var
        (_, var_exp, exp) = x
        var = basic_eval(var_exp)
        env.find(var)[var_name(var)] = basic_eval(exp, env)

    # TODO make define a part of set! ?
    elif x[0] == 'define':
        #(_, var, exp) = x
        #env[var] = eval(exp, env)
        (_, var_exp, exp) = x
        var = basic_eval(var_exp)
        env[var] = basic_eval(exp, env)

    # User's procedures
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
        # it calls basic_eval on body in the env extended with params
        # TODO so, it works in lexical scope of the definition! add namespaces!
        # but if you keep everything global there is no difference

    # a user's list call
    else:                          # (proc arg...)
        first_symbol = basic_eval(x[0], env)
        logging.debug('calling first_symbol %s: %s' % (repr(x[0]), repr(first_symbol)))
        # usually it must return a callable procedure
        # but here I extend this to 3 types:
        # a ready procedure
        # or a symbol -- find the procedure
        # or a number -- repeate the following as a call itself

        # TODO: these proc calls need current and lexical name spaces!
        if callable(first_symbol):
            logging.debug('calling procedure: %d with %s' % (id(first_symbol), x[1:]))
            #logging.debug('environment of the call: %s' % repr(first_symbol.env))
            return first_symbol(x[1:])
        elif isinstance(first_symbol, Symbol):
            proc = env.find(first_symbol)[first_symbol]
            logging.debug('found proc %d with params x[1:]: %s' % (id(proc), repr(x[1:])))
            res = proc(x[1:])
            logging.debug('result %s' % repr(res))
            return res
        elif isinstance(first_symbol, int):
            logging.debug('calling number: %s' % repr(first_symbol))
            last_value = None
            for i in range(first_symbol):
                basic_eval(x[1:])
            return last_value
        else:
            #print("absolutely not callable object: %s" % repr(first_symbol), file=stderr)
            print("absolutely not callable object: %s" % repr(first_symbol))
        # TODO: can a list be callable?
        #elif isinstance(first_symbol, list):


def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x                
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        # in case it is a list (proc arg...)
        # find the symbol proc
        proc = eval(x[0], env)
        # evaluate args
        args = [eval(exp, env) for exp in x[1:]]
        # instead make an eval procedure for current env
        #caller_eval = Procedure(
        # call the symbol proc with evaluated arguments
        return proc(*args)


def binary_operator(oper):
    return lambda (a, b): oper(a, b)

def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        #'+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        #'add': lambda (a, b): op.add(a, b),
        'add': binary_operator(op.add),
        'sub': binary_operator(op.sub),
        'mul': binary_operator(op.mul),
        'div': binary_operator(op.truediv),

        #'+': lambda
        #'-': lambda
        #'*': lambda
        #'/': lambda

        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   apply,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        #'map':     map,
        'map':     lambda x: map(basic_eval(x[0]), x[1:]),
        #(basic_eval (map basic_eval (foo bar)))
        #'eval':    lambda x: basic_eval(map(basic_eval, x)),
        'basic_eval': basic_eval, # not defined
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'exit': lambda _: exit(),
    })
    return env

global_env.update(standard_env())

tests = [
#'(+ 1 2)',
'(add 1 2)',
'(define + (lambda (x y) (eval (add (eval (eval x)) (eval (eval y))))))',
'(+ 1 2)',
'(+ (+ 11 28) 2)',
]

# (define + (lambda (x y) (eval add x y)))
# TODO: now local namespace does not work
#       because it calls things in the lexical scope of `add`, not in `+`!!!


def test():
    for t in tests:
        val = basic_eval(parse(t))
        if val is not None: 
            print(lispstr(val))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = "run tests and start repl",
        epilog = """Example:\nrlwrap python lis_sym.py\nrlwrap python lis_sym.py --debug"""
        )

    parser.add_argument("--debug",  action='store_true', help="DEBUG level of logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    test()
    repl()

