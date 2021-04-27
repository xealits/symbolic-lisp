from sym_lis3 import GlobalEnv


def test_source_file():
    g = GlobalEnv()
    g.eval_str('(source root_env "applications/lib_foo.lisp")')

    assert 'foo' in g

def test_source_lib_chain():
    g = GlobalEnv()
    g.eval_str('(source root_env "applications/lib_bar.lisp")')

    assert 'bar' in g
    assert 'foo' in g

'''
def test_source_lib():
    g = GlobalEnv()
    g.eval_str('(source root_env "applications/lib_func.lisp")')

    assert 'func' in g
    assert 'substitute_example' in g
    assert g.eval_str('substitute_example')  == [1, 2, 5]
    assert g.eval_str('substitute_example2') == \
           g.eval_str('(quote (1 2 5))')
'''
