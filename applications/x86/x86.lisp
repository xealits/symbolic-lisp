(source "../lib_func.lisp")
(print "PRINT: x86.lisp")

(quote (
	;some assembly stuff
	;probably it's language constructions too?
	))

(func .section (name) (print ".section" name))
(func .rodata  () (.section  ".rodata"))
(func .data    () (.section  ".data"))
(func .text    () (.section  ".text"))

(.section "foo")
(.data)

(func .globl  (name) (print '.globl  name))
(func .global (name) (print '.global name))

(func label  (name) (print (+ name ':)))

(func .ascii (text) (print '.ascii text))
(func .long  (text) (print '.long  text))


(quote (the instructions))

(func one_operand_instruction (name x)   (print name x))
(func two_operand_instruction (name x y) (print name x ', y))

(func movl  (x y) (two_operand_instruction 'movl x y))
(func mov   (x y) (two_operand_instruction 'mov  x y))
(func cmpl  (x y) (two_operand_instruction 'cmpl x y))
(func popq  (x)   (one_operand_instruction 'popq x))
(func pushq (x)   (one_operand_instruction 'push x))
(func popl  (x)   (one_operand_instruction 'popl  x))
(func pushl (x)   (one_operand_instruction 'pushl x))
(func je    (op)   (one_operand_instruction 'je   op))
(func jle   (x)   (one_operand_instruction 'jle  x))
(func jmp   (x)   (one_operand_instruction 'jmp  x))
(func incl  (x)   (one_operand_instruction 'incl x))

(func ret     () (print 'ret))
(func syscall () (print 'syscall))


(func address1 (addr_label reg_index offset)
	(join "" (list addr_label par_l ', reg_index ', offset par_r))
)

(quote(
	;(func address_byte (addr_label reg_index offset))
))

(func address_byte  (init_address relative_offset)
	(join "" (list par_l init_address '+ relative_offset par_r))
	)
(func address_word  (init_address relative_offset) (address_byte init_address (* 2 relative_offset)))
(func address_dword (init_address relative_offset) (address_byte init_address (* 4 relative_offset)))
(func address_qword (init_address relative_offset) (address_byte init_address (* 8 relative_offset)))

(quote ( registers ))

(define 'eax '%eax)
(define 'ebx '%ebx)
(define 'ecx '%ecx)
(define 'edx '%edx)
(define 'esx '%esx)

(define 'rax '%rax)
(define 'rdx '%rdx)

(define 'esp '%esp)
(define 'ebp '%ebp)
(define 'edi '%edi)

(define 'rsp '%rsp)
(define 'rbp '%rbp)

(define 'rdi '%rdi)
(define 'rsi '%rsi)

(func call (symbolname) (print 'call symbolname))


(quote (
	;language
	; (global_variable '.byte 'variable (list 111 222 333))
	))

(func static_variable (type varname data)
	(begin
		(print (+ varname ':))
		(print type (if (list? data) (join ', data) data)))
	)
(quote(
	; FIXME: type must be passed as a function and run it
	))

(quote ( linux ))

(quote ( order of arguments in syscalls
	%eax	Name	    Source 	            %ebx	        %ecx	        %edx	%esx	%edi
	))

(define 'KERNEL '$0x80)

(func interrupt_to   (code) (one_operand_instruction 'int code))
(func exit_to_kernel (exit_code)
	(begin (movl exit_code ebx) (movl '$1 eax) (interrupt_to KERNEL))
)

