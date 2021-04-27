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

def test_source_lib():
    g = GlobalEnv()
    g.eval_str('(source root_env "applications/lib_substitute.lisp")')

    assert g.eval_str('(in? root_env "substitute")')
    assert g.eval_str('(in? root_env "substitute_example")')
    assert g.eval_str('substitute_example')  == [1, 2, 5]
