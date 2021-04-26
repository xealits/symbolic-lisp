from sym_lis3 import GlobalEnv
import pytest


@pytest.mark.parametrize("noneref", [
    ("None", None),
])
def test_none(noneref):
    g = GlobalEnv()
    assert g.eval_str(noneref[0]) is noneref[1]

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

def test_not_found_name():
    g = GlobalEnv()
    with pytest.raises(NameError):
        g.eval_str('foo')

def test_foo():
    g = GlobalEnv()
    var_foo_addr = g.eval_str('(define "foo" (lambda (x y) (+ 2 (+ x y))))')
    assert g.eval_str('foo') is var_foo_addr

@pytest.fixture
def define_foo():
    g = GlobalEnv()
    g.eval_str('(define "foo" (lambda (x y) (+ 2 (+ x y))))')
    g.eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))')
    return g

@pytest.mark.parametrize("foo_inp, foo_res", [
    ((4, 2), 8),
    ((5, 2), 9),
    ((13, 7), 22),
])
def test_define(define_foo, foo_inp, foo_res):
    g = define_foo
    assert g.eval_str('(foo %d %d)' % foo_inp) == foo_res

def test_concat_symbols():
    g = GlobalEnv()
    assert g.eval_str('(+ (quote foo) (quote _bar))') == 'foo_bar'

def test_define_dynamic(define_foo):
    g = define_foo
    g.eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))')
    assert callable(g.eval_str('foo_bar'))

def test_define_dynamic_eval(define_foo):
    g = define_foo
    assert g.eval_str('(foo_bar 4 2)') == g.eval_str('(foo 4 2)')

def test_set():
    g = GlobalEnv()
    g.eval_str('(define "x" 5)')
    assert g.eval_str('x') == 5
    g.eval_str('(set! "x" 111)')
    assert g.eval_str('x') == 111

def test_set_dyn_name():
    g = GlobalEnv()
    g.eval_str('(define (+ "foo" "1") 5)')
    assert g.eval_str('foo1') == 5
    g.eval_str('(set!   (+ "foo" "1") 111)')
    assert g.eval_str('foo1') == 111

def test_set_not_found_name():
    g = GlobalEnv()
    g.eval_str('(define "x" 5)')

    assert 'x'     in g
    assert 'y' not in g

    g.eval_str('(set! "x" 1)')
    with pytest.raises(NameError):
        g.eval_str('(set! "y" 35)')

@pytest.mark.parametrize("test_input,expected", [
  ('(if 1 4 2)', 4),
  ('(if 0 4 2)', 2),
])
def test_if(test_input, expected):
    g = GlobalEnv()
    assert g.eval_str(test_input) == expected
