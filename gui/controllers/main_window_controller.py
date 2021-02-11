import sys
from io import TextIOWrapper
from subprocess import Popen, PIPE

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QSizeGrip, QGraphicsDropShadowEffect, QFileDialog
from gui.views.ui_main_window import Ui_MainWindow

## ==> GLOBALS
GLOBAL_STATE = 0
GLOBAL_TITLE_BAR = True

## ==> COUT INITIAL MENU
count = 1

class MainWindowController(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindowController, self).__init__()
        self.setupUi(self)
        self.initialize_crawler_processes()

    def setupUi(self,MainWindow):
        Ui_MainWindow.setupUi(self, MainWindow)

        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        ## SHOW ==> DROP SHADOW
        # self.shadow = QGraphicsDropShadowEffect(self)
        # self.shadow.setBlurRadius(17)
        # self.shadow.setXOffset(0)
        # self.shadow.setYOffset(0)
        # self.shadow.setColor(QColor(0, 0, 0, 150))
        # self.frame_main.setGraphicsEffect(self.shadow)
        #
        # ==> RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        ### ==> MINIMIZE
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())

        ## ==> MAXIMIZE/RESTORE
        self.btn_maximize_restore.clicked.connect(lambda: self.maximize_restore())

        ## SHOW ==> CLOSE APPLICATION
        self.btn_close.clicked.connect(lambda: self.close())

        ## TAB ==> tabs button click events
        self.pushButton_home.clicked.connect(lambda: self.switch_tab("home"))
        self.pushButton_crawler.clicked.connect(lambda: self.switch_tab("crawler"))
        self.pushButton_comments.clicked.connect(lambda: self.switch_tab("comments"))
        self.pushButton_commandInjection.clicked.connect(lambda: self.switch_tab("command_injection"))
        self.pushButton_localFileInclusion.clicked.connect(lambda: self.switch_tab("local_file_inclusion"))
        self.pushButton_sqlInjection.clicked.connect(lambda: self.switch_tab("sql_injection"))
        self.pushButton_stored_xssInjection.clicked.connect(lambda: self.switch_tab("xss_injection"))

        ##Upload file url events
        self.pushButton_url_file_open.clicked.connect(self.browse_url_file)

        ##Crawling event
        self.pushButton_start_crawling.clicked.connect(self.start_crawling)

        ##log
        sys.stdout = ConsoleLog(self.plainTextEdit_home_log,"color:rgb(85, 255, 127);")
        sys.stderr = ConsoleLog(self.plainTextEdit_home_log,"color:rgb(225, 0, 0);")

    def initialize_crawler_processes(self):
        #Crawler process
        self.crawler_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.crawler_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("crawler"))
        self.crawler_process.readyReadStandardError.connect(lambda: self.handle_stderr("crawler"))
        # self.p.stateChanged.connect(self.handle_state)
        self.crawler_process.finished.connect(self.crawler_process_finished)  # Clean up once complete.

        #Scanner process
        self.scanner_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.scanner_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("comments"))
        self.scanner_process.readyReadStandardError.connect(lambda: self.handle_stderr("comments"))
        # self.p.stateChanged.connect(self.handle_state)
        # self.scanner_process.finished.connect(self.crawler_process_finished)  # Clean up once complete.

        #Upload process
        self.upload_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.upload_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("command_injection"))
        self.upload_process.readyReadStandardError.connect(lambda: self.handle_stderr("command_injection"))
        # self.p.stateChanged.connect(self.handle_state)
        # self.upload_process.finished.connect(self.crawler_process_finished)  # Clean up once complete.

        #LFI Scanner process
        self.lfi_scanner_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.lfi_scanner_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("local_file_inclusion"))
        self.lfi_scanner_process.readyReadStandardError.connect(lambda: self.handle_stderr("local_file_inclusion"))
        # self.p.stateChanged.connect(self.handle_state)
        # self.lfi_scanner_process.finished.connect(self.crawler_process_finished)  # Clean up once complete.

        #SQLI Checker process
        self.sqli_checker_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.sqli_checker_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("sql_injection"))
        self.sqli_checker_process.readyReadStandardError.connect(lambda: self.handle_stderr("sql_injection"))
        # self.p.stateChanged.connect(self.handle_state)
        # self.sqli_checker_process.finished.connect(self.crawler_process_finished)  # Clean up once complete.

        #Stored XSS Checker process
        self.stored_xss_checker_process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.stored_xss_checker_process.readyReadStandardOutput.connect(lambda: self.handle_stdout("xss_injection"))
        self.stored_xss_checker_process.readyReadStandardError.connect(lambda: self.handle_stderr("xss_injection"))
        # self.p.stateChanged.connect(self.handle_state)
        # self.stored_xss_checker.finished.connect(self.crawler_process_finished)  # Clean up once complete.

    def crawler_process_finished(self):
        try:
            # start other process
            print("Starting Comments")
            self.scanner_process.start("python", ['tabs/comments/comments.py'])
            print("Starting Command Injection")
            self.upload_process.start("python", ['tabs/command_injection/command_injection.py'])
            print("Starting Local File Inclusion")
            self.lfi_scanner_process.start("python", ['tabs/local_file_inclusion/local_file_inclusion.py'])
            print("Starting SQL Injection")
            self.sqli_checker_process.start("python", ['tabs/sql_injection/sql_injection.py'])
            print("Starting XSS Injection")
            self.stored_xss_checker_process.start("python", ['tabs/xss_injection/xss_injection.py'])

        except Exception as e:
            print(e)

    def start_crawling(self):
        filename=self.lineEdit_url_file_path.text().strip()
        if filename!="":
            try:
                links = open(filename).read().strip().split("\n")
                print("Links Found")
                for link in links:
                    print(link)
                self.crawler_process.start("python", ['tabs/crawler/crawler.py'])
                print("Crawler Started!")
            except Exception as e:
                print(e)
        else:
            raise Exception("Please command_injection a url file first")

    def handle_stdout(self,process):
        if process=="crawler":
            self.plainTextEdit_crawler_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.crawler_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_crawler_log.insertPlainText(text)
        elif process=="comments":
            self.plainTextEdit_comments_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.scanner_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_comments_log.insertPlainText(text)
        elif process=="command_injection":
            self.plainTextEdit_command_injection_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.upload_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_command_injection_log.insertPlainText(text)
        elif process=="local_file_inclusion":
            self.plainTextEdit_local_file_inclusion_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.lfi_scanner_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_local_file_inclusion_log.insertPlainText(text)
        elif process=="sql_injection":
            self.plainTextEdit_sql_injection_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.sqli_checker_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_sql_injection_log.insertPlainText(text)
        elif process=="xss_injection":
            self.plainTextEdit_xss_injection_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = bytes(self.stored_xss_checker_process.readAllStandardOutput()).decode("utf8")
            self.plainTextEdit_xss_injection_log.insertPlainText(text)
        else:
            self.plainTextEdit_home_log.setStyleSheet("color:rgb(85, 255, 127);")
            text = str(self.process.readAllStandardOutput())
            self.plainTextEdit_home_log.insertPlainText(text)

    def handle_stderr(self,process):
        if process == "crawler":
            self.plainTextEdit_crawler_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.crawler_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_crawler_log.insertPlainText(text)
        elif process == "comments":
            self.plainTextEdit_comments_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.scanner_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_comments_log.insertPlainText(text)
        elif process == "command_injection":
            self.plainTextEdit_command_injection_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.upload_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_command_injection_log.insertPlainText(text)
        elif process == "local_file_inclusion":
            self.plainTextEdit_local_file_inclusion_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.lfi_scanner_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_local_file_inclusion_log.insertPlainText(text)
        elif process == "sql_injection":
            self.plainTextEdit_sql_injection_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.sqli_checker_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_sql_injection_log.insertPlainText(text)
        elif process == "xss_injection":
            self.plainTextEdit_xss_injection_log.setStyleSheet("color:rgb(225, 0, 0);")
            text = bytes(self.stored_xss_checker_process.readAllStandardError()).decode("utf8")
            self.plainTextEdit_xss_injection_log.insertPlainText(text)
        else:
            text = str(self.process.readAllStandardError())
            self.plainTextEdit_home_log.insertPlainText(text)

    def browse_url_file(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open URL File", "",
                                                  "Text Files (*);;URL File (*.txt)", options=options)
        if fileName:
            print("URL File Selected: "+fileName)
            self.lineEdit_url_file_path.setText(fileName)
        else:
            print("No File Selected!")

    def reset_tab_buttons_color(self):
        self.pushButton_home.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_crawler.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_comments.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_commandInjection.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_localFileInclusion.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_sqlInjection.setStyleSheet("padding:10px 15px;color:white;")
        self.pushButton_stored_xssInjection.setStyleSheet("padding:10px 15px;color:white;")

    def switch_tab(self,tab):
        if tab=="home":
            self.reset_tab_buttons_color()
            self.pushButton_home.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(0)
        elif tab=="crawler":
            self.reset_tab_buttons_color()
            self.pushButton_crawler.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(1)
        elif tab=="comments":
            self.reset_tab_buttons_color()
            self.pushButton_comments.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(2)
        elif tab=="command_injection":
            self.reset_tab_buttons_color()
            self.pushButton_commandInjection.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(3)
        elif tab=="local_file_inclusion":
            self.reset_tab_buttons_color()
            self.pushButton_localFileInclusion.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(4)
        elif tab=="sql_injection":
            self.reset_tab_buttons_color()
            self.pushButton_sqlInjection.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(5)
        elif tab=="xss_injection":
            self.reset_tab_buttons_color()
            self.pushButton_stored_xssInjection.setStyleSheet("padding:10px 15px;color:white;background-color:rgb(0, 170, 255);")
            self.stackedWidget_tabs.setCurrentIndex(6)

    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status == 0:
            self.showMaximized()
            GLOBAL_STATE = 1
            # self.centralWidget.setContentsMargins(0, 0, 0, 0)
            self.btn_maximize_restore.setToolTip("Restore")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-restore.png"))
            self.frame_top_btns.setStyleSheet("background-color: rgb(27, 29, 35)")
            self.frame_size_grip.hide()
        else:
            GLOBAL_STATE = 0
            self.showNormal()
            self.resize(800, 600)
            # self.ui.horizontalLayout.setContentsMargins(10, 10, 10, 10)
            self.btn_maximize_restore.setToolTip("Maximize")
            self.btn_maximize_restore.setIcon(QtGui.QIcon(u":/16x16/icons/16x16/cil-window-maximize.png"))
            self.frame_top_btns.setStyleSheet("background-color: rgba(27, 29, 35, 200)")
            self.frame_size_grip.show()

class ConsoleLog(TextIOWrapper):
    def __init__(self, edit,stylesheet):
        self.textEdit = edit
        self.stylesheet=stylesheet

    def write(self, message):
        self.textEdit.setStyleSheet(self.stylesheet)
        self.textEdit.insertPlainText(message)

    def flush(self):
        pass
