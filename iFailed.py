# -*- coding: utf-8 -*-
import json
import os
import re

import requests
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from BaseLayout import BaseUI


class Implementation(QMainWindow, BaseUI):
    def __init__(self, parent=None):
        super(Implementation, self).__init__(parent)
        self.setUI(self)

        self.video_info_flag = False
        self.ts_url = []
        self.ts_pref_url = ''
        self.title = ''
        self.up = ''

        self.search_btn.clicked.connect(self.get_video_info_and_show)
        self.download_btn.clicked.connect(self.download_video)

    def get_video_info_and_show(self):
        input_data = self.input_box.text()
        ac_num = re.findall(r'(ac\d+)', input_data)[0]
        ac_url = 'https://www.acfun.cn/v/' + ac_num
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}
        res = requests.get(ac_url, headers=headers).text
        data = re.findall(r'window.videoInfo = (.*?);\n        window.qualityConfig =', res)[0]
        data_json = json.loads(data)
        self.title = data_json['title']
        self.up = data_json['user']['name']
        ksPlay_info = data_json['currentVideoInfo']['ksPlayJson']
        ksPlay_json = json.loads(ksPlay_info)
        m3u8_file_url = ksPlay_json['adaptationSet']['representation'][0]['url']
        res = requests.get(m3u8_file_url).text
        self.ts_url = re.findall(r',\n(.*?)\n#', res)
        self.ts_pref_url = re.search(r'https(.*?)segment/', m3u8_file_url)[0]
        self.video_info_flag = True
        self.update_table_show()

    def update_table_show(self):
        self.table_widget.setItem(0, 1, QtWidgets.QTableWidgetItem(self.title))
        self.table_widget.setItem(1, 1, QtWidgets.QTableWidgetItem(self.up))

    def download_video(self):
        if self.video_info_flag is False:
            self.get_video_info_and_show()
        for i in range(0, len(self.ts_url)):
            ts = requests.get(self.ts_pref_url + self.ts_url[i])
            # with open(str.split(url_info, '?')[0], 'wb') as code:
            with open('{:0>6d}.ts'.format(i), 'wb') as code:
                code.write(ts.content)
                code.close()
        file_name = self.title + '.mp4'
        os.system('copy /b *.ts' + ' ' + re.sub(r'[\/\\\:\*\?\"\<\>\|\s\n]', '-', file_name) + ' && ' + 'del *.ts')
        QtWidgets.QMessageBox.information(self, '我真的输了', '视频下载完成', QtWidgets.QMessageBox.Yes)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Implementation()
    w.show()
    sys.exit(app.exec_())
