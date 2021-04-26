from sym_lis3 import GlobalEnv
import pytest


def test_dyn():
    g = GlobalEnv()
    g.eval_str('(define "foo" (lambda (x y) (if (in? x dyn_env) y 0)))')

    assert not g.eval_str('(in? "x" root_env)')

    assert g.eval_str('(foo "x" 1)')  == 1
    assert g.eval_str('(foo "+" 1)')  == 0
    assert g.eval_str('(foo "y" 55)') == 55
