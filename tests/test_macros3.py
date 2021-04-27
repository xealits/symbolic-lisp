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

