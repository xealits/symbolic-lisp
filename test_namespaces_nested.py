'''
add_tests([
"(env (quote ('foo 5)) (quote (3 7)))",
"(define foo (env (quote ('foo 5)) (quote (3 7))))",
"foo",
"/foo",
"/./foo",
"./foo",
"././foo",
"(define foo/bar/baz 55)",
"foo",
"(foo 'bar)",
"(foo 'brr 51)",
"foo/bar",
"foo/bar/",
"((foo 'bar) 'baz)",
"foo/bar/baz",
"(+ foo/bar/baz 33)",
], 'tests_namespaces_nested')
'''

import pytest
from nsp_lis import lisp_eval_str, Env


@pytest.fixture
def redefine_foo_bar_env():
    foo_env = lisp_eval_str("(define foo (env (quote (foo 5)) (quote (3 7))))")
    bar_env = lisp_eval_str("(define foo/bar (env))")
    mpt_env = lisp_eval_str("(define foo/stp/mpt/boo 600)")
    baz_var = lisp_eval_str("(define foo/bar/baz 55)")
    lisp_eval_str("(define foo/par (env (quote (3 21)) (quote (1 22))))")
    return foo_env, bar_env, baz_var


@pytest.mark.parametrize('varname', [
  ('foo'),
  ('/foo'),
  ('./foo'),
  ('.//foo'),
  ('/./foo'),
  ('././foo'),
])
def test_names_foo(redefine_foo_bar_env, varname):
    foo, _, _ = redefine_foo_bar_env
    assert lisp_eval_str(varname) is foo

@pytest.mark.parametrize('varref', [
  ("(foo 'bar)"),
  ('foo/bar'),
  ('foo/bar/'),
  ('/foo/../foo/bar'),
])
#('./foo/../foo/bar'),
def test_names_bar(redefine_foo_bar_env, varref):
    _, bar, _ = redefine_foo_bar_env
    assert lisp_eval_str(varref) is bar

@pytest.mark.parametrize('varref', [
  ("((foo 'bar) 'baz)"),
  ('foo/bar/baz'),
  ("((foo 'par) '../bar/baz)"),
])
def test_names_baz(redefine_foo_bar_env, varref):
    _, _, baz = redefine_foo_bar_env
    assert lisp_eval_str(varref) is baz


def test_env_default(redefine_foo_bar_env):
    assert lisp_eval_str("(foo 'brr 51)") == 51

def test_baz(redefine_foo_bar_env):
    assert lisp_eval_str("(+ foo/bar/baz 33)") == 55 + 33
    lisp_eval_str("(define /foo/bar/baz2 foo/bar/baz)")
    assert lisp_eval_str("/foo/bar/baz") == lisp_eval_str("foo/bar/baz2")

def test_nesting(redefine_foo_bar_env):
    assert lisp_eval_str('foo/stp/mpt/boo') == 600
    assert lisp_eval_str("(foo 'foo)") == 5
    lisp_eval_str("(set! foo/foo 11)")
    assert lisp_eval_str("(foo 'foo)") == 11

