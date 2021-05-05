(source root_env "x86.lisp")

(quote (
(static_variable "db" "message"
    (list
	  (join (str) (list double_quote "Hello, world!" double_quote))
	  10
	  )
	)

(print "message:" ".byte"
	  (join (str) (list double_quote "Hello, world!" double_quote ","))
	  10
	)

global _start
section .data
message: db 'hello, world!', 10
section .text

_start:
mov     rax, 1           ;system call number should be stored in rax
mov     rdi, 1           ; argument #1 in rdi: where to write (descriptor)?
mov     rsi, message     ; argument #2 in rsi: where does the string start?
mov     rdx, 14          ; argument #3 in rdx: how many bytes to write?
syscall                  ; this instruction invokes a system call
))


(.data)
(static_variable ".ascii" "message"
	  (join (str) (list double_quote "Hello, world!\n\0" double_quote))
	)

(.text)
(.globl "_start")
(label "_start")

(mov "$1" rax)
(mov "$1" rdi)
(mov "$message" rsi)
(mov "$14" rdx)
(syscall)

(quote (syscall exit process))
(mov "$60"     rax)
(mov "$0"      rdi)
(syscall)
