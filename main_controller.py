import inspect
import os
import sys
import threading
import traceback
import shutil
import importlib
import math

import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

from design import main_window, plugin_window
from time import gmtime, strftime
from plugins import base


class plugin_thread(threading.Thread):
    plugin_object = None
    index_list = []
    statistic = ""
    progress = 0
    text = ""
    plugin = {}

    colored_text = ""

    def __init__(self, plugin_id, plugin, text):
        threading.Thread.__init__(self)
        self.threadID = plugin_id
        self.name = plugin['name']
        self.text = text
        self.plugin = plugin

    def run(self):
        plugin = __import__(self.plugin["import_path"])
        plugin_objs = getattr(plugin, self.plugin["name_package"])
        plugin_obj = getattr(plugin_objs,
                             self.plugin["import_path"].split('.')[len(self.plugin["import_path"].split('.')) - 1],
                             "not_result")

        for elem in dir(plugin_obj):
            obj = getattr(plugin_obj, elem)
            if inspect.isclass(obj):
                if issubclass(obj, base.Plugin):
                    try:
                        self.plugin_object = obj()
                        self.index_list = self.plugin_object.textAnalysis(self.text, self.plugin["option"]) or ""
                        if isinstance(self.index_list, list) and len(self.index_list) == 2 and str(self.index_list[0]) \
                                == "error":
                            with open('log.txt', 'a', encoding='utf-8') as log:
                                log.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\nПлагин " + self.plugin["name"]
                                          + " вернул ошибку.\nДалее представлено описание ошибки:\n"
                                          + str(self.index_list[1]) + "\n")
                            self.index_list = "error"


                        if self.index_list != "error" and self.index_list != "invalid_options":
                            self.colorize_the_text()


                        if self.plugin["is_statistics"]:
                            self.statistic = self.plugin_object.getStatistics() or ""
                    except Exception:
                        with open('log.txt', 'a', encoding='utf-8') as log:
                            log.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\nПлагин " + self.plugin["name"]
                                      + " вернул ошибку.\nДалее представлено описание ошибки:\n"
                                      + traceback.format_exc() + "\n")
                        self.index_list = "error"

    def convert_index_list(self, index_list, length=13):
        i = 0
        resuit_index_list = []
        for group in index_list:
            for word in group:
                word.append(i)
                resuit_index_list.append(word)
            i += 1
            if i == length:
                i = 0
        return sorted(resuit_index_list, key=lambda lol: lol[0])

    def colorize_the_text(self):
        colors = ["#f08080", "#FFB6C1", "#FF7F50", "#BDB76B", "#EE82EE", "#BC8F8F", "#90EE90",
                  "#3CB371", "#6B8E23", "#66CDAA", "#AFEEEE", "#A9A9A9", "#FFD700"]
        try:
            converted_index_list = self.convert_index_list(self.index_list)
            self.colored_text = self.text
            for word in reversed(converted_index_list):
                if word[0] >= 0 and word[1] >= 0:
                    self.colored_text = self.colored_text[0:word[0]] + "<span style=\"background-color:" + colors[word[2]] + "\">" \
                       + self.colored_text[word[0]:word[1]] + "</span>" + self.colored_text[word[1]:]
                else:
                    raise Exception
        except:
            self.colored_text = ""

    def get_progress(self):
        try:
            if self.progress < 100 and self.plugin["is_progress"]:
                self.progress = math.ceil(self.plugin_object.getProgress()) or 0
            elif self.progress > 100:
                self.progress = 100
            return self.progress
        except Exception:
            self.progress = 0
            return self.progress


class pluginWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None, delete=False):
        self.parent = parent
        self.delete = delete
        super(pluginWindow, self).__init__(parent)
        self.ui = plugin_window.Ui_PluginWindow()
        self.ui.setupUi(self)
        self.draw_table()

    def draw_table(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clear()
        self.ui.tableWidget.setRowCount(len(self.parent.all_plugins))
        if self.delete:
            self.setWindowTitle(_translate("PluginWindow", "Удаление плагинов"))
            self.ui.pushButton.hide()
            self.ui.tableWidget.setColumnCount(2)
            self.ui.tableWidget.setHorizontalHeaderLabels(('Имя', 'Удалить'))
        else:
            self.ui.tableWidget.setColumnCount(4)
            self.ui.tableWidget.setHorizontalHeaderLabels(('Имя', 'Параметры', 'Использовать', 'Справка'))
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionsClickable(False)
        header.setFont(self.ui.font_header)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        _translate = QtCore.QCoreApplication.translate

        for row in range(len(self.parent.all_plugins)):
            name = QtWidgets.QTableWidgetItem(self.parent.all_plugins[row]['name'])
            name.setFont(self.parent.ui.font_label)
            self.ui.tableWidget.setItem(row, 0, name)

            if self.delete:
                btn = QtWidgets.QPushButton()
                btn.setFont(self.ui.font)
                btn.setObjectName(str(row))
                btn.setText(_translate("PluginWindow", "Удалить"))
                btn.setFixedSize(80, 25)
                btn.clicked.connect(self.click_delete_plugin)
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(widget)
                layout.addWidget(btn)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                self.ui.tableWidget.setCellWidget(row, 1, widget)
            else:
                option = QtWidgets.QLineEdit()
                option.setFixedSize(110, 25)
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(widget)
                layout.addWidget(option)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                self.ui.tableWidget.setCellWidget(row, 1, widget)

                check = QtWidgets.QCheckBox()
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(widget)
                layout.addWidget(check)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                self.ui.tableWidget.setCellWidget(row, 2, widget)

                btn = QtWidgets.QPushButton()
                btn.setFont(self.ui.font)
                btn.setObjectName(str(row))
                btn.setText(_translate("PluginWindow", "Справка"))
                btn.setFixedSize(80, 25)
                btn.clicked.connect(self.click_help_plugin)
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout(widget)
                layout.addWidget(btn)
                layout.setAlignment(QtCore.Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                self.ui.tableWidget.setCellWidget(row, 3, widget)

    def click_help_plugin(self):
        try:
            os.startfile(os.path.normpath(self.parent.all_plugins[int(self.sender().objectName())]['path']
                                          + r'\\help.pdf'))
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Файл справки не был найден.")

    def click_delete_plugin(self):
        shutil.rmtree(os.path.abspath(self.parent.all_plugins[int(self.sender().objectName())]['path']),
                      ignore_errors=True)
        self.parent.all_plugins.pop(int(self.sender().objectName()))
        self.ui.tableWidget.removeRow(int(self.sender().objectName()))

    def start_plugin_window(self):
        self.parent.text = self.parent.new_text
        self.parent.selected_plugins.clear()
        for row in range(self.ui.tableWidget.rowCount()):
            if self.ui.tableWidget.cellWidget(row, 2).findChild(type(QtWidgets.QCheckBox())).isChecked():
                selected_plugin = {
                    'name': self.parent.all_plugins[row]['name'],
                    'path': self.parent.all_plugins[row]['path'],
                    'option': self.ui.tableWidget.cellWidget(row, 1).findChild(type(QtWidgets.QLineEdit())).text(),
                    'progress': 0,
                    'index_list': [],
                    'statistic': "",
                    'name_package': self.parent.all_plugins[row]['name_package'],
                    'is_statistics': self.parent.all_plugins[row]['is_statistics'],
                    'is_progress': self.parent.all_plugins[row]['is_progress'],
                    'import_path': self.parent.all_plugins[row]['import_path'],
                    'colored_text': ""
                }
                self.parent.selected_plugins.append(selected_plugin)
        if len(self.parent.selected_plugins) == 0:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Вы не выбрали плагины для анализа.")
        else:
            for i in range(len(self.parent.selected_plugins)):
                self.parent.selected_plugins[i]["thread"] = plugin_thread(i, self.parent.selected_plugins[i],
                                                                          self.parent.text)
                self.parent.selected_plugins[i]["thread"].start()

            self.parent.ui.progressBar_shared.setVisible(True)
            self.parent.ui.pushButton.setVisible(True)
            self.parent.ui.pushButton.setEnabled(False)
            self.parent.ui.pushButton_2.setVisible(True)
            self.parent.ui.pushButton_4.setEnabled(True)
            self.parent.ui.pushButton_3.setEnabled(False)
            self.parent.ui.action.setEnabled(False)
            self.parent.ui.action_2.setEnabled(False)

            self.exit()
            self.parent.is_reset = True
            self.parent.plugin_execution_manager()

    def exit(self):
        self.close()


class mainWindow(QtWidgets.QMainWindow):
    timer = None
    is_reset = True
    is_error = False
    current_page = -1
    plugin_dir = "plugins"
    text = ""
    new_text = ""
    current_progress = 0
    all_plugins = []
    selected_plugins = []

    def __init__(self):
        super(mainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

    def show_info(self):
        QtWidgets.QMessageBox.about(self, "О программе", "Расширяемая система стилистического анализа текста. "
                                                         "\nЕрушев Ю.В. \n2020")

    @staticmethod
    def show_log():
        try:
            os.startfile(r'log.txt')
        except Exception:
            with open('log.txt', 'w', encoding='utf-8') as log:
                log.write("")
            os.startfile(r'log.txt')

    def open_help(self):
        try:
            os.startfile(r'help.pdf')
        except Exception:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Файл справки не был найден.")

    def install_plugin(self):
        name = ""
        flags = {'lib': False, 'py': False, 'not_one_py': False}
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать папку с плагином", "/home",
                                                          QtWidgets.QFileDialog.ShowDirsOnly
                                                          | QtWidgets.QFileDialog.DontResolveSymlinks)
        if os.path.isdir(path):
            find = False
            for dir in os.listdir(path):
                if dir == "lib" and len(os.listdir(os.path.join(os.path.normpath(path), dir))) > 0:
                    flags['lib'] = True
                elif dir.endswith(".py"):
                    if not find:
                        name = dir[: -3]
                        flags['py'] = True
                        find = True
                    else:
                        flags['not_one_py'] = True
            if flags['lib'] and flags['py'] and not flags['not_one_py']:
                try:
                    if not os.path.exists(self.plugin_dir):
                        os.mkdir(os.path.realpath(self.plugin_dir))
                    for dir in os.listdir(self.plugin_dir):
                        if path.split("/")[len(path.split("/")) - 1] == dir:
                            raise Exception("0")
                    shutil.copytree(os.path.abspath(path), os.path.abspath(
                        os.path.join(self.plugin_dir, path.split("/")[len(path.split("/")) - 1])))
                    check = self.check_plugin(
                        self.plugin_dir + "." + path.split("/")[len(path.split("/")) - 1] + "." + name,
                        path.split("/")[len(path.split("/")) - 1],
                        os.path.abspath(os.path.join(self.plugin_dir, path.split("/")[len(path.split("/")) - 1])))
                    if isinstance(check, int) and check > 0:
                        QtWidgets.QMessageBox.information(self, "Сообщение", "Плагин установлен.")
                    else:
                        shutil.rmtree(
                            os.path.abspath(os.path.join(self.plugin_dir, path.split("/")[len(path.split("/")) - 1])),
                            ignore_errors=True)
                        with open('log.txt', 'a', encoding='utf-8') as log:
                            log.write(check)
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин не соответствует спецификации."
                                                                       "\nОбратитесь к файлу логов.")
                except IOError:
                    with open('log.txt', 'w', encoding='utf-8') as log:
                        log.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\nПлагин " + path.split(".")[
                            len(path.split(".")) - 1] + \
                                  " не удалось установить.\nДалее представлено описание ошибки:\n" + traceback.format_exc() + "\n")
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Произошла неизвестная ошибка при установке."
                                                                   "\nОбратитесь к файлу логов.")
                except Exception as e:
                    if str(e) == "0":
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин с такой же директорией уже существует. "
                                                                       "\nПереименуйте папку с устанавливаемым плагином")
                    else:
                        with open('log.txt', 'w', encoding='utf-8') as log:
                            log.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\nПлагин " + path.split(".")[
                                len(path.split(".")) - 1] + \
                                      " не удалось установить.\nДалее представлено описание ошибки:\n" + traceback.format_exc() + "\n")
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Произошла неизвестная ошибка при установке."
                                                                       "\nОбратитесь к файлу логов.")
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин не соответствует спецификации.")

    def delete_plugin(self):
        self.search_all_plugins(delete=True)
        if len(self.all_plugins) > 0:
            self.plugin_window = pluginWindow(self, delete=True)
            self.plugin_window.show()

    def stop_main_window(self):
        self.timer.stop()
        _translate = QtCore.QCoreApplication.translate
        self.selected_plugins.clear()
        self.all_plugins.clear()
        self.ui.label.setText(_translate("MainWindow", "Введите текст"))
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setVisible(False)
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton_2.setVisible(False)
        self.ui.pushButton_5.setVisible(False)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.textBrowser.setReadOnly(False)
        self.ui.progressBar_shared.setVisible(False)
        self.ui.progressBar_local.setVisible(False)
        self.ui.action.setEnabled(True)
        self.ui.action_2.setEnabled(True)
        if self.current_page != -1:
            self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
            self.ui.textBrowser.setPlainText(self.new_text)
        self.current_page = -1
        self.new_text = ""

    def previous_page(self):
        _translate = QtCore.QCoreApplication.translate
        if self.current_page > 0:
            self.current_page -= 1
            self.ui.label.setText(_translate("MainWindow", self.selected_plugins[self.current_page]["name"]))
            self.ui.pushButton_2.setEnabled(True)
            if self.selected_plugins[self.current_page]["statistic"]:
                self.ui.pushButton_5.setVisible(True)
            else:
                self.ui.pushButton_5.setVisible(False)
            if len(self.selected_plugins[self.current_page]["index_list"]) != 0:
                if self.selected_plugins[self.current_page]["index_list"] == "invalid_options":
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Были заданы неверные параметры.")
                    self.ui.pushButton_5.setVisible(False)
                elif self.selected_plugins[self.current_page]["index_list"] == "error":
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин вернул ошибку или завершился некорректно."
                                                                   "\nОбратитесь к файлу логов.")
                    self.ui.pushButton_5.setVisible(False)
                else:
                    self.colorize_the_text()
            else:
                self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
                self.ui.textBrowser.setPlainText(self.text)
                self.ui.textBrowser.setReadOnly(True)
        else:
            self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
            self.current_page -= 1
            self.ui.label.setText(_translate("MainWindow", "Введите текст"))
            self.ui.pushButton.setEnabled(False)
            self.ui.textBrowser.setReadOnly(False)
            self.ui.pushButton_5.setVisible(False)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.textBrowser.setPlainText(self.new_text)

    # def convert_index_list(self, index_list, length=13):
    #     i = 0
    #     resuit_index_list = []
    #     for group in index_list:
    #         for word in group:
    #             word.append(i)
    #             resuit_index_list.append(word)
    #         i += 1
    #         if i == length:
    #             i = 0
    #     return sorted(resuit_index_list, key=lambda lol: lol[0])

    def colorize_the_text(self):
        # colors = ["#f08080", "#FFB6C1", "#FF7F50", "#BDB76B", "#EE82EE", "#BC8F8F", "#90EE90",
        #           "#3CB371", "#6B8E23", "#66CDAA", "#AFEEEE", "#A9A9A9", "#FFD700"]
        if len(self.selected_plugins[self.current_page]["colored_text"]) == 0:
            self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
            self.ui.textBrowser.setPlainText(self.text)
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин вернул некорректные данные.")
            # try:
            #     text = self.text
            #     converted_index_list = self.convert_index_list(self.selected_plugins[self.current_page]["index_list"])
            #     for word in reversed(converted_index_list):
            #         text = text[0:word[0]] + "<span style=\"background-color:" + colors[word[2]] + "\">" \
            #                + text[word[0]:word[1]] + "</span>" + text[word[1]:]
            #     self.selected_plugins[self.current_page]["colored_text"] = text
            # except:
            #     self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
            #     self.ui.textBrowser.setPlainText(self.text)
            #     QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин вернул некорректные данные.")
        else:
            self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
            self.ui.textBrowser.setText(self.selected_plugins[self.current_page]["colored_text"])
            self.ui.textBrowser.setReadOnly(True)

    def next_page(self):
        if self.current_page == -1:
            self.new_text = self.ui.textBrowser.toPlainText()
        if self.current_page < len(self.selected_plugins):
            _translate = QtCore.QCoreApplication.translate
            self.current_page += 1
            self.ui.label.setText(_translate("MainWindow", self.selected_plugins[self.current_page]["name"]))
            self.ui.pushButton.setEnabled(True)
            if self.current_page == len(self.selected_plugins) - 1:
                self.ui.pushButton_2.setEnabled(False)
            if self.selected_plugins[self.current_page]["statistic"]:
                self.ui.pushButton_5.setVisible(True)
            else:
                self.ui.pushButton_5.setVisible(False)
            if len(self.selected_plugins[self.current_page]["index_list"]) != 0:
                if self.selected_plugins[self.current_page]["index_list"] == "invalid_options":
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Были заданы неверные параметры.")
                    self.ui.pushButton_5.setVisible(False)
                elif self.selected_plugins[self.current_page]["index_list"] == "error":
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Плагин вернул ошибку или завершился некорректно."
                                                                   "\nОбратитесь к файлу логов.")
                    self.ui.pushButton_5.setVisible(False)
                else:
                    self.colorize_the_text()
            else:
                self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
                self.ui.textBrowser.setPlainText(self.text)
                self.ui.textBrowser.setReadOnly(True)

    def show_statistic(self):
        QtWidgets.QMessageBox.about(self, "Сводка по тексту",
                                    str(self.selected_plugins[self.current_page]["statistic"]))

    def reset(self):
        _translate = QtCore.QCoreApplication.translate
        self.current_page = -1
        self.ui.label.setText(_translate("MainWindow", "Введите текст"))
        self.ui.pushButton.setEnabled(False)
        self.ui.textBrowser.setReadOnly(False)
        self.ui.pushButton_5.setVisible(False)
        self.ui.pushButton_2.setEnabled(True)
        self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
        self.ui.textBrowser.setPlainText(self.text)
        self.new_text = ""
        self.is_reset = False

    def plugin_execution_manager(self):
        if self.is_reset:
            self.reset()
            while self.is_reset:
                kek = 0

        all_finished = True
        self.current_progress = 0
        for i in range(len(self.selected_plugins)):
            if not self.selected_plugins[i]["thread"] is None:
                if self.selected_plugins[i]["thread"].is_alive():
                    all_finished = False
                    self.selected_plugins[i]["progress"] = self.selected_plugins[i]["thread"].get_progress()
                else:
                    self.selected_plugins[i]["progress"] = 100
                    self.selected_plugins[i]["index_list"] = self.selected_plugins[i]["thread"].index_list
                    self.selected_plugins[i]["statistic"] = self.selected_plugins[i]["thread"].statistic
                    self.selected_plugins[i]["colored_text"] = self.selected_plugins[i]["thread"].colored_text
                    self.selected_plugins[i]["thread"] = None
                    self.selected_plugins[i]["complete"] = True
            self.current_progress += self.selected_plugins[i]["progress"]

        if all_finished:
            self.timer.stop()
            if len(self.selected_plugins) > 0:
                if self.current_page != -1:
                    if len(self.selected_plugins[self.current_page]["index_list"]) != 0 and \
                            self.selected_plugins[self.current_page]["complete"]:
                        self.selected_plugins[self.current_page]["complete"] = False
                        if self.selected_plugins[self.current_page]["index_list"] == "invalid_options":
                            QtWidgets.QMessageBox.critical(self, "Ошибка", "Были заданы неверные параметры.")
                        elif self.selected_plugins[self.current_page]["index_list"] == "error":
                            QtWidgets.QMessageBox.critical(self, "Ошибка",
                                                           "Плагин вернул ошибку или завершился некорректно."
                                                           "\nОбратитесь к файлу логов.")
                        else:
                            self.colorize_the_text()

                    elif self.selected_plugins[self.current_page]["thread"] is None \
                            and len(self.selected_plugins[self.current_page]["index_list"]) == 0:
                        self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
                        self.ui.textBrowser.setPlainText(self.text)
                        self.ui.textBrowser.setReadOnly(True)
                    if self.selected_plugins[self.current_page]["statistic"]:
                        self.ui.pushButton_5.setVisible(True)

                self.ui.progressBar_shared.setProperty("value", math.ceil(self.current_progress / len(self.selected_plugins)))
                self.ui.progressBar_shared.setVisible(False)
                self.ui.progressBar_local.setVisible(False)
                self.ui.pushButton_4.setEnabled(False)
                self.ui.pushButton_3.setEnabled(True)
                self.ui.action.setEnabled(True)
                self.ui.action_2.setEnabled(True)
        else:
            self.ui.progressBar_shared.setProperty("value", int(self.current_progress / len(self.selected_plugins)))

            if self.current_page != -1:
                if len(self.selected_plugins[self.current_page]["index_list"]) != 0 and \
                        self.selected_plugins[self.current_page]["complete"]:
                    self.selected_plugins[self.current_page]["complete"] = False
                    if self.selected_plugins[self.current_page]["index_list"] == "invalid_options":
                        QtWidgets.QMessageBox.critical(self, "Ошибка", "Были заданы неверные параметры.")
                    elif self.selected_plugins[self.current_page]["index_list"] == "error":
                        QtWidgets.QMessageBox.critical(self, "Ошибка",
                                                       "Плагин вернул ошибку или завершился некорректно."
                                                       "\nОбратитесь к файлу логов.")
                    else:
                        self.colorize_the_text()

                elif self.selected_plugins[self.current_page]["thread"] is None \
                        and len(self.selected_plugins[self.current_page]["index_list"]) == 0:
                    self.ui.textBrowser.setTextCursor(QtGui.QTextCursor())
                    self.ui.textBrowser.setPlainText(self.text)
                    self.ui.textBrowser.setReadOnly(True)
                if self.selected_plugins[self.current_page]["statistic"]:
                    self.ui.pushButton_5.setVisible(True)

                if self.selected_plugins[self.current_page]["progress"] != 100:
                    self.ui.progressBar_local.setVisible(True)
                    self.ui.progressBar_local.setProperty("value", self.selected_plugins[self.current_page]["progress"])
                else:
                    self.ui.progressBar_local.setProperty("value", self.selected_plugins[self.current_page]["progress"])
                    self.ui.progressBar_local.setVisible(False)
            else:
                self.ui.progressBar_local.setVisible(False)

            self.timer.start(1000)

    def start_main_window(self):
        with open('log.txt', 'w', encoding='utf-8') as log:
            log.write("")
        if self.current_page == -1:
            self.new_text = self.ui.textBrowser.toPlainText()
        if 0 < len(self.new_text) <= 500000:
            self.search_all_plugins()
            if len(self.all_plugins) > 0:
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.plugin_execution_manager)
                self.plugin_window = pluginWindow(self)
                self.plugin_window.show()
                if self.is_error:
                    self.is_error = False
                    QtWidgets.QMessageBox.critical(self, "Ошибка",
                                                  "Некоторые плагины не соответствуют \nспецификации или установлены "
                                                  "неправильно. \nОбратитесь к файлу логов.")
        elif len(self.new_text) > 500000:
            QtWidgets.QMessageBox.critical(self, "Ошибка",
                                           "Текст слишком большой.")
        else:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Введите текст для анализа.")

    @staticmethod
    def check_plugin(path, package, plugin_dir):
        result = 0
        try:
            if os.path.isdir(os.path.join(plugin_dir, 'lib')):
                sys.path.append(os.path.join(plugin_dir, 'lib'))
            else:
                raise Exception('"lib" directory not found on path: ' + os.path.abspath(plugin_dir))
            importlib.invalidate_caches()
            plugin = __import__(path)
            plugin_objs = getattr(plugin, package)
            plugin_obj = getattr(plugin_objs, path.split('.')[len(path.split('.')) - 1], "not_result")
        except Exception:
            return strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\nПлагин " + path.split(".")[len(path.split(".")) - 1] + \
                   " не удалось загрузить и проверить.\nДалее представлено описание ошибки:\n" + traceback.format_exc() + "\n"

        for elem in dir(plugin_obj):
            obj = getattr(plugin_obj, elem)
            if inspect.isclass(obj):
                if issubclass(obj, base.Plugin):
                    lines = inspect.getsourcelines(obj.textAnalysis)
                    if lines[0][1].find("pass") == -1:
                        result += 1
                    if result == 1:
                        lines = inspect.getsourcelines(obj.getStatistics)
                        if lines[0][1].find("pass") == -1:
                            result += 2
                        lines = inspect.getsourcelines(obj.getProgress)
                        if lines[0][1].find("pass") == -1:
                            result += 4
        return result

    def search_all_plugins(self, delete=False):
        self.all_plugins.clear()
        if os.path.exists(self.plugin_dir) and len(os.listdir(self.plugin_dir)) > 0:
            # len(os.listdir(self.plugin_dir)) > 0:
            for dir in os.listdir(self.plugin_dir):
                plugin_dir = os.path.join(os.path.abspath('.'), self.plugin_dir, dir)
                if os.path.isdir(plugin_dir):
                    find = False
                    for plugin_file in os.listdir(plugin_dir):
                        if plugin_file.endswith(".py"):
                            plugin_name = plugin_file[: -3]
                            if plugin_name != "base" and plugin_name != "__init__":
                                check = self.check_plugin(self.plugin_dir + "." + dir + "." + plugin_name, dir,
                                                          plugin_dir)
                                if isinstance(check, str):
                                    self.is_error = True
                                    with open('log.txt', 'a', encoding='utf-8') as log:
                                        log.write(check)
                                elif check > 0 and not find:
                                    find = True
                                    current_plugin = {
                                        'name': plugin_name,
                                        'path': plugin_dir,
                                        'name_package': dir,
                                        'is_statistics': (True if check == 3 or check == 7 else False),
                                        'is_progress': (True if check == 5 or check == 7 else False),
                                        'import_path': self.plugin_dir + "." + dir + "." + plugin_name
                                    }
                                    self.all_plugins.append(current_plugin)
            if len(self.all_plugins) == 0:
                self.is_error = False
                if delete:
                    QtWidgets.QMessageBox.warning(self, "Предупреждение", "Нет установленных плагинов.")
                else:
                    print(os.listdir(self.plugin_dir))
                    if len(os.listdir(self.plugin_dir)) == 2 and os.listdir(self.plugin_dir)[0] == "base.py" and \
                            os.listdir(self.plugin_dir)[1] == "__pycache__":
                        QtWidgets.QMessageBox.warning(self, "Предупреждение", "Нет установленных плагинов.")
                    else:
                        QtWidgets.QMessageBox.critical(self, "Ошибка",
                                                       "Все имеющиеся плагины не соответствуют \nспецификации или установлены "
                                                       "неправильно. \nОбратитесь к файлу логов.")
        else:
            QtWidgets.QMessageBox.warning(self, "Предупреждение", "Нет установленных плагинов.")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = mainWindow()
    application.show()

    sys.exit(app.exec())
