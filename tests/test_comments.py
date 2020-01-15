import pytest
from sym_lis import GlobalEnv


def test_inline_annotate():
    g = GlobalEnv()
    g.eval_str("(define baz (_note (quote (foo bar)) 5))")
    assert g.eval_str('baz') == 5
    assert g.eval_str('baz').note == g.eval_str('(quote (foo bar))')
    assert g.eval_str("(+ (_note 'foo 2) 3)") == 5

def test_block_comment():
    g = GlobalEnv()
    script = '''
    (* 3 4)

    (quote (lkasdhj 
    sdlh 
    asdkh 
    sadahjs
    ))

    (+ 2 3)
    '''
    assert g.eval_str(script) == 5
