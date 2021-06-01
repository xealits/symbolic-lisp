(source root_env "libio.lisp")

(define "prog" (list

(def_exit)
(def_string_length)

(.data)
(static_variable ".ascii" "string_variable" (list double_quote "Hello,_world daskhdjef\0" double_quote))

(.text)
(.globl "_start")
(label "_start")

(mov "$string_variable" rdi)
(call "string_length")    (comment 1)

(mov rax rdi)
(call "exit")             (comment (so this and 1 must pull the definitions like exit from the lib))


))

(print_prog prog)
