import subprocess

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
