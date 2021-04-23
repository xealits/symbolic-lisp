(define "proc_nsp"
            (nsp (list "_proc")
                 (quote ((
                     (nsp (list "_proc") (list (map (eval _dyn) _args)))
                     ))
                 )
            )
    )

(define "eval_explicit2"
            (nsp (list "_proc")
                 (quote ((
                     (print "EVAL EXPL _args: " _args)

                     (define 'target_name  (eval2 _dyn (index 0 _args)))
                     (define 'substitution (eval2 _dyn (index 1 _args)))
                     (define 'expr                     (index 2 _args))

                     (if (list? expr)
                         None
                         (print 'EVAL_EXPLICIT2_list expr))

                     (if (list? expr)
                         (map (eval_explicit2 target_name substitution) expr)
                         (if (equal? expr target_name)
                             substitution
                             expr)
                     )))
                 )
            )
    )

(define 'func (nsp
    (quote ("_proc"))
    (quote ((
        (print "_args" _args)
        (print "_dyn"  (nsp_keys _dyn))
        (define 'name      (index 0 _args))
        (define 'arguments (index 1 _args))
        (define 'body      (index 2 _args))
        (print '_ARGS _args ":" name arguments)

        (define name (proc_nsp
              (eval_explicit2 "eval_explicit2" arguments
              (define "nsp_matched_args"
                    (nsp (quote eval_explicit2)
                         (map (eval .) _args))))
              (quote (print "LOG:   nsp_matched_args" nsp_matched_args))
              (list 'eval 'nsp_matched_args body)
         ) _dyn)
    )))))

(func foo (x y) (+ x y))

(func substitute (target_name sub expr)
      (if (list? expr)
          (map (eval_explicit2 target_name sub) expr)
          (if (equal? expr target_name)
              sub
              expr)
      ))

(print "try substitute")

(define 'substitute_example  (eval_explicit2 "eval_explicit2" 5 (1 2 eval_explicit2)))
(define 'substitute_example2 (substitute "x" 5 (quote (1 2 x))))
