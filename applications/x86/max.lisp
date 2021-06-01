(source root_env "x86.lisp")

(define "prog" (list

(.data)
(label "data_items")

(.long "3,67,234,232,45,75,54,34,44,33,22,11,66,0")

(.text)
(.globl "_start")

(label "_start")

(movl "$0" edi)                  (comment ( move 0 into the index register))

(comment (
	;old addressing was done with a literal string
	;(movl 'data_items(,%edi,4) eax) (comment ( load the first byte of data))
))

(movl (address1 "data_items" edi 4) eax) (comment ( load the first byte of data))

(movl eax ebx)

(comment (
	;since this is the first item, %eax is
	;the biggest
	))

(label "start_loop") (comment ( LOOP semantics? for? while? complex automaton?))

(comment (;if semantics 1
		))
(cmpl "$0" eax)
(je "loop_exit")     (comment ( LOOP))

(incl edi)
(movl (address1 "data_items" edi 4) eax)

(comment (; if semantics 2
			))

(cmpl ebx eax)
(jle "start_loop")   (comment ( LOOP))
(movl eax ebx)
(jmp "start_loop")   (comment ( LOOP))

(label "loop_exit")  (comment ( LOOP))

(comment (
	;(exit_to_kernel ebx) ; copies ebx into ebx
	(exit_to_kernel 0)
	))

(comment (
	; copies ebx into ebx
	))
(exit_to_kernel ebx)

))

(print_prog prog)
