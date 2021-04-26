from sym_lis3 import GlobalEnv
import pytest


@pytest.fixture
def define_str_hook():
    g = GlobalEnv()
    g.eval_str('(define "not_found" (lambda (x) (str x)))')
    return g

def test_not_found(define_str_hook):
    g = define_str_hook
    assert g.eval_str('foo') == "foo"

