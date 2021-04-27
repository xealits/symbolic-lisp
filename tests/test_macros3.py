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

