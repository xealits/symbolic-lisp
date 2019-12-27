(define substitute
  (lambda (x varname sub)
    (if (symbol? x)
        (if (equal? x varname) sub x)
        (if (list? x) (map (lambda (i) (substitute i varname sub)) x)
            x)
    )
  )
)
