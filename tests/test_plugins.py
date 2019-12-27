import pytest
from sym_lis import GlobalEnv
import logging

def test_plugin():
    g = GlobalEnv()
    assert g.eval_str("_Python")
    assert g.eval_str("(env? _Python)")
    g.eval_str("(_Python/import 'math)")
    assert callable(g.eval_str(" (_Python/get 'math.ceil)"))
    assert g.eval_str("((_Python/get 'math.ceil) 6.2)") == 7.
    assert g.eval_str("((_Python/get 'math.ceil) 6.7)") == 7.

@pytest.fixture
def lisp_w_shell():
    g = GlobalEnv()
    g.eval_str("(_Python/import 'plugin_shell)")
    return g

def test_shellplugin(lisp_w_shell):
    assert callable(lisp_w_shell.eval_str("(_Python/get 'plugin_shell.find_command)"))
    assert lisp_w_shell.eval_str("((_Python/get 'plugin_shell.find_command) 'foo)") is None
    assert callable(lisp_w_shell.eval_str("((_Python/get 'plugin_shell.find_command) 'echo)"))

def test_shell_call(lisp_w_shell):
    res = lisp_w_shell.eval_str("(((_Python/get 'plugin_shell.find_command) \
    'echo) 'hello 'world)")
    logging.debug(res)
    assert res

def test_shell_call_exit(lisp_w_shell):
    script = '''((_Python/get 'plugin_shell.get_exit)
    (((_Python/get 'plugin_shell.find_command) 'echo) 'hello 'world)
    )
    '''
    res = lisp_w_shell.eval_str(script)
    assert res == 0

def test_shell_call_stdout(lisp_w_shell):
    script = '''((_Python/get 'plugin_shell.get_stdout)
    (((_Python/get 'plugin_shell.find_command) 'echo) 'hello 'world)
    )
    '''
    res = lisp_w_shell.eval_str(script)
    assert res

def test_shell_call_stderr(lisp_w_shell):
    script = '''((_Python/get 'plugin_shell.get_stderr)
    (((_Python/get 'plugin_shell.find_command) 'ls) 'no 'such 'files)
    )
    '''
    res = lisp_w_shell.eval_str(script)
    assert res

def test_shell_for_missing(lisp_w_shell):
    script = '''(define /_missing_handler (_Python/get
    'plugin_shell.find_command))
    (define /stdext (_Python/get 'plugin_shell.get_exit))
    (define /stdout (_Python/get 'plugin_shell.get_stdout))
    (define /stderr (_Python/get 'plugin_shell.get_stderr))
    '''
    lisp_w_shell.eval_str(script)
    res = lisp_w_shell.eval_str(" echo  ")
    assert callable(res)
    assert lisp_w_shell.eval_str("( echo 'foo 'bar )  ")
    assert lisp_w_shell.eval_str("(stdext ( echo 'foo 'bar ))") == 0
    assert lisp_w_shell.eval_str("(stdout ( ls 'sym_lis.py ))") == b'sym_lis.py\n'
    assert lisp_w_shell.eval_str("(stderr ( ls 'sym_lis.py ))") == b''
