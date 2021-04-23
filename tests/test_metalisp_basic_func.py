from sym_lis2 import GlobalEnv as Env
import pytest

'''
(func name (a b) (body a b))
'''


@pytest.fixture
def define_proc_nsp():
    g = Env()

    # this also evaluates dynamically the given commands
    # in test_metalisp_handy it just passes the commands
    g.eval_str('''(define "proc_nsp"
            (nsp (list "_proc")
                 (quote ((
                     (nsp (list "_proc") (list (map (eval _dyn) _args)))
                     ))
                 )
            )
    )''')

    return g

@pytest.fixture
def define_func(define_proc_nsp):
    g = define_proc_nsp

    g.eval_str('''(define "eval_explicit2"
            (nsp (list "_proc")
                 (quote ((
                     (print "EVAL EXPL _args: " _args)

                     (define 'substitution (eval2 _dyn (index 0 _args)))
                     (define 'expr                     (index 1 _args))

                     (if (list? expr)
                         None
                         (print 'EVAL_EXPLICIT2_list expr))

                     (if (list? expr)
                         (map (eval_explicit2 substitution) expr)
                         (if (equal? expr "eval_explicit2")
                             substitution
                             expr)
                     )))
                 )
            )
    )''')

    g.eval_str('''(define 'func (nsp
    (quote ("_proc"))
    (quote ((
        (print "_args" _args)
        (print "_dyn"  (nsp_keys _dyn))
        (define 'name      (index 0 _args))
        (define 'arguments (index 1 _args))
        (define 'body      (index 2 _args))
        (print '_ARGS _args ":" name arguments)

        (define name (proc_nsp
              (eval_explicit2 arguments
              (define "nsp_matched_args"
                    (nsp (quote eval_explicit2)
                         (map (eval .) _args))))
              (quote (print "LOG:   nsp_matched_args" nsp_matched_args))
              (list 'eval 'nsp_matched_args body)
         ) _dyn)
    )))))''')

    return g


def test_basic_func_builtin_explicit_macro(define_proc_nsp):
    g = define_proc_nsp

    g.eval_str('''(define 'func (nsp
    (quote ("_proc"))
    (quote ((
        (print "_args" _args)
        (print "_dyn"  _dyn)
        (define 'name      (index 0 _args))
        (define 'arguments (index 1 _args))
        (define 'body      (index 2 _args))
        (print '_ARGS _args ":" name arguments)
        (print '_ARGS (eval . arguments))

        (define name (proc_nsp
              (eval_explicit (define "nsp_matched_args"
                    (nsp (quote (eval_explicit arguments))
                         (map (eval .) _args))))
              (quote (print "nsp_matched_args" nsp_matched_args))
              (list 'eval 'nsp_matched_args body)
         ) _dyn)
    )))))''')

    g.eval_str('(func foo (x y) (+ x y))')
    assert g.eval_str('(foo 1 2)') == 3
    assert g.eval_str('(foo 1 (+ 10 2))') == 13
    assert g.eval_str('(foo (* 2 3) (foo 10 2))') == 18


def test_basic_func_custom_macro(define_func):
    g = define_func

    g.eval_str("(print 'DEFINE 'FOO)")
    g.eval_str('''(func foo (x y) (+ x y))''')
    g.eval_str("(print 'FOO foo)")

    assert g.eval_str('(foo 1 2)') == 3
    assert g.eval_str('(foo 1 (+ 10 2))') == 13
    assert g.eval_str('(foo (* 2 3) (foo 10 2))') == 18

def test_basic_func_nested(define_func):
    g = define_func

    g.eval_str('(func bar (x) (+ x 2))')
    g.eval_str('(func foo (x y) (* (bar x) y))')

    assert g.eval_str('(foo 4 3)') == 18

