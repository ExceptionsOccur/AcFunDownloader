# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class BaseUI(object):
    def setUI(self, MWin):

        _translate = QtCore.QCoreApplication.translate

        MWin.setObjectName('GUI_MWin')
        MWin.setFixedSize(400, 120)
        # MWin.resize(400, 120)
        # MWin.setMinimumSize(QtCore.QSize(400, 120))
        # MWin.setMaximumSize(QtCore.QSize(600, 120))
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        MWin.setFont(font)
        MWin.setWindowTitle(_translate('MWin', '我真的输了'))
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap('02.png'), QtGui.QIcon.Normal)     # TO DO：图标换个识别度好的
        # MWin.setWindowIcon(icon)

        self.central_widget = QtWidgets.QWidget(MWin)   # create based parent widget
        self.central_widget.setObjectName('central_widget')
        self.central_widget.resize(400, 120)

        self.vertical_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.vertical_layout.setContentsMargins(10, 10, 10, 10)
        self.vertical_layout.setSpacing(6)
        self.vertical_layout.setObjectName('vertical_layout')

        # self.central_frame = QtWidgets.QFrame(self.central_widget)
        # self.central_frame.setStyleSheet("background-color:green;")

        self.up_layout = QtWidgets.QHBoxLayout()
        self.up_layout.setSpacing(10)
        self.up_layout.setObjectName('up_layout')

        self.input_box = QtWidgets.QLineEdit(self.central_widget)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setPointSize(10)
        self.input_box.setFont(font)
        self.input_box.setPlaceholderText(_translate('GUI_MWin', '输入视频链接'))
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
        self.vertical_layout.addLayout(self.up_layout)

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
        self.table_widget.setRowCount(2)
        self.vertical_layout.addWidget(self.table_widget)
        self.up_layout.setStretchFactor(self.input_box, 8)
        self.up_layout.setStretchFactor(self.search_btn, 2)
        self.up_layout.setStretchFactor(self.download_btn, 2)
        self.table_widget.setColumnWidth(0, 40)
        self.table_widget.setColumnWidth(1, 338)
        # self.table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem('标题').setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))
        # self.table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem('up主').setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter))
        self.table_widget.setItem(0, 0, QtWidgets.QTableWidgetItem('标题'))
        self.table_widget.setItem(1, 0, QtWidgets.QTableWidgetItem('up主'))

        # TO DO：子线程更新进度条
