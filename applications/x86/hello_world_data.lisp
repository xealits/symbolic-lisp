
(quote (the following is x86 assembly for hello world))

(source 'x86.lisp)

(.data)
(static_variable '.ascii 'message '"Hello,_world!\n\0")

(.globl 'message)
