# -*- coding: utf-8 -*-
import json
import os
import re
import time
import sys
import requests
import cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from BaseLayout import BaseUI

ts_url = []
ts_pref_url = ''
path = ''
last_ac = ''
PAUSE = 0
CANCEL = -1
START = 1
download_flag = False
global title
global up
global create_time
global duration
ts_url_section = r',\n(.*?)\n#'
ts_pref_url_section = r'https(.*?)hls/'
illegal_name = r'[\/\\\:\*\?\"\<\>\|\s\n]'
m3u8_section = r'(?<=window.videoInfo = )(.*?)(?=;(\s.*)window.videoResource)'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}


def get_mp4_duration(file_name):
    cap = cv2.VideoCapture(file_name)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration_time = frame_num / rate
        [m, s] = divmod(duration_time, 60)
        return '{:0>2d}:{:0>2d}'.format(int(m), int(s))
    return -1


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
            data = temp[0][0]
            data_json = json.loads(data)
            title = data_json['title']
            up = data_json['user']['name']
            create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data_json['videoList'][0]['uploadTime'] / 1000))
            [m, s] = divmod(data_json['videoList'][0]['durationMillis'] / 1000, 60)
            duration = '{:0>2d}:{:0>2d}'.format(int(m), int(s))
            ksPlay_info = data_json['currentVideoInfo']['ksPlayJson']
            ksPlay_json = json.loads(ksPlay_info)
            m3u8_file_url = ksPlay_json['adaptationSet'][0]['representation'][0]['url']
            res = requests.get(m3u8_file_url).text
            ts_url = re.findall(ts_url_section, res)
            ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
            info_list = [title, up, create_time, duration]
            self.signal.emit(info_list)


class DownloadThread(QThread):

    signal = pyqtSignal(int)
    pause_point = pyqtSignal(int)
    file_exits = pyqtSignal(str)
    file_error = pyqtSignal(str)

    def __init__(self):
        super(DownloadThread, self).__init__()

    def run(self):
        global path
        global duration
        global START
        global download_flag
        input_title = re.sub(illegal_name, '-', self.data[0])
        start_point = self.data[2]
        total_num = len(ts_url)
        file_name = input_title + '.mp4'
        with open(path + '/' + file_name, 'ab') as f:
            download_flag = True
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
                    download_flag = False
                    os.remove(path + '/' + file_name)
                    self.signal.emit(0)
                    return
            f.close()
            START = 0
        self.signal.emit(100)
        download_flag = False
        local_file_duration = get_mp4_duration(path + '/' + file_name)
        if duration != local_file_duration:
            self.file_error.emit('文件错误，下载文件时长不符！')
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
        global path
        self.title = ''
        self.up = ''
        self.create_time = ''
        self.pause_point = 0
        self.win_pos = self.pos()
        self.button_flag = False
        self.get_info_thread = GetInfoThread()
        self.download_thread = DownloadThread()
        path = os.getcwd()
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
        self.download_thread.file_error.connect(self.pop_information)
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:    # 使用 is 不生效
            self.button_flag = True
            self.win_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if Qt.LeftButton and self.button_flag:
            self.move(event.globalPos() - self.win_pos)
            event.accept()
            self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.button_flag = False
        self.setCursor(Qt.ArrowCursor)

    def store_pause_point(self, i):
        self.pause_point = i

    def pop_information(self, s):
        QMessageBox.information(self, '好像哪里不对！', s)

    def pause_task(self):
        if self.download_thread.data[1] is PAUSE:
            self.pause_btn.setText('暂停')
            self.download_thread.data = [self.title, START, self.pause_point]
            self.download_thread.start()
        elif self.download_thread.data[1] is START:
            self.pause_btn.setText('开始')
            self.download_thread.data[1] = PAUSE


    def cancel_task(self):
        global download_flag
        if download_flag is not True:
            self.pop_information('当前没有下载任务')
            return
        if self.download_thread.isRunning():
            self.download_thread.data[1] = CANCEL
            self.download_bar.setValue(0)
            # self.download_btn.setText('下载')
        else:
            os.remove(path + '/' + self.title + '.mp4')
            self.download_bar.setValue(0)
            # self.download_btn.setText('暂停')
        download_flag = False
        self.pause_btn.setText('暂停')
        self.pause_point = 0
        self.pause_btn.disconnect()
        self.cancel_btn.disconnect()

    # def continue_task(self):
    #     self.download_thread.data = [self.title, False, self.pause_point]
    #     self.download_thread.start()

    def get_directory(self):
        global path
        path = QFileDialog.getExistingDirectory(None, "选择保存文件夹", os.getcwd())
        if len(path) is 0:
            path = os.getcwd()
        if len(path) > 20:
            show_dir = path.split('/')[-1]
            show_path = path[0:3] + '../' + show_dir
        else:
            show_path = path
        self.fold_btn.setText(show_path)

    def get_info_callback(self, callback_list):
        global duration
        self.title = callback_list[0]
        self.up = callback_list[1]
        self.create_time = callback_list[2]
        duration = callback_list[3]
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.title))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(self.up))
        self.table_widget.setItem(2, 1, QtWidgets.QTableWidgetItem(self.create_time))
        self.table_widget.setItem(3, 1, QtWidgets.QTableWidgetItem(duration))

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
        global duration
        global download_flag
        if download_flag is True:
            self.pop_information('当前正在下载')
            return
        if ts_pref_url is '':
            input_data = self.input_box.text()
            if len(input_data) is 0:
                QMessageBox.information(self, '好像哪里不对！', '输入为空')
                return
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
            duration = '{:0>2d}:{:0>2d}'.format(int(m), int(s))
            ks_play_info = data_json['currentVideoInfo']['ksPlayJson']
            ks_play_json = json.loads(ks_play_info)
            m3u8_file_url = ks_play_json['adaptationSet'][0]['representation'][0]['url']
            res = requests.get(m3u8_file_url).text
            ts_url = re.findall(ts_url_section, res)
            ts_pref_url = re.search(ts_pref_url_section, m3u8_file_url)[0]
            self.update_ui(self.title, self.up, self.create_time, duration)
        input_title = re.sub(illegal_name, '-', self.title)
        file_name = input_title + '.mp4'
        if os.path.exists(path + '/' + file_name) is True:
            self.pop_information('该文件已存在')
            return
        self.download_thread.data = [self.title, START, self.pause_point]
        self.download_thread.start()
        self.pause_btn.clicked.connect(self.pause_task)
        self.cancel_btn.clicked.connect(self.cancel_task)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AcFunDownloader()
    w.show()
    sys.exit(app.exec_())
