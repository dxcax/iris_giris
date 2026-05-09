import sys
from PyQt5.QtWidgets import QApplication
from arayuz.ana_pencere import AnaPencere


def main():
    uygulama = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(uygulama.exec_())


if __name__ == "__main__":
    main()