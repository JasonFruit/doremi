(defvar doremi2-mode-hook (list (lambda ()
				  (setq indent-tabs-mode nil))))

(defvar doremi2-mode-map
  (let ((map (make-keymap)))
    (define-key map "\C-j" 'newline-and-indent)
    map)
  "Keymap for Doremi 2e major mode")

(add-to-list 'auto-mode-alist '("\\.drm\\'" . doremi2-mode))

(defconst doremi2-font-lock-keywords
  '(("\\(fermata\\|slur\\|tie\\|-\\|+\\)" . font-lock-builtin-face)
    ("\"[^\"]+\"" . font-lock-string-face)     ;; quoted string
    ("[0-9]+/[0-9]+" . font-lock-string-face) ;; fraction
    ("[0-9\.]+" . font-lock-string-face) ;; numbers and note durations
    ("[A-Ga-g]\\(b\\|\\#\\|\\)\\{0,1\\} \\(major\\|minor\\)" . font-lock-string-face) ;; key
    ("[a-zA-Z][a-zA-Z0-9#\-]*:" . font-lock-type-face) ;; tags
    ("\\b\\(do\\|di\\|ra\\|re\\|ri\\|me\\|mi\\|fa\\|fi\\|se\\|sol\\|si\\|le\\|la\\|li\\|te\\|ti\\)\\b" . font-lock-comment-face)
    ("[a-zA-Z][a-zA-Z0-9#\-]*" . font-lock-builtin-face) ;; names
    ("[{}[\]]" . font-lock-builtin-face))     ;; brackets
  "Highlighting expressions for Doremi 2e major mode")

;;;indentation rules
;; 1. everything is indented to the column after the last open brace
;;    or bracket

(defun doremi2-indent-line ()
  (interactive)
  (beginning-of-line)
  (if (bobp)
      (indent-line-to 0)
    (let ((cur-point (point))
	  (indents '(0))
	  (line-start 0))
      (beginning-of-buffer)
      (while (not (= (point) cur-point))
	(if (bolp) (setq line-start (point)))
	(if (or (= (char-after) 91)
		(= (char-after) 123))
	    (setq indents (cons (+ (- (point) line-start) 1) indents)))
	(if (or (= (char-after) 93)
		(= (char-after) 125))
	    (setq indents (cdr indents)))
	(forward-char))
      (indent-line-to (car indents)))))

(defvar doremi2-mode-syntax-table
  (let ((st (make-syntax-table)))
    (modify-syntax-entry ?- "w" st)
    (modify-syntax-entry ?# "w" st)
    (modify-syntax-entry ?+ "w" st)
    st)
  "Syntax table for the Doremi 2e major mode")

(defun doremi2-mode ()
  "Major mode for editing Doremi music-representation files (2e)"
  (interactive)
  (kill-all-local-variables)
  (set-syntax-table doremi2-mode-syntax-table)
  (use-local-map doremi2-mode-map)
  (set (make-local-variable 'font-lock-defaults) '(doremi2-font-lock-keywords))
  (set (make-local-variable 'indent-line-function) 'doremi2-indent-line)
  (setq major-mode 'doremi2-mode)
  (setq mode-name "Doremi 2e")
  (run-hooks 'doremi2-mode-hook))

(provide 'doremi2-mode)
