(source 'x86.lisp)

(.data)
(.ascii '"Hello,_world\0")

(.text)
(.globl '_start)

(label '_start)

(movl '$12 ebx)
(movl '$1  eax)
(interrupt_to KERNEL)
