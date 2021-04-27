(define "func" (lambda (func_name args body)
          (define
              (out (out dyn_env))
              func_name
              (nest (out (out dyn_env)) (env (list "_args" "_body") (list args body))))
      ))
