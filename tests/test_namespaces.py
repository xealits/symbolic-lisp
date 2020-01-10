from sym_lis import GlobalEnv, Env


g = GlobalEnv()

def test_list():
    assert g.eval_str("(quote (env (quote 'foo 5) (quote 3 7)))") == ['env', ['quote', "'foo", 5], ['quote', 3, 7]]

def test_env():
    assert isinstance(g.eval_str("(env (quote ('foo 5)) (quote (3 7)))"), Env)
    assert g.eval_str("(env? (env (quote ('foo 5)) (quote (3 7))))")

def test_access():
    assert g.eval_str("((env (quote ('foo 5)) (quote (3 7))) 3)") == 7

