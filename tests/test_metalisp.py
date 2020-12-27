from sym_lis2 import GlobalEnv as Env
import pytest


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
              (print _dyn)
              (+ (get _dyn "foo") (get _dyn "bar"))
            )))))''')
    g.eval_str('''(define 'sum_wrapper
            (nsp (quote ("_proc")) (quote ((
              (define 'foo 30)
              (define 'bar 6)
              (print _dyn)
              (sum_dyn)
            )))))''')
    assert g.eval_str('(sum_wrapper)') == 36

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

def test_basic_func():
    g = Env()
    '''
    (func name (a b) (body a b))
    '''

    # this also evaluates dynamically the given commands
    # in test_metalisp_handy it just passes the commands
    g.eval_str('''(define "proc_nsp"
            (nsp (list "_proc")
                 (quote ((
                     (nsp (list "_proc") (list (map (eval _dyn) _args)))
                     ))
                 )
            )
    )''')

    g.eval_str('''(define "eval_explicit2"
            (nsp (list "_proc")
                 (quote ((
                     (define 'expr (index 0 _args))
                     (if (list? expr)
                         (print 'EVAL_EXPLICIT2_list expr (index 1 expr))
                         None)
                     (if (list? expr)
                         (if (equal? (index 0 expr) "eval_explicit2")

                             (eval . (index 1 expr))

                             (map (eval_explicit2) expr))
                         expr)
                     ))
                 )
            )
    )''')

    #                         (do
    #                             (define 'got_expr_val (eval . (index 1 expr)))
    #                             (eval _dyn got_expr_val)
    #                         )

    # TODO: so, many relative namespace mess up everythin
    # (eval . (index 1 expr))
    # eval . causes everything to be evaluated in .
    # when I want only to lookup expr and get its 1 element (arguments) in .
    # then I want to eval the result in _dyn
    # in Python's extension it is trivial,
    # because everything is done in Python's call_nsp
    # and evals are called separately as needed
    #
    # here I cannot just (eval _dyn (eval . ...)
    # because of the nesting
    # -- there is no way to pass a value from eval in one namespace to another one
    #    again, it's the mix of different built-in procedures
    #    since there are 2 explicit namespaces now, the 1-D hardcoded
    #    procedures do not with well

    g.eval_str('''(define 'func (nsp
    (quote ("_proc"))
    (quote ((
        (print "_args" _args)
        (print "_dyn"  _dyn)
        (define 'name      (index 0 _args))
        (define 'arguments (index 1 _args))
        (define 'body      (index 2 _args))
        (print '_ARGS _args ":" name arguments)
        (print '_ARGS (eval . arguments))

        (define name (proc_nsp
              (eval_explicit2 (define "nsp_matched_args"
                    (nsp (quote (eval_explicit2 arguments))
                         (map (eval .) _args))))
              (quote (print "nsp_matched_args" nsp_matched_args))
              (list 'eval 'nsp_matched_args body)
         ) _dyn)
    )))))''')

    """
    map _dyn =
    {'_args': [['quote', ['eval_explicit2', 'arguments']]],
     '_dyn':
        {'_args': [['nsp', ['quote', ['eval_explicit2', 'arguments']], ['map', ['eval', '.'], '_args']]],
         '_dyn':
            {'_args': [['define', 'nsp_matched_args', ['nsp', ['quote', ['eval_explicit2', 'arguments']], ['map', ['eval', '.'], '_args']]]],
             '_dyn':
                 {'_args': ['foo', ['x', 'y'], ['+', 'x', 'y']],
                  '_dyn':
                     {'+': <built-in function add>, '-': <built-in function sub>, '*': <built-in function mul>, '/': <built-in function truediv>, '>': <built-in function gt>, '<': <built-in function lt>, '>=': <built-in function ge>, '<=': <built-in function le>, '=': <built-in function eq>, 'sum': <built-in function sum>, 'equal?': <built-in function eq>, 'length': <built-in function len>, 'print': <built-in function print>, 'type': <class 'type'>, 'eval': {'_callable': <function proc_eval at 0x7fc71dc0ee50>}, 'eval_explicit': {'_callable': <function proc_eval_explicit at 0x7fc71dc0eee0>}, 'define': {'_callable': <function proc_define at 0x7fc71dc0ef70>}, 'map': {'_callable': <function proc_map at 0x7fc71dc78040>}, 'list?': <function standard_nsp.<locals>.<lambda> at 0x7fc71db52c10>, 'proc_nsp': {'_proc': [['nsp', ['list', '_proc'], ['list', ['map', ['eval', '_dyn'], '_args']]]]}, 'eval_explicit2': {'_proc': [['define', "'expr", ['index', 0, '_args']], ['if', ['list?', 'expr'], ['if', ['equal?', ['index', 0, 'expr'], 'eval_explicit2'], ['eval', '.', [['index', 1, 'expr']]], ['map', ['eval_explicit2'], 'expr']], 'expr']]}, 'func': {'_proc': [['print', '_args', '_args'], ['print', '_dyn', '_dyn'], ['define', "'name", ['index', 0, '_args']], ['define', "'arguments", ['index', 1, '_args']], ['define', "'body", ['index', 2, '_args']], ['print', '_args', ':', 'name', 'arguments'], ['define', 'name', ['proc_nsp', ['eval_explicit2', ['define', 'nsp_matched_args', ['nsp', ['quote', ['eval_explicit2', 'arguments']], ['map', ['eval', '.'], '_args']]]], ['quote', ['print', 'nsp_matched_args', 'nsp_matched_args']], ['list', "'eval", "'nsp_matched_args", 'body']], '_dyn']]}},
                  'name': 'foo',
                  'arguments': ['x', 'y'],
                  'body': ['+', 'x', 'y']},
             'expr': ['define', 'nsp_matched_args', ['nsp', ['quote', ['eval_explicit2', 'arguments']], ['map', ['eval', '.'], '_args']]]},
         'expr': ['nsp', ['quote', ['eval_explicit2', 'arguments']], ['map', ['eval', '.'], '_args']]},
     'expr': ['quote', ['eval_explicit2', 'arguments']]}
    """

    # can also be (eval_explicit (eval nsp_matched_args (eval_explicit body)))

    '''
    То есть здесь проблема в том что я хочу выполнить что-то для создания
    дерева вызовов, именно `_args`, поэтому `quote` не подходит и нужен
    `list` с кучей цитируемых символов.
    Нужен quote, который пройдёт по всем узлам и выполнит какие-то из них.
    '''

    g.eval_str("(print 'DEFINE 'FOO)")
    g.eval_str('''(func foo (x y) (+ x y))''')
    g.eval_str("(print 'FOO foo)")

    assert g.eval_str('(foo 1 2)') == 3
    assert g.eval_str('(foo 1 (+ 10 2))') == 13
    assert g.eval_str('(foo (* 2 3) (foo 10 2))') == 18

'''
And eval's special forms are not exposed in the namespace!!!!
And if eval is added to the std namespace, it won't hook into
the global namespace! The std thing is handy only for functional stuff.
'''


'''
Получается проблема:
    я хочу манипулировать списки пользователя как они есть, не исполняя их
    но процедуры стандартного lisp_eval2 исполняют всё до конца рекурсивно
    нет чего-то типа (head _args) который вытащит лист из переменной _args
    и вернёт его первый элемент

    это как нынешняя разница между list & quote

    и эта семантика - включение-выключение исполнения - редка и не понятна
    в языках вообще
'''

