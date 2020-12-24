from sym_lis2 import GlobalEnv as Env
import pytest

'''
(nsp (list "_proc")
     (quote ((
        (com1)
        (com2)
        ))
     )
)

(nsp (list "_proc")
     (list (list_quote
        (com1)
        (com2)
     ))
)

(proc_nsp
        (com1)
        (com2)
)
'''

def test_quoted_list_for_func_defs():
    g = Env()

    g.eval_str('''(define "list_quote"
            (nsp (list "_proc")
                 (quote ((
                     _args
                     ))
                 )
            )
    )''')
    assert g.eval_str('(list_quote (foo 1) (bar) 5)') == \
                           [['foo', 1], ['bar'], 5]

    #               (print _args)
    #               (print (type _args))
    g.eval_str('''(define "sum_typ_usual"
            (nsp (list "_proc")
                 (quote ((
                    (+ (0 _args) (1 _args))
            )))))''')
    assert g.eval_str('(sum_typ_usual 1 2)') == 3
    assert g.eval_str('(sum_typ_usual 33 (sum_typ_usual 1 2))') == 36

    g.eval_str('''(define "sum_typ_short"
            (nsp (list "_proc")
                 (list (list_quote
                    (print (type _args) _args)
                    (+ (0 _args) (1 _args))
            ))))''')
    assert g.eval_str('(sum_typ_short 1 2)') == 3
    assert g.eval_str('(sum_typ_short 33 (sum_typ_short 1 2))') == 36

def test_proc_nsp():
    g = Env()

    g.eval_str('''(define "proc_nsp"
            (nsp (list "_proc")
                 (quote ((
                     (nsp (list "_proc") (list _args))
                     ))
                 )
            )
    )''')
    assert g.eval_str( '(proc_nsp (foo 1) (bar) 5)') == \
            {'_proc': [['foo', 1], ['bar'], 5]}

    g.eval_str('''(define "sum_typ_shorter"
            (proc_nsp
                    (print (type _args) _args)
                    (+ (0 _args) (1 _args))
            ))''')
    assert g.eval_str('(sum_typ_shorter 1 2)') == 3
    assert g.eval_str('(sum_typ_shorter 33 (sum_typ_shorter 1 2))') == 36

