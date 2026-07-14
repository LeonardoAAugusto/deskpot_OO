"""
main.py
-------
Ponto de entrada do sistema. Rode com:

    python main.py

Requer apenas Python 3.8+ (Tkinter e sqlite3 já vêm na instalação padrão do
Windows/Python — nenhuma biblioteca externa é necessária).
"""

from gui import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
