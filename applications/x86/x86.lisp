;(format t "hello world")
;(defun literal 
;need simple ' '.join(strings) with normal escapes

; some assembly stuff
; probably it's language constructions too?
(defun .section (name) (format t ".section ~a~%" name))
(defun .data () (.section  ".data"))
(defun .text () (.section  ".text"))

; lisp doc
; http://www.lispworks.com/documentation/lw50/CLHS/Body/f_format.htm
; (format t ...)   to print to stdout
; (format nil ...) to return a string

;(defun .ascii (text) (format t ".ascii ~s~%" text))
(defun .ascii (text) (format t ".ascii \"~a\"~%" text))

(defun label (name) (format t "~a:~%" name))

; data types

(defun .byte (data) (format t ".byte ~a~%" data))
(defun .long (data) (format t ".long ~a~%" data))

(defconstant .byte (function .byte))
(defconstant .long (function .long))

; -------------- electronic datasheet, architecture instructions and definitions
(defun one_operand_instruction (name x)   (format t "~a ~a~%"     name x))
(defun two_operand_instruction (name x y) (format t "~a ~a, ~a~%" name x y))

;(defun movl (x y) (format t "movl ~a, ~a~%" x y))
(defun movl (x y) (two_operand_instruction "movl" x y))
(defun cmpl (x y) (two_operand_instruction "cmpl" x y))
(defun popq  (x)   (one_operand_instruction "popq" x))
(defun pushq (x)   (one_operand_instruction "push" x))
(defun popl  (x)   (one_operand_instruction "popl"  x))
(defun pushl (x)   (one_operand_instruction "pushl" x))
(defun je    (x)   (one_operand_instruction "je"   x))
(defun jle   (x)   (one_operand_instruction "jle"  x))
(defun jmp   (x)   (one_operand_instruction "jmp"  x))
(defun incl  (x)   (one_operand_instruction "incl" x))

(defun ret () (format t "ret~%"))

(defun interrupt_to (code) (format t "int $0x~x~%" code))

;(defun ebx () (format nil "%ebx"))
;(defun eax () (format nil "%eax"))

(defconstant ebx "%ebx")
(defconstant eax "%eax")
(defconstant esp "%esp")
(defconstant ebp "%ebp")
(defconstant edi "%edi")

; ----------------------------------- language constructions
(defconstant KERNEL #x80)
;(defun exit_to_kernel () (movl "$1" eax) (interrupt_to KERNEL)) ; exit code is already in ebx
;(defun exit_to_kernel (exit_code) (movl exit_code ebx) (movl "$1" eax) (interrupt_to KERNEL))

;(defgeneric exit_to_kernel (object)
;  (:documentation "blah"))
;
;(defmethod exit_to_kernel () (movl "$1" eax) (interrupt_to KERNEL)) ; exit code is already in ebx
;(defmethod exit_to_kernel (exit_code) (movl exit_code ebx) (movl "$1" eax) (interrupt_to KERNEL))

; https://rosettacode.org/wiki/Variadic_function#Common_Lisp
(defun exit_to_kernel (&rest exit_code) (dolist (code exit_code) (movl code ebx)) (movl "$1" eax) (interrupt_to KERNEL))

;(movl (adress_byte variable 0) (ebx))    ; exit code
;(defun address_byte (init_address relative_offset) (movl relative_offset edi))
; -- not so easy, address_byte is used inside of another call,
;    movl to edi must be done before the call, outside the parentheses

; let calls work like this:
; (call a b)
; =
; (preparatory calls, like movl $0, %edi)
; and return the address of result, which can be plugged into another function
; -- it won't scale of course

; so, for exit_to_kernel I need
;     movl variable, %ebx
;     ->
;     movl $0, %edi
;     movl variable(,%edi,1), %ebx

(defun index (addr base index multiplier) (format nil "~a(~a, ~a, ~a)" addr base index multiplier))
; base and index must be registers
; the others are not
(defun index_byte (init_address relative_offset) (movl relative_offset edi) (index init_address "" edi 1))

; displacement addressing, works with registers and labels
; was implemented in x64!
; apparently for labels these are equivalent:
; label   = (label)
; label+1 = (label+1)
(defun address_byte  (init_address relative_offset) (format nil "(~a+~a)" init_address relative_offset))
(defun address_word  (init_address relative_offset) (address_byte init_address (* 2 relative_offset)))
(defun address_dword (init_address relative_offset) (address_byte init_address (* 4 relative_offset)))
(defun address_qword (init_address relative_offset) (address_byte init_address (* 8 relative_offset)))

; (cons (function foo1) (function bar1))
(defun address (size)
    (cdr (assoc size
	        (list
	            (cons (function .byte) (function address_byte))
	            (cons (function .long) (function address_qword))
			)))
)



; macro defining a global variable:
;     reserve the space and label it
;     define a call returning the address of the variable
; (.data)
; (label "variable")   ; must be (variable .byte A)
; ; which defines the label and the function to access the values of the memory range: (A 0) (A 5) etc
; (.byte "111,222,333")
;(defun global_variable (var_size name init_data)
;    (.data)
;	(label name)
;	(funcall var_size init_data)
;	; define the address function for the variable name
;	;(defun (intern name) () (address var_size))
;	;(setf (symbol-function (intern name)) (lambda () (address var_size)))
;	(setf (fdefinition (intern name)) (lambda () (address var_size)))
;)

;(defmacro custom (name op const)
;  (let ((arg (gensym)))
;    `(defun ,name (,arg)
;       (,op ,const ,arg))))

(defmacro global_variable (var_size name init_data)
     (.data)
	 (label name)
	 (funcall var_size init_data)
    `(defun (intern name) ()
       (address ,var_size))
)


; name, params, locals, body and return register
; general structure:
; (let (each param or local = defun address relative to ebp)
;      body)
; the body refers to params and locals -- they expand to addresses
(defun c_frame (name params locals body return_addr)

    ; pop the frame
	(movl ebp esp) ; restore the stack pointer
	(popl ebp)     ; restore the base pointer
	(ret)
    )

