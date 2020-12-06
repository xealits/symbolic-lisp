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

def lisp_eval2(x, nsp=None):
    """Evaluate an expression in a namespace.

    If no namespace is given, evaluate in a blank namespace.
    """

    if nsp is None:
        nsp = {}

    if isinstance(x, Symbol):          # name reference
        if x == '.': return nsp        # current namespace
        elif x[0] == "'": return x[1:] # quoted name
        else:
            found_nsp = nsp.find(x)
            return found_nsp [x]

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
        return lisp_eval2(l[x[0]], nsp) # to eval
        #return l[x[0]]  # or not to eval

    elif x[0] == 'index':
        ind = x[1]
        assert isinstance(ind, Int)
        l = lisp_eval2(x[2], nsp)
        assert isinstance(l, list)
        return l[ind]  # or not to eval

    # setting names in current namespace
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

    elif x[0] == 'quote':
        return x[1]

    elif x[0] == 'list':
        args = [lisp_eval2(a, nsp) for a in x[1:]]
        return args

    # and my procedure call protocol
    else:
        symb = lisp_eval2(x[0], nsp)
        args = x[1:]

        if isinstance(symb, Namespace):
            assert '_proc' in symb or '_callable' in symb
            # custom procedure, a _proc or a callable
            '''
            _proc is a [list] of calls
            it is evaluated sequencially
            in a Namespace derived from lexical nsp of symb
            with 2 dynamic definitions:
              _args, which are not pre-evaled
              _dyn, which points to the current, dynamic nsp
            '''
            call_nsp = Namespace(('_args', '_dyn'), (args, nsp), symb)

            if '_proc' in symb:
                proc = symb['_proc']

                r = None
                for p in proc: # TODO: this is a fixed control flow - must be programmable
                    r = lisp_eval2(p, call_nsp)
                return r

            elif '_callable' in symb:
                return symb['_callable'](*args, _dyn=nsp)

        # calls to Python extensions
        elif callable(symb):
            args = [lisp_eval2(exp, nsp) for exp in args]
            return symb(*args)
            '''
            and the contact with nsp is gone
            but the eval forms do need nsp
            (and so do the user forms)
            that's the fundamental difference
            which forces me to constantly extend eval
            instead of adding simple callables in the global namespace
            at the same time
            eval forms must be exported into the global namespace somehow
            to be used in user macros
            the callable form is a natural choice, but it collides with
            the requirement that callables can only be functional
            - let's try exporting eval forms as user forms!
            '''
            """
            def callable_in_dyn_eval_namespace(symb, args):
                _dyn = nsp
                return symb(*args)
            return callable_in_dyn_eval_namespace(symb, args)
            """

        else:
            # TODO temporary work-around, figure out if this is indeed a special case
            # lookup-eval
            return lisp_eval2(symb, nsp)
            raise ValueError(f'unknown custom call {symb} from {x}')

'''
so a normal function will have to
1) know its interface, the list of var names
2) loop through it and the _args
3) define-ing each var name to the eval-ed expression in _args
'''

'''
    elif x[0] == 'eval':
        assert 1 < len(x) < 4
        in_namespace = lisp_eval2(x[2], nsp) if len(x) == 3 else nsp
        r = lisp_eval2(x[1], in_namespace)
        print(f'eval {x[1]} = {r}')
        return r
'''

def proc_eval(expr, in_nsp_exp, _dyn=None):
    in_namespace = lisp_eval2(in_nsp_exp, _dyn)
    r = lisp_eval2(expr, in_namespace)
    print(f'eval in_namespace {in_nsp_exp} = {in_namespace}')
    print(f'eval {expr} = {r}')
    return r

proc_eval_nsp = Namespace()
proc_eval_nsp['_callable'] = proc_eval

# (define var exp [in_nsp])
def proc_define(var_exp, exp, in_nsp=None, _dyn=None):
    assert _dyn is not None
    nsp = _dyn
    if in_nsp is None:
        in_nsp = nsp
    else:
        in_nsp = lisp_eval2(in_nsp, nsp)

    # eval here
    var_name = lisp_eval2(var_exp, nsp) 
    var_val  = lisp_eval2(exp, nsp)
    # define, optionally, in another namespace
    print('define:', var_name, var_val)
    in_nsp[var_name] = var_val

proc_define_nsp = Namespace()
proc_define_nsp['_callable'] = proc_define

def standard_nsp():
    "An environment with some Scheme standard procedures."
    nsp = Namespace()
    nsp.update({
        '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>': op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'sum': sum,
        'equal?':  op.eq, 
        'length':  len, 
        'print':  print,
        'type':  type,
        'eval':  proc_eval_nsp,
        'define': proc_define_nsp,
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
        elif isinstance(env, Namespace):
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

