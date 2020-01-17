(source 'x86.lisp)

(quote (hello world assembly in x86_64

mov     rax, 1           ;system call number should be stored in rax
mov     rdi, 1           ; argument #1 in rdi: where to write (descriptor)?
mov     rsi, message     ; argument #2 in rsi: where does the string start?
mov     rdx, 14          ; argument #3 in rdx: how many bytes to write?
))

(.rodata)
(static_variable '.ascii 'message '"Hello,_world!\n\0")

(.text)
(.global '_start)

(label '_start)

(mov '$1       rax) (quote (syscall ID write))
(mov '$1       rdi) (quote (file descriptor = 1, stdout ))
(mov '$message rsi)
(mov '$14      rdx)
(syscall)

(quote (syscall ID exit))
(mov '$60      rax)
(mov '$0       rdi)
(syscall)
