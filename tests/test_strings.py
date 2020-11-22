import pytest
from sym_lis import GlobalEnv


def test_foo():
    g = GlobalEnv()
    var_foo_addr = g.eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')
    assert g.eval_str('foo') is var_foo_addr

@pytest.mark.parametrize('var_name, val', [
  ("foo", 'foo bar (bax c d) and ( more a b) brr t'),
  ("bar", "foo (bar baz)"),
])
def test_quotes(var_name, val):
    g = GlobalEnv()
    g.eval_str('(define %s "%s")' % (var_name, val))
    assert g.eval_str(var_name) == val

def test_print_parentheses():
    g = GlobalEnv()
    assert g.eval_str("(+ par_l (+ 'foo par_r))") == '(foo)'

@pytest.mark.parametrize('test_input, expected', [
  ("(join str_empty (list 'data par_l 'foo par_r))", "data(foo)"),
  ("(join ',        (list 'data par_l 'foo par_r))", "data,(,foo,)"),
])
def test_join_string(test_input, expected):
    g = GlobalEnv()
    assert g.eval_str(test_input) == expected
