from sym_lis2 import GlobalEnv as Env
import pytest


"""
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

                             (do
                                 (print 'NAMESPACE_DYN (nsp_keys _dyn))
                                 (print 'NAMESPACE_.   (nsp_keys .))
                                 (eval . (index 1 expr)))

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

    '''
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
    '''

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
"""

