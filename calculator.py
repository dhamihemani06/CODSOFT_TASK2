"""
CalcCraft Pro — Advanced Desktop Calculator
Python 3.10+ | Tkinter GUI | No third-party packages

Features:
- GUI calculator with keyboard support
- Addition, subtraction, multiplication, division, modulo, power
- Parentheses and decimal expressions
- Safe expression parser (does not use eval)
- Calculation history with reuse and clear options
- Memory buttons: MC, MR, M+, M-
- Copy result to clipboard
- Input validation and division-by-zero handling
"""

from __future__ import annotations

import ast
import operator
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


class SafeCalculator:
    """Evaluates arithmetic expressions using a strict AST allow-list."""

    BINARY_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    @classmethod
    def evaluate(cls, expression: str) -> float | int:
        expression = expression.strip().replace("×", "*").replace("÷", "/").replace("−", "-")
        if not expression:
            raise ValueError("Enter an expression first.")
        if len(expression) > 250:
            raise ValueError("Expression is too long.")
        try:
            parsed = ast.parse(expression, mode="eval")
        except (SyntaxError, ValueError) as exc:
            raise ValueError("Invalid expression. Check the numbers and operators.") from exc
        result = cls._walk(parsed.body, depth=0)
        if isinstance(result, complex) or not isinstance(result, (int, float)):
            raise ValueError("The expression did not produce a real number.")
        if abs(result) > 1e100:
            raise ValueError("Result is too large to display.")
        if isinstance(result, float) and (result != result or abs(result) == float("inf")):
            raise ValueError("Result is not a finite number.")
        return result

    @classmethod
    def _walk(cls, node: ast.AST, depth: int) -> float | int:
        if depth > 30:
            raise ValueError("Expression is too complex.")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 1e100:
                raise ValueError("Number is too large.")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls.BINARY_OPERATORS:
            left = cls._walk(node.left, depth + 1)
            right = cls._walk(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")
            try:
                return cls.BINARY_OPERATORS[type(node.op)](left, right)
            except ZeroDivisionError as exc:
                raise ZeroDivisionError("Cannot divide by zero.") from exc
            except (OverflowError, ValueError) as exc:
                raise ValueError("This calculation is outside the supported range.") from exc
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.UNARY_OPERATORS:
            return cls.UNARY_OPERATORS[type(node.op)](cls._walk(node.operand, depth + 1))
        raise ValueError("Only basic arithmetic operators and parentheses are allowed.")


def display_number(value: float | int) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


class CalcCraftApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CalcCraft Pro | Smart Calculator")
        self.geometry("980x650")
        self.minsize(820, 560)
        self.configure(bg="#eef2f7")

        self.expression = tk.StringVar()
        self.result_text = tk.StringVar(value="Ready")
        self.memory: float = 0.0
        self.last_result: float | int = 0
        self.history: list[tuple[str, str, str]] = []
        self.just_calculated = False

        self._style()
        self._build()
        self._bind_keyboard()
        self.expression.trace_add("write", self._on_expression_change)
        self.entry.focus_set()

    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#eef2f7")
        style.configure("TLabel", background="#eef2f7", foreground="#172033", font=("Segoe UI", 10))
        style.configure("Heading.TLabel", font=("Segoe UI", 22, "bold"), foreground="#174b3a")
        style.configure("Muted.TLabel", foreground="#68758a", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 11), padding=(8, 10))
        style.configure("Accent.TButton", background="#1c654d", foreground="white",
                        font=("Segoe UI", 12, "bold"), padding=(8, 10))
        style.map("Accent.TButton", background=[("active", "#174e3d")])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=27,
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=7)

    def _build(self) -> None:
        root = ttk.Frame(self, padding=22)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="CalcCraft Pro", style="Heading.TLabel").pack(side="left")
        ttk.Label(header, text="Accurate • Simple • Smart", style="Muted.TLabel").pack(side="right", pady=8)

        content = ttk.Frame(root)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        calculator = ttk.Frame(content, padding=(0, 0, 18, 0))
        calculator.grid(row=0, column=0, sticky="nsew")
        history_panel = ttk.Frame(content)
        history_panel.grid(row=0, column=1, sticky="nsew")
        history_panel.rowconfigure(1, weight=1)
        history_panel.columnconfigure(0, weight=1)

        display = tk.Frame(calculator, bg="#172033", padx=18, pady=15)
        display.pack(fill="x", pady=(0, 12))
        tk.Label(display, text="EXPRESSION", bg="#172033", fg="#a8b7cb",
                 font=("Segoe UI", 9, "bold")).pack(anchor="e")
        self.entry = tk.Entry(display, textvariable=self.expression, justify="right",
                              font=("Segoe UI", 23), relief="flat", bd=0,
                              bg="#172033", fg="white", insertbackground="white")
        self.entry.pack(fill="x", pady=(8, 7), ipady=5)
        self.entry.bind("<Return>", lambda _event: self.calculate())
        self.entry.bind("<KP_Enter>", lambda _event: self.calculate())
        tk.Label(display, textvariable=self.result_text, bg="#172033", fg="#74d6ac",
                 font=("Segoe UI", 12, "bold")).pack(anchor="e")

        memory_row = ttk.Frame(calculator)
        memory_row.pack(fill="x", pady=(0, 8))
        for label, command in (
            ("MC", self.memory_clear), ("MR", self.memory_recall),
            ("M+", self.memory_add), ("M−", self.memory_subtract),
        ):
            ttk.Button(memory_row, text=label, command=command).pack(side="left", expand=True, fill="x", padx=2)

        buttons = [
            [("C", self.clear, "danger"), ("⌫", self.backspace, "normal"), ("(", lambda: self.insert("("), "normal"), (")", lambda: self.insert(")"), "normal")],
            [("7", lambda: self.insert("7"), "normal"), ("8", lambda: self.insert("8"), "normal"), ("9", lambda: self.insert("9"), "normal"), ("÷", lambda: self.insert("/"), "operator")],
            [("4", lambda: self.insert("4"), "normal"), ("5", lambda: self.insert("5"), "normal"), ("6", lambda: self.insert("6"), "normal"), ("×", lambda: self.insert("*"), "operator")],
            [("1", lambda: self.insert("1"), "normal"), ("2", lambda: self.insert("2"), "normal"), ("3", lambda: self.insert("3"), "normal"), ("−", lambda: self.insert("-"), "operator")],
            [("0", lambda: self.insert("0"), "normal"), (".", lambda: self.insert("."), "normal"), ("%", lambda: self.insert("%"), "operator"), ("+", lambda: self.insert("+"), "operator")],
        ]
        grid = tk.Frame(calculator, bg="#eef2f7")
        grid.pack(fill="both", expand=True)
        for r, row in enumerate(buttons):
            grid.rowconfigure(r, weight=1)
            for c, (label, command, kind) in enumerate(row):
                grid.columnconfigure(c, weight=1)
                bg = {"normal": "#ffffff", "operator": "#dcebe5", "danger": "#ffe4e4"}[kind]
                fg = "#172033" if kind == "normal" else ("#174b3a" if kind == "operator" else "#a51d2d")
                button = tk.Button(grid, text=label, command=command, font=("Segoe UI", 15, "bold"),
                                   bg=bg, fg=fg, activebackground="#c8d9d2",
                                   relief="flat", bd=0, cursor="hand2")
                button.grid(row=r, column=c, sticky="nsew", padx=4, pady=4, ipadx=4, ipady=5)

        bottom = ttk.Frame(calculator)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Copy result", command=self.copy_result).pack(side="left")
        ttk.Button(bottom, text="Use last answer (Ans)", command=self.insert_answer).pack(side="left", padx=8)
        ttk.Button(bottom, text="=", style="Accent.TButton", command=self.calculate).pack(side="right", ipadx=20)

        ttk.Label(history_panel, text="Calculation History", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        columns = ("time", "expression", "result")
        self.history_tree = ttk.Treeview(history_panel, columns=columns, show="headings", height=15)
        self.history_tree.heading("time", text="Time")
        self.history_tree.heading("expression", text="Expression")
        self.history_tree.heading("result", text="Result")
        self.history_tree.column("time", width=65, minwidth=55)
        self.history_tree.column("expression", width=145, minwidth=90)
        self.history_tree.column("result", width=90, minwidth=70)
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(history_panel, orient="vertical", command=self.history_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.bind("<Double-1>", self._reuse_history)

        history_actions = ttk.Frame(history_panel)
        history_actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(history_actions, text="Reuse selected", command=self.reuse_history).pack(side="left")
        ttk.Button(history_actions, text="Clear history", command=self.clear_history).pack(side="right")

        ttk.Label(history_panel, text="Tip: double-click a history row to reuse it.",
                  style="Muted.TLabel", wraplength=300).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

    def _bind_keyboard(self) -> None:
        self.bind("<Escape>", lambda _event: self.clear())
        self.bind("<Control-l>", lambda _event: self.clear())
        self.bind("<Control-c>", lambda _event: self.copy_result())
        self.bind("<KeyPress>", self._keyboard_feedback)

    def _keyboard_feedback(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "KP_Enter"):
            self.after(1, self.calculate)

    def _on_expression_change(self, *_args) -> None:
        if not self.expression.get().strip():
            self.result_text.set("Ready")
        elif not self.just_calculated:
            self.result_text.set("Enter = to calculate")
        self.just_calculated = False

    def insert(self, value: str) -> None:
        try:
            start = self.entry.index(tk.INSERT)
            self.entry.insert(start, value)
        except tk.TclError:
            self.expression.set(self.expression.get() + value)
        self.entry.focus_set()

    def clear(self) -> None:
        self.expression.set("")
        self.result_text.set("Ready")
        self.entry.focus_set()

    def backspace(self) -> None:
        try:
            start = self.entry.index(tk.INSERT)
            if start > 0:
                self.entry.delete(start - 1)
        except tk.TclError:
            self.expression.set(self.expression.get()[:-1])
        self.entry.focus_set()

    def calculate(self) -> None:
        original = self.expression.get().strip()
        if not original:
            self.result_text.set("Enter an expression first")
            return
        try:
            value = SafeCalculator.evaluate(original)
            result = display_number(value)
            self.last_result = value
            self.result_text.set(f"= {result}")
            self.just_calculated = True
            self._add_history(original, result)
        except ZeroDivisionError as exc:
            self.result_text.set(str(exc))
        except (ValueError, TypeError) as exc:
            self.result_text.set(str(exc))
        self.entry.focus_set()

    def _add_history(self, expression: str, result: str) -> None:
        time_text = datetime.now().strftime("%H:%M:%S")
        item_id = self.history_tree.insert("", 0, values=(time_text, expression, result))
        self.history.append((expression, result, time_text))
        if len(self.history) > 500:
            self.history.pop()
        self.history_tree.selection_set(item_id)

    def _selected_history(self) -> tuple[str, str, str] | None:
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showinfo("Select history", "Select a calculation from the history first.", parent=self)
            return None
        values = self.history_tree.item(selection[0], "values")
        return (str(values[1]), str(values[2]), str(values[0]))

    def reuse_history(self) -> None:
        selected = self._selected_history()
        if selected:
            self.expression.set(selected[0])
            self.entry.icursor(tk.END)
            self.entry.focus_set()

    def _reuse_history(self, _event: tk.Event) -> None:
        self.reuse_history()

    def clear_history(self) -> None:
        if not self.history_tree.get_children():
            return
        if messagebox.askyesno("Clear history", "Remove all calculations from this session?", parent=self):
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            self.history.clear()

    def copy_result(self) -> None:
        text = self.result_text.get()
        if text.startswith("= "):
            text = text[2:]
        elif self.result_text.get() == "Ready":
            text = display_number(self.last_result)
        if text and text not in ("Ready", "Enter = to calculate"):
            self.clipboard_clear()
            self.clipboard_append(text)
            self.result_text.set(f"Copied: {text}")

    def insert_answer(self) -> None:
        self.insert(f"({display_number(self.last_result)})")

    def _current_numeric_value(self) -> float:
        text = self.result_text.get()
        if text.startswith("= "):
            try:
                return float(text[2:])
            except ValueError:
                pass
        try:
            return float(SafeCalculator.evaluate(self.expression.get()))
        except (ValueError, ZeroDivisionError, TypeError):
            return float(self.last_result)

    def memory_clear(self) -> None:
        self.memory = 0.0
        self.result_text.set("Memory cleared")

    def memory_recall(self) -> None:
        self.insert(display_number(self.memory))

    def memory_add(self) -> None:
        self.memory += self._current_numeric_value()
        self.result_text.set(f"Memory = {display_number(self.memory)}")

    def memory_subtract(self) -> None:
        self.memory -= self._current_numeric_value()
        self.result_text.set(f"Memory = {display_number(self.memory)}")


if __name__ == "__main__":
    app = CalcCraftApp()
    app.mainloop()
