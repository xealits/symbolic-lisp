import pytest
from sym_lis import GlobalEnv

l = GlobalEnv()

# test macro
l.eval_str('(define test equal?)')
# not really a macro at all

def test_pass():
    assert l.eval_str('(test (+ 3 2) 5)')

def test_notpass():
    assert l.eval_str('(test (+ 3 2) 5)')

# to test map
l.eval_str('(define double (lambda (x) (* 2 x)))')
l.eval_str('(define add    (lambda (x y) (+ y x)))')

def test_map():
    assert all(a==b for a, b in zip(l.eval_str('(map double (list 1 2 3))'),
        [2*i for i in [1,2,3]]))

def test_map_tuples():
    # this won't work
    #assert list(l.eval_str('(map add (quote ((1 2) (2 3))))')) == [3, 5]
    assert list(l.eval_str('''(map
        (lambda (x) (add (0 x) (1 x)))
        (quote ((1 2) (2 3))))''')) == [3, 5]

# printf-like substitute macro
l.eval_str('''
(define substitute
  (lambda (x varname sub)
    (if (symbol? x)
        (if (equal? x varname) sub x)
        (if (list? x) (map (lambda (i) (substitute i varname sub)) x)
            x)
    )
  )
)
''')

def test_if_eval():
    l.eval_str('''
    (define issym (lambda (x) (symbol? x)))
    ''')
    assert l.eval_str("(issym 'x)")
    assert not l.eval_str("(issym 5)")

def test_recursion():
    l.eval_str('''(define fact (lambda (x)
      (if (<= x 1)
           1
          (* x (fact (- x 1))))))''')
    assert l.eval_str('(fact 0)') == 1
    assert l.eval_str('(fact 1)') == 1
    assert l.eval_str('(fact 3)') == 6
    assert l.eval_str('(fact 6)') == 720

def test_substitute():
    assert l.eval_str("(substitute (quote (1 2 x)) 'x 5)") == \
    l.eval_str('(quote (1 2 5))')
    assert l.eval_str("(substitute (quote (1 (x x 3) 2 x)) 'x 5)") == \
    l.eval_str('(quote (1 (5 5 3) 2 5))')
    assert l.eval_str("(substitute (quote (+ (+ x x) 2 x)) 'x 5)") == \
    l.eval_str('(quote (+ (+ 5 5) 2 5))')
