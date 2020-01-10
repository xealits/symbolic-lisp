import pytest
from sym_lis import Env, GlobalEnv


@pytest.fixture
def redefine_foo_bar_env():
    g = GlobalEnv()
    foo_env = g.eval_str("(define foo (env (quote (foo 5)) (quote (3 7))))")
    bar_env = g.eval_str("(define foo/bar (env))")
    mpt_env = g.eval_str("(define foo/stp/mpt/boo 600)")
    baz_var = g.eval_str("(define foo/bar/baz 55)")
    g.eval_str("(define foo/par (env (quote (3 21)) (quote (1 22))))")
    g.eval_str('(define foo/par/proc  (lambda (x) (+ x 5)))')
    g.eval_str('(define foo/par/proc2 (lambda (x) (+ x scope_y)))')
    g.eval_str('(define foo/par/proc3 (lambda (x) (+ x /global_y)))')
    return g, (foo_env, bar_env, baz_var)


@pytest.mark.parametrize('varname', [
  ('foo'),
  ('/foo'),
  ('./foo'),
  ('.//foo'),
  ('/./foo'),
  ('././foo'),
])
def test_names_foo(redefine_foo_bar_env, varname):
    g, (foo, _, _) = redefine_foo_bar_env
    assert g.eval_str(varname) is foo

@pytest.mark.parametrize('varref', [
  ("(foo 'bar)"),
  ('foo/bar'),
  ('foo/bar/'),
  ('/foo/../foo/bar'),
])
#('./foo/../foo/bar'),
def test_names_bar(redefine_foo_bar_env, varref):
    g, (_, bar, _) = redefine_foo_bar_env
    assert g.eval_str(varref) is bar

@pytest.mark.parametrize('varref', [
  ("((foo 'bar) 'baz)"),
  ('foo/bar/baz'),
  ("((foo 'par) '../bar/baz)"),
])
def test_names_baz(redefine_foo_bar_env, varref):
    g, (_, _, baz) = redefine_foo_bar_env
    assert g.eval_str(varref) is baz


def test_env_default(redefine_foo_bar_env):
    g, _ = redefine_foo_bar_env
    assert g.eval_str("(foo 'brr 51)") == 51

def test_baz(redefine_foo_bar_env):
    g, _ = redefine_foo_bar_env
    assert g.eval_str("(+ foo/bar/baz 33)") == 55 + 33
    g.eval_str("(define /foo/bar/baz2 foo/bar/baz)")
    assert g.eval_str("/foo/bar/baz") == g.eval_str("foo/bar/baz2")

def test_nesting(redefine_foo_bar_env):
    g, _ = redefine_foo_bar_env
    assert g.eval_str('foo/stp/mpt/boo') == 600
    assert g.eval_str("(foo 'foo)") == 5
    g.eval_str("(set! foo/foo 11)")
    assert g.eval_str("(foo 'foo)") == 11

def test_nested_var_scopes(redefine_foo_bar_env):
    g, _ = redefine_foo_bar_env
    assert g.eval_str('(foo/par/proc 2)') == 7

    with pytest.raises(TypeError):
        assert g.eval_str('(foo/par/proc2 2)') == 7

    g.eval_str('(define foo/scope_y 5)')
    assert g.eval_str('(foo/par/proc2 2)') == 7

    with pytest.raises(TypeError):
        assert g.eval_str('(foo/par/proc3 2)') == 7

    g.eval_str('(define global_y 5)')
    assert g.eval_str('(foo/par/proc3 2)') == 7
