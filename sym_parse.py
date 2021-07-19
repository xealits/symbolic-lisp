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
