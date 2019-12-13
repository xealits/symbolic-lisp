'''
add_tests([
'(+ 1 2)',
'(+ (+ 11 28) 2)',
'(+ (+ 11 28) (* 1 2))',
'(+ (list 1 2 3) (list 34 3 2))',
'(define foo (lambda (x y) (+ 2 (+ x y))))',
'(foo 4 2)',
'(+ (quote foo) (quote _bar))',
'(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))',
'(foo_bar 4 2)',
], name='passed_tests')
'''

from nsp_lis import lisp_eval_str



def test_calc1():
    assert lisp_eval_str('(+ 1 2)') == 3
    assert lisp_eval_str('(+ (+ 11 28) 2)') == 41
    assert lisp_eval_str('(+ (+ 11 28) (* 1 2))') == 41

def test_add_lists():
    assert lisp_eval_str('(+ (list 1 2 3) (list 34 3 2))') == lisp_eval_str('(list 1 2 3 34 3 2)')

lisp_eval_str('(define foo (lambda (x y) (+ 2 (+ x y))))')

def test_define():
    assert lisp_eval_str('(foo 4 2)') == 8

def test_define2():
    assert lisp_eval_str('(foo 5 2)') == 9

def test_concat_symbols():
    assert lisp_eval_str('(+ (quote foo) (quote _bar))') == 'foo_bar'

def test_define_dynamic():
    assert callable(lisp_eval_str('(define (+ (quote foo) (quote _bar)) (lambda (x y) (+ 2 (+ x y))))'))

def test_define_dynamic_eval():
    assert lisp_eval_str('(foo_bar 4 2)') == lisp_eval_str('(foo 4 2)')

