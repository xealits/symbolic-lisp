from collections import UserString
from pyparsing import Word, Char, Optional, alphas, nums, nestedExpr, QuotedString, Combine

################ Types

# A Lisp Symbol is implemented as a Python str
class Symbol(UserString):
    pass

class String(str): #(UserString):
    pass

List   = list         # A Lisp List is implemented as a Python list
Number = (int, float) # A Lisp Number is implemented as a Python int or float

class Int(int):
    pass


################ Parsing: parse, tokenize, and read_from_tokens
lisp_integer = Word(nums)
lisp_integer.setParseAction(lambda s,l,t: Int(t[0]))

lisp_float   = Combine(Word(nums) + '.' + Word(nums))
lisp_float.setParseAction(lambda s,l,t: float(t[0]))

lisp_number  = lisp_integer | lisp_float

lisp_string = QuotedString(quoteChar='"', escChar='\\', multiline=True)
lisp_string.setParseAction(lambda s,l,t: String(t[0]))

special = "_-+*/^><=:'"
#lisp_symbol = Word(alphas + nums + '_-' + '?!') # any order
#lisp_symbol = Combine(Char(alphas) + Word(alphas + nums + '?' + '!')) # starts with alphas
lisp_symbol = Combine(Char(alphas+special) + Optional(Word(alphas + nums+special)) + Optional(Char('?!'))) # Ruby style

lisp_symbol.setParseAction(lambda s,l,t: Symbol(t[0]))

lisp_atom = lisp_symbol | lisp_string | lisp_number

lisp_list = nestedExpr(opener='(', closer=')', content = lisp_atom, ignoreExpr=lisp_string)
#lisp_list.setParseAction(lambda s,l,t: List(t)) # does not work


lisp_expr = lisp_atom | lisp_list

def parse(program):
    try:
        return lisp_expr[...].parseString(program, parseAll=True).asList()
    except Exception as e:
        raise SyntaxError(e)


def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)


"""
import re
from collections import UserString

def parse(program):
    "Read a Scheme expression from a string."
    return read_all_from_tokens(tokenize(program))

# the reg for the "-quoted strings
string_pattern = re.compile(r'\"([^"]+?)\"')
def tokenize(s):
    '''Convert a string into a list of tokens.

    an example:
    >>> tokenize('foo (a   b "bar (baz d)" z "seven (7 two)" ab (foo jaz ))')
    ['foo' '(' 'a' 'b' "bar (baz d)" 'z' "seven (7 two)" 'ab' '(' 'foo' 'jaz' ')' ')']
    '''
    # tokenize the text between the strings
    tokens = []
    prev_char = 0
    for m in string_pattern.finditer(s):
        mstart, mend = m.span()
        prev_toks = s[prev_char: mstart].replace('(',' ( ').replace(')',' ) ').split()
        tokens.extend(prev_toks + [String(m.group()[1:-1])]) # tokens and String
        prev_char = mend
    # the last chunk of the input string
    tokens += s[prev_char:].replace('(',' ( ').replace(')',' ) ').split()
    return tokens

def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

def read_all_from_tokens(tokens):
    '''Read all ()-closed expressions from tokens.'''

    all_expr = []
    while tokens:

        try:
            an_expr = read_from_tokens(tokens)
            # read_from_tokens pops the expression from tokens
            all_expr.append(an_expr)

        except SyntaxError as err:
            print("Currenlty parsed expressions:")
            for expr in all_expr:
                print(expr)

            raise err

    return all_expr

def read_from_tokens(tokens):
    '''Read one expression from a sequence of tokens.

    An expression is either a List or an atom.'''

    token = tokens.pop(0)
    # parse one nesting
    if '(' == token and not isinstance(token, String):
        L_one_expr = List()
        while not (tokens[0] == ')' and not isinstance(tokens[0], String)):
            L_one_expr.append(read_from_tokens(tokens))

            # unclosed expression
            if len(tokens) == 0:
                report_expr = lispstr(L_one_expr)[:-1] + ' _!)_'
                raise SyntaxError('Unclosed expression {}'.format(report_expr))

        tokens.pop(0) # pop off ')'
        return L_one_expr

    elif ')' == token and not isinstance(token, String):
        raise SyntaxError('Unexpected ) before tokens {}'.format(tokens))
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    if isinstance(token, String):
        return token
    try: return Int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

"""
