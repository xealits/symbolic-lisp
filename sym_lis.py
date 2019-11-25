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

class SymNamespace(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None, dynamic_namespace=None):
        self.update([("_dynamic_namespace", dynamic_namespace)])
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

global_namespace = SymNamespace()

################ Procedures

class SymbolicProcedure(object):
    "A user-defined procedure."
    def __init__(self, parms, body, lexical_namespace, macro=False):
        self.parms, self.body, self.lexical_namespace = parms, body, lexical_namespace
        self.macro = macro
        '''
        here lexical_namespace is the lexical environment where this procedure is defined
        body is a list (proc a b c)
        can be (begin (foo a b c) ...)
        '''

    def __call__(self, *args, _dynamic_namespace=None): 
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

        if self.macro:
          # immediately eval argument names
          args = [sym_eval(i, _dynamic_namespace) for i in args]
          logging.debug('macro call: params=%s\nargs=%s\n%s' % (repr(self.parms), repr(args), repr(_dynamic_namespace)))
          call_namespace = SymNamespace(self.parms, args,
            outer = _dynamic_namespace)
        else:
          call_namespace = SymNamespace(self.parms, args,
            outer = self.lexical_namespace,
            dynamic_namespace = _dynamic_namespace)
        return sym_eval(self.body, call_namespace)

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

def sym_repl(prompt='sym_lis> '):
    "A prompt-read-eval-print loop."
    while True:
        user_inp = raw_input(prompt)
        if not user_inp:
            continue

        # run eval on user's program
        #val = eval(parse(user_inp))
        val = sym_eval(parse(user_inp))
        if val is not None: 
            print(lispstr(val))

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

################ eval

def var_name(var):
    assert isinstance(var, Symbol)
    return var.split('/')[-1]

__sym_eval_counter = 0
def sym_eval(x, _dynamic_namespace=global_namespace):
    """sym_eval(x, _dynamic_namespace=global_namespace)

    Parse basic elements:
    x = string -- treat it as a name, look up the corresponding value in the current _dynamic_namespace
    x = int    -- return it
    x = [list] -- sym_eval the first position and call it with the rest
                  if the first position is int
                  look for a list in the seocnd argument and return the element from the list
                  or return the int

    Find a symbol in a _dynamic_namespace or the first symbol of a list."""

    global __sym_eval_counter
    logging.debug('%3d: %s' % (__sym_eval_counter, repr(x)))
    __sym_eval_counter += 1

    if 'x' in _dynamic_namespace: logging.debug('sym_eval _dynamic_namespace["x"] = %s' % _dynamic_namespace['x'])

    if isinstance(x, Symbol):
        if _dynamic_namespace.find(x):
            return _dynamic_namespace.find(x)[var_name(x)]
        else:
            logging.debug('Symbol %s not found' % repr(x))
            return x

    elif not isinstance(x, List):  # constant literal
        return x

    # a list
    elif x[0] == 'quote':          # (quote exp)
        #_, exp = x
        #return exp
        return x[1:]

    elif x[0] == 'begin':
        return [sym_eval(i, _dynamic_namespace) for i in x[1:]][-1]

    # elementary lists
    elif x[0] == 'sym_define':
        _, var, exp = x
        var = var if isinstance(var, Symbol) else sym_eval(var, _dynamic_namespace) # dynamic names
        val = sym_eval(exp, _dynamic_namespace)
        logging.debug('sym_define: %s = %s' % (repr(var), repr(val)))
        _dynamic_namespace[var] = val

    # the usual eval
    elif x[0] == 'eval':
        #assert len(x) > 1 # (eval something)
        _, expr = x
        if not isinstance(expr, List):
            return sym_eval(expr, _dynamic_namespace)
        else:
            # pre-eval args
            args = [sym_eval(i, _dynamic_namespace) for i in expr[1:]]
            logging.debug('pre-eval-ed args: %s' % repr(args))
            # and call
            return sym_eval([expr[0]]+args, _dynamic_namespace)

    elif x[0] == 'if':
        _, test, conseq, alt = x
        exp = conseq if sym_eval(test, _dynamic_namespace) else alt
        return sym_eval(exp, _dynamic_namespace)

    elif x[0] == 'macro':
        _, parms, body = x
        logging.debug('macro procedure')
        #return SymbolicProcedure(parms, body, lexical_namespace=_dynamic_namespace)
        return SymbolicProcedure(parms, body, lexical_namespace=_dynamic_namespace, macro=True)

    elif x[0] == 'lambda':
        _, parms, body = x
        logging.debug('lambda procedure')
        return SymbolicProcedure(parms, body, lexical_namespace=_dynamic_namespace)

    # couple special lists
    else:
        logging.debug('calling symbolic first_symbol: %s' % repr(x[0]))
        first_symbol = sym_eval(x[0], _dynamic_namespace)
        logging.debug('eval-ed symbolic first_symbol: %s' % repr(first_symbol))

        # elementary options
        if isinstance(first_symbol, int):
            rest = x[1:]
            return rest[first_symbol]
            # or should I eval it?

        # here I can insert handling 1-element list of name ["name"]
        # to eval the value instead of doing it by default

        # user procedures
        elif callable(first_symbol):
            res = first_symbol(*x[1:], _dynamic_namespace=_dynamic_namespace)
            logging.debug('res: %s' % repr(res))
            return res

        else:
            print("not callable symbol: %s" % repr(first_symbol))


def sym_binary_operator(oper):
    def bin_oper(a, b, _dynamic_namespace=None):
        return oper(a, b)
    return bin_oper

#def begin(*args, _dynamic_namespace):
#    return [sym_eval(i) for i in args][-1]

def standard_nsp():
    "An environment with some Scheme standard procedures."
    nsp = SymNamespace()
    nsp.update(vars(math)) # sin, cos, sqrt, pi, ...
    nsp.update({
        #'+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        #'add': lambda (a, b): op.add(a, b),
        'add': sym_binary_operator(op.add),
        'sub': sym_binary_operator(op.sub),
        'mul': sym_binary_operator(op.mul),
        'div': sym_binary_operator(op.truediv),

        #'+': lambda
        #'-': lambda
        #'*': lambda
        #'/': lambda

        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        #'apply':   apply,
        #'begin':   lambda *x: [sym_eval(i) for i in x][-1],
        #'begin':   begin,
        #'begin':   lambda *x: x[-1],
        # (begin (add 1 2) (sub 3 4))
        # ((add 1 2) (sub 3 4))
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y, _dynamic_namespace: [x] + y,
        'fjoin':   lambda x, y, _dynamic_namespace: sym_eval(x + [sym_eval(y, _dynamic_namespace=_dynamic_namespace)], _dynamic_namespace=_dynamic_namespace),
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x, _dynamic_namespace: list(x),
        'list?':   lambda x: isinstance(x,list),
        #'map':     map,
        'map':     lambda x: map(basic_eval(x[0]), x[1:]),
        #(basic_eval (map basic_eval (foo bar)))
        #'eval':    lambda x, _dynamic_namespace: sym_eval(list(map(sym_eval, x))),
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
    return nsp

global_namespace.update(standard_nsp())


passed_tests = [
#'(+ 1 2)',
'(add 1 2)',
'(add foobar _bazzzz)',
'(add (add 1 2) (add 3 4))',
'(sym_define + (lambda (x y) (eval (add (eval (eval x)) (eval (eval y))))))',
'(+ 1 2)',
'(+ (+ 11 28) 2)',
'(+ (+ 11 28) (mul 1 2))',
]

'''
how would a usual pre-eval function work?

(func (params) (body))
->
(lambda (params) (eval (body with (eval (eval param)))))

-- not trivial parsing
better to use begin
'''

'(sym_define eeval (macro (x) (eval (eval x))))',

tests = [
'(cons 5 (1 2 3))',
'(add 3 4)',
'(fjoin (list) (add 3 4))',
'(fjoin (cons 5) (fjoin (list) (add 3 4)))',
]

tests = tests_begin_crash = [
'(sym_define eeval (macro (x) (fjoin (eval) (eval x))))',
'(sym_define ++ (lambda (x y) (begin (sym_define x (eeval x)) (sym_define y (eeval y)) (eval (add x y)))))',
'(++ 1 2)',
'(++ (++ 11 28) 2)',
'(++ (++ 11 28) (mul 1 2))',
]

[
]

tests_more = [
'(define + (lambda (x y) (eval (add (eval (eval x)) (eval (eval y))))))',
'(+ 1 2)',
'(+ (+ 11 28) 2)',
'(begin ((add 1 2) (add 3 4)))',
'''(define ++ (lambda (x y)
    (begin ((set! x (eval (eval x))) (set! y (eval (eval y))) (eval (add x y))))
    ))''',
'(++ 1 2)',
'(++ (++ 11 28) 2)',
]

#'begin':   lambda *x: x[-1],
# (begin (add 1 2) (sub 3 4))
# ((add 1 2) (sub 3 4))
#'(define + (lambda (x y) (eval (add (eval (eval x)) (eval (eval y))))))',

# (define + (lambda (x y) (eval add x y)))
# TODO: now local namespace does not work
#       because it calls things in the lexical scope of `add`, not in `+`!!!


def test(eval_proc=sym_eval):
    for t in tests:
        val = eval_proc(parse(t))
        if val is not None: 
            print("%40s = %s" % (t, lispstr(val)))

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
        test(sym_eval)
    else:
        #repl()
        sym_repl()

