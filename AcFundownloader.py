# -*- coding: utf-8 -*-
import json
import os
import re
import time
import sys
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication
from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from BaseLayout import BaseUI

ts_url = []
ts_pref_url = ''
last_ac = ''
global title
global up
global create_time
global duration
PAUSE = 0
CANCEL = -1
START = 1
ts_url_section = r',\n(.*?)\n#'
ts_pref_url_section = r'https(.*?)segment/'
illegal_name = r'[\/\\\:\*\?\"\<\>\|\s\n]'
m3u8_section = r'window.videoInfo = (.*?);\n        window.qualityConfig ='
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}


class GetInfoThread(QThread):

    signal = pyqtSignal(list)
    no_this_ac = pyqtSignal(str)
    ac_num_is_illegal = pyqtSignal(str)
    same_result = pyqtSignal(str)

    def __init__(self):
        super(GetInfoThread, self).__init__()

    def run(self):
        global ts_url
        global ts_pref_url
        global last_ac
        global title
        global up
        global create_time
        global duration
        global PAUSE
        input_data = self.data
        if input_data is '':
            self.no_this_ac.emit('输入为空')
            return
        pause_point = 0
        PAUSE = False
        ac_num = ''
        temp = re.findall(r'(ac\d+)', input_data)
        if len(temp) is 0:
            temp = re.findall(r'(\d+)', input_data)
            if len(temp) is 0:
                self.ac_num_is_illegal.emit('识别不到输入的ac号')
            else:
                ac_num = 'ac' + temp[0]
        else:
            ac_num = temp[0]
        if ac_num == last_ac:
            self.signal.emit([title, up, create_time, duration])
            self.same_result.emit('与上次输入的识别结果相同')
            return
        else:
            last_ac = ac_num
            ac_url = 'https://www.acfun.cn/v/' + ac_num
            res = requests.get(ac_url, headers=headers).text
            temp = re.findall(m3u8_section, res)
            if len(temp) is 0:
                self.no_this_ac.emit('世界线可能发生了变动，无法找到该视频')
                return
            data = temp[0]
            data_json = json.loads(data)
            title = data_json['title']
            up = data_json['user']['name']
            create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data_json['videoList'][0]['uploadTime'] / 1000))
            [m, s] = divmod(data_json['videoList'][0]['durationMillis'] / 1000, 60)
            duration = '{:0>2d}:{:0>2d}'.format(int(m), int(s))
            ksPlay_info = data_json['currentVideoInfo']['ksPlayJson']
            ksPlay_json = json.loads(ksPlay_info)
            m3u8_file_url = ksPlay_json['adaptationSet']['representation'][0]['url']
            res = requests.get(m3u8_file_url).text
            ts_url = re.findall(ts_url_section, res)
            ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
            info_list = [title, up, create_time, duration]
            self.signal.emit(info_list)


class DownloadThread(QThread):

    signal = pyqtSignal(int)
    pause_point = pyqtSignal(int)
    file_exits = pyqtSignal(str)

    def __init__(self):
        super(DownloadThread, self).__init__()

    def run(self):
        global path
        input_title = re.sub(illegal_name, '-', self.data[0])
        start_point = self.data[2]
        total_num = len(ts_url)
        file_name = input_title + '.mp4'
        if os.path.exists(path + '/' + file_name) is True:
            self.file_exits.emit('该文件已存在')
            return
        with open(path + '/' + file_name, 'ab') as f:
            for i in range(start_point, total_num):
                ts = requests.get(ts_pref_url + ts_url[i])
                f.write(ts.content)
                self.signal.emit(int(100 * i / total_num))
                if self.data[1] is PAUSE:
                    if i == total_num:
                        f.close()
                        return
                    else:
                        self.pause_point.emit(i + 1)
                        f.close()
                        return
                if self.data[1] is CANCEL:
                    f.close()
                    os.remove(path + '/' + file_name)
                    self.signal.emit(0)
                    return
            f.close()
        self.signal.emit(100)
        # for i in range(0, total_num):
        #     ts = requests.get(ts_pref_url + ts_url[i])
        #     # with open(str.split(url_info, '?')[0], 'wb') as code:
        #     with open('{:0>6d}.ts'.format(i), 'wb') as code:
        #         code.write(ts.content)
        #         code.close()
        #     self.signal.emit(int(100 * i / total_num))
        # file_name = title + '.mp4'
        # os.system('copy /b *.ts' + ' ' + re.sub(illegal_name, '-', file_name) + ' && ' + 'del *.ts')


class AcFunDownloader(QMainWindow, BaseUI):
    def __init__(self, parent=None):
        super(AcFunDownloader, self).__init__(parent)
        self.setUI(self)
        with open('./Style.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.flag = True
        self.position = self.pos()
        self.title = ''
        self.up = ''
        self.duration = ''
        self.create_time = ''
        self.pause_point = 0
        self.get_info_thread = GetInfoThread()
        self.download_thread = DownloadThread()
        self.setMouseTracking(True)
        self.path = os.getcwd()
        self.search_btn.clicked.connect(self.get_info_and_show)
        self.download_btn.clicked.connect(self.download_video)
        self.fold_btn.clicked.connect(self.get_directory)
        self.close_btn.clicked.connect(self.close)
        self.mini_btn.clicked.connect(self.showMinimized)

        self.get_info_thread.signal.connect(self.get_info_callback)
        self.download_thread.signal.connect(self.download_callback)
        self.download_thread.pause_point.connect(self.store_pause_point)
        self.download_thread.file_exits.connect(self.pop_information)
        self.get_info_thread.no_this_ac.connect(self.pop_information)
        self.get_info_thread.ac_num_is_illegal.connect(self.pop_information)
        self.get_info_thread.same_result.connect(self.pop_information)

    def store_pause_point(self, i):
        self.pause_point = i

    def pop_information(self, s):
        QMessageBox.information(self, '好像哪里不对！', s)

    def pause_task(self):
        self.download_thread.data[1] = PAUSE
        self.download_btn.setText('开始')

    def cancel_task(self):
        if self.download_thread.isRunning():
            self.download_thread.data[1] = CANCEL
            self.download_bar.setValue(0)
            self.download_btn.setText('下载')
        else:
            os.remove(path + '/' + self.title + '.mp4')
            self.download_bar.setValue(0)
            self.download_btn.setText('下载')
        self.pause_btn.disconnect()
        self.cancel_btn.disconnect()

    def continue_task(self):
        self.download_thread.data = [self.title, False, self.pause_point]
        self.download_thread.start()

    def get_directory(self):
        self.path = QFileDialog.getExistingDirectory(None, "选择保存文件夹", os.getcwd())
        if len(self.path) is 0:
            self.path = os.getcwd()
        if len(self.path) > 20:
            show_dir = self.path.split('/')[-1]
            show_path = self.path[0:3] + '../' + show_dir
        else:
            show_path = self.path
        self.fold_btn.setText(show_path)

    def get_info_callback(self, callback_list):
        self.title = callback_list[0]
        self.up = callback_list[1]
        self.create_time = callback_list[2]
        self.duration = callback_list[3]
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.title))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(self.up))
        self.table_widget.setItem(2, 1, QtWidgets.QTableWidgetItem(self.create_time))
        self.table_widget.setItem(3, 1, QtWidgets.QTableWidgetItem(self.duration))

    def update_ui(self, t, u, c, d):
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(t))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(u))
        self.table_widget.setItem(2, 1, QtWidgets.QTableWidgetItem(c))
        self.table_widget.setItem(3, 1, QtWidgets.QTableWidgetItem(d))

    def download_callback(self, i):
        self.download_bar.setValue(i)

    def get_info_and_show(self):
        self.get_info_thread.data = self.input_box.text()
        self.get_info_thread.start()

    def download_video(self):
        global ts_pref_url
        global ts_url
        if ts_pref_url is '':
            input_data = self.input_box.text()
            ac_num = ''
            temp = re.findall(r'(ac\d+)', input_data)
            if len(temp) is 0:
                temp = re.findall(r'(\d+)', input_data)
                if len(temp) is 0:
                    self.ac_num_is_illegal.emit('识别不到输入的ac号')
                else:
                    ac_num = 'ac' + temp[0]
            else:
                ac_num = temp[0]
            ac_url = 'https://www.acfun.cn/v/' + ac_num
            res = requests.get(ac_url, headers=headers).text
            temp = re.findall(m3u8_section, res)
            if len(temp) is 0:
                self.no_this_ac.emit('世界线可能发生了变动，无法找到该视频')
                return
            data = temp[0]
            data_json = json.loads(data)
            self.title = re.sub(illegal_name, '-', data_json['title'])
            self.up = data_json['user']['name']
            self.create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data_json['videoList'][0]['uploadTime'] / 1000))
            [m, s] = divmod(data_json['videoList'][0]['durationMillis'] / 1000, 60)
            self.duration = '{:0>2d}:{:0>2d}'.format(int(m), int(s))
            ks_play_info = data_json['currentVideoInfo']['ksPlayJson']
            ks_play_json = json.loads(ks_play_info)
            m3u8_file_url = ks_play_json['adaptationSet']['representation'][0]['url']
            res = requests.get(m3u8_file_url).text
            ts_url = re.findall(ts_url_section, res)
            ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
            self.update_ui(self.title, self.up, self.create_time, self.duration)
        self.download_thread.data = [self.title, START, self.pause_point]
        self.download_thread.start()
        self.pause_btn.clicked.connect(self.pause_task)
        self.cancel_btn.clicked.connect(self.cancel_task)

    def mousePressEvent(self, event):
        if event.button() is Qt.Qt.LeftButton:
            self.flag = True
            self.position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(Qt.QCursor(Qt.Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if event.button() is Qt.Qt.LeftButton and self.flag:
            self.move(event.globalPos() - self.position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.flag = False
        self.setCursor(Qt.QCursor(Qt.Qt.ArrowCursor))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AcFunDownloader()
    w.show()
    sys.exit(app.exec_())
