
(quote (
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

(.ascii 'Hello,_world!\n\0)

x86_64: https://filippo.io/linux-syscall-table/
1	write	sys_write	fs/read_write.c
%rdi	              %rsi	            %rdx
unsigned int fd	const char __user * buf	size_t count
and
use syscall instruction

x86: https://www.informatik.htw-dresden.de/~beck/ASM/syscall_list.html
%eax	Name	    Source 	            %ebx	        %ecx	        %edx	%esx	%edi
4	    sys_write	fs/read_write.c 	unsigned int	const char *	size_t	-       -
and
use int 0x80 instruction
))


(quote (the following is x86 assembly for hello world))

(source 'x86.lisp)

(.data)
(static_variable '.ascii 'message '"Hello,_world!\n\0")

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
