#   cat x86.lisp global_variable.lisp | sbcl --script > global_variable.s
#   as global_variable.s -o global_variable.o
#   ld global_variable.o
#   ./a.out 

all: global_variable2.out global_variable.out exit.out qexit.out max.out

%.s: %.lisp x86.lisp
	cat x86.lisp $< | sbcl --script > $@

%.o: %.s
	as $< -o $@

%.out: %.o
	ld $< -o $@

clean:
	rm *.o *.s

.PRECIOUS: %.s %.o

