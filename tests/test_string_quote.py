'''
add_tests([
'(define foo (lambda (x y) (+ 2 (+ x y))))',
"foo",
"'foo",
"(define (+ 'foo '_bar) (lambda (x y) (+ 2 (+ x y))))",
'(foo_bar 4 2)',
], 'test_string_quote')
'''

from nsp_lis import lisp_eval_str


def test_foo():
    var_foo_addr = lisp_eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')
    assert lisp_eval_str('foo') is var_foo_addr

