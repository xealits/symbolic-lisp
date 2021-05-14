(source root_env "x86.lisp")

(' ( a little i/o library))

(.text)


(' (TODO make these lisp functions, so that they are not just copied to assembly, but pulled by lisp
		 then make some dependancy system between them))



(label "exit")

(' ( exit process
     input: rdi
	 returns it as the exit code))

(' ( 32 bit exit
(movl   rdi ebx)
(movl "$1"  eax)    (' (exit system call number))
(interrupt_to KERNEL)
))

(' ((mov   rdi ebx) 64 bit grabs exit code from rdi))

(mov "$60"  rax)    (' (exit system call number))
(syscall)


(label "string_length")

(' ( calculate the length of the string given by a pointer

     input: rdi -- pointer

	 returns the lenth in rax))

(xor rax rax)    (' (it is the return register, init to 0 and increment for each string character))

(label ".loop")

(cmpb "$0" (address_byte rdi rax))

(je ".end")

(' (TODO
	 .end symbol must return ".end"
	 how to get .end if it is defined later?))

(inc rax)
(jmp ".loop")

(label ".end")
(ret)
