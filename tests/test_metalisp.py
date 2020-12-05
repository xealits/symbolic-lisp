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

def test_procedure():
    g = Env()
    g.eval_str('(define "echo" (nsp (quote ("_proc")) (quote (((eval _args))))))')
    assert g.eval_str('(echo foo bar)') == ['foo', 'bar']

def test_integer_arithmetics():
    g = Env()
    assert g.eval_str('(+ 1 2)') == 3
    assert g.eval_str('(+ 33 (+ 1 2))') == 36
    assert g.eval_str('(* 1 2)') == 2
    assert g.eval_str('(* 33 (+ 1 2))') == 99

def test_dyn_scope():
    g = Env()
    g.eval_str('''(define "sum_typ"
            (nsp (quote ("_proc")) (quote ((
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
    assert g.eval_str('(eval bar .)')   == 111
    assert g.eval_str('(eval bar foo)') == 5

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


def test_basic_func():
    g = Env()
    '''
    (func name (a b) (body a b))
    '''

    g.eval_str('''(define 'func (nsp
    (quote ("_proc"))
    (quote ((
        (print "_args" _args)
        (print "_dyn"  _dyn)
        (define 'name      (0 _args) _dyn)
        (define 'arguments (1 _args))
        (define 'body      (2 _args))
        (print _args ":" name arguments)

        (define name (nsp
            (list "_proc")
            (list 
              (list 'define ''nsp_parsed_args
                    (list 'nsp arguments '_args))

              (quote (eval body nsp_parsed_args))
            )
         ) _dyn)
    )))))''')

    g.eval_str('''(func "foo" (x y) (+ x y))''')
    assert g.eval_str('(foo 1 2)') == 3

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

