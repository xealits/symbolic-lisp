# Symbolic Lisp
# (c) Alex Toldaiev, 2019
# https://github.com/xealits/symbolic-lisp

from collections import UserString
import logging
import re

import math
import operator as op
from sys import exit
import pdb

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

############ LISP itself

# a fast name look up Namespace class
class Namespace(dict):
    "A namespace: a dict of {'var':val} pairs, with an outer Namespace."
    def __init__(self, names=(), values=(), outer=None):
        self.update(zip(names, values))
        self.outer = outer

    def __str__(self):
        "Pretty nsp repr"

        all_nsps = []
        nsp = self
        indent = 0
        while nsp is not None:
            all_nsps.append('\t'*indent + str(nsp.keys()))
            nsp = nsp.outer
            indent += 1

        return '\n'.join(all_nsps)

    def call_stack(self):
        "list of nsp names that led to this one"

        if self.outer is None:
            return ['root_nsp']
        else:
            my_name = None
            for name, obj in self.outer.items():
                if obj is self:
                    my_name = name
                    break

            return self.outer.call_stack() + [str(my_name)]

        pdb.set_trace()

    def find(self, var):
        "Find the innermost Namespace where var appears."
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise NameError(f"Cannot find {var}")

    def nsp_keys(self):
        if self.outer is None:
            return self.keys()
        else:
            return self.keys(), self.outer.nsp_keys()

def lisp_eval2(x, nsp=None):
    """Evaluate an expression in a namespace.

    If no namespace is given, evaluate in a blank namespace.
    """

    if nsp is None:
        nsp = Namespace()

    logging.debug(str(nsp.call_stack())) # stack of nsp names up to current

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
        logging.debug("LOG index %s" % str((x[2], ind, l)))
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

            #TODO: it breaks stuff because defines in the nested _dyn are discarded
            call_dyn = nsp # Namespace(outer = nsp.get('_dyn', nsp))
            call_nsp = Namespace(('_args', '_dyn'), (args, call_dyn), symb)
            ##call_nsp = Namespace(('_args',), (args,), symb)
            ##call_nsp['_dyn'] = Namespace(outer = call_nsp)

            """
            в чём разница между call_nsp & _dyn?
            call_nsp <- symb lexical space
            _dyn     <- eval namespace

            -- where _dyn does not nest properly,
            instead it creates _dyn: {_dyn: {_dyn: ...}} nesting.
            It must be a pointer to another, properly nested Namespace.
            """

            if '_proc' in symb:
                proc = symb['_proc']

                r = None
                for p in proc: # TODO: this is a fixed control flow - must be programmable
                    r = lisp_eval2(p, call_nsp)
                return r

            # Python extensions do not have a call_nsp
            # because they do not have a lexical namespace within Lisp
            # they are completely dynamic for Lisp
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
        logging.debug(f'eval {x[1]} = {r}')
        return r
'''

def lisp_eval_str(string, env=None):
    res = None
    for expr in parse(string):
        res = lisp_eval2(expr) if env is None else lisp_eval2(expr, env)
    return res

def proc_eval(in_nsp_exp, expr, _dyn=None):
    in_namespace = lisp_eval2(in_nsp_exp, _dyn)
    r = lisp_eval2(expr, in_namespace)
    logging.debug(f'eval in_namespace {in_nsp_exp} = {in_namespace.nsp_keys()}')
    logging.debug(f'eval {expr} = {r}')
    return r

proc_eval_nsp = Namespace()
proc_eval_nsp['_callable'] = proc_eval

def proc_eval2(in_nsp_exp, expr, _dyn=None):
    in_namespace = lisp_eval2(in_nsp_exp, _dyn)
    var_name     = lisp_eval2(expr,       _dyn)
    r = lisp_eval2(var_name, in_namespace)
    logging.debug(f'''eval2 in_namespace {in_nsp_exp} = {in_namespace.nsp_keys()}
      {expr} = {var_name}
      {r}''')
    return r

proc_eval2_nsp = Namespace()
proc_eval2_nsp['_callable'] = proc_eval2

def proc_do(*args, _dyn=None):
    r = None
    for arg in args:
        logging.debug('do', arg)
        r = lisp_eval2(arg, _dyn)

    return r

proc_do_nsp = Namespace()
proc_do_nsp['_callable'] = proc_do

# def proc_eval_explicit(in_nsp_exp, expr, _dyn=None):
# let's make it always dynamic
def proc_eval_explicit(expr, _dyn=None):
    #in_namespace = lisp_eval2(in_nsp_exp, _dyn)
    in_namespace = _dyn

    # if the list starts with `eval` -- launch the usual eval
    # if not -- recurse into child lists
    if isinstance(expr, List) and len(expr) > 0:
        if expr[0] == 'eval_explicit':
            r = lisp_eval2(expr[1], in_namespace)
        else:
            r = list(map(lambda x: proc_eval_explicit(x, _dyn), expr))
    else:
        r = expr

    #logging.debug(f'eval_explicit in_namespace = {in_namespace.nsp_keys()}')
    #logging.debug(f'eval_explicit {expr} = {r}')
    return r

proc_eval_explicit_nsp = Namespace()
proc_eval_explicit_nsp['_callable'] = proc_eval_explicit

# (define var exp [in_nsp])
def proc_define(var_exp, exp, in_nsp=None, _dyn=None):
    assert _dyn is not None

    #pdb.set_trace()

    nsp = _dyn
    if in_nsp is None:
        in_nsp = nsp
    else:
        in_nsp = lisp_eval2(in_nsp, nsp)

    # eval here
    var_name = lisp_eval2(var_exp, nsp) 
    var_val  = lisp_eval2(exp, nsp)
    # define, optionally, in another namespace
    logging.debug('define: %s = %s' % (str(var_name), str(var_val)))
    in_nsp[var_name] = var_val

proc_define_nsp = Namespace()
proc_define_nsp['_callable'] = proc_define

def proc_map(expr, list_expr, _dyn=None):
    logging.debug(f'map _dyn = {_dyn.nsp_keys()}')
    l = lisp_eval2(list_expr, _dyn)
    assert isinstance(l, List)

    #
    if isinstance(expr, Symbol): expr = [expr]
    r = [lisp_eval2(expr + [arg], _dyn) for arg in l]

    logging.debug(f'map {expr} on {l} = {r}')
    return r

proc_map_nsp = Namespace()
proc_map_nsp['_callable'] = proc_map

def proc_source(*args, _dyn=None):
    logging.debug('proc_source: args, _dyn: %s\n%s' % (str(args), str(_dyn)))

    env = _dyn # lisp_eval2(where_to, _dyn)
    logging.debug('proc_source: env: %s', str(env))

    filenames = [lisp_eval2(exp, env) for exp in args]
    logging.debug('proc_source: filenames: %s', str(filenames))

    results = []
    for fname in filenames:
        with open(fname.data) as f:
            file_program = f.read()

            logging.debug('proc_source: file_program: %s', file_program)
            res = lisp_eval_str(file_program, env)
            results.append(res)

    return results

proc_source_nsp = Namespace()
proc_source_nsp['_callable'] = proc_source

def repr_double_quote(obj):
    r = repr(obj)
    return f'"{r[1:-1]}"' if isinstance(obj, String) else r

def standard_nsp():
    "An environment with some Scheme standard procedures."
    nsp = Namespace()
    nsp.update({
        #'root_nsp': nsp, # TODO: it does not work now, it is not updated with defines
        'exit':      exit,
        '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>': op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'sum': sum,
        'equal?':  op.eq, 
        'length':  len, 
        'print':  print,
        'debug':  lambda *x: logging.debug(' '.join([str(i) for i in x])),
        'type':  type,
        'eval':   proc_eval_nsp,
        'eval2':  proc_eval2_nsp,
        'eval_explicit':  proc_eval_explicit_nsp,
        'define': proc_define_nsp,
        'map': proc_map_nsp,
        'list?':   lambda x: isinstance(x, List), 
        'None': None,
        'do': proc_do_nsp,
        'nsp_keys': lambda x:      x.nsp_keys(),
        'in':       lambda nsp, x: nsp[x],
        'repr':   repr_double_quote,
        'source': proc_source_nsp,
        'symbol?': lambda x: isinstance(x, Symbol),
        'join':    lambda s, l: s.join(l),
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
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
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

        # populate with root namespace
        self["root_nsp"] = self

    def eval(self, x):
        return lisp_eval2(x, self)

    def eval_str(self, string):
        res = None
        for expr in parse(string):
            res = self.eval(expr)
        return res

