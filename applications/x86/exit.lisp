
(.data)
(.ascii "Hello, world\\0")

(.text)
(format t ".globl _start~%")

(label "_start")

;(movl "$12" (ebx))    ; exit code
;(movl "$1"  (eax))    ; linux syscall code, 1 = exit
;(interrupt_to KERNEL) ; interrupt, call kernel

(exit_to_kernel "$12")

