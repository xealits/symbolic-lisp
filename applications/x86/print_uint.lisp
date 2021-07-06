(source root_env "libio.lisp")

(define "prog" (list

(def_exit)
(def_print_uint)
(def_print_newline)

(.text)
(.globl "_start")
(label "_start")

(comment (rdi is input))
(mov "$923115" rdi)
(call _print_uint)

(call _print_newline)

(comment (mov rax rdi or move something to rdi, but print returns nothing))
(call _exit)

))

(print_prog prog)
