from sym_lis3 import GlobalEnv
import pytest


@pytest.mark.parametrize("true_test", [
    ('(in? e0 "foo")'),
    ('(not (in? e0 "+"))'),
])
def test_content(true_test):
    g = GlobalEnv()
    g.eval_str('(define "e0" (env (list "foo" "bar") (list 2 3)))')

    assert g.eval_str(true_test)

def test_retrieve():
    g = GlobalEnv()
    assert g.eval_str('(in (env (list "foo" "bar") (list 2 3)) "foo")') == 2

    with pytest.raises(KeyError):
        g.eval_str('(in (env (list "foo" "bar") (list 2 3)) "baz")') == 2

def test_nest():
    g = GlobalEnv()

    # return None for not found vars
    #g.eval_str('(define "not_found" (lambda (var) None))')
    # no, the not_found handler is attached per env chain
    # a custom env will not randomly search for it in root_env

    g.eval_str('(define "e0" (env (list "foo" "bar") (list 2 3)))')

    with pytest.raises(NameError):
        g.eval_str('(find e0 "+")')

    g.eval_str('(nest root_env e0)')

    assert g.eval_str('(find e0 "+")') is g.eval_str('+')

def test_define_nested():
    g = GlobalEnv()

    g.eval_str('(define "e1" (nest root_env (env (list "foo" "bar") (list 2 3))))')
    assert g.eval_str('(find e1 "+")') is g.eval_str('+')

def test_define_nested_dynamic():
    g = GlobalEnv()

    g.eval_str('(define "e1" (nest dyn_env (env (list "foo" "bar") (list 2 3))))')
    assert g.eval_str('(find e1 "+")') is g.eval_str('+')

    g.eval_str('(define e1 "ka" (env (list "zzz" "qwe") (list 55 77)))')
    assert not g.eval_str('(in? root_env "ka")')
    assert     g.eval_str('(in? e1 "ka")')
    assert g.eval_str('(in (in e1 "ka") "qwe")') == 77

def test_define_nest_empty_env():
    g = GlobalEnv()

    g.eval_str('(define "e0" (env))')
    assert g.eval_str('(in? root_env "e0")')

    g.eval_str('(define e0 "foo" 5)')
    assert "foo" in g.eval_str('e0')

def test_define_wrong_arity():
    g = GlobalEnv()

    with pytest.raises(ValueError):
        g.eval_str('(define "foo" "bar" "e1" "value")')

def test_env_lambda():
    g = GlobalEnv()

    g.eval_str('(define "foo" (lambda (x y) (* (+ 2 x) y)))')

    assert g.eval_str('(in? foo "_args")')
    assert g.eval_str('(in? foo "_body")')

    assert g.eval_str('(in foo "_args")') == ['x', 'y']
    assert g.eval_str('(in foo "_body")') == ['*', ['+', 2, 'x'], 'y']

def test_env_lambda_diy():
    g = GlobalEnv()

    g.eval_str('(define "foo" (lambda (x y) (* (+ 2 x) y)))')

    g.eval_str('''(define "foo2"
        (nest root_env
            (env (list "_args" "_body")
                 (' (("x" "y") (* (+ 2 x) y)))
         )))''')

    assert g.eval_str('(foo 3 4)') == g.eval_str('(foo2 3 4)') == 20

def test_outer_env():
    g = GlobalEnv()

    g.eval_str('(define "e0" (env))')
    assert g.eval_str('(in? root_env "e0")')

    g.eval_str('(define e0 "bar" 5)')

    g.eval_str('''(define e0 "foo"
        (nest root_env
            (env (list "_args" "_body")
                 (' (("x" "y") (* (+ 2 x) y)))
         )))''')

    assert "bar" in g.eval_str('e0')
    assert "foo" in g.eval_str('e0')
    assert g.eval_str('(find? (in e0 "foo") "bar")') is False
    assert g.eval_str('(find? (in e0 "foo") "+")')   is True

    assert g.eval_str('(out (in e0 "foo"))') is g.eval_str('root_env')

