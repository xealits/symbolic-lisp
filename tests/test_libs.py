from sym_lis import GlobalEnv

def test_consecutive_exprs():
    g = GlobalEnv()
    g.eval_str('''
    (define foo (lambda (x) 5))
    (define x (foo))
    ''')
    assert g.eval_str('x') == 5

def test_source_file():
    g = GlobalEnv()
    g.eval_str("(source 'applications/lib_foo.lisp)")
    assert g.eval_str("(substitute (quote (1 2 x)) 'x 5)") == \
           g.eval_str('(quote (1 2 5))')


#def test_env_begin_define():
#    g = GlobalEnv()
#    g.eval_str('''
#    (define e (env (begin
#    (define foo (lambda (x) 5))
#    (define x (foo))
#    ''')
#    assert True
