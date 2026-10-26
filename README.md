# CalcCraft Pro — Advanced Python Calculator

CalcCraft Pro is a desktop calculator project built with Python and Tkinter. It extends the basic two-number calculator task with an interactive interface, expression parsing, memory functions, and calculation history.

## Features

- Addition, subtraction, multiplication, division, modulo, and exponentiation
- Parentheses and decimal arithmetic
- Keyboard input and Enter-to-calculate support
- Memory functions: MC, MR, M+, and M−
- Calculation history with reuse and clear controls
- Copy result to clipboard
- Handles invalid expressions and division by zero
- Uses a restricted AST parser rather than Python `eval`
- No third-party packages required

## Requirements

- Python 3.10 or newer
- Tkinter (usually included with Python)
- No `pip install` needed

## Run the application

1. Extract the ZIP archive.
2. Open Command Prompt or a terminal inside the `CalcCraft_Pro` folder.
3. Run:

   ```bash
   python calculator.py
   ```

## How to use

- Click the calculator buttons or type an expression into the display.
- Press **Enter** or click **=** to calculate.
- Use parentheses to control calculation order, for example `(12 + 8) * 3`.
- Use **Ans** to insert the previous answer.
- Use the memory buttons to store and recall a value.
- Double-click a history entry or select it and choose **Reuse selected**.

## Project structure

```text
CalcCraft_Pro/
├── calculator.py     # GUI, safe arithmetic parser, history and memory
├── README.md         # Setup and usage guide
└── requirements.txt  # No third-party packages required
```

## Concepts demonstrated

- Object-oriented programming
- GUI programming with Tkinter
- Event-driven programming and keyboard bindings
- Expression parsing using Python's Abstract Syntax Tree (AST)
- Operator mapping and arithmetic logic
- Exception handling and input validation
- Lists and tuples for session history
- Clipboard interaction
- Separation of interface and calculation logic

## Suggested future enhancements

- Scientific functions such as square root, logarithms, and trigonometry
- Persistent history using SQLite
- Theme switching
- Unit tests and an installer
