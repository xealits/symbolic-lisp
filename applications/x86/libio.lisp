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

(mov "$60"  rax)    (comment (exit system call number))
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

None
