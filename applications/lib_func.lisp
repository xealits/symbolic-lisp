(define "func" (macro (func_name args body)
    (define
        (out (out dyn_env))
              func_name
              (nest (out (out dyn_env)) (env (list "_args" "_body") (list args body))))
    ))

(debug "sourced lib_func")
