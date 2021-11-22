from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtPrintSupport import QPrintDialog
from functools import partial


import os
import sys
import re
import json
import subprocess


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.editor = QPlainTextEdit()
        self.resize(600, 450)
        self.number_of_instances = 0
        self.tree_window = None
        self.information = 0
        self.audit_result_window = None

        # Setup the QTextEdit editor configuration
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        layout.addWidget(self.editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save As...", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)

        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Copy", self)
        copy_action.setStatusTip("Copy selected text")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        ############################################################################################################

        search_toolbar = QToolBar("Search")
        search_toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(search_toolbar)

        search_action = QAction("Search", self)
        search_action.triggered.connect(self.show_new_window)
        search_action.setStatusTip("Search button")
        search_toolbar.addAction(search_action)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.update_file_text)
        refresh_action.setStatusTip("Refresh button")
        search_toolbar.addAction(refresh_action)

        audit_action = QAction("Audit Workstation", self)
        audit_action.triggered.connect(self.show_audit_workstation_window)
        audit_action.setStatusTip("Audit workstation by selected options.")
        search_toolbar.addAction(audit_action)

        self.update_title()
        self.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt);All files (*.*)")

        if path:
            try:
                with open(path) as f:
                    text = f.readlines()
                text = self.transform_to_json_format(str(text))
                self.editor.setPlainText(json.dumps(self.information, indent=4, sort_keys=True))
            except Exception as e:
                self.dialog_critical(str(e))

            else:
                self.path = path
                self.editor.setPlainText(json.dumps(self.information, indent=4, sort_keys=True))
                self.update_title()

    def transform_to_json_format(self, text):

        lines = re.sub('\n', '', text)
        lines = re.findall('<custom_item>(.*?)</custom_item>', lines)

        li = []
        for element in lines:

            mapper = {}
            element = re.sub('\\\\n', '', element)
            element = re.sub('\\\\\\\\', '\\\\', element)

            element = re.sub('\'', '', element)
            element = re.sub(' , ', ' ', element)
            element = re.sub('\s+', ' ', element)
            element = element.strip()
            element = re.findall('(\w+)\s+:\s(\w+|\".*?\")', element)

            for key, value in element:
                value = re.sub('\"', '', value)
                mapper[key] = value
            li.append(mapper)
        print(li)
        self.number_of_instances = len(li)
        self.information = li
        return li

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        self._save_to_path(self.path)

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text documents (*.txt);All files (*.*)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

    def _save_to_path(self, path):

        text = self.editor.toPlainText()

        try:
            name_of_json = re.findall('\/(\w+).json', path)[0]
            with open(f'{name_of_json}.json', 'w') as outfile:
                json.dump(text, outfile)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path

    def update_title(self):
        self.setWindowTitle("%s - No2Pads" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    def search_in_txt(self):
        txt_to_search = self.lineEdit.text()
        try:
            result = self.plainTextEdit_2.find(txt_to_search)
            if not result:
                # move cursor to the beginning and restart search
                self.plainTextEdit_2.moveCursor(QTextCursor.Start)
                self.plainTextEdit_2.find(txt_to_search)
        except:
            self.statusbar.showMessage("This is the last iteration founded")
        return

    def show_audit_workstation_window(self):
        print(len(self.information), self.information)
        # try:
        self.audit_result_window = AuditWindow(self.path, self.information)
        print('good')
        self.audit_result_window.show()
        # except:
             # print('No information uploaded')

    def show_new_window(self):
        try:
            self.tree_window = Window(self.path, self.number_of_instances, self.information)
            self.tree_window.show()
            if self.tree_window.block_count:
                self.update_file_text
        except:
            print('No information uploaded')

    def update_file_text(self):

        new_information = []
        if self.tree_window.block_count:
            for element in self.tree_window.block_count:
                new_information.append(self.information[element])

            self.number_of_instances = len(new_information)
            self.information = new_information
            self.editor.setPlainText(json.dumps(self.information, indent=4, sort_keys=True))


class AuditWindow(QWidget):
    # def __init__(self, path, information):
    #     super().__init__()
    #     self.path = re.findall(r'[^\/]+(?=\.)', path)[0]
    #     self.number_of_instances = len(self.information)
    #
    #     self.information = information
    #     self.results = []
    #     self.setWindowTitle(self.path)
    #     self.resize(400, 100)
    #     self.run_cmd()
    #     # Create an outer layout
    #     self.layout = QVBoxLayout()
    #
    #     optionsLayout = QVBoxLayout()
    #
    #     # groupBox.setLayout(optionsLayout)
    #
    #     for element, result in zip(range(self.number_of_instances), self.results):
    #         label = QLabel(f"Block{element} - {result}")
    #         optionsLayout.addWidget(label)
    #
    #     self.layout.addLayout(optionsLayout)
    #     # Set the window's main layout
    #     self.setLayout(self.layout)
    #     self.show()
    def __init__(self, path, information):
        super().__init__()
        self.path = re.findall(r'[^\/]+(?=\.)', path)[0]
        self.number_of_instances = len(information)
        self.information = information
        self.setWindowTitle('Audit Workstation')

        self.resize(400, 100)
        # Create an outer layout
        outerLayout = QVBoxLayout()
        # Create a form layout for the label and line edit
        topLayout = QFormLayout()
        # self.block_count = []
        self.policies_check = []

        self.run_cmd()
        # Add a label and a line edit to the form layout
        # self.lineEdit = QLineEdit(self)
        # self.lineEdit.setStatusTip('Search and mark the block that contain the syntax')
        # topLayout.addRow(":", self.lineEdit)

        # Create a layout for the checkboxes
        optionsLayout = QVBoxLayout()
        # Add some checkboxes to the layout
        groupBox = QGroupBox("Content")

        self.checkBoxes = []
        for i, policy_status in zip(range(self.number_of_instances), self.policies_check):
            if policy_status == 'Passed':
                checkBox = QCheckBox(f"Block - {i} ____ Policy Status: {policy_status}")
                checkBox.setStyleSheet('color : green')
                optionsLayout.addWidget(checkBox)
                self.checkBoxes.append(checkBox)
            else:
                checkBox = QCheckBox(f"Block - {i} ____ Policy Status: {policy_status}")
                checkBox.setStyleSheet('color : red')
                optionsLayout.addWidget(checkBox)
                self.checkBoxes.append(checkBox)

        self.checkBoxNone = QCheckBox("Select none")
        self.checkBoxNone.setCheckState(Qt.Unchecked)
        self.checkBoxNone.stateChanged.connect(
            partial(self.selectBoxes, False))
        optionsLayout.addWidget(self.checkBoxNone)

        self.checkBoxAll = QCheckBox("Select All")
        self.checkBoxAll.setCheckState(Qt.PartiallyChecked)
        self.checkBoxAll.stateChanged.connect(
            partial(self.selectBoxes, True))
        optionsLayout.addWidget(self.checkBoxAll)

        groupBox.setLayout(optionsLayout)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        outerLayout.addWidget(scroll)

        # Button to records the indexes that where chosen
        btn = QPushButton("Apply", self)
        btn.setToolTip("Apply changes")
        btn.clicked.connect(self.run_cmd)
        topLayout.addWidget(btn)

        # btn_line = QPushButton("Check policies", self)
        # btn_line.clicked.connect(self.run_cmd)
        # topLayout.addWidget(btn_line)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout)

        # Set the window's main layout
        self.setLayout(outerLayout)

    def checkStates(self):
        states = [c.isChecked() for c in self.checkBoxes]

        # temporarily block signals so that there is no recursive calls
        self.checkBoxAll.blockSignals(True)
        self.checkBoxNone.blockSignals(True)

        # set the "select all" fully checked too if all boxes are checked, otherwise make it partially checked
        self.checkBoxAll.setCheckState(
            Qt.Checked if all(states) else Qt.PartiallyChecked)

        # set the "select none" unchecked only if all boxes are unchecked, otherwise make it partially checked
        self.checkBoxNone.setCheckState(
            Qt.Unchecked if not any(states) else Qt.PartiallyChecked)

        # unblock signals back
        self.checkBoxAll.blockSignals(False)
        self.checkBoxNone.blockSignals(False)

    def selectBoxes(self, state):

        for check in self.checkBoxes:

            check.blockSignals(True)
            check.setChecked(state)
            check.blockSignals(False)
        self.checkStates()

    def run_cmd(self):
        for block in self.information:

            try:
                out = os.system(block['cmd'])
                out_filtered = re.search('(\w+)|(\d+)', out)
                expected_filter = re.search('(\w+)|(\d+)', block['expec'])
                # if out == block['expect']:
                if any(element in expected_filter for element in out_filtered):
                    self.policies_check.append('Passed')
                else:
                    self.policies_check.append('Not passed')
            except:
                self.policies_check.append('Not passed')


class Window(QWidget):
    def __init__(self, path, number_of_instances, information):
        super().__init__()
        self.path = re.findall(r'[^\/]+(?=\.)', path)[0]
        self.number_of_instances = number_of_instances
        self.information = information

        self.setWindowTitle(self.path)
        self.resize(400, 100)
        # Create an outer layout
        outerLayout = QVBoxLayout()
        # Create a form layout for the label and line edit
        topLayout = QFormLayout()
        self.block_count = []
        self.search_block = []

        # Add a label and a line edit to the form layout
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setStatusTip('Search and mark the block that contain the syntax')
        topLayout.addRow("Search:", self.lineEdit)

        # Create a layout for the checkboxes
        optionsLayout = QVBoxLayout()
        # Add some checkboxes to the layout
        groupBox = QGroupBox("Content")

        self.checkBoxes = []
        for i in range(self.number_of_instances):
            checkBox = QCheckBox(f"Block - {i}")
            optionsLayout.addWidget(checkBox)
            self.checkBoxes.append(checkBox)

        self.checkBoxNone = QCheckBox("Select none")
        self.checkBoxNone.setCheckState(Qt.Unchecked)
        self.checkBoxNone.stateChanged.connect(
            partial(self.selectBoxes, False))
        optionsLayout.addWidget(self.checkBoxNone)

        self.checkBoxAll = QCheckBox("Select All")
        self.checkBoxAll.setCheckState(Qt.PartiallyChecked)
        self.checkBoxAll.stateChanged.connect(
            partial(self.selectBoxes, True))
        optionsLayout.addWidget(self.checkBoxAll)

        groupBox.setLayout(optionsLayout)
        scroll = QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(400)
        outerLayout.addWidget(scroll)

        # Button to records the indexes that where chosen
        btn = QPushButton("Apply", self)
        btn.setToolTip("Close Application")
        btn.clicked.connect(self.checkStates_block_index)
        topLayout.addWidget(btn)

        btn_line = QPushButton("Search text", self)
        btn_line.clicked.connect(self.search_text_blocks)

        topLayout.addWidget(btn_line)

        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout)

        # Set the window's main layout
        self.setLayout(outerLayout)

    def search_text_blocks(self):

        self.checkBoxNone.setCheckState(Qt.PartiallyChecked)

        for check in self.checkBoxes:
            check.setCheckState(Qt.Unchecked)

        text = self.lineEdit.text()
        count = 0
        for element in self.information:
            find_match = re.search(text, str(element).lower())
            if find_match is not None:
                self.search_block.append(count)
            count += 1

        for index_check in self.search_block:
            self.checkBoxes[index_check].setCheckState(Qt.Checked)

    def checkStates_block_index(self):
        states = [c.isChecked() for c in self.checkBoxes]
        count = 0
        for i in states:
            if i:
                self.block_count.append(count)
            count += 1
        print(self.block_count)

    def checkStates(self):
        states = [c.isChecked() for c in self.checkBoxes]

        # temporarily block signals so that there is no recursive calls
        self.checkBoxAll.blockSignals(True)
        self.checkBoxNone.blockSignals(True)

        # set the "select all" fully checked too if all boxes are checked, otherwise make it partially checked
        self.checkBoxAll.setCheckState(
            Qt.Checked if all(states) else Qt.PartiallyChecked)

        # set the "select none" unchecked only if all boxes are unchecked, otherwise make it partially checked
        self.checkBoxNone.setCheckState(
            Qt.Unchecked if not any(states) else Qt.PartiallyChecked)

        # unblock signals back
        self.checkBoxAll.blockSignals(False)
        self.checkBoxNone.blockSignals(False)

    def selectBoxes(self, state):

        for check in self.checkBoxes:

            check.blockSignals(True)
            check.setChecked(state)
            check.blockSignals(False)
        self.checkStates()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("Notepad")

    window = MainWindow()
    app.exec_()

