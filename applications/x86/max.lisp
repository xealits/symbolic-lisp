(source root_env "x86.lisp")

(.data)
(label "data_items")

(.long "3,67,234,232,45,75,54,34,44,33,22,11,66,0")

(.text)
(.globl "_start")

(label "_start")

(movl "$0" edi)                  (quote ( move 0 into the index register))

(quote (
	;old addressing was done with a literal string
	;(movl 'data_items(,%edi,4) eax) (quote ( load the first byte of data))
))

(movl (address1 "data_items" edi 4) eax) (quote ( load the first byte of data))

(movl eax ebx)

(quote (
	;since this is the first item, %eax is
	;the biggest
	))

(label "start_loop") (quote ( LOOP semantics? for? while? complex automaton?))

(quote (;if semantics 1
		))
(cmpl "$0" eax)
(je "loop_exit")     (quote ( LOOP))

(incl edi)
(movl (address1 "data_items" edi 4) eax)

(quote (; if semantics 2
			))

(cmpl ebx eax)
(jle "start_loop")   (quote ( LOOP))
(movl eax ebx)
(jmp "start_loop")   (quote ( LOOP))

(label "loop_exit")  (quote ( LOOP))

(quote (
	;(exit_to_kernel ebx) ; copies ebx into ebx
	(exit_to_kernel 0)
	))

(quote (
	; copies ebx into ebx
	))
(exit_to_kernel ebx)
