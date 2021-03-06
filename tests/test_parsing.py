from sym_lis import GlobalEnv, lispstr, parse
import pytest


g = GlobalEnv()

def test_no_tokens():
    assert g.eval_str("") is None

def test_unknown_name():
    with pytest.raises(TypeError):
        g.eval_str("(foo 1 2)")

@pytest.mark.parametrize("test_input", [
    (")"),
    ("(+ 2 (* 1 2)))"),
    ("(+ 11 28) 2)"),
])
def test_closing_parenthes(test_input):
    with pytest.raises(SyntaxError):
        g.eval_str(test_input)

def test_string():
    inp_str = '(foo bar)'
    assert lispstr(parse(inp_str)[0]) == inp_str
