from sym_lis2 import GlobalEnv

#def test_consecutive_exprs():
#    g = GlobalEnv()
#    g.eval_str('''
#    (define 'foo (lambda (x) 5))
#    (define 'x (foo))
#    ''')
#    assert g.eval_str('x') == 5

def test_source_file():
    g = GlobalEnv()
    g.eval_str('(source "applications/lib_foo.lisp")')

    assert 'foo' in g

def test_source_lib():
    g = GlobalEnv()
    g.eval_str('(source "applications/lib_func.lisp")')

    assert 'func' in g
    assert 'substitute_example' in g
    assert g.eval_str('substitute_example')  == [1, 2, 5]
    assert g.eval_str('substitute_example2') == \
           g.eval_str('(quote (1 2 5))')

#def test_env_begin_define():
#    g = GlobalEnv()
#    g.eval_str('''
#    (define e (env (begin
#    (define foo (lambda (x) 5))
#    (define x (foo))
#    ''')
#    assert True
