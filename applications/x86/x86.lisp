(source root_env "../lib_func.lisp")

(define "comment" (macro (comment) None))

(define "print_prog" (lambda (p)
	  (if (list? p)
		(map print_prog p)
		(if (is? p None)
		  None
		  (print (newlineit p))
		)
	  )
))

(func .section (name) (format "%s %s" ".section" name))
(func .rodata  () (.section  ".rodata"))
(func .data    () (.section  ".data"))
(func .text    () (.section  ".text"))

(func .globl  (name) (format "%s %s" ".globl"  name))
(func .global (name) (format "%s %s" ".global" name))

(func label  (name) (format "%s:" name))

(func .ascii (text) (format "%s %s" ".ascii" text))
(func .long  (text) (format "%s %s" ".long"  text))


(quote (the instructions))

(func one_operand_instruction (name x)   (format "%s %s" name x))
(func two_operand_instruction (name x y) (format "%s %s, %s" name x y))

(func movl  (x y) (two_operand_instruction "movl" x y))
(func mov   (x y) (two_operand_instruction "mov"  x y))
(func xor   (x y) (two_operand_instruction "xor" x y))
(func cmp   (x y) (two_operand_instruction "cmp"  x y))
(func cmpb  (x y) (two_operand_instruction "cmpb" x y))
(func cmpl  (x y) (two_operand_instruction "cmpl" x y))

(func pop   (x)   (one_operand_instruction "pop"  x))
(func push  (x)   (one_operand_instruction "push" x))
(func popq  (x)   (one_operand_instruction "popq" x))
(func pushq (x)   (one_operand_instruction "push" x))
(func popl  (x)   (one_operand_instruction "popl"  x))
(func pushl (x)   (one_operand_instruction "pushl" x))

(func je    (op)  (one_operand_instruction "je"   op))
(func jle   (x)   (one_operand_instruction "jle"  x))
(func jmp   (x)   (one_operand_instruction "jmp"  x))

(func dec   (x)   (one_operand_instruction "dec"  x))
(func inc   (x)   (one_operand_instruction "inc"  x))
(func incl  (x)   (one_operand_instruction "incl" x))

(func div  (x)     (one_operand_instruction "div" x))
(func sub  (x y)   (two_operand_instruction "sub" x y))
(func add  (x y)   (two_operand_instruction "add" x y))

(func ret     () "ret")
(func syscall () "syscall")

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

(func address_regs  (init_reg offset_reg step)
	(join (str) (list "(" init_reg "," offset_reg "," step ")"))
	)

(func address_reg_relative  (init_reg offset)
	(join (str) (list offset "(" init_reg ")"))
	)

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
(def_reg_att  dx)
(def_reg_att  dh)
(def_reg_att  dl)

(def_reg_att rcx)

(def_reg_att esp)
(def_reg_att ebp)
(def_reg_att edi)

(def_reg_att rsp)
(def_reg_att rbp)

(def_reg_att rdi)
(def_reg_att rsi)

(def_reg_att r8)
(def_reg_att r9)
(def_reg_att r10)

(comment (function inputs order: rdi, rsi, rcx, r8, r9))

(quote (
))

(func call (symbolname) (format "%s %s" "call" symbolname))


(quote (
	;language
	; (global_variable '.byte 'variable (list 111 222 333))
	))

(func static_variable (type varname data)
  (begin
    (define (out (out dyn_env)) varname (format "$%s" varname))
	(+
		(format "%s:\n" varname)
		(format "%s %s" type (if (list? data) (join "," data) data)))
  ))
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
	(format "%s\n%s\n%s" (movl exit_code ebx) (movl "$1" eax) (interrupt_to KERNEL))
)

(debug "sourced x86.lisp")
