import sym_lis3
from sym_lis3 import GlobalEnv


def test_types():
    g = GlobalEnv()

    assert g.eval_str('(type? 5)')     == sym_lis3.Int
    assert g.eval_str('(type? "foo")') == sym_lis3.String
    assert g.eval_str('(type? (quote type))') == sym_lis3.Symbol
    assert g.eval_str('(type? type?)')  == type(g['type?'])

    assert g.eval_str('(type? (str "foo"))') == str

def test_version():
    g = GlobalEnv()

    assert g.eval_str('(_getattr _sys (str "version"))')[0] == '3'
