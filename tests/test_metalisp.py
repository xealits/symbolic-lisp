from sym_lis2 import GlobalEnv as Env
import pytest


'''
@pytest.mark.parametrize("test_input,expected", [
    ("(+ 1 2)", 3),
    ("(+ (+ 11 28) 2)", 41),
    ("(+ (+ 11 28) (* 1 2))", 41),
])
def test_calc1(test_input, expected):
    g = Env()
    assert g.eval_str(test_input) == expected
'''

def test_defines():
    g = Env()

    g.eval_str('(define "foo" "bar")')
    assert g.eval_str('foo') == 'bar'

    g.eval_str('(define "bar" 5)')
    assert g.eval_str('bar') == 5

    g.eval_str('(define "baz" (nsp (quote ("a")) (quote ("b"))))')
    assert g.eval_str('baz') == {'a': 'b'}

def test_procedure():
    g = Env()
    g.eval_str('(define "echo" (nsp (quote ("_proc")) (quote (((eval _args))))))')
    assert g.eval_str('(echo foo bar)') == ['foo', 'bar']

def test_integer_arithmetics():
    g = Env()
    assert g.eval_str('(+ 1 2)') == 3
    assert g.eval_str('(+ 33 (+ 1 2))') == 36
    assert g.eval_str('(* 1 2)') == 2
    assert g.eval_str('(* 33 (+ 1 2))') == 99

def test_dyn_scope():
    g = Env()
    g.eval_str('''(define "sum_typ"
            (nsp (quote ("_proc")) (quote ((
              (print _args)
              (print (type _args))
              (+ (0 _args) (1 _args))
            )))))''')
    assert g.eval_str('(sum_typ 1 2)') == 3
    assert g.eval_str('(sum_typ 33 (sum_typ 1 2))') == 36

    g.eval_str('''(define "sum_lex"
            (nsp (quote ("_proc")) (quote ((
              (+ foo bar)
            )))))''')
    g.eval_str("(define 'foo 1)")
    g.eval_str("(define 'bar 2)")
    assert g.eval_str('(sum_lex)') == 3

    g.eval_str('''(define 'sum_dyn
            (nsp (quote ("_proc")) (quote ((
              (print _dyn)
              (+ (get _dyn "foo") (get _dyn "bar"))
            )))))''')
    g.eval_str('''(define 'sum_wrapper
            (nsp (quote ("_proc")) (quote ((
              (define 'foo 30)
              (define 'bar 6)
              (print _dyn)
              (sum_dyn)
            )))))''')
    assert g.eval_str('(sum_wrapper)') == 36


def test_basic_func():
    g = Env()
    #g.eval_str('''(define sumup
    #  (nsp ("_proc") (
    #    (define counter (head (eval _args)))
    #    (define rest (tail (eval _args)))
    #    (if (eq? (len rest) 0)
    #      counter
    #      (sumup () ())) )))''')
    assert g.eval_str('(+ 1 2)') == 3
    assert g.eval_str('(+ 33 (+ 1 2))') == 36

