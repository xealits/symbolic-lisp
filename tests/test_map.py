import pytest
from sym_lis3 import GlobalEnv


def test_map_basic():
    g = GlobalEnv()

    assert list(g.eval_str('(map (lambda (x) (* 2 x)) (list 1 2 3))')) == [2, 4, 6]

def test_map_curry():
    g = GlobalEnv()

    g.eval_str('(define "foo" (lambda (x y) (* x y)))')

    assert list(g.eval_str('(map (curry foo 2) (list 1 2 3))')) == [2, 4, 6]
