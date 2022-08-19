from PyQt5.QtCore import QObject, pyqtSignal
from threading import Thread

import datetime
import codecs

class Client(QObject, Thread):
    initialization = pyqtSignal(str)
    getData = pyqtSignal(list, str)  # отправка принятого массива данных и комментария

    def __init__(self, socket_, address_):
        QObject.__init__(self)
        Thread.__init__(self)

        self.socket = socket_
        self.address = address_

        self.numPacked = 0
        self.maxPacked = 20

        self.dataPackageSize = 2048 * 1000 * 1000

        self.working = False
        self.init = False

        # данные, принятые клиентом
        self.data = []

    def run(self):
        self.working = True

        print("поток для принятия данных запущен!")
        self.arrFull = []
        while (self.working):
            data = self.socket.recv(self.dataPackageSize)
            if not data:
                break

            #  есди клиент еще не инциализирован, то значит ему отправили данные, связанные с этим
            if not self.init:
                self.name = data.decode("utf-8")
                self.initialization.emit(self.name)

                self.init = True

                dataOUT = "Server set client!"

            else:
                if self.numPacked == 0:
                    timeGetData = datetime.datetime.now().time()

                arr = [int(data[i:i + 2], 16) for i in range(0, len(data), 2)]
                self.arrFull += arr

                if self.upPacked():
                    dataOUT = "Server get packed!"
                else:
                    # инициализвция входного значения для сети
                    dataOUT = "Server get data!"

                    time_1 = datetime.timedelta(hours=timeGetData.hour, milliseconds=timeGetData.minute,
                                                seconds=timeGetData.second)
                    currentTime = datetime.datetime.now().time()
                    time_2 = datetime.timedelta(hours=currentTime.hour, milliseconds=currentTime.minute,
                                                seconds=currentTime.second)
                    text = str(datetime.datetime.now().time())[0:-7] + ": получены данные от " + self.name + " (за " + str(time_2.seconds - time_1.seconds) + " секунд)"

                    self.getData.emit(self.arrFull, text)
                    self.arrFull.clear()

            print(dataOUT)
            dataOUT = codecs.encode(dataOUT, 'UTF-8')
            self.socket.sendall(dataOUT)

    def stopGetData(self):
        self.working = False
        self.join()

    def getSocket(self):
        return self.socket
    def getAddress(self):
        return self.address
    def getName(self):
        return self.name
    def getNumPacked(self):
        return self.numPacked
    def upPacked(self):
        if self.numPacked != self.maxPacked:
            self.numPacked += 1
            return True
        else:
            self.numPacked = 0
            return False