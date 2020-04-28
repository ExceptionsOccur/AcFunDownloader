# -*- coding: utf-8 -*-
import json
import os
import re

import requests
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import sys
from BaseLayout import BaseUI

ts_url = []
ts_pref_url = ''
path = ''
last_ac = ''
title = ''
up = ''
ts_url_section = r',\n(.*?)\n#'
ts_pref_url_section = r'https(.*?)segment/'
illegal_name = r'[\/\\\:\*\?\"\<\>\|\s\n]'
m3u8_section = r'window.videoInfo = (.*?);\n        window.qualityConfig ='
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}


class GetInfoThread(QThread):

    signal = pyqtSignal(list)

    def __init__(self):
        super(GetInfoThread, self).__init__()

    def run(self):
        global ts_url
        global ts_pref_url
        global last_ac
        global title
        global up
        input_data = self.data
        ac_num = re.findall(r'(ac\d+)', input_data)[0]
        if ac_num == last_ac:
            self.signal.emit([title, up])
            return
        else:
            last_ac = ac_num
            ac_url = 'https://www.acfun.cn/v/' + ac_num
            res = requests.get(ac_url, headers=headers).text
            data = re.findall(m3u8_section, res)[0]
            data_json = json.loads(data)
            title = data_json['title']
            up = data_json['user']['name']
            ksPlay_info = data_json['currentVideoInfo']['ksPlayJson']
            ksPlay_json = json.loads(ksPlay_info)
            m3u8_file_url = ksPlay_json['adaptationSet']['representation'][0]['url']
            res = requests.get(m3u8_file_url).text
            ts_url = re.findall(ts_url_section, res)
            ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
            info_list = [title, up]
            self.signal.emit(info_list)


class DownloadThread(QThread):

    signal = pyqtSignal(int)

    def __init__(self):
        super(DownloadThread, self).__init__()

    def run(self):
        input_title = self.data
        total_num = len(ts_url)
        file_name = input_title + '.mp4'
        with open(path + '/' + file_name, 'ab') as f:
            for i in range(0, total_num):
                ts = requests.get(ts_pref_url + ts_url[i])
                f.write(ts.content)
                self.signal.emit(int(100 * i / total_num))
            f.close()
        # for i in range(0, total_num):
        #     ts = requests.get(ts_pref_url + ts_url[i])
        #     # with open(str.split(url_info, '?')[0], 'wb') as code:
        #     with open('{:0>6d}.ts'.format(i), 'wb') as code:
        #         code.write(ts.content)
        #         code.close()
        #     self.signal.emit(int(100 * i / total_num))
        # file_name = title + '.mp4'
        # os.system('copy /b *.ts' + ' ' + re.sub(illegal_name, '-', file_name) + ' && ' + 'del *.ts')
        self.signal.emit(100)


class Implementation(QMainWindow, BaseUI):
    def __init__(self, parent=None):
        super(Implementation, self).__init__(parent)
        self.setUI(self)

        self.video_info_flag = False
        self.title = ''
        self.up = ''

        self.get_info_thread = GetInfoThread()
        self.download_thread = DownloadThread()

        self.search_btn.clicked.connect(self.get_info_and_show)
        self.download_btn.clicked.connect(self.download_video)
        self.fold_btn.clicked.connect(self.get_directory)

        self.get_info_thread.signal.connect(self.get_info_callback)
        self.download_thread.signal.connect(self.download_callback)

    def get_directory(self):
        global path
        path = QFileDialog.getExistingDirectory(None, "选择保存文件夹", os.getcwd())
        if len(path) > 20:
            show_dir = path.split('/')[-1]
            show_path = path[0:3] + '../' + show_dir
        else:
            show_path = path
        self.fold_btn.setText(QCoreApplication.translate('GUI_MWin', show_path))

    def get_info_callback(self, callback_list):
        self.title = callback_list[0]
        self.up = callback_list[1]
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.title))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(self.up))

    def update_ui(self, title, up):
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(title))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(up))

    def download_callback(self, i):
        self.download_bar.setValue(i)

    def get_info_and_show(self):
        self.get_info_thread.data = self.input_box.text()
        self.get_info_thread.start()

    def download_video(self):
        global ts_pref_url
        global ts_url
        # if ts_pref_url is '':
            # new_thread = GetInfoThread()
            # new_thread.data = self.input_box.text()
            # new_thread.signal.connect(self.get_info_callback)
            # new_thread.start()
            # new_thread.wait()
        input_data = self.input_box.text()
        ac_num = re.findall(r'(ac\d+)', input_data)[0]
        ac_url = 'https://www.acfun.cn/v/' + ac_num
        res = requests.get(ac_url, headers=headers).text
        data = re.findall(m3u8_section, res)[0]
        data_json = json.loads(data)
        self.title = data_json['title']
        self.up = data_json['user']['name']
        ks_play_info = data_json['currentVideoInfo']['ksPlayJson']
        ks_play_json = json.loads(ks_play_info)
        m3u8_file_url = ks_play_json['adaptationSet']['representation'][0]['url']
        res = requests.get(m3u8_file_url).text
        ts_url = re.findall(ts_url_section, res)
        ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
        self.update_ui(self.title, self.up)
        self.download_thread.data = self.title
        self.download_thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Implementation()
    w.show()
    sys.exit(app.exec_())
