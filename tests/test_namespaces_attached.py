'''
add_tests([
"(define foo  (env (quote ('foo 5)) (quote (3 7))))",
"(define foo2 (env (quote  (foo 5)) (quote (3 7))))",
"(define bar (env_attached (quote ('foo 5)) (quote (3 7))))",
"(define bar/baz (env_attached (quote ('foo 5)) (quote (3 7))))",
"(define globalvar 55)",
"foo",
"bar",
"(foo 3)",
"(bar 3)",
"(bar 'globalvar)",
"(bar 'baz)",
"((bar 'baz) 'globalvar)",
"(in? (quote (3 7)) 3)",
"(in? (quote (4 7)) 3)",
"(in? foo  3)",
"(in? foo  'foo)",
"(in? foo2 'foo)",
"(foo 'globalvar 1)",
"(foo 'globalvar)",
"(foo 333)",
"(foo 'globalvar)",
], 'tests_namespaces_attached')
'''

import pytest
from sym_lis import lisp_eval_str


@pytest.fixture
def redefine_foo_bar_env():
    var_foo  = lisp_eval_str("(define foo  (env (quote ('foo 5)) (quote (3 7))))")
    var_foo2 = lisp_eval_str("(define foo2 (env (quote  (foo 5)) (quote (3 7))))")
    var_bar  = lisp_eval_str("(define bar (env_anonymous (quote ('foo 5)) (quote (3 7))))")
    var_baz  = lisp_eval_str("(define bar/baz (env_anonymous (quote ('foo 5)) (quote (3 7))))")
    var_globalvar = lisp_eval_str("(define globalvar 55)")
    return var_foo, var_foo2, var_bar, var_baz, var_globalvar

def test_var(redefine_foo_bar_env):
    var_foo, var_foo2, var_bar, var_baz, var_globalvar = redefine_foo_bar_env
    assert lisp_eval_str('foo')  is var_foo
    assert lisp_eval_str('foo2') is var_foo2
    assert lisp_eval_str('bar')  is var_bar
    assert lisp_eval_str('/bar/baz')  is var_baz

    assert lisp_eval_str("(foo 3)") == 7
    assert lisp_eval_str("(bar 3)") == 7

@pytest.mark.parametrize("ref,expected", [
  ("(foo 'globalvar)", 55),
  ("(bar 'globalvar 1)", 1),
])
def test_global(redefine_foo_bar_env, ref, expected):
    assert lisp_eval_str(ref) == expected

@pytest.mark.parametrize("ref", [
  ("(bar     'globalvar)"),
  ("(bar/baz 'globalvar)"),
  ("(foo 333)"),
])
def test_noglobal(redefine_foo_bar_env, ref):
    assert lisp_eval_str(ref) is None

@pytest.mark.parametrize("expr, result", [
  ("(in? (quote (3 7)) 3)", True),
  ("(in? (quote (4 7)) 3)", False),
  ("(in? foo 3)", True),
  ("(in? foo (quote 'foo))", True),
  ('(in? foo2 (quote foo))', True),
])
def test_in(redefine_foo_bar_env, expr, result):
    assert lisp_eval_str(expr) is result

