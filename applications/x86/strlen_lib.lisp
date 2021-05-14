(source root_env "libio.lisp")

(.data)
(static_variable ".ascii" "string_variable" (list double_quote "Hello,_world abdef\0" double_quote))

(.text)
(.globl "_start")
(label "_start")

(mov "$string_variable" rdi)
(call "string_length")

(mov rax rdi)
(call "exit")
