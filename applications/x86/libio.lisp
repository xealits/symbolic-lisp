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



(define "loop" (macro (name body end)
(begin
  (assert (string? name))
  (assert (list?   body))
  (assert (list?   end))

  (define dyn_env "loop_name" (+ ".loop" name))
  (define dyn_env "loop_end"  (+ ".end"  name))

  (list
    (label loop_name)
    (map (curry eval dyn_env) body)
    (jmp   loop_name)
    (label loop_end)
    (map (curry eval dyn_env) end))
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

(loop "_string_len"
  (
    (cmpb "$0" (address_byte rdi rax))
    (je loop_end)
    (inc rax)
	)

  ( (ret) )
  )

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
  " "
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
  " "
  )

))



(func def_print_newline () (begin
(comment (print_newline  prints 0x0A to stdout.
     input: rdi -- char code
     returns nothing
     ))

(define (out (out dyn_env)) "_print_newline" "print_newline")

(list
  (comment (use print_char))
  (if (find? dyn_env "_print_char")
	None
	(def_print_char)
	)

  (.text)
  (label "print_newline")

  (mov "$10" rdi)
  (call _print_char)
  (ret)
  " "
  )

))


(func def_print_uint () (begin
(comment (
    print_uint Outputs an unsigned 8-byte integer in decimal format.

    We suggest you create a buffer on the stack and store the division results there. Each
    time you divide the last value by and store the corresponding digit inside the
    buffer. Do not forget, that you should transform each digit into its ASCII code
    (e.g., 0x04 becomes 0x34).

	div "$10"
	Unsigned divide RDX:RAX by r/m64, with
    result stored in RAX ← Quotient, RDX ←
    Remainder.

    input: rdi -- uint to print
    returns nothing
    ))

(define (out (out dyn_env)) "_print_uint" "print_uint")

(list
  (.text)
  (label "print_uint")

  (comment (div input))
  (mov rdi rax)
  (xor rdx rdx)

  (comment ((xor rcx rcx) rcx and r11 are modified by the syscall instruction))
  (xor r9 r9)    (comment (counter of digits))
  (mov "$10" r8) (comment (divider))

  (comment (the place for the byte buffer on the stack))
  (mov rsp r10) 
  (dec r10)

  (label ".loop_digit")

  (comment ((div "$10") does div by literal work?
                        no:
                        Error: operand type mismatch for `div'))

  (div r8)
  (comment (don't push-pop the stack - just address it mov %cl, (%esi,%eax,1)))
  (add "$0x30" dl)
  (mov dl (address_reg_relative r10 0))

  (comment ((push  rdx)   manual has no way to push only 1 byte... so how will it work?))

  (inc r9)

  (comment (if nothing is left in rax - done, else loop))
  (cmp "$0" rax)
  (je ".end")

  (xor rdx rdx)
  (dec r10)
  (jmp ".loop_digit")

  (label ".end")
  (comment (syscall arguments))
  (mov r9  rdx)  (comment (length, number of bytes in the string))
  (mov r10 rsi)  (comment (the pointer to the beginning of the string))

  (mov "$1" rax) (comment (write syscall number))
  (mov "$1" rdi) (comment (the output fd, stdout=1))
  (syscall)

  (comment ((sub r9 rsp) no need to clear the stack))
  (ret)
  " "
  )

))

None
