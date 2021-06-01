(source root_env "x86.lisp")

(define "prog" (list

(.data)
(.ascii (join (str) (list double_quote "Hello,_world\0" double_quote)))

(.text)
(.globl "_start")

(label "_start")


(comment (movl esp ebx
(exit_to_kernel "$0")
))

(exit_to_kernel esp)

))

(print_prog prog)
