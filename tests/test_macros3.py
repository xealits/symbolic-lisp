import pytest
from sym_lis3 import GlobalEnv


def test_substitute():
    g = GlobalEnv()

    g.eval_str('''(define "substitute" (lambda (target_name sub expr)
      (if (list? expr)
          (map (curry substitute target_name sub) expr)
          (if (equal? expr target_name)
              sub
              expr)
      )))''')

    assert g.eval_str('(substitute "x" 5 (quote (1 2 x)))') == [1, 2, 5]

def test_func():
    g = GlobalEnv()

    #g.eval_str('''(define "func" (lambda (func_name args body)
    #      (define (out (out dyn_env)) func_name (lambda args body))
    #  ))''')
    # TODO: there is a limitation in lambda here: it always sets outer to its
    # current dyn_env, not to the one where I do the define -- it only attaches
    # it. The Env handles it with `nest`.

    g.eval_str('''(define "func" (lambda (func_name args body)
          (define
              (out (out dyn_env))
              func_name
              (nest (out (out dyn_env)) (env (list "_args" "_body") (list args body))))
      ))''')

    g.eval_str('(func "foo" (list "x" "y") (quote (+ x y)))')

    assert g.eval_str('(in? root_env "foo")')
    assert g.eval_str('(out foo)') is g # root_env
    assert g.eval_str('(foo 2 7)') == 9

def test_macro():
    g = GlobalEnv()

    g.eval_str('(define "foo" (macro (x y) (list x y)))')

    assert g.eval_str('(foo (a b) (bar (c d)))') == [['a', 'b'], ['bar', ['c', 'd']]]

def test_macro_lambda0():
    g = GlobalEnv()

    g.eval_str('(define "foo1" (macro (x y) (list x y)))')
    g.eval_str('(define "foo2" (macro (x y) (list (eval dyn_env x) (eval dyn_env y))))')

    assert g.eval_str('(foo1 (+ 2 3) (* 4 5))') == [['+', 2, 3], ['*', 4, 5]]
    assert g.eval_str('(foo2 (+ 2 3) (* 4 5))') == [5, 20]

def test_macro_lambda_diy():
    g = GlobalEnv()

    g.eval_str('''(define "foo"
        (macro (x y)
            (begin
                (print dyn_env (eval (out dyn_env) x))
                (set! "x" (eval (out dyn_env) x))
                (set! "y" (eval (out dyn_env) y))
                (+ x y))))''')

    assert g.eval_str('(foo (+ 3 5) (* 7 8))') == 64

    g.eval_str('(define "X" 55)')
    assert g.eval_str('(foo X (* 7 8))') == 111

    assert g.eval_str('(in? root_env "foo")')
    assert not g.eval_str('(in? root_env "x")')

    g.eval_str('(define "x" 45)')
    assert g.eval_str('(foo x (* 7 8))') == 101

def test_macro_lambda_diy_func():
    g = GlobalEnv()

    g.eval_str('''(define "func" (macro (func_name args body)
          (define
              (out (out dyn_env))
              func_name
              (nest (out (out dyn_env)) (env (list "_args" "_body") (list args body))))
      ))''')

    g.eval_str('(func foo (x y) (+ x y))')

    # signature
    assert g.eval_str('(in? root_env "foo")')
    assert g.eval_str('(in foo "_args")') == ['x', 'y']
    assert g.eval_str('(in foo "_body")') == ['+', 'x', 'y']

    # action
    assert g.eval_str('(foo (+ 3 5) (* 7 8))') == 64

    g.eval_str('(define "X" 55)')
    assert g.eval_str('(foo X (* 7 8))') == 111

    assert g.eval_str('(in? root_env "foo")')
    assert not g.eval_str('(in? root_env "x")')

    g.eval_str('(define "x" 45)')
    assert g.eval_str('(foo x (* 7 8))') == 101


