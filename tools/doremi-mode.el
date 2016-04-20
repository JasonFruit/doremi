(require 'generic-x)

(define-generic-mode 'doremi-mode
  '("#")
  '("fermata" "slur" "tie" "-" "+")
  '(("\"[^\"]+\"" . 'font-lock-string-face)     ;; quoted string
    ("[0-9]+/[0-9]+" . 'font-lock-string-face) ;; fraction
    ("[0-9\.]+" . 'font-lock-string-face) ;; numbers and note durations
    ("[A-Ga-g]\\(b\\|\\#\\|\\)\\{0,1\\} \\(major\\|minor\\)" . 'font-lock-string-face) ;; key
    ("[a-zA-Z][a-zA-Z0-9#\-]*:" . 'font-lock-type-face) ;; tags
    ("\\b\\(do\\|di\\|ra\\|re\\|ri\\|me\\|mi\\|fa\\|fi\\|se\\|sol\\|si\\|le\\|la\\|li\\|te\\|ti\\)\\b" . 'font-lock-comment-face)
    ("[a-zA-Z][a-zA-Z0-9#\-]*" . 'font-lock-builtin-face) ;; names
    ("[{}[\]]" . 'font-lock-builtin-face))     ;; brackets
  '("\\.drm$")
  nil
  "A major mode for editing Doremi music specification files")

(provide 'doremi-mode)

    ;; ("[a-zA-Z][a-zA-Z0-9#\-]*" . 'font-lock-builtin-face) ;; names
