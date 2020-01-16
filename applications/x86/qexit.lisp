(source 'x86.lisp)

(.data)
(.ascii '"Hello,_world\0")

(.text)
(.globl '_start)

(label '_start)

(quote (movl esp ebx
(exit_to_kernel '$0)
))

(exit_to_kernel esp)
