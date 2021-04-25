# symbolic lisp 3: a lisp interpreter in Python

## based on Peter Norvig's [Lispy](http://norvig.com/lispy.html)

from __future__ import division
import math
import operator as op
import re
from collections import UserString
import logging
import pdb

from sys import exit

################ Types

# A Lisp Symbol is implemented as a Python str
class Symbol(UserString):
    pass

class String(UserString):
    pass

List   = list         # A Lisp List is implemented as a Python list
Number = (int, float) # A Lisp Number is implemented as a Python int or float

class Int(int):
    pass

################ Parsing: parse, tokenize, and read_from_tokens

def parse(program):
    "Read a Scheme expression from a string."
    return read_all_from_tokens(tokenize(program))

# the reg for the "-quoted strings
string_pattern = re.compile(r'\"([^"]+?)\"')
def tokenize(s):
    '''Convert a string into a list of tokens.

    an example:
    >>> tokenize('foo (a   b "bar (baz d)" z "seven (7 two)" ab (foo jaz ))')
    ['foo' '(' 'a' 'b' "bar (baz d)" 'z' "seven (7 two)" 'ab' '(' 'foo' 'jaz' ')' ')']
    '''
    # tokenize the text between the strings
    tokens = []
    prev_char = 0
    for m in string_pattern.finditer(s):
        mstart, mend = m.span()
        prev_toks = s[prev_char: mstart].replace('(',' ( ').replace(')',' ) ').split()
        tokens.extend(prev_toks + [String(m.group()[1:-1])]) # tokens and String
        prev_char = mend
    # the last chunk of the input string
    tokens += s[prev_char:].replace('(',' ( ').replace(')',' ) ').split()
    return tokens

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
            if len(tokens) == 0: # unclosed expression
                report_expr = lispstr(L_one_expr)[:-1] + ' _!)_'
                raise(IndexError(f'Unclosed expression {report_expr}'))
        tokens.pop(0) # pop off ')'
        # TODO the rest of tokens could be used for literate documentation
        # for now would nice to just run them in sequence
        # but it breaks
        #if nesting==0 and tokens:
        #    #
        #    raise SyntaxError('unexpected continuation %s' % lispstr(tokens))
        return L_one_expr
    elif ')' == token:
        raise SyntaxError(f'Unexpected ) before tokens {tokens}')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    if isinstance(token, String):
        return token
    try: return Int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

################ Environments

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
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'callable?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'in?':     lambda x, e: x in e,
        'is?':     lambda x, y: x is y,
        'type?':   type,
        'print':   lambda *x: print(*x),
        'None':    None,
    })
    return env

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        #pdb.set_trace()
        if var in self:
            return self
        elif self.outer is None:
            # not found name handler hook
            if "not_found" in self:
                return self["not_found"](var)
            raise NameError("Lisp could not find %s" % var)
            return None
        else:
            return self.outer.find(var)

global_env = standard_env()
class GlobalEnv(Env):

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

        # populate with root namespace
        self["root_env"] = self

    def eval(self, x):
        return lisp_eval(x, self)

    def eval_str(self, string):
        res = None
        for expr in parse(string):
            res = self.eval(expr)
        return res

################ Procedures

class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return lisp_eval(self.body, Env(self.parms, args, self.env))

################ eval

def lisp_eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        if x == 'dyn_env':
            return env
        return env.find(x)[x]
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
        (_, var_exp, exp) = x
        var = lisp_eval(var_exp, env) # dynamic name
        env[var] = lisp_eval(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = lisp_eval(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = lisp_eval(x[0], env)
        args = [lisp_eval(exp, env) for exp in x[1:]]
        return proc(*args)
