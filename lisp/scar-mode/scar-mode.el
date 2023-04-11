;;; scar-mode.el -*- lexical-binding: t; no-byte-compile: t; -*-
;;-- header
;;
;; Copyright (C) 2023 John Grey
;;
;; Author: John Grey <https://github.com/jgrey4296>
;; Maintainer: John Grey <johngrey4296 at gmail.com>
;; Created: April 07, 2023
;; Modified: April 07, 2023
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
;;  A Mode for interacting with relic scar files (dawn of war 2)
;;
;;; Code:

;;-- end header

(defvar-local scar-mode-map
  (make-sparse-keymap))

;; Fontlock:
;; List of '(regex (groupnum "face")+)
(rx-let (

         )

  (defconst scar-font-lock-keywords
    '(

      )
    "Highlighting for scar-mode"
    )
  )

(defvar scar-mode-syntax-table
  (let ((st (make-syntax-table)))
    (modify-syntax-entry ?. "." st)
    (modify-syntax-entry ?! "." st)
    (modify-syntax-entry ?$ "_" st)
    ;;underscores are valid parts of words:
    (modify-syntax-entry ?_ "w" st)
    (modify-syntax-entry ?/ "<12" st)
    (modify-syntax-entry ?\n ">" st)
    (modify-syntax-entry ?\" """" st)
    (modify-syntax-entry ?\( "()" st)
    (modify-syntax-entry ?\[ "(]" st)
    (modify-syntax-entry ?: ".:2" st)
    st)
  "Syntax table for the scar-mode")


(define-derived-mode scar-mode fundamental-mode
    "scar"
    (interactive)
    (kill-all-local-variables)
    (use-local-map scar-mode-map)

    ;; font-lock-defaults: (keywords disable-syntactic case-fold syntax-alist)
    ;; (set (make-local-variable 'font-lock-defaults) (list scar-font-lock-keywords nil))
    ;; (set (make-local-variable 'font-lock-syntactic-face-function) 'scar-syntactic-face-function)
    ;; (set (make-local-variable 'indent-line-function) 'scar-indent-line)
    ;; (set (make-local-variable 'comment-style) '(plain))
    ;; (set (make-local-variable 'comment-start) "//")
    ;; (set (make-local-variable 'comment-use-syntax) t)
    ;; (set-syntax-table scar-mode-syntax-table)
    ;;
    (setq major-mode 'scar-mode)
    (setq mode-name "scar")
    (run-mode-hooks)
    (outline-minor-mode)
    (yas-minor-mode)

    )
(add-to-list 'auto-mode-alist '("\.scar" . scar-mode))

(provide 'scar-mode)
;;; scar-mode.el ends here
