import pytest
from sym_lis import GlobalEnv

def test_standard_missing_names():
    g = GlobalEnv()
    assert callable(g.eval_str('_missing_handler'))
    assert g.eval_str('foo') is None

def test_set_none_for_missing_names():
    g = GlobalEnv()
    g.eval_str('(define /_missing_handler (lambda (varname) 5))')
    assert g.eval_str('foo') == 5
