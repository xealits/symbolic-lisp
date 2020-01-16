(quote (
	;some assembly stuff
	;probably it's language constructions too?
	))

(define .section (lambda (name) (stdout '.section name)))
(define .data    (lambda () (.section  '.data)))
(define .text    (lambda () (.section  '.text)))

(define .globl (lambda (name) (stdout '.globl name)))

(define label  (lambda (name) (stdout (+ name ':))))

(define .ascii (lambda (text) (stdout '.ascii text)))
(define .long  (lambda (text) (stdout '.long  text)))


(quote (the instructions))

(define one_operand_instruction (lambda (name x)   (stdout name x)))
(define two_operand_instruction (lambda (name x y) (stdout name x ', y)))

(define movl  (lambda (x y) (two_operand_instruction 'movl x y)))
(define cmpl  (lambda (x y) (two_operand_instruction 'cmpl x y)))
(define popq  (lambda (x)   (one_operand_instruction 'popq x)))
(define pushq (lambda (x)   (one_operand_instruction 'push x)))
(define popl  (lambda (x)   (one_operand_instruction 'popl  x)))
(define pushl (lambda (x)   (one_operand_instruction 'pushl x)))
(define je    (lambda (x)   (one_operand_instruction 'je   x)))
(define jle   (lambda (x)   (one_operand_instruction 'jle  x)))
(define jmp   (lambda (x)   (one_operand_instruction 'jmp  x)))
(define incl  (lambda (x)   (one_operand_instruction 'incl x)))

(define ret (lambda () (stdout 'ret)))


(define address1 (lambda (addr_label reg_index offset)
	(join addr_label par_l ', reg_index ', offset par_r)
))

(quote ( registers ))

(define ebx '%ebx)
(define eax '%eax)
(define esp '%esp)
(define ebp '%ebp)
(define edi '%edi)

(quote ( linux ))

(define KERNEL '$0x80)

(define interrupt_to (lambda (code) (one_operand_instruction 'int code)))
(define exit_to_kernel (lambda (exit_code)
	(begin (movl exit_code ebx) (movl '$1 eax) (interrupt_to KERNEL))
))
