# Symbolic Lisp
# (c) Alex Toldaiev, 2019
# https://github.com/xealits/symbolic-lisp

from collections import UserString
import logging
import re

import math
import operator as op

# Types
#class List(list):
#    """A Lisp List is implemented as a Python list"""
#    pass
#    implement slicing or just use Python's list
List = list

class String(UserString):
    pass

class Symbol(UserString):
    pass

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
    if isinstance(token, String):
        return token
    try: return Int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

############ LISP itself

# a fast name look up Namespace class
class Namespace(dict):
    "A namespace: a dict of {'var':val} pairs, with an outer Namespace."
    def __init__(self, names=(), values=(), outer=None):
        self.update(zip(names, values))
        self.outer = outer
    def find(self, var):
        "Find the innermost Namespace where var appears."
        return self if (var in self) else self.outer.find(var)

def lisp_eval2(x, nsp={}):
    """Evaluate an expression in a namespace.

    If no namespace is given, evaluate in a blank namespace.
    """

    if nsp is None:
        nsp = {}

    if isinstance(x, Symbol):        # variable reference
        if x[0] == "'": return x[1:] # quoted variable
        else:
            return nsp.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x                

    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if lisp_eval2(test, nsp) else alt)
        return lisp_eval2(exp, nsp)

    # getting stuff from List
    elif x[0] == 'head':
        l = lisp_eval2(x[1], nsp)
        assert isinstance(l, List)
        return lisp_eval2(l[0], nsp)
    elif x[0] == 'tail':
        l = lisp_eval2(x[1], nsp)
        assert isinstance(l, list)
        return lisp_eval2(l[1:], nsp)
    elif isinstance(x[0], Int):
        l = lisp_eval2(x[1], nsp)
        assert isinstance(l, list)
        return lisp_eval2(l[x[0]], nsp)

    # setting names in current namespace
    elif x[0] == 'define':         # (define var exp)
        (_, var_exp, exp) = x
        var_name = lisp_eval2(var_exp, nsp)
        nsp[var_name] = lisp_eval2(exp, nsp)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var_exp, exp) = x
        var_name = lisp_eval2(var_exp, nsp)
        nsp.find(var_name)[var_name] = lisp_eval2(exp, nsp)
    elif x[0] == 'get':            # (get nsp varname_exp)
        nsp, var = lisp_eval2(x[1], nsp), lisp_eval2(x[2], nsp)
        return nsp.find(var)[var]

    # preparation for meta-call
    elif x[0] == 'nsp':
        (_, names, values) = x
        names, values = lisp_eval2(names, nsp), lisp_eval2(values, nsp)
        return Namespace(names, values, nsp)

    elif x[0] == 'eval':
        r = lisp_eval2(x[1], nsp)
        return r
    elif x[0] == 'quote':
        return x[1]

    # and my procedure call protocol
    else:
        symb = lisp_eval2(x[0], nsp)
        args = x[1:]

        if isinstance(symb, Namespace):
            assert '_proc' in symb # caustom procedure
            '''
            _proc is a [list] of calls
            it is evaluated sequencially
            in a Namespace derived from lexical nsp of symb
            with 2 dynamic definitions:
              _args, which are not pre-evaled
              _dyn, which points to the current, dynamic nsp
            '''
            proc = symb['_proc']
            call_nsp = Namespace(('_args', '_dyn'), (args, nsp), symb)

            r = None
            for p in proc:
                r = lisp_eval2(p, call_nsp)
            return r

        # calls to Python extensions
        elif callable(symb):
            args = [lisp_eval2(exp, nsp) for exp in args]
            return symb(*args)

'''
so a normal function will have to
1) know its interface, the list of var names
2) loop through it and the _args
3) define-ing each var name to the eval-ed expression in _args
'''

def standard_nsp():
    "An environment with some Scheme standard procedures."
    nsp = Namespace()
    nsp.update({
        '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'equal?':  op.eq, 
        'length':  len, 
        'print':  print,
        'type':  type,
        })
    """
        'abs':     abs,
        'append':  op.add,  
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
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    nsp.update(vars(math)) # sin, cos, sqrt, pi, ...
    """
    return nsp

class GlobalEnv(Namespace):

    def __init__(self, env=None):
        '''Initialize an independent global environment.

        env = None or Namespace class
            the initial state of the global environment
        '''

        # make an empty Env
        super().__init__()

        # populate it with defaults
        if env is None:
            self.update(standard_nsp())
        elif isinstance(env, Env):
            self.update(env)
        else:
            raise TypeError("wrong content for GlobalEnv: %s" % repr(env))

    def eval(self, x):
        return lisp_eval2(x, self)

    def eval_str(self, string):
        res = None
        for expr in parse(string):
            res = self.eval(expr)
        return res

