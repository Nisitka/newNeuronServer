import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem

import serverNeuronsNetworkGui as Gui  # конвертированный файл дизайна
import datetime
import socket as socketNetwork
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import Server

class coreApp(QtWidgets.QMainWindow, Gui.Ui_Form):
    numClient = 0

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self) # для инициализации нашего дизайна

        # -----------настройка внешнего вида главного виджета--------------
        self.setWindowTitle("Server neural network")
        self.setFixedSize(500, 420)

        palette = QPalette()
        pixFon = QPixmap("fon.jpg")
        palette.setBrush(QPalette.Background, QBrush(pixFon))
        self.setPalette(palette)

        #  гифка для сервера
        self.gif = QtGui.QMovie("stp.gif")
        self.gif.setScaledSize(QSize(100, 100))
        self.gifLabel.setMovie(self.gif)
        self.gif.start()
        self.gif.jumpToFrame(2)
        self.gif.stop()

        #  гифка для нейронной сети
        self.gifNeuron = QtGui.QMovie("neuron.gif")
        self.gifNeuron.setScaledSize(QSize(400, 200))
        self.neuronGifLabel.setMovie(self.gifNeuron)
        self.gifNeuron.start()

        self.styleSheet = """
        
        QTabBar::tab {
            border: 2px solid #C4C4C3;
            border-bottom-color: #C2C7CB;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            min-width: 32ex;  
            padding: 2px;
            
            color: rgb(0,0,0);
        }

        QTabBar::tab:selected {
            background: #FFFFFF;
            color: rgb(0,0,0);
        }
        
        QTabBar::tab:hover {
            background: #FFFFFF;
            color: rgb(0,0,0);
        }

        QTabBar::tab:selected {
            border-bottom-color: #FFFFFF;
            color: rgb(0,0,0);
        }

        QTabBar::tab:!selected {
            margin-top: 3px;
            color: rgb(97,197,242);
        }

        """
        self.TabWidgetApp.setStyleSheet(self.styleSheet)

        self.setStartServerButton()
        # -----------------------------------------------------------------

        # --------------установка пар-ов сети------------------------------
        self.portLineEdit.setText("2323")
        h_name = socketNetwork.gethostname()
        IP_addres = socketNetwork.gethostbyname(h_name)

        self.hostLabel.setText("Хост: " + h_name)
        self.IPLabel.setText("IPv4-адрес: " + IP_addres)
        # -----------------------------------------------------------------

        # --------------установка пар-ов клиентов------------------------------
        self.clientsTableWidget.setColumnCount(2)

        self.clientsTableWidget.setHorizontalHeaderLabels(["Имя клиента", "Адрес"])
        self.clientsTableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        # -----------------------------------------------------------------

        self.workingServer = False
        self.StartStopPushButton.clicked.connect(self.changeServerWorking)

        self.TabWidgetApp.currentChanged.connect(self.onChange)

        #  выбор раздела с сервером
        self.TabWidgetApp.setCurrentIndex(0)
        self.onChange(0)

    def onChange(self, index):
        if index == 0:
            self.TabWidgetApp.setStyleSheet(self.styleSheet + """
             QTabWidget>QWidget>QWidget{background: rgb(255,255,255);
        }}""")
        if index == 1:
            self.TabWidgetApp.setStyleSheet(self.styleSheet + """
            QTabWidget>QWidget>QWidget{background: rgb(255,255,255);
        }}""")
        if index == 2:
            self.TabWidgetApp.setStyleSheet(self.styleSheet + """
            QTabWidget>QWidget>QWidget{background: rgb(20,20,21);
        }""")

    #  прием текстовой информации о данных и самих данных для нейронной сети
    def appendData(self, info, data):
        self.textInfoServer.append(info)
        print(data)

    def addNewClient(self, name, address):
        current_date_time = datetime.datetime.now()
        current_time = current_date_time.time()
        self.textInfoServer.append(str(current_time)[0:-7] + ": подключен новый клиент (" + name + ")")

        self.clientsTableWidget.setRowCount(self.clientsTableWidget.rowCount() + 1)

        self.clientsTableWidget.setItem(self.clientsTableWidget.rowCount() - 1, 0, QTableWidgetItem(name))
        self.clientsTableWidget.setItem(self.clientsTableWidget.rowCount() - 1, 1, QTableWidgetItem(address))

    def setStartServerButton(self, type=True):
        if (type):
            self.StartStopPushButton.setText("старт")
            self.StartStopPushButton.setStyleSheet('''
                                            QPushButton {
                                                background-color: rgb(78,198,26); color: rgb(9,100,24);
                                                
                                                border-style: outset;
                                                border-radius: 5px;
                                                border-width: 1px;
                                                border-color: rgb(0,0,0);
                                            }
                                            QPushButton:hover {
                                                background-color : rgb(98,218,46); color: rgb(29,120,44);
                                                border-color: rgb(0,0,0);
                                            }
                                        ''')
        else:
            self.StartStopPushButton.setText("стоп")
            self.StartStopPushButton.setStyleSheet('''
                                            QPushButton {
                                                background-color: rgb(204,0,0); color: rgb(104,0,0);
                                                
                                                border-style: outset;
                                                border-radius: 5px;
                                                border-width: 1px;
                                                border-color: rgb(0,0,0);
                                            }
                                            QPushButton:hover {
                                                background-color : rgb(224,0,0); color: rgb(104,0,0);
                                                border-color: rgb(0,0,0);
                                            }
                                        ''')

    def changeServerWorking(self):
        if (not self.workingServer):
            self.startServer()
            self.setStartServerButton(False)

        else:
            self.stopServer()
            self.setStartServerButton(True)

    def startServer(self):
        self.server = Server.threadServer("threadServer", self.portLineEdit.text())
        # соединяем сигнал сервера об новом клиенте с соответствующим методом
        self.server.newClientConnection.connect(self.addNewClient)
        # соединяем сигнал сервера об получении данных с соответствующим методом
        self.server.getDataClient.connect(self.appendData)

        self.server.start()

        self.gif.start()
        self.gif.jumpToFrame(0)

        self.workingServer = True

        current_date_time = datetime.datetime.now()
        current_time = current_date_time.time()
        self.textInfoServer.append(str(current_time)[0:-7] + ": Сервер запущен")

    def stopServer(self):
        self.server.stop()
        self.server.join()

        self.gif.jumpToFrame(0)
        self.gif.stop()

        # очистка полей таблицы с клиентами
        while (self.clientsTableWidget.rowCount() > 0):
            self.clientsTableWidget.removeRow(0)

        self.workingServer = False

        current_date_time = datetime.datetime.now()
        current_time = current_date_time.time()
        self.textInfoServer.append(str(current_time)[0:-7] + ": Сервер выключен")

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication

    window = coreApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно

    app.exec_()  # и запускаем приложение