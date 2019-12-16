'''
add_tests([
"(None)",
'(+ 1 2)',
'(+ (+ 11 28) 2)',
'(+ (+ 11 28) (* 1 2))',
'(+ (list 1 2 3) (list 34 3 2))',
'(define foo (lambda (x y) (+ 2 (+ x y))))',
'(foo 4 2)',
'(+ (quote foo) (quote _bar))',
'(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))',
'(foo_bar 4 2)',
], name='passed_tests')
'''

from nsp_lis import lisp_eval_str
import pytest


def test_no_tokens():
    with pytest.raises(SyntaxError):
        lisp_eval_str("")

@pytest.mark.parametrize("noneref", [
    ("(None)"),
])
def test_none(noneref):
    assert lisp_eval_str(noneref) is None


@pytest.mark.parametrize("test_input,expected", [
    ("(+ 1 2)", 3),
    ("(+ (+ 11 28) 2)", 41),
    ("(+ (+ 11 28) (* 1 2))", 41),
])
def test_calc1(test_input, expected):
    assert lisp_eval_str(test_input) == expected

def test_add_lists():
    assert lisp_eval_str('(+ (list 1 2 3) (list 34 3 2))') == lisp_eval_str('(list 1 2 3 34 3 2)')

@pytest.fixture
def redefine_foo():
    lisp_eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')

#def test_define_0():
#    assert lisp_eval_str('(foo 4 2)') == 8

def test_define(redefine_foo):
    assert lisp_eval_str('(foo 4 2)') == 8

def test_define2(redefine_foo):
    assert lisp_eval_str('(foo 5 2)') == 9

def test_concat_symbols():
    assert lisp_eval_str('(+ (quote foo) (quote _bar))') == 'foo_bar'

def test_define_dynamic():
    assert callable(lisp_eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))'))

def test_define_dynamic_eval():
    assert lisp_eval_str('(foo_bar 4 2)') == lisp_eval_str('(foo 4 2)')

