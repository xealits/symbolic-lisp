(quote (
        .global main

        .text
main:                                   # This is called by C library's startup code
        mov     $message, %rdi          # First integer (or pointer) parameter in %rdi
        call    puts                    # puts(message)
        ret                             # Return to C library code
message:
        .asciz "Hola, mundo"            # asciz puts a 0 byte at the end
		))

(quote (
  gcc   -fno-pie puts.s -o puts.out
  -- does not work
  gcc -fno-pie -no-pie puts.s -o puts.out
  clang -fno-pie puts.s -o puts.out
  ))

(source 'x86.lisp)

(.globl 'main)

(.text)

(static_variable '.ascii 'message '"Hello,_world!\n\0")

(label 'main)
(mov '$message rdi)
(call 'puts)
(ret)

