from sql_formatter_gui import SQLFormatterApp
from PySide6.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    window = SQLFormatterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()