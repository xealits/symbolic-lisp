'''
add_tests([
"(1 'foo 'bar 77)",
"(3 'foo 'bar 77)",
"(5 'foo 'bar 77)",
], 'tests_iterations', 'ERROR!')
'''

import pytest
from nsp_lis import lisp_eval_str


def test_indexes():
    assert lisp_eval_str("(1 'foo 'bar 77)") == "'foo"
    assert lisp_eval_str("(3 'foo 'bar 77)") == 77

def test_index_boundary():
    #with pytest.raises(ZeroDivisionError):
    with pytest.raises(IndexError):
        lisp_eval_str("(5 'foo 'bar 77)")

