from sym_lis2 import GlobalEnv as Env
import pytest


def test_not_defined():
    g = Env()
    with pytest.raises(NameError):
        g.eval_str('(sum_typ_usual 33 (sum_typ 1 2))') == 36

def test_no_closing_brace():
    g = Env()
    with pytest.raises(IndexError):
        g.eval_str('(sum_typ_usual 33')
