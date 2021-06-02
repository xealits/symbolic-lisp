(source root_env "libio.lisp")

(define "prog" (list

(def_exit)
(def_string_length)

(.data)
(static_variable ".ascii" "string_variable" (list double_quote "Hello,_world daskhdjef\0" double_quote))

(.text)
(.globl "_start")
(label "_start")

(mov string_variable rdi)
(call _string_length)

(mov rax rdi)
(call _exit)


))

(comment (
there are 2 ways to do it:
1. explicitly manually def the functions you need from a lib
   and def some handy symbol that is invoked in (call <func_symbol>)
2. do it automatically: source lib is like from x import *
   but the compiler finds the minimal complete tree from the sources
   - it is C style plus the minimal complete tree resolution

explicit way is better
but C way is handy))

(print_prog prog)
