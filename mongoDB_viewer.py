from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import json
from pymongo import MongoClient
from cryptography.fernet import Fernet


class EncryptingData:

    def __init__(self, path_to_file):
        self.path_to_file = path_to_file

        with open(self.path_to_file) as f:
            self.data = json.load(f)

        self.write_key()
        self.key = self.load_key()

    def write_key(self):
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        return open("key.key", "rb").read()

    def store_db_encrypted_data(self):

        f = Fernet(self.key)

        for idx_key, key in enumerate(self.data.keys()):
            new_data = [f.encrypt(element.encode('ascii')) for element in self.data[key]]
            self.data[key] = new_data

        return self.data, self.key

    def create_db(self):
        self.store_db_encrypted_data()
        client = MongoClient('localhost', 9010)
        db = client['secure']
        collection = db["data"]
        collection.insert_one(self.data)

        return collection


enc = EncryptingData('good.json')
res, key = enc.store_db_encrypted_data()


class MainWindow(QMainWindow):
    def __init__(self, data, key):
        super(MainWindow, self).__init__()
        self.data = data
        self.key = key
        self.new_data = {}
        self.table_window = None

        self.setWindowTitle("MongoDB Visualizer")
        self.setGeometry(400, 400, 300, 260)

        self.data_json = QPushButton(self)
        self.data_json.setText("Data Decoded")
        self.data_json.clicked.connect(self.db_visualize_decode)
        self.data_json.setToolTip("Visualise decoded data")

        self.data_db = QPushButton(self)
        self.data_db.setText("Data Encoded")
        self.data_db.clicked.connect(self.db_visualize_encode)
        self.data_db.setToolTip("Visualise encoded data")

        self.data_json.resize(150, 50)
        self.data_db.resize(150, 50)

        self.data_json.move(80, 80)
        self.data_db.move(80, 140)

    def db_visualize_encode(self):
        try:
            print(self.data)
            self.table_window = TableView(self.data)
            self.table_window.show()

        except:
            print('Bad')

    def db_visualize_decode(self):
        try:
            f = Fernet(self.key)

            for idx_key, key in enumerate(self.data.keys()):

                new_data = [(str(f.decrypt(element))) for element in self.data[key]]
                self.new_data[key] = new_data
            self.table_window = TableView(self.new_data)
            self.table_window.show()
        except:
            print('Bad')


class TableView(QWidget):
    def __init__(self, data):
        super().__init__()
        self.title = 'MongoDB - Reader'

        self.data = data
        self.rows, self.columns = len(self.data[list(self.data.keys())[0]]), len(list(self.data.keys()))

        self.left = 0
        self.top = 0
        self.width = 600
        self.height = 400

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # Show window
        self.show()

    # Create table
    def createTable(self):
        self.tableWidget = QTableWidget()

        # Row count
        self.tableWidget.setRowCount(self.rows)

        # Column count
        self.tableWidget.setColumnCount(self.columns)
        horHeaders = []
        for idx_key, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for idx_element, element in enumerate(self.data[key]):
                print(idx_element, element)
                self.tableWidget.setItem(idx_element, idx_key, QTableWidgetItem(str(element)))

        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableWidget.setHorizontalHeaderLabels(horHeaders)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow(res, key)
    ex.show()
    sys.exit(app.exec_())
