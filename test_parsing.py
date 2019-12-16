from nsp_lis import lisp_eval_str
import pytest


def test_no_tokens():
    with pytest.raises(SyntaxError):
        lisp_eval_str("")

@pytest.mark.parametrize("test_input", [
    (")"),
    ("(+ 2 (* 1 2)))"),
    ("(+ 11 28) 2)"),
])
def test_closing_parenthes(test_input):
    with pytest.raises(SyntaxError):
        lisp_eval_str(test_input)

