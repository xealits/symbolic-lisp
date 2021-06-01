(source root_env "x86.lisp")

(define "prog" (list

(.data)
(static_variable ".byte" "variable" (list 111 222 333))

(.text)
(.globl "_start")

(label "_start")

(comment ( ; foo
))

(exit_to_kernel (address_var_byte "variable" 1))

))

(print_prog prog)
