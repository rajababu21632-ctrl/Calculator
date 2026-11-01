"""
MCA Scientific Calculator
Python + Tkinter desktop application.

Features:
- GUI with modern dark theme
- Basic arithmetic, parentheses, decimals, powers and modulo
- Square root and percentage conversion
- Calculation history panel
- Save history to a text file
- Keyboard support
- Safe arithmetic expression parsing (no unrestricted eval)
- Error handling for invalid expressions and division by zero
"""

import ast
import math
import operator
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime


# ---------- Safe calculator engine ----------

BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    """Evaluate only numeric constants and approved arithmetic operations."""
    expression = (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
    ).strip()

    if not expression:
        raise ValueError("Please enter a calculation.")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
            left = visit(node.left)
            right = visit(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Cannot divide by zero.")

            if isinstance(node.op, ast.Mod) and right == 0:
                raise ZeroDivisionError("Cannot modulo by zero.")

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")

            result = BINARY_OPERATORS[type(node.op)](left, right)

            if isinstance(result, complex) or not math.isfinite(float(result)):
                raise ValueError("Result is outside the supported range.")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
            return UNARY_OPERATORS[type(node.op)](visit(node.operand))

        raise ValueError("Only numbers and basic arithmetic operators are allowed.")

    try:
        return visit(ast.parse(expression, mode="eval"))
    except (SyntaxError, OverflowError) as exc:
        raise ValueError("Invalid expression. Check your input.") from exc


def format_result(value):
    """Format results without unnecessary trailing decimal zeros."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


# ---------- GUI application ----------

class ScientificCalculator:
    BG = "#101827"
    PANEL = "#172235"
    DISPLAY_BG = "#0b1220"
    TEXT = "#f8fafc"
    MUTED = "#a8b6ca"
    BUTTON = "#26364e"
    BUTTON_ACTIVE = "#3b5270"
    BLUE = "#2563eb"
    GREEN = "#059669"
    RED = "#dc2626"
    ORANGE = "#ea580c"

    def __init__(self, root):
        self.root = root
        self.root.title("MCA Scientific Calculator")
        self.root.geometry("900x650")
        self.root.minsize(760, 570)
        self.root.configure(bg=self.BG)

        self.expression = tk.StringVar(value="0")
        self.status = tk.StringVar(value="Ready — enter a calculation")
        self.history = []

        self.build_interface()
        self.bind_keyboard()

    def build_interface(self):
        # Header
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=22, pady=(18, 10))

        tk.Label(
            header, text="SCIENTIFIC CALCULATOR",
            font=("Segoe UI", 20, "bold"),
            fg=self.TEXT, bg=self.BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="MCA Python Project  |  Tkinter GUI  |  Safe Expression Engine",
            font=("Segoe UI", 10),
            fg=self.MUTED, bg=self.BG
        ).pack(anchor="w", pady=(3, 0))

        # Main content
        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill="both", expand=True, padx=22, pady=8)

        calculator_panel = tk.Frame(content, bg=self.PANEL, padx=14, pady=14)
        calculator_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

        history_panel = tk.Frame(content, bg=self.PANEL, padx=14, pady=14, width=260)
        history_panel.pack(side="right", fill="y")
        history_panel.pack_propagate(False)

        # Display
        self.display = tk.Entry(
    calculator_panel,
    textvariable=self.expression,
    font=("Consolas", 25, "bold"),
    justify="right",
    state="readonly",
    readonlybackground="#FFFFFF",
    foreground="#000000",
    relief="flat",
    bd=0
)
        self.display.pack(fill="x", ipady=18, pady=(0, 12))

        # Buttons grid
        button_frame = tk.Frame(calculator_panel, bg=self.PANEL)
        button_frame.pack(fill="both", expand=True)

        buttons = [
            [("(", self.BUTTON), (")", self.BUTTON), ("%", self.BUTTON), ("⌫", self.RED)],
            [("7", self.BUTTON), ("8", self.BUTTON), ("9", self.BUTTON), ("÷", self.BLUE)],
            [("4", self.BUTTON), ("5", self.BUTTON), ("6", self.BUTTON), ("×", self.BLUE)],
            [("1", self.BUTTON), ("2", self.BUTTON), ("3", self.BUTTON), ("−", self.BLUE)],
            [("0", self.BUTTON), (".", self.BUTTON), ("^", self.BUTTON), ("+", self.ORANGE)],
            [("√", self.GREEN), ("±", self.BUTTON), ("C", self.RED), ("=", self.GREEN)],
        ]

        for row_index, row in enumerate(buttons):
            button_frame.rowconfigure(row_index, weight=1)
            for col_index, (label, color) in enumerate(row):
                button_frame.columnconfigure(col_index, weight=1)
                tk.Button(
                    button_frame,
                    text=label,
                    command=lambda value=label: self.button_click(value),
                    font=("Segoe UI", 15, "bold"),
                    bg=color,
                    fg=self.TEXT,
                    activebackground=self.BUTTON_ACTIVE,
                    activeforeground=self.TEXT,
                    relief="flat",
                    bd=0,
                    cursor="hand2"
                ).grid(
                    row=row_index, column=col_index,
                    sticky="nsew", padx=4, pady=4, ipadx=3, ipady=5
                )

        # History panel
        tk.Label(
            history_panel, text="CALCULATION HISTORY",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT, bg=self.PANEL
        ).pack(anchor="w", pady=(0, 8))

        self.history_list = tk.Listbox(
            history_panel,
            bg=self.DISPLAY_BG,
            fg=self.TEXT,
            selectbackground=self.BLUE,
            selectforeground=self.TEXT,
            relief="flat",
            font=("Consolas", 10),
            activestyle="none"
        )
        self.history_list.pack(fill="both", expand=True)
        self.history_list.bind("<Double-Button-1>", self.reuse_history)

        tk.Button(
            history_panel, text="Save History",
            command=self.save_history,
            bg=self.BUTTON, fg=self.TEXT,
            activebackground=self.BUTTON_ACTIVE,
            relief="flat", font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        ).pack(fill="x", pady=(10, 5))

        tk.Button(
            history_panel, text="Clear History",
            command=self.clear_history,
            bg=self.BUTTON, fg=self.TEXT,
            activebackground=self.BUTTON_ACTIVE,
            relief="flat", font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(fill="x")

        # Footer/status
        tk.Label(
            self.root, textvariable=self.status,
            anchor="w", bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(fill="x", padx=25, pady=(0, 12))

    def set_display(self, value):
        self.expression.set(str(value))

    def append_to_display(self, value):
        current = self.expression.get()
        if current == "0":
            current = ""
        self.set_display(current + value)

    def button_click(self, value):
        if value == "C":
            self.set_display("0")
            self.status.set("Display cleared")
            return

        if value == "⌫":
            current = self.expression.get()
            self.set_display(current[:-1] if len(current) > 1 else "0")
            self.status.set("Last character removed")
            return

        if value == "±":
            current = self.expression.get()
            if current == "0":
                self.set_display("-")
            elif current.startswith("-"):
                self.set_display(current[1:])
            else:
                self.set_display("-" + current)
            return

        if value == "√":
            try:
                number = safe_calculate(self.expression.get())
                if number < 0:
                    raise ValueError("Square root of a negative number is not real.")
                result = math.sqrt(number)
                self.add_history(f"√({number}) = {format_result(result)}")
                self.set_display(format_result(result))
                self.status.set("Square root calculated")
            except Exception as exc:
                self.show_error(str(exc))
            return

        if value == "%":
            try:
                number = safe_calculate(self.expression.get())
                result = number / 100
                self.add_history(f"{number}% = {format_result(result)}")
                self.set_display(format_result(result))
                self.status.set("Percentage converted")
            except Exception as exc:
                self.show_error(str(exc))
            return

        if value == "=":
            self.calculate()
            return

        self.append_to_display(value)
        self.status.set("Ready")

    def calculate(self):
        expression = self.expression.get()
        try:
            result = safe_calculate(expression)
            formatted = format_result(result)
            self.add_history(f"{expression} = {formatted}")
            self.set_display(formatted)
            self.status.set("Calculation successful")
        except ZeroDivisionError as exc:
            self.show_error(str(exc))
        except (ValueError, TypeError, OverflowError) as exc:
            self.show_error(str(exc))

    def add_history(self, record):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp}  {record}"
        self.history.insert(0, entry)
        self.history_list.insert(0, record)

    def reuse_history(self, _event=None):
        selection = self.history_list.curselection()
        if selection:
            record = self.history_list.get(selection[0])
            if " = " in record:
                expression = record.split(" = ", 1)[0]
                self.set_display(expression)
                self.status.set("History expression loaded")

    def clear_history(self):
        self.history.clear()
        self.history_list.delete(0, tk.END)
        self.status.set("History cleared")

    def save_history(self):
        if not self.history:
            messagebox.showinfo("Save History", "No calculations to save yet.")
            return

        path = filedialog.asksaveasfilename(
            title="Save calculation history",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write("MCA SCIENTIFIC CALCULATOR HISTORY\n")
                file.write("=" * 40 + "\n")
                file.write("\n".join(self.history))
            self.status.set("History saved successfully")
            messagebox.showinfo("Saved", "History saved successfully.")
        except OSError as exc:
            self.show_error(f"Could not save history: {exc}")

    def show_error(self, message):
        self.status.set("Error: " + message)
        messagebox.showerror("Calculation Error", message)

    def bind_keyboard(self):
        self.root.bind("<Key>", self.keyboard_input)
        self.root.bind("<Return>", lambda _event: self.calculate())
        self.root.bind("<KP_Enter>", lambda _event: self.calculate())
        self.root.bind("<BackSpace>", lambda _event: self.button_click("⌫"))
        self.root.bind("<Escape>", lambda _event: self.button_click("C"))

    def keyboard_input(self, event):
        if event.char in "0123456789.+-*/()%":
            mapped = {"*": "×", "/": "÷", "-": "−"}.get(event.char, event.char)
            self.append_to_display(mapped)
        elif event.char == "^":
            self.append_to_display("^")


if __name__ == "__main__":
    main_window = tk.Tk()
    app = ScientificCalculator(main_window)
    main_window.mainloop()
