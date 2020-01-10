import pytest
from sym_lis import GlobalEnv


@pytest.fixture
def define_foo_bar_env():
    g = GlobalEnv()
    var_foo  = g.eval_str("(define foo  (env (quote ('foo 5)) (quote (3 7))))")
    var_foo2 = g.eval_str("(define foo2 (env (quote  (foo 5)) (quote (3 7))))")
    var_bar  = g.eval_str("(define bar (env_anonymous (quote ('foo 5)) (quote (3 7))))")
    var_baz  = g.eval_str("(define bar/baz (env_anonymous (quote ('foo 5)) (quote (3 7))))")
    var_globalvar = g.eval_str("(define globalvar 55)")
    return g, (var_foo, var_foo2, var_bar, var_baz, var_globalvar)

def test_var(define_foo_bar_env):
    g, (var_foo, var_foo2, var_bar, var_baz, var_globalvar) = define_foo_bar_env
    assert g.eval_str('foo')  is var_foo
    assert g.eval_str('foo2') is var_foo2
    assert g.eval_str('bar')  is var_bar
    assert g.eval_str('/bar/baz')  is var_baz

    assert g.eval_str("(foo 3)") == 7
    assert g.eval_str("(bar 3)") == 7

@pytest.mark.parametrize("ref,expected", [
  ("(foo 'globalvar)", 55),
  ("(bar 'globalvar 1)", 1),
])
def test_global(define_foo_bar_env, ref, expected):
    g, _ = define_foo_bar_env
    assert g.eval_str(ref) == expected

@pytest.mark.parametrize("ref", [
  ("(bar     'globalvar)"),
  ("(bar/baz 'globalvar)"),
  ("(foo 333)"),
])
def test_noglobal(define_foo_bar_env, ref):
    g, _ = define_foo_bar_env
    assert g.eval_str(ref) is None

@pytest.mark.parametrize("expr, result", [
  ("(in? (quote (3 7)) 3)", True),
  ("(in? (quote (4 7)) 3)", False),
  ("(in? foo 3)", True),
  ("(in? foo (quote 'foo))", True),
  ('(in? foo2 (quote foo))', True),
])
def test_in(define_foo_bar_env, expr, result):
    g, _ = define_foo_bar_env
    assert g.eval_str(expr) is result

