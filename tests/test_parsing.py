from sym_lis3 import GlobalEnv, lispstr, parse
import pytest


g = GlobalEnv()

def test_no_tokens():
    assert g.eval_str("") is None

def test_unknown_name():
    with pytest.raises(NameError):
        g.eval_str("(foo 1 2)")

@pytest.mark.parametrize("test_input", [
    (")"),
    ("(+ 2 (* 1 2)))"),
    ("(+ 11 28) 2)"),
    ("(* 3 4"),
    ("(unclosed expression"),
])
def test_closing_parenthes(test_input):
    with pytest.raises(SyntaxError):
        g.eval_str(test_input)

def test_string():
    inp_str = '(foo bar)'
    assert lispstr(parse(inp_str)[0]) == inp_str

@pytest.mark.parametrize("test_input, parsed", [
    ('(join (str) (list "(" "," reg_index "," offset ")"))',
     [['join', ['str'], ['list', '(', ',', 'reg_index', ',', 'offset', ')']]]),
])
def test_strings(test_input, parsed):
    assert parse(test_input) == parsed
