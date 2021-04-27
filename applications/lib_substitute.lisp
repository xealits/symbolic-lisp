(define "substitute" (lambda (target_name sub expr)
      (if (list? expr)
          (map (curry substitute target_name sub) expr)
          (if (equal? expr target_name)
              sub
              expr)
      )))

(print "try substitute")

(define "substitute_example" (substitute "x" 5 (quote (1 2 x))))

