import pytest
from sym_lis3 import GlobalEnv


@pytest.mark.parametrize('var_name, val', [
  ("foo", 'foo bar (bax c d) and ( more a b) brr t'),
  ("bar", "foo (bar baz)"),
])
def test_quotes(var_name, val):
    g = GlobalEnv()
    g.eval_str('(define "%s" "%s")' % (var_name, val))
    assert g.eval_str(var_name) == val

def test_print_parentheses():
    g = GlobalEnv()
    assert g.eval_str('(+ "foo" ")")') == 'foo)'
    assert g.eval_str('(+ "(" (+ "foo" ")"))') == '(foo)'

@pytest.mark.parametrize('test_input, expected', [
  ('(join (str)  (list "data" "(" "foo" ")"))', "data(foo)"),
  ('(join ","    (list "data" "(" "foo" ")"))', "data,(,foo,)"),
])
def test_join_string(test_input, expected):
    g = GlobalEnv()
    assert g.eval_str(test_input) == expected

def test_quotation_mark():
    g = GlobalEnv()

    g.eval_str('''(define "foo" (join (str) (list double_quote "Hello world!"
            double_quote )))''')

    assert g.eval_str('foo') == '"Hello world!"'
