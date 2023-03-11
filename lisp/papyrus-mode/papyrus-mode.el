;;; papyrus-mode.el -*- lexical-binding: t; no-byte-compile: t; -*-
;;-- header
;; Major mode for Bethesda's Papyrus
;; by Ricky Taylor (ricky26)
;; https://www.creationkit.com/index.php?title=Emacs_Setup
;;-- end header


;;;#autoload

(add-to-list 'auto-mode-alist '("\\.psc\\'" . papyrus-mode))

;; These are what I used to generate the regex.

;; (regexp-opt '("ScriptName" "scriptName" "as" "As"
;;               "extends" "Extends" "new" "New"
;;               "Property" "property" "EndProperty" "endProperty"
;;               "Auto" "AutoReadOnly" "auto" "autoReadOnly"
;;               "Conditional" "conditional"
;;               "Event" "event"
;;               "EndEvent" "endEvent"
;;               "Function" "function"
;;               "EndFunction" "endFunction"
;;               "If" "EndIf" "if" "endIf" "else" "Else" "elseIf" "ElseIf"
;;               "While" "EndWhile" "while" "endWhile"
;;               "state" "State" "endState" "EndState"
;;               "parent" "Parent" "hidden" "Hidden"))


;; (regexp-opt '("int" "Int" "string" "String" "bool "Bool"
;;               "Float" "float" "GlobalVariable" "globalVariable"
;;               "Quest" "quest"
;;               "objectReference" "ObjectReference"
;;               "Game" "Debug"))

(defvar papyrus-mode-hook nil)
(defvar papyrus-tab-width nil)
(defvar papyrus-compiler "PapyrusCompiler.exe")
(defvar papyrus-flags ())

(defvar papyrus-mode-map
  (let ((map (make-keymap)))
    ;(define-key map "\C-j" 'newline-and-indent)
    map)
  "Keymap for Papyrus major mode")

(defvar papyrus-font-lock-keywords
  (list
   '("{[^}]*}" . font-lock-string-face)
   '("\\<\\(?:A\\(?:s\\|uto\\(?:ReadOnly\\)?\\)\\|Conditional\\|E\\(?:lse\\|nd\\(?:Event\\|Function\\|If\\|Property\\|\\(?:Stat\\|Whil\\)e\\)\\|vent\\|xtends\\)\\|Function\\|Hidden\\|If\\|New\\|P\\(?:arent\\|roperty\\)\\|S\\(?:\\(?:criptNam\\|tat\\)e\\)\\|While\\|a\\(?:s\\|uto\\(?:ReadOnly\\)?\\)\\|conditional\\|e\\(?:lse\\|nd\\(?:Event\\|Function\\|If\\|ElseIf\\|elseIf\\|Property\\|\\(?:Stat\\|Whil\\)e\\)\\|vent\\|xtends\\)\\|function\\|hidden\\|if\\|new\\|p\\(?:arent\\|roperty\\)\\|\\(?:s\\(?:criptNam\\|tat\\)\\|whil\\)e\\)\\>"
 . font-lock-keyword-face)
   '("\\<\\(?:Bool\\|Debug\\|Float\\|G\\(?:\\(?:am\\|lobalVariabl\\)e\\)\\|Int\\|ObjectReference\\|Quest\\|String\\|bool\\|float\\|globalVariable\\|int\\|objectReference\\|quest\\|string\\)\\>" . font-lock-builtin-face)
   '("\"[^\"]*\"" . font-lock-string-face)
   '(".\\<[A-Za-z0-9_]+" . font-lock-variable-name-face)
   )
  )

(defun papyrus-indent-line ()
  "Indent papyrus code"
  (interactive)
  (beginning-of-line)
  (if (bobp)
      (indent-line-to 0)
    (let ((not-indented t) (case-fold-search t) cur-indent)
      (if (looking-at "^[ \t]*End")
          (progn
            (save-excursion
              (forward-line -1)
              (setq cur-indent (- (current-indentation) default-tab-width)))
            (if (< cur-indent 0)
                (setq cur-indent 0)))
        (save-excursion
          (while not-indented
            (forward-line -1)
            (if (looking-at "^[ \t]*End")
                (progn
                  (setq cur-indent (current-indentation))
                  (setq not-indented nil))
              (if (looking-at "^[ \t]*\\([A-Za-z0-9_]+\\)?\\(Function\\|Event\\|While\\|State\\|If\\|Else\\|ElseIf\\|Property\\)")
                  (progn
                    (setq cur-indent (+ (current-indentation) default-tab-width))
                    (setq not-indented nil))
                (if (bobp)
                    (setq not-indented nil)))))))
      (if cur-indent
          (indent-line-to cur-indent)
        (indent-line-to 0)))))

(defvar papyrus-mode-syntax-table
  (let ((st (make-syntax-table)))
        (modify-syntax-entry ?_ "w" st)
        st))

(define-derived-mode papyrus-mode prog-mode "Papyrus script"
  "Papyrus mode is for editing Skyrim's scripts"

  (set-syntax-table papyrus-mode-syntax-table)
  (use-local-map papyrus-mode-map)

  ;; setup syntax highlighting
  (set (make-local-variable 'font-lock-defaults) '(papyrus-font-lock-keywords nil t))
  (set (make-local-variable 'indent-line-function) 'papyrus-indent-line)

  ;; setup tab-width
  (when papyrus-tab-width
    (setq tab-width papyrus-tab-width))

  (setq comment-start ";")
  (setq comment-end "")

  (modify-syntax-entry ?\; "< b" papyrus-mode-syntax-table)
  (modify-syntax-entry ?\n "> b" papyrus-mode-syntax-table)

  (setq major-mode 'papyrus-mode)
  (setq mode-name "Papyrus")
  (run-hooks 'papyrus-mode-hook)
  )

(when (load "flymake" t)
  (defun flymake-papyrus-init (&optional trigger-type)
    (let* ((temp-file (flymake-init-create-temp-buffer-copy
                       'flymake-create-temp-with-folder-structure))
           (local-file (file-relative-name
                        temp-file
                        (file-name-directory buffer-file-name)))
           (options (when trigger-type (list ""))))
      (list papyrus-compiler (append papyrus-flags options (list local-file)))))

  (add-to-list 'flymake-err-line-patterns
               '("\\([A-Za-z0-9_\\\.]*\\)\(\\([0-9]*\\),\\([0-9]*\\)):\\(.*\\)"
                 1 2 3 4))

  (add-to-list 'flymake-allowed-file-name-masks
               '("\\.psc\\'" flymake-papyrus-init)))

(provide 'papyrus-mode)
;;; papyrus-mode.el ends here
