(source root_env "libio.lisp")

(define "prog" (list

(def_exit)
(def_print_string)

(comment (test the dependency is defined))
(assert (find? dyn_env "_string_length"))

(.data)
(static_variable ".ascii" "string_variable" (list double_quote "Hello, null-terminated lib _world daskhdjef\0" double_quote))

(.text)
(.globl "_start")
(label "_start")

(mov string_variable rdi)
(call _print_string)

(comment (mov rax rdi or move something to rdi, but print returns nothing))
(call _exit)

))

(print_prog prog)
