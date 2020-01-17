(quote (
	;some assembly stuff
	;probably it's language constructions too?
	))

(define .section (lambda (name) (stdout '.section name)))
(define .rodata  (lambda () (.section  '.rodata)))
(define .data    (lambda () (.section  '.data)))
(define .text    (lambda () (.section  '.text)))

(define .globl  (lambda (name) (stdout '.globl  name)))
(define .global (lambda (name) (stdout '.global name)))

(define label  (lambda (name) (stdout (+ name ':))))

(define .ascii (lambda (text) (stdout '.ascii text)))
(define .long  (lambda (text) (stdout '.long  text)))


(quote (the instructions))

(define one_operand_instruction (lambda (name x)   (stdout name x)))
(define two_operand_instruction (lambda (name x y) (stdout name x ', y)))

(define movl  (lambda (x y) (two_operand_instruction 'movl x y)))
(define mov   (lambda (x y) (two_operand_instruction 'mov  x y)))
(define cmpl  (lambda (x y) (two_operand_instruction 'cmpl x y)))
(define popq  (lambda (x)   (one_operand_instruction 'popq x)))
(define pushq (lambda (x)   (one_operand_instruction 'push x)))
(define popl  (lambda (x)   (one_operand_instruction 'popl  x)))
(define pushl (lambda (x)   (one_operand_instruction 'pushl x)))
(define je    (lambda (x)   (one_operand_instruction 'je   x)))
(define jle   (lambda (x)   (one_operand_instruction 'jle  x)))
(define jmp   (lambda (x)   (one_operand_instruction 'jmp  x)))
(define incl  (lambda (x)   (one_operand_instruction 'incl x)))

(define ret     (lambda () (stdout 'ret)))
(define syscall (lambda () (stdout 'syscall)))


(define address1 (lambda (addr_label reg_index offset)
	(join str_empty (list addr_label par_l ', reg_index ', offset par_r))
))

(quote(
	;(define address_byte (lambda (addr_label reg_index offset)))
))

(define address_byte  (lambda (init_address relative_offset)
	(join str_empty (list par_l init_address '+ relative_offset par_r))
	))
(define address_word  (lambda (init_address relative_offset) (address_byte init_address (* 2 relative_offset))) )
(define address_dword (lambda (init_address relative_offset) (address_byte init_address (* 4 relative_offset))) )
(define address_qword (lambda (init_address relative_offset) (address_byte init_address (* 8 relative_offset))) )

(quote ( registers ))

(define eax '%eax)
(define ebx '%ebx)
(define ecx '%ecx)
(define edx '%edx)
(define esx '%esx)

(define rax '%rax)
(define rdx '%rdx)

(define esp '%esp)
(define ebp '%ebp)
(define edi '%edi)

(define rsp '%rsp)
(define rbp '%rbp)

(define rdi '%rdi)
(define rsi '%rsi)

(quote (
	;language
	; (global_variable '.byte 'variable (list 111 222 333))
	))

(define static_variable (lambda (type varname data)
	(begin
		(stdout (+ varname ':))
		(stdout type (if (list? data) (join ', data) data)))
	))
(quote(
	; FIXME: type must be passed as a function and run it
	))

(quote ( linux ))

(quote ( order of arguments in syscalls
	%eax	Name	    Source 	            %ebx	        %ecx	        %edx	%esx	%edi
	))

(define KERNEL '$0x80)

(define interrupt_to (lambda (code) (one_operand_instruction 'int code)))
(define exit_to_kernel (lambda (exit_code)
	(begin (movl exit_code ebx) (movl '$1 eax) (interrupt_to KERNEL))
))
