from sym_lis2 import lispstr, GlobalEnv as Env
import pytest


def test_not_defined():
    g = Env()
    with pytest.raises(NameError):
        g.eval_str('(sum_typ_usual 33 (sum_typ 1 2))') == 36

def test_no_closing_brace():
    g = Env()
    with pytest.raises(IndexError):
        g.eval_str('(sum_typ_usual 33')

def test_extra_closing_brace():
    g = Env()
    with pytest.raises(SyntaxError):
        g.eval_str('(sum_typ_usual 33))')

def test_lispstr():
    g = Env()
    a_str = '(sum_typ_usual 33)'
    assert lispstr(g.eval_str('(quote %s)' % a_str)) == a_str
