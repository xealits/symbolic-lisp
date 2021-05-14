#   cat x86.lisp global_variable.lisp | sbcl --script > global_variable.s
#   as global_variable.s -o global_variable.o
#   ld global_variable.o
#   ./a.out 

all: global_variable3.out exit.out qexit.out max.out hello_world.out strlen_lib.lisp

#./sym_repl.py --script applications/x86/exit_test.lisp

%.s: %.lisp x86.lisp
	#cat x86.lisp $< | sbcl --script > $@
	#cat x86.lisp $< | ../../sym_repl.py --script > $@
	../../sym_repl.py --script $< > $@

%.o: %.s
	as $< -o $@

%.out: %.o
	ld $< -o $@

clean:
	rm *.o *.s

.PRECIOUS: %.s %.o

