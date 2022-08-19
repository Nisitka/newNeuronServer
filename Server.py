from PyQt5.QtCore import QObject, pyqtSignal
from threading import Thread
import socket as socketNetwork

from Client import Client

class threadServer(QObject, Thread):
    newClientConnection = pyqtSignal(str, str)  # сигнал подключения клиента
    getDataClient = pyqtSignal(str, list)  # сигнал получения данных

    listClient = []  # список клиентов

    def __init__(self, name, port_):
        Thread.__init__(self)
        QObject.__init__(self)

        self.working = False
        self.address = socketNetwork.gethostname() # "192.168.3.4"

        self.port = int(port_)

        self.socket = socketNetwork.socket()

        self.socket.bind((str(self.address), int(self.port)))

        self.socket.listen(10)  # максимальное кол-во подключений
        self.numPacked = 0
        self.maxPacked = 20

    # трансляция сигнала для передачи данных в ядро приложения
    def addData(self, data_, text):
        self.getDataClient.emit(text, data_)

    def addNewClient(self, strName):
        self.newClientConnection.emit(self.listClient[-1].getName(), str(self.listClient[-1].getAddress()))

    def run(self):
        self.working = True

        # ожидание нового подключения
        while (self.working):
            # ожидание подключения: новый сокет и адрес клиента.
            # Именно этот сокет и будет использоваться для приема и посылке клиенту данных.
            connection, clientAddress = self.socket.accept()

            # добаление очередного клиента
            self.listClient.append(Client(connection, clientAddress))  # initialization

            #  соединение со слотом добавления нового клиента на сервер
            self.listClient[-1].initialization.connect(self.addNewClient)
            #  соединение со слотом принятия данных для нейронной сети
            self.listClient[-1].getData.connect(self.addData)

            self.listClient[-1].start()  # запуск потока-клинта

            #  self.newClientConnection.emit(self.listClient[-1].getName(), str(clientAddress))
            print(f"{clientAddress} has connected")

    def stop(self):
        self.working = False  # прекращаем ожидание подключения

        # если есть соединения с клиентами, сначала отсоединить их
        # и выключить потоки принятия данных

        if (len(self.listClient) > 0):
            for i in range(len(self.listClient)):
                self.listClient[i].getSocket().close()
                self.listClient[i].stopGetData()

        self.socket.close()  # выключаем сокет сервера
        self.listClient.clear()  # очищаем список клиентов

    def setPort(self, port_):
        self.port = port_