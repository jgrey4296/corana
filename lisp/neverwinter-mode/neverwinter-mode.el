;;; neverwinter-mode.el -*- lexical-binding: t; no-byte-compile: t; -*-
;;-- header
;;
;; Copyright (C) 2022 John Grey
;;
;; Author: John Grey <https://github.com/jgrey4296>
;; Maintainer: John Grey <johngrey4296 at gmail.com>
;; Created: November 09, 2022
;; Modified: November 09, 2022
;; Version: 0.0.1
;; Keywords:
;; Homepage: https://github.com/jgrey4296
;; Package-Requires: ((emacs "24.3"))
;; Package written on: ((emacs 28.2))
;;
;; This file is not part of GNU Emacs.
;;
;;; Commentary:
;;
;; Mode for infinity engine `.d` files,
;; as exported from weidu
;;
;;; Code:

;;-- end header

(defvar-local neverwinter-mode-map

  (make-sparse-keymap))

;; List of '(regex (groupnum "face")+)
(defconst neverwinter-font-lock-keywords
  (list
   ;;backquote (,(rx ) (subexp facename override laxmatch))
   )
  "Highlighting for neverwinter-mode"
  )

(define-derived-mode neverwinter-mode fundamental-mode
  "neverwinter"
  (interactive)
  (kill-all-local-variables)
  (use-local-map neverwinter-mode-map)

  ;; font-lock-defaults: (keywords disable-syntactic case-fold syntax-alist)
  ;; (set (make-local-variable 'font-lock-defaults) (list neverwinter-font-lock-keywords nil))
  ;; (set (make-local-variable 'font-lock-syntactic-face-function) 'neverwinter-syntactic-face-function)
  ;; (set (make-local-variable 'indent-line-function) 'neverwinter-indent-line)
  ;; (set (make-local-variable 'comment-style) '(plain))
  ;; (set (make-local-variable 'comment-start) "//")
  ;; (set (make-local-variable 'comment-use-syntax) t)
  ;; (set-syntax-table neverwinter-mode-syntax-table)
  ;;
  (setq major-mode 'neverwinter-mode)
  (setq mode-name "neverwinter")
  (run-mode-hooks)
  (outline-minor-mode)
  (yas-minor-mode)

  )
(add-to-list 'auto-mode-alist '("\.neverwinter" . neverwinter-mode))

(provide 'neverwinter-mode)
;;; neverwinter-mode.el ends here
