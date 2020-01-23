
(quote (the following is x86 assembly for hello world))

(source 'x86.lisp)

(.text)
(.globl '_start)

(label '_start)

(movl '$4       eax) (quote (syscall ID write))
(movl '$1       ebx) (quote (file descriptor = 1, stdout ))
(movl '$message ecx)
(movl '$14      edx)
(interrupt_to KERNEL)

(movl '$1       eax) (quote (syscall ID exit))
(movl '$0       ebx) (quote (exit code))
(interrupt_to KERNEL)
