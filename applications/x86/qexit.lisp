(source "x86.lisp")

(print "PRINT: qexit.lisp")

(.data)
(.ascii "Hello,_world\0")

(quote (movl esp ebx
(.text)
(.globl '_start)

(label '_start)

(exit_to_kernel '$0)

(exit_to_kernel esp)
))
