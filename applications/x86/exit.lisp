(source root_env "x86.lisp")

(.data)
(.ascii (join (str) (list double_quote "Hello,_world\0" double_quote)))

(.text)
(.globl "_start")

(label "_start")

(movl "$12" ebx)
(movl "$1"  eax)
(interrupt_to KERNEL)
