'''
add_tests([
"(1 'foo 'bar 77)",
"(3 'foo 'bar 77)",
"(5 'foo 'bar 77)",
], 'tests_iterations', 'ERROR!')
'''

import pytest
from nsp_lis import lisp_eval_str

@pytest.mark.parametrize('test_input, expected', [
  ("(0 (list 'foo 'bar 77))", "foo"),
  ("(2 (list 'foo 'bar 77))", 77),
])
def test_indexes(test_input, expected):
    assert lisp_eval_str(test_input) == expected

def test_index_boundary():
    #with pytest.raises(ZeroDivisionError):
    with pytest.raises(IndexError):
        lisp_eval_str("(5 (list 'foo 'bar 77))")
