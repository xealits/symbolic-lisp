import pytest
from sym_lis import GlobalEnv

g = GlobalEnv()

@pytest.mark.parametrize('test_input, expected', [
  ("(0 (list 'foo 'bar 77))", "foo"),
  ("(2 (list 'foo 'bar 77))", 77),
])
def test_indexes(test_input, expected):
    assert g.eval_str(test_input) == expected

def test_index_boundary():
    #with pytest.raises(ZeroDivisionError):
    with pytest.raises(IndexError):
        g.eval_str("(5 (list 'foo 'bar 77))")
