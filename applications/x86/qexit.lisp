(source root_env "x86.lisp")

(.data)
(.ascii (join (str) (list double_quote "Hello,_world\0" double_quote)))

(.text)
(.globl "_start")

(label "_start")


(quote (movl esp ebx
(exit_to_kernel "$0")
))

(exit_to_kernel esp)
