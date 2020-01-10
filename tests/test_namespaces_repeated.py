import pytest
from sym_lis import GlobalEnv, Env


@pytest.fixture
def define_foo():
    g = GlobalEnv()
    g.eval_str("(define foo (env (quote (foo 5)) (quote (3 7))))")
    return g

def test_foo(define_foo):
    assert isinstance(define_foo.eval_str('foo'), Env)

def test_foofoo(define_foo):
    assert define_foo.eval_str('foo/foo') == 5
