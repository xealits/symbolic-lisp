(source root_env "x86.lisp")

(' ( a little i/o library))

(.text)


(' (TODO make these lisp functions, so that they are not just copied to assembly, but pulled by lisp
		 then make some dependancy system between them))


(func def_exit () (begin
(define (out (out dyn_env)) "_exit" "exit")
(list

(.text)

(label "exit")

(comment ( exit process
     input: rdi
	 returns it as the exit code))

(comment ( 32 bit exit
(movl   rdi ebx)
(movl "$1"  eax)    (comment (exit system call number))
(interrupt_to KERNEL)
))

(comment ((mov   rdi ebx) 64 bit grabs exit code from rdi))

(mov "$60"  rax)    (comment (exit system call number, exit code must be in rdi))
(syscall)
" "
)))



(func def_string_length () (begin
(define (out (out dyn_env)) "_string_length" "string_length")
(list

(.text)

(label "string_length")

(comment ( calculate the length of the string given by a pointer

     input: rdi -- pointer

	 returns the lenth in rax))

(xor rax rax)    (comment (it is the return register, init to 0 and increment for each string character))

(label ".loop")

(cmpb "$0" (address_byte rdi rax))

(je ".end")

(comment (TODO
	 .end symbol must return ".end"
	 how to get .end if it is defined later?))

(inc rax)
(jmp ".loop")

(label ".end")
(ret)
" "
)))






(func def_print_string () (begin
(comment (print null-terminated string to stdout via write syscall
     input: rdi -- pointer
     returns nothing
     ))

(define (out (out dyn_env)) "_print_string" "print_string")

(list
  (comment (string length of the null-terminated array for the write syscall))
  (if (find? dyn_env "_string_length")
	None
	(def_string_length)
	)

  (.text)
  (label "print_string")

  (comment (rdi already contains the pointer to the string))
  (call _string_length)   (comment (output -> rax))

  (comment (syscall arguments))
  (mov rax rdx)  (comment (length, number of bytes in the string))
  (mov rdi rsi)  (comment (the func input in rdi -> rsi for the syscall))

  (mov "$1" rax)
  (mov "$1" rdi)
  (syscall)
  (ret)
  )

))


(func def_print_char () (begin
(comment (print_char Accepts a character code directly as its first argument and prints it to stdout.
     input: rdi -- char code
     returns nothing
     ))

(define (out (out dyn_env)) "_print_char" "print_char")

(list
  (.text)
  (label "print_char")

  (comment (push the character on the stack to pass the stack pointer to the syscall))
  (push rdi)     (comment (it will push 64 bits, let's hope the syscall will get the correct 8 bits))

  (comment (syscall arguments))
  (mov "$1" rdx)  (comment (only 1 byte to write))
  (mov rsp rsi)   (comment (the stack pointer points to the char code))

  (mov "$1" rax)
  (mov "$1" rdi)
  (syscall)
  (pop rdi)       (comment (clear the stack))
  (ret)
  )

))



(func def_print_newline () (begin
(comment (print_newline  prints 0x0A to stdout.
     input: rdi -- char code
     returns nothing
     ))

(define (out (out dyn_env)) "_print_newline" "print_newline")

(list
  (.text)
  (label "print_newline")
  (comment (use print_char))
  (if (find? dyn_env "_print_char")
	None
	(def_print_char)
	)

  (mov "$10" rdi)
  (call _print_char)
  (ret)
  )

))


None
