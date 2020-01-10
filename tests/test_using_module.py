import sym_lis

def test_global_calls():
    assert sym_lis.lisp_eval_str('(+ 1 2)') == 3
    assert callable(sym_lis.lisp_eval_str('(define foo (lambda (x y) (+ x (* y 2))))'))
    assert sym_lis.lisp_eval_str('foo') is None
