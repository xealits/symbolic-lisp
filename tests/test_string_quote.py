from sym_lis import GlobalEnv


def test_foo():
    g = GlobalEnv()
    var_foo_addr = g.eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')
    assert g.eval_str('foo') is var_foo_addr

