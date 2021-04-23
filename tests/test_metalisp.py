import sym_lis2
from sym_lis2 import GlobalEnv as Env
import pytest, mock


'''
@pytest.mark.parametrize("test_input,expected", [
    ("(+ 1 2)", 3),
    ("(+ (+ 11 28) 2)", 41),
    ("(+ (+ 11 28) (* 1 2))", 41),
])
def test_calc1(test_input, expected):
    g = Env()
    assert g.eval_str(test_input) == expected
'''

def test_defines():
    g = Env()

    g.eval_str('(define "foo" "bar")')
    assert g.eval_str('foo') == 'bar'

    g.eval_str('(define "bar" 5)')
    assert g.eval_str('bar') == 5

    g.eval_str('(define "baz" (nsp (quote ("a")) (quote ("b"))))')
    assert g.eval_str('baz') == {'a': 'b'}

'''
def test_procedure():
    g = Env()
    g.eval_str('(define "echo" (nsp (quote ("_proc")) (quote (((eval _args))))))')
    assert g.eval_str('(echo foo bar)') == ['foo', 'bar']
'''

def test_integer_arithmetics():
    g = Env()
    assert g.eval_str('(+ 1 2)') == 3
    assert g.eval_str('(+ 33 (+ 1 2))') == 36
    assert g.eval_str('(* 1 2)') == 2
    assert g.eval_str('(* 33 (+ 1 2))') == 99

def test_string_manipulation():
    g = Env()
    assert g.eval_str('(+ "foo_" "bar")') == "foo_bar"

    g.eval_str('(define (+ "foo_" "bar") 5)')
    assert g.eval_str('foo_bar') == 5

def test_index_n_eval():
    g = Env()
    print(g.eval_str('(quote ((+ 1 2) (+ 3 4)))'))
    print(g.eval_str('(0 (quote ((+ 1 2) (+ 3 4))))'))
    assert g.eval_str('(0 (quote ((+ 1 2) (+ 3 4))))') == 3
    assert g.eval_str('(1 (quote ((+ 1 2) (+ 3 4))))') == 7

def test_dyn_scope():
    g = Env()
    g.eval_str('''(define "sum_typ"
            (nsp (list "_proc")
                 (quote ((
                    (print _args)
                    (print (type _args))
                    (+ (0 _args) (1 _args))
            )))))''')
    assert g.eval_str('(sum_typ 1 2)') == 3
    assert g.eval_str('(sum_typ 33 (sum_typ 1 2))') == 36

    g.eval_str('''(define "sum_lex"
            (nsp (quote ("_proc")) (quote ((
              (+ foo bar)
            )))))''')
    g.eval_str("(define 'foo 1)")
    g.eval_str("(define 'bar 2)")
    assert g.eval_str('(sum_lex)') == 3

    g.eval_str('''(define 'sum_dyn
            (nsp (quote ("_proc")) (quote ((
              (print 'sum_dyn (nsp_keys _dyn))
              (+ (get _dyn "foo") (get _dyn "bar"))
            )))))''')
    g.eval_str('''(define 'sum_wrapper
            (nsp (quote ("_proc")) (quote ((
              (define 'foo 30)
              (define 'bar 6)
              (print 'sumwrapper 'NAMESPACE_dyn (nsp_keys _dyn))
              (sum_dyn)
            )))))''')
    assert g.eval_str('(sum_wrapper)') == 36

    '''
    ( dict_keys(['_args', '_dyn', 'foo', 'bar']),
      (dict_keys(['_proc']),
       dict_keys(['+', '-', '*', '/', '>', '<', '>=', '<=', '=', 'sum', 'equal?', 'length', 'print', 'type', 'eval', 'eval_explicit', 'define', 'map', 'list?', 'None', 'do', 'nsp_keys', 'sum_typ', 'sum_lex', 'foo', 'bar', 'sum_dyn', 'sum_wrapper']))
    )

    so, _dyn is the call nsp here!
    but not in the basic_func???
    '''

    g.eval_str('''(define 'sum_dyn2
            (nsp (quote ("_proc"))
                 (quote ((
                    (+ (get . "foo") (get . "bar"))
                    )))
            ))''')
    g.eval_str('''(define 'sum_wrapper2
            (nsp (quote ("_proc")) (quote ((
              (define 'foo 30)
              (define 'bar 6)
              (print _dyn)
              (sum_dyn2)
            )))))''')
    assert g.eval_str('(sum_wrapper2)') == 3

def test_dyn_nested_scope():
    g = Env()

    g.eval_str('''(define 'sum_dyn
            (nsp (quote ("_proc")) (quote ((
              (print 'sum_dyn '_dyn (nsp_keys _dyn))
              (print 'sum_dyn '.    (nsp_keys .))
              (+ (get _dyn "foo") (get _dyn "bar"))
            )))))''')

    g.eval_str('''(define 'sum_dyn_nested
            (nsp (quote ("_proc")) (quote ((
              (define 'a_var_in_sum_dyn_nested_call 6)
              (print 'sum_dyn_nested '_dyn (nsp_keys _dyn))
              (print 'sum_dyn_nested '.    (nsp_keys .))
              (sum_dyn)
            )))))''')

    g.eval_str('''(define 'sum_wrapper
            (nsp (quote ("_proc")) (quote ((
              (define 'foo 30)
              (define 'bar 6)
              (print 'sumwrapper 'NAMESPACE_dyn (nsp_keys _dyn))
              (sum_dyn_nested)
            )))))''')
    with pytest.raises(NameError):
        # cannot find the variable, because the dynamic scope does not nest
        g.eval_str('(sum_wrapper)') == 36

def test_add_quotes():
    g = Env()
    assert g.eval_str('(+ (quote  (1 2))  (quote (3 4)))') == [1, 2, 3, 4]
    assert g.eval_str('(+ (quote ((1 2))) (quote (3 4)))') == [[1, 2], 3, 4]

def test_list():
    g = Env()
    assert g.eval_str('(list (+ (quote  (1 2))  (quote (3 4))))') == [[1, 2, 3, 4]]
    assert g.eval_str('(list (+ (quote ((1 2))) (quote ((3 4)))))') == \
            [[[1, 2], [3, 4]]]

def test_nsp_proc_structure():
    g = Env()

    assert g.eval_str('''(nsp
    (quote ("_proc"))
    (quote ((
      (foo bar)
      (baz 22)
    ))))''') == {'_proc': [['foo', 'bar'], ['baz', 22]]}

    assert g.eval_str('''(nsp
    (quote ("_proc"))
    (list (+
      (quote (
        (foo bar)
      ))
      (quote (
        (baz 22)
      ))
    )))''') == {'_proc': [['foo', 'bar'], ['baz', 22]]}

def test_remote_define():
    g = Env()
    g.eval_str('''(define 'foo (nsp (quote ()) (quote ())))''')
    assert g.eval_str('foo') == {}

    g.eval_str('''(define 'bar 5 foo)''')
    g.eval_str('''(define 'bar 111)''')

    assert g.eval_str('foo') == {'bar': 5}
    assert g.eval_str('(eval .   bar)')   == 111
    assert g.eval_str('(eval foo bar)') == 5

def test_semibuild_list():
    g = Env()
    assert g.eval_str('''(list
        (+ 1 2)
        (quote (foo bar))
        'baz
        )''') == [3, ['foo', 'bar'], 'baz']

def test_multiplus():
    g = Env()
    assert g.eval_str('(sum (list 1 2 3))') == 6

def test_multicall():
    g = Env()
    g.eval_str("(define 'foo 5)")
    g.eval_str('''(define 'foo_inc (nsp
        (quote ("_proc"))
        (quote ((
          (print foo)
          (set! 'foo (+ foo 1))
          foo_inc
          )))
        ))''')

    assert g.eval_str('foo') == 5
    print(g.eval_str('(((foo_inc)))'))
    assert g.eval_str('foo') == 8

def test_quote_eval():
    g = Env()
    g.eval_str("(define 'q (quote (define 'nome (nsp (list 'foo 'bar) (list 2 3)))))")
    assert g.eval_str('q') == \
      ['define', "'nome", ['nsp', ['list', "'foo", "'bar"], ['list', 2, 3]]]
    print('test eval q')
    # (eval (eval q)) does not make sense because eval is recursive allready

    g.eval_str('(q)') 
    #g.eval_str("(define 'nome (nsp (list 'foo 'bar) (list 2 3)))")

    # TODO (q) must be == (eval q)? or it doesn't make sense?
    # TODO: is this a special control form?
    print(g.eval_str('nome'))
    assert g.eval_str('nome') == {'foo': 2, 'bar': 3}

def test_map_eval():
    g = Env()
    r = g.eval_str('(map (eval .) (quote (1 (+ 1 10) (* 2 (1 (list 0 5 10))))))')
    print(r)
    assert r == [1, 11, 10]

'''
What if make
 foo  = "foo"
(foo) = lookup foo variable
'''

"""
def test_basic_procedure():
    '''
    (proc name (body a b))
    ->
    g.eval_str('''(define name (nsp
        (quote ("_proc"))
        (quote (
           (body a b)
           ))
        ))''')
    '''
"""

def test_eval_explicit():
    g = Env()
    """
    def proc_eval_explicit(expr, _dyn=None):
    # if the list starts with `eval` -- launch the usual eval
    # if not -- recurse into child lists
    if isinstance(expr, List) and len(expr) > 0:
        if expr[0] == 'eval_explicit':
            r = lisp_eval2(expr[1], in_namespace)
        else:
            r = list(map(lambda x: proc_eval_explicit(x, _dyn), expr))
    else:
        r = expr
    """

    g.eval_str('''(define "eval_explicit2"
            (nsp (list "_proc")
                 (quote ((
                     (define 'expr (index 0 _args))
                     (if (list? expr)
                         (if (equal? (index 0 expr) "eval_explicit2")
                             (eval . ((index 1 expr)))
                             (map (eval_explicit2) expr))
                         expr)
                     ))
                 )
            )
    )''')

    g.eval_str('(print "eval_explicit2" eval_explicit2)')
    assert g.eval_str('''(eval_explicit2
        (eval foo (bar (map (eval .) baz))
            (eval_explicit2 (+ 1 2))))''') == \
        ['eval', 'foo', ['bar', ['map', ['eval', '.'], 'baz']], 3]

    g.eval_str('(define "args" (quote (1 2 3)))')
    assert g.eval_str('''(eval_explicit2
        (eval bar (eval_explicit2 args)))''') == \
        ['eval', 'bar', [1, 2, 3]]

def test_exit():
    g = Env()

    with pytest.raises(SystemExit) as ex:
        g.eval_str('(exit 0)')

    assert ex.type == SystemExit
    assert ex.value.code == 0

