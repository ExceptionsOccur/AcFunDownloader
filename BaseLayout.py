# -*- coding: utf-8 -*-
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette, QBrush, QPixmap


class BaseUI(object):
    def setUI(self, MWin):

        _translate = QtCore.QCoreApplication.translate

        MWin.setObjectName('GUI_MWin')
        MWin.setFixedSize(420, 260)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        MWin.setWindowOpacity(0.9)
        # MWin.setAttribute(QtCore.Qt.WA_TintedBackground)
        # MWin.resize(400, 120)
        # MWin.setMinimumSize(QtCore.QSize(400, 120))
        # MWin.setMaximumSize(QtCore.QSize(600, 120))
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap('./ac.png')))
        MWin.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        MWin.setFont(font)
        MWin.setWindowTitle(_translate('MWin', 'AcFunDownloader'))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('icon.ico'), QtGui.QIcon.Normal)     # TO DO：图标换个识别度好的
        MWin.setWindowIcon(icon)

        self.central_widget = QtWidgets.QWidget(MWin)   # create based parent widget
        self.central_widget.setObjectName('central_widget')
        self.central_widget.resize(420, 260)

        self.text_box = QtWidgets.QLabel(self.central_widget)
        self.text_box.setFixedSize(400, 15)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(8)
        self.text_box.setFont(font)
        # self.text_box.setText(_translate('MWin', 'AcFun - 认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ'))
        self.text_box.setText('AcFun - 认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ')
        self.text_box.setAlignment(QtCore.Qt.AlignCenter)

        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setContentsMargins(10, 10, 10, 10)
        self.vertical_layout.setSpacing(6)
        self.vertical_layout.setObjectName('vertical_layout')

        # self.central_frame = QtWidgets.QFrame(self.central_widget)
        # self.central_frame.setStyleSheet("background-color:green;")

        self.console_layout = QtWidgets.QHBoxLayout()
        # self.console_layout.setSpacing(10)
        self.console_layout.setObjectName('console_layout')

        self.close_btn = QtWidgets.QPushButton(self.central_widget)
        self.close_btn.setObjectName('close_btn')
        self.close_btn.setFixedSize(18, 18)
        self.close_btn.setText(_translate('GUI_MWin', 'x'))

        self.mini_btn = QtWidgets.QPushButton(self.central_widget)
        self.mini_btn.setObjectName('mini_btn')
        self.mini_btn.setFixedSize(18, 18)
        self.mini_btn.setText(_translate('GUI_MWin', '-'))

        self.console_layout.addWidget(self.close_btn)
        self.console_layout.addWidget(self.mini_btn)
        self.console_layout.addStretch()
        self.vertical_layout.addLayout(self.console_layout)


        self.up_layout = QtWidgets.QHBoxLayout()
        self.up_layout.setSpacing(10)
        self.up_layout.setObjectName('up_layout')

        self.input_box = QtWidgets.QLineEdit(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.input_box.setFont(font)
        self.input_box.setPlaceholderText(_translate('GUI_MWin', '输入ac号或视频链接'))
        self.input_box.setObjectName('input_box')
        self.up_layout.addWidget(self.input_box)

        self.search_btn = QtWidgets.QPushButton(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.search_btn.setFont(font)
        self.search_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.search_btn.setObjectName('search_btn')
        self.search_btn.setText(_translate('GUI_MWin', '搜索'))
        self.up_layout.addWidget(self.search_btn)

        self.download_btn = QtWidgets.QPushButton(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.download_btn.setFont(font)
        self.download_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.download_btn.setObjectName('download_btn')
        self.download_btn.setText(_translate('GUI_MWin', '下载'))
        self.up_layout.addWidget(self.download_btn)
        # self.up_layout.setStretchFactor(self.input_box, 8)
        # self.up_layout.setStretchFactor(self.search_btn, 8)
        # self.up_layout.setStretchFactor(self.download_btn, 2)
        self.vertical_layout.addLayout(self.up_layout)




        self.tips_layout = QtWidgets.QHBoxLayout()
        self.tips_layout.setSpacing(10)
        self.tips_layout.setObjectName('tips_layout')

        # self.download_bar = QtWidgets.QProgressBar(self.central_widget)
        # self.download_bar.setMinimum(0)
        # self.download_bar.setMaximum(100)
        # self.download_bar.setOrientation(QtCore.Qt.Horizontal)
        # self.download_bar.setObjectName('download_bar')
        # self.tips_layout.addWidget(self.download_bar)

        self.fold_btn = QtWidgets.QPushButton(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.fold_btn.setFont(font)
        self.fold_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.fold_btn.setObjectName('fold_btn')
        self.fold_btn.setText(_translate('GUI_MWin', os.getcwd()))
        self.tips_layout.addWidget(self.fold_btn)

        self.pause_btn = QtWidgets.QPushButton(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.pause_btn.setFont(font)
        self.pause_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pause_btn.setObjectName('fold_btn')
        self.pause_btn.setText(_translate('GUI_MWin', '暂停'))
        self.tips_layout.addWidget(self.pause_btn)

        self.cancel_btn = QtWidgets.QPushButton(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.cancel_btn.setFont(font)
        self.cancel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cancel_btn.setObjectName('fold_btn')
        self.cancel_btn.setText(_translate('GUI_MWin', '取消'))
        self.tips_layout.addWidget(self.cancel_btn)


        self.vertical_layout.addLayout(self.tips_layout)

        self.table_widget = QtWidgets.QTableWidget(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.table_widget.setFont(font)
        self.table_widget.setObjectName('table_widget')

        self.table_widget.horizontalHeader().setVisible(False)
        self.table_widget.verticalHeader().setVisible(False)
        # self.table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # 自动铺满父控件
        self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.table_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.table_widget.setShowGrid(False)

        # self.table_widget.setFocusPolicy(QtCore.Qt.StrongFocus)
        # self.table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_widget.setLayoutDirection(QtCore.Qt.LeftToRight)
        # self.table_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        # self.table_widget.setFrameShadow(QtWidgets.QFrame.Plain)
        # self.table_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.table_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        # self.table_widget.setGridStyle(QtCore.Qt.SolidLine)
        self.table_widget.setColumnCount(2)
        self.table_widget.setObjectName("table_widget")
        self.table_widget.setRowCount(4)
        self.vertical_layout.addWidget(self.table_widget)
        self.table_widget.setColumnWidth(0, 60)
        self.table_widget.setColumnWidth(1, 318)
        # self.table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem('标题').setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))
        # self.table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem('up主').setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))
        self.table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem('标题'))
        self.table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem('up主'))
        self.table_widget.setItem(2, 0, QtWidgets.QTableWidgetItem('上传时间'))
        self.table_widget.setItem(3, 0, QtWidgets.QTableWidgetItem('时长'))
        [self.table_widget.item(x, y).setTextAlignment(QtCore.Qt.AlignCenter) for x in range(4) for y in range(1)]


        self.download_bar = QtWidgets.QProgressBar(self.central_widget)
        self.download_bar.setMinimum(0)
        self.download_bar.setMaximum(100)
        self.download_bar.setOrientation(QtCore.Qt.Horizontal)
        self.download_bar.setObjectName('download_bar')

        self.vertical_layout.addWidget(self.download_bar)
