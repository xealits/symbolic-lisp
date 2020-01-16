from sym_lis import GlobalEnv


def test_foo():
    g = GlobalEnv()
    var_foo_addr = g.eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')
    assert g.eval_str('foo') is var_foo_addr

def test_print_parentheses():
    g = GlobalEnv()
    assert g.eval_str("(+ par_l (+ 'foo par_r))") == '(foo)'

def test_join_string():
    g = GlobalEnv()
    assert g.eval_str("(join 'data par_l 'foo par_r)") == 'data(foo)'
