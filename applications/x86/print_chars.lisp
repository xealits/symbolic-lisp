(source root_env "libio.lisp")

(define root_env "ascii_table" (env
(list
    "NUL"     "DLE"     " "          "0"     "@"     "P"   "`"   "p" 
    "SOH"     "DC1"     "!"          "1"     "A"     "Q"   "a"   "q" 
    "STX"     "DC2"     double_quote "2"     "B"     "R"   "b"   "r" 
    "ETX"     "DC3"     "#"          "3"     "C"     "S"   "c"   "s" 
    "EOT"     "DC4"     "$"          "4"     "D"     "T"   "d"   "t" 
    "ENQ"     "NAK"     "%"          "5"     "E"     "U"   "e"   "u" 
    "ACK"     "SYN"     "&"          "6"     "F"     "V"   "f"   "v" 
    "BEL"     "ETB"     single_quote "7"     "G"     "W"   "g"   "w" 
    "BS"      "CAN"     "("          "8"     "H"     "X"   "h"   "x" 
    "HT"      "EM"      ")"          "9"     "I"     "Y"   "i"   "y" 
    "LF"      "SUB"     "*"          ":"     "J"     "Z"   "j"   "z" 
    "VT"      "ESC"     "+"          ";"     "K"     "["   "k"   "{" 
    "FF"      "FS"      ","          "<"     "L"     "\\"  "l"   "|" 
    "CR"      "GS"      "-"          "="     "M"     "]"   "m"   "}" 
    "SO"      "RS"      "."          ">"     "N"     "^"   "n"   "~" 
    "SI"      "US"      "/"          "?"     "O"     "_"   "o"   "DEL"
	)

(list
   "$0"   "$16"  "$32"   "$48"   "$64"  "$80"  "$96" "$112"
   "$1"   "$17"  "$33"   "$49"   "$65"  "$81"  "$97" "$113"
   "$2"   "$18"  "$34"   "$50"   "$66"  "$82"  "$98" "$114"
   "$3"   "$19"  "$35"   "$51"   "$67"  "$83"  "$99" "$115"
   "$4"   "$20"  "$36"   "$52"   "$68"  "$84" "$100" "$116"
   "$5"   "$21"  "$37"   "$53"   "$69"  "$85" "$101" "$117"
   "$6"   "$22"  "$38"   "$54"   "$70"  "$86" "$102" "$118"
   "$7"   "$23"  "$39"   "$55"   "$71"  "$87" "$103" "$119"
   "$8"   "$24"  "$40"   "$56"   "$72"  "$88" "$104" "$120"
   "$9"   "$25"  "$41"   "$57"   "$73"  "$89" "$105" "$121"
  "$10"   "$26"  "$42"   "$58"   "$74"  "$90" "$106" "$122"
  "$11"   "$27"  "$43"   "$59"   "$75"  "$91" "$107" "$123"
  "$12"   "$28"  "$44"   "$60"   "$76"  "$92" "$108" "$124"
  "$13"   "$29"  "$45"   "$61"   "$77"  "$93" "$109" "$125"
  "$14"   "$30"  "$46"   "$62"   "$78"  "$94" "$110" "$126"
  "$15"   "$31"  "$47"   "$63"   "$79"  "$95" "$111" "$127"
    )

))

(define "prog" (list

(def_exit)
(def_print_char)
(def_print_newline)

(.text)
(.globl "_start")
(label "_start")

(comment (
(mov "$72"  rdi)   (call _print_char)
(mov "$101" rdi)   (call _print_char)
(mov "$108" rdi)   (call _print_char)
(mov "$108" rdi)   (call _print_char)
(mov "$111" rdi)   (call _print_char)
))

(mov (in ascii_table "H") rdi)   (call _print_char)
(mov (in ascii_table "e") rdi)   (call _print_char)
(mov (in ascii_table "l") rdi)   (call _print_char)
(mov (in ascii_table "l") rdi)   (call _print_char)
(mov (in ascii_table "o") rdi)   (call _print_char)

(call _print_newline)

(comment (mov rax rdi or move something to rdi, but print returns nothing))
(call _exit)

))

(print_prog prog)
