(source root_env "../lib_func.lisp")

(func .section (name) (print ".section" name))
(func .rodata  () (.section  ".rodata"))
(func .data    () (.section  ".data"))
(func .text    () (.section  ".text"))

(func .globl  (name) (print ".globl"  name))
(func .global (name) (print ".global" name))

(func label  (name) (print (+ name ":")))

(func .ascii (text) (print ".ascii" text))
(func .long  (text) (print ".long"  text))


(quote (the instructions))

(func one_operand_instruction (name x)   (print name x))
(func two_operand_instruction (name x y) (print name x "," y))

(func movl  (x y) (two_operand_instruction "movl" x y))
(func mov   (x y) (two_operand_instruction "mov"  x y))
(func xor   (x y) (two_operand_instruction "xor" x y))
(func cmp   (x y) (two_operand_instruction "cmp"  x y))
(func cmpb  (x y) (two_operand_instruction "cmpb" x y))
(func cmpl  (x y) (two_operand_instruction "cmpl" x y))
(func popq  (x)   (one_operand_instruction "popq" x))
(func pushq (x)   (one_operand_instruction "push" x))
(func popl  (x)   (one_operand_instruction "popl"  x))
(func pushl (x)   (one_operand_instruction "pushl" x))
(func je    (op)  (one_operand_instruction "je"   op))
(func jle   (x)   (one_operand_instruction "jle"  x))
(func jmp   (x)   (one_operand_instruction "jmp"  x))
(func inc   (x)   (one_operand_instruction "inc"  x))
(func incl  (x)   (one_operand_instruction "incl" x))

(func ret     () (print "ret"))
(func syscall () (print "syscall"))

(func address1 (addr_label reg_index offset)
	(join (str) (list addr_label "(" "," reg_index "," offset ")"))
)

(quote (
	(func address_byte (addr_label reg_index offset))
))

(quote (
	some assembly stuff
	probably its language constructions too?
	))

(func address_var_byte  (init_address relative_offset)
	(join (str) (list "(" init_address "+" relative_offset ")"))
	)
(func address_var_word  (init_address relative_offset) (address_var_byte init_address (* 2 relative_offset)))
(func address_var_dword (init_address relative_offset) (address_var_byte init_address (* 4 relative_offset)))
(func address_var_qword (init_address relative_offset) (address_var_byte init_address (* 8 relative_offset)))

(func address  (init_address relative_offset num_bytes)
	(join (str) (list "(" init_address "," relative_offset "," num_bytes ")"))
	)
(func address_byte  (init_address relative_offset) (address init_address relative_offset 1))
(func address_word  (init_address relative_offset) (address init_address relative_offset 2))
(func address_dword (init_address relative_offset) (address init_address relative_offset 4))
(func address_qword (init_address relative_offset) (address init_address relative_offset 8))

(quote ( registers ))

(define "def_reg_att" (macro (reg_name) (define root_env (str reg_name) (+ "%" (str reg_name)))))

(def_reg_att eax)
(def_reg_att eax)
(def_reg_att ebx)
(def_reg_att ecx)
(def_reg_att edx)
(def_reg_att esx)

(def_reg_att rax)
(def_reg_att rdx)

(def_reg_att esp)
(def_reg_att ebp)
(def_reg_att edi)

(def_reg_att rsp)
(def_reg_att rbp)

(def_reg_att rdi)
(def_reg_att rsi)

(quote (
))

(func call (symbolname) (print "call" symbolname))


(quote (
	;language
	; (global_variable '.byte 'variable (list 111 222 333))
	))

(func static_variable (type varname data)
	(begin
		(print (+ varname ":"))
		(print type (if (list? data) (join "," data) data)))
	)
(quote(
	; FIXME: type must be passed as a function and run it
	))

(quote ( linux ))

(quote ( order of arguments in syscalls
	%eax	Name	    Source 	            %ebx	        %ecx	        %edx	%esx	%edi
	))

(define "KERNEL" "$0x80")

(func interrupt_to   (code) (one_operand_instruction "int" code))
(func exit_to_kernel (exit_code)
	(begin (movl exit_code ebx) (movl "$1" eax) (interrupt_to KERNEL))
)

(debug "sourced x86.lisp")
