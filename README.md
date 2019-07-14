Test an idea:
for `(foo (a b) c)` find `foo` by the `eval` in the current namespace
and pass the decision what to do with the rest to the `foo`,
with pointers to the current (caller) namespace and to the namespace of `foo` (lexical).

