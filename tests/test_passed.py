from sym_lis import GlobalEnv
import pytest


@pytest.mark.parametrize("noneref", [
    ("(None)"),
])
def test_none(noneref):
    g = GlobalEnv()
    assert g.eval_str(noneref) is None


@pytest.mark.parametrize("test_input,expected", [
    ("(+ 1 2)", 3),
    ("(+ (+ 11 28) 2)", 41),
    ("(+ (+ 11 28) (* 1 2))", 41),
])
def test_calc1(test_input, expected):
    g = GlobalEnv()
    assert g.eval_str(test_input) == expected

def test_add_lists():
    g = GlobalEnv()
    assert g.eval_str('(+ (list 1 2 3) (list 34 3 2))') == g.eval_str('(list 1 2 3 34 3 2)')

@pytest.fixture
def define_foo():
    g = GlobalEnv()
    g.eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')
    g.eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))')
    return g

#def test_define_0():
#    assert g.eval_str('(foo 4 2)') == 8

def test_define(define_foo):
    g = define_foo
    assert g.eval_str('(foo 4 2)') == 8

def test_define2(define_foo):
    g = define_foo
    assert g.eval_str('(foo 5 2)') == 9

def test_concat_symbols():
    g = GlobalEnv()
    assert g.eval_str('(+ (quote foo) (quote _bar))') == 'foo_bar'

def test_define_dynamic():
    g = GlobalEnv()
    assert callable(g.eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))'))

def test_define_dynamic_eval(define_foo):
    g = define_foo
    assert g.eval_str('(foo_bar 4 2)') == g.eval_str('(foo 4 2)')

@pytest.mark.parametrize("test_input,expected", [
  ('(if 1 4 2)', 4),
  ('(if 0 4 2)', 2),
])
def test_if(test_input, expected):
    g = GlobalEnv()
    assert g.eval_str(test_input) == expected
