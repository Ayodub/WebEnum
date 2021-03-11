from PyQt5 import QtWidgets
import sys

from gui.controllers.splash_screen_controller import SplashScreenController

if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    ui = SplashScreenController()
    ui.show()
    sys.exit(app.exec_())


    
