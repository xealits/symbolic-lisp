import subprocess
from sym_lis import GlobalEnv

def test_repl_session():
    comlist = ['./sym_repl.py']
    script = b'(+ 3 5)\n\n(exit)\n\n'
    res = subprocess.run(comlist, input=script,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # monkeypatch fixture did not work
    # the first input call in the repl gets EOF
    #monkeypatch.setattr('sys.stdin', io.StringIO('(+ 3 5)\n(exit)\n'))
    #res = subprocess.run(comlist,
    #        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert res.returncode == 0
    assert b'8\n' in res.stdout
    assert res.stderr == b''

def test_repl_session_debug():
    comlist = ['./sym_repl.py', '--debug']
    script = b'(+ 3 5)\n\n(exit)\n\n'
    res = subprocess.run(comlist, input=script,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # monkeypatch fixture did not work
    # the first input call in the repl gets EOF
    #monkeypatch.setattr('sys.stdin', io.StringIO('(+ 3 5)\n(exit)\n'))
    #res = subprocess.run(comlist,
    #        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert res.returncode == 0
    assert b'8\n' in res.stdout
    assert b'DEBUG' in res.stderr

def test_repl_script_lisp():
    g = GlobalEnv()
    assert g.eval_str('') is None

SCRIPT = '''
(+ 1 2)
(print "foo" "bar")
(print (+ ( * 5 44) 2))

(exit 0)
'''

def test_repl_script(tmp_path):
    p = tmp_path / 'test_script.lisp'
    p.write_text(SCRIPT)
    assert p.read_text() == SCRIPT
    assert len(list(tmp_path.iterdir())) == 1

    comlist = ['./sym_repl.py', '--script', p]
    script = b''
    res = subprocess.run(comlist, input=script,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert res.returncode == 0
    assert b'foo bar\n222\n'   in res.stdout
    assert b'' == res.stderr

BLANK_SCRIPT = '    \n   '

def test_repl_script_empty(tmp_path):
    p = tmp_path / 'test_script.lisp'
    p.write_text(BLANK_SCRIPT)

    comlist = ['./sym_repl.py', '--script', p]
    script = b''
    res = subprocess.run(comlist, input=script,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert res.returncode == 0
    assert b'' == res.stdout
    assert b'WARNING' in res.stderr and b'empty' in res.stderr
