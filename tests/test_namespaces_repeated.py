import pytest
from nsp_lis import lisp_eval_str, Env


@pytest.fixture
def redefine_foo():
    foo_env = lisp_eval_str("(define foo (env (quote (foo 5)) (quote (3 7))))")
    #bar_env = lisp_eval_str("(define foo/bar (env))")
    #boo_var = lisp_eval_str("(define foo/foo/mpt/boo 600)")
    return foo_env #, bar_env, boo_var


def test_foo(redefine_foo):
    assert isinstance(lisp_eval_str('foo'), Env)


def test_foofoo(redefine_foo):
    assert lisp_eval_str('foo/foo') == 5
