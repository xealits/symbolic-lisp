'''
add_tests([
"(quote (env (quote 'foo 5) (quote 3 7)))",
"(env (quote ('foo 5)) (quote (3 7)))",
"(env? (env (quote ('foo 5)) (quote (3 7))))",
"((env (quote ('foo 5)) (quote (3 7))) 3)",
], 'tests_namespaces')
'''

from sym_lis import lisp_eval_str, Env


def test_list():
    assert lisp_eval_str("(quote (env (quote 'foo 5) (quote 3 7)))") == ['env', ['quote', "'foo", 5], ['quote', 3, 7]]

def test_env():
    assert isinstance(lisp_eval_str("(env (quote ('foo 5)) (quote (3 7)))"), Env)
    assert lisp_eval_str("(env? (env (quote ('foo 5)) (quote (3 7))))")

def test_access():
    assert lisp_eval_str("((env (quote ('foo 5)) (quote (3 7))) 3)") == 7

