(source 'x86.lisp)

(.data)
(static_variable '.byte 'variable (list 111 222 333))

(.text)
(.globl '_start)

(label '_start)

(quote ( ; foo
))

(exit_to_kernel (address_byte 'variable 1))
