import copy
import datetime
import os.path
from socket import socket
import psutil

from PySide6.QtCore import QFile, Qt, QThread, QModelIndex, Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMessageBox, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidgetItem, \
    QComboBox, QAbstractItemView

from action.MsgPackAction import MsgPackAction
from action.SocketAction import SocketAction
from typing import Optional
from action.ThreadAction import UdpReceiverThread, UdpSenderWorker

import re
from action.ReadCsv import ReadCsv
from action.TimeGenerator import AutoTimeGenerator
from functools import partial


class TrdpWindow(QMainWindow):
    # msg_packed = Singal()
    def __init__(self):
        super().__init__()

    def setup(self, base_path):
        '''数据结构'''
        self.data_length = 0
        self.header_data = None
        self.send_custom_data = None
        # self.send_msg = None
        self.snd_data = b''
        self.recv_dataset = None
        self.header_options_text = ['None', '固定值', '程序自增(+1)', 'CRC-仅头部']

        '''文件路径'''
        self.base_path = base_path
        self.cfg_dir_name = "config"
        self.ui_dir_name = "ui"
        self.ui_file_name = "simTIMS.ui"
        # 子窗口ui文件路径
        self.header_window_ui_name = "setHeaderWindow.ui"
        self.recv_detail_ui_name = "recvMsgDetailWindow.ui"

        self.header_csv_path = ""
        # self.send_csv_path = os.path.join(self.base_path, self.cfg_dir_name, "send_thms.csv")
        self.send_csv_path = ""
        self.recv_csv_path = ""

        self.local_ip_a = ""
        self.local_port_a = ""

        self.peer_ip_a = ""
        self.peer_port_a = ""
        self.peer_ip_b = ""
        self.peer_port_b = ""

        # 运行时状态
        self.is_running = False
        self.network_mode = "dual"

        self.send_socket_a = None
        self.send_socket_b = None

        self.recv_socket = None
        self.udp_send_socket_action_a = None
        self.udp_send_socket_action_b = None

        self.udp_recv_socket_action_a = None
        self.udp_recv_socket_action_b = None

        self.sender_thread_a = None
        self.sender_thread_b = None

        self.sender_worker_a= None
        self.sender_worker_b= None

        self.receiver_thread_a: Optional[UdpReceiverThread] = None
        self.receiver_thread_b: Optional[UdpReceiverThread] = None

        self.receive_count = 0
        self.send_count = 0

        self.start_datetime = None
        self.time_generator = None

        self.sub_header_window = None

        '''类对象'''
        self.pack_action = MsgPackAction()

        '''加载主窗口UI文件'''
        loader = QUiLoader()
        ui_file_path = os.path.join(self.base_path, self.ui_dir_name, self.ui_file_name)
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.OpenModeFlag.ReadOnly)
        print(ui_file_path)
        self.main_ui = loader.load(ui_file)
        ui_file.close()

        # 初始化控件状态与信号
        self.setup_ui_logic()
        self.main_ui.show()

    '''窗口ui逻辑初始化'''
    def setup_ui_logic(self):
        try:
            # 本地通信ip地址初始化
            self.init_local_ip_from_cards()
            # 网络模式选择框初始化
            self.init_network_mode_combox()

            # “发送计数”和“接收计数”文本框初始显示为0
            if hasattr(self.main_ui, "sndCountLineEdit"):
                self.main_ui.sndCountLineEdit.setText("0")
            if hasattr(self.main_ui, "revCountLineEdit"):
                self.main_ui.revCountLineEdit.setText("0")
            # 发送文本框和接收文本框清空
            if hasattr(self.main_ui, "sendMsgTree"):
                self.main_ui.sendMsgTree.clear()
            if hasattr(self.main_ui, "recvMsgTableWidget"):
                self.main_ui.recvMsgTableWidget.setRowCount(0)
                self.main_ui.recvMsgTableWidget.setColumnCount(1)
                self.main_ui.recvMsgTableWidget.setWordWrap(True)
            # 绑定按钮信号槽
            self.init_ui_singnal()
            # ui元素状态初始化，恢复为未连接状态
            self.set_disconnect_ui_state()
            # 初始默认双网模式
            self.main_ui.networkModeComboBox.setCurrentIndex(1)

        except Exception as exc:
            print(f"初始化UI逻辑时出错: {exc}")
            # 如果GUI不可用，至少显示错误信息
            try:
                QMessageBox.critical(self.main_ui, "错误", f"程序启动失败:\n{exc}")
            except:
                print(f"程序启动失败: {exc}")

    '''初始化ui元素信号槽'''
    def init_ui_singnal(self):
        # '选择头部结构'按钮
        if hasattr(self.main_ui, "openHeaderFilePushBtn"):
            self.main_ui.openHeaderFilePushBtn.clicked.connect(self.select_header_csv)
        # ‘设置头部’按钮
        if hasattr(self.main_ui, "setHeaderPushBtn"):
            self.main_ui.setHeaderPushBtn.clicked.connect(self.set_header_btn_cilcked)
        # '连接'按钮
        if hasattr(self.main_ui, "connBtn"):
            self.main_ui.connBtn.clicked.connect(self.start_trdp)
        # '断开'按钮
        if hasattr(self.main_ui, "disconnBtn"):
            self.main_ui.disconnBtn.clicked.connect(self.stop_trdp)
        # '选择数据结构'按钮，选择发送消息的结构csv文件
        if hasattr(self.main_ui, "openMsgFilePushBtn"):
            self.main_ui.openMsgFilePushBtn.clicked.connect(self.open_file)
        # '加载'按钮
        if hasattr(self.main_ui, "loadStructPushButton"):
            self.main_ui.loadStructPushButton.clicked.connect(self.load_snd_custom_data)
        # 发送按钮关联信号
        if hasattr(self.main_ui, "sendMsgBtn"):
            self.main_ui.sendMsgBtn.clicked.connect(self.send_message)
        # 持续发送复选框
        if hasattr(self.main_ui, "keepSndCheckBox"):
            self.main_ui.keepSndCheckBox.checkStateChanged.connect(self.interval_send_check)
        # 时间自增字段
        if hasattr(self.main_ui, "dateTimeLineEdit"):
            self.main_ui.dateTimeLineEdit.editingFinished.connect(self.get_start_datetime)

        # 清空接收按钮
        if hasattr(self.main_ui, "ClearRecvTablePushButton"):
            self.main_ui.ClearRecvTablePushButton.clicked.connect(self.clear_recv)
        # 双击时，弹出选中行的对应解析窗口
        if hasattr(self.main_ui, "recvMsgTableWidget"):
            self.main_ui.recvMsgTableWidget.doubleClicked.connect(self.recv_msg_parse)
        # '选择数据结构'按钮，选择接收消息的结构csv文件
        if hasattr(self.main_ui, "openRecvMsgFilePushButton"):
            self.main_ui.openRecvMsgFilePushButton.clicked.connect(self.open_file)
        # 选择单双网
        if hasattr(self.main_ui, "networkModeComboBox"):
            self.main_ui.networkModeComboBox.currentIndexChanged.connect(self.network_mode_changed_action)


    '''点击‘连接’按钮关联的处理'''
    def start_trdp(self):
        if self.is_running:
            return
        try:
            self.create_recv_socket(self.network_mode)
            self.create_send_socket(self.network_mode)

            # 使能ui
            self.set_connect_ui_state()
            print(f"TRDP已启动，监听 {self.local_ip_a}:{self.local_port_a}")

        except Exception as exc:
            if hasattr(self.main_ui, "statusbar"):
                self.main_ui.statusbar.showMessage("启动失败")
            QMessageBox.critical(self.main_ui, "启动失败", f"无法启动TRDP: {exc}")
            print(f"启动TRDP失败: {exc}")

    '''点击‘断开’按钮关联的处理'''
    def stop_trdp(self):
        if not self.is_running:
            return
        print("开始停止连接...")
        try:
            self.stop_recv_socket(self.network_mode)
            # 停止发送工作对象和线程
            self.stop_interval_send()
            self.is_running = False
            self.start_datetime = None
            if self.time_generator and self.time_generator._running:
                self.time_generator.stop()

            # ui界面部分置灰
            self.set_disconnect_ui_state()
        except Exception as exc:
            print(f"停止连接时出现严重错误：{exc}")
            # QMessageBox.warning(self.main_ui, "停止异常", f"停止TRDP时出现问题: {exc}")

    '''设置ui界面为连接状态'''
    def set_connect_ui_state(self):
        '''更新UI状态'''
        if hasattr(self.main_ui, "connBtn"):
            self.main_ui.connBtn.setEnabled(False)
        if hasattr(self.main_ui, "disconnBtn"):
            self.main_ui.disconnBtn.setEnabled(True)

        self.update_connect_status(True)
        # 单双网通信参数组件不可编辑
        if hasattr(self.main_ui, "localIpAComboBox"):
            self.main_ui.localIpAComboBox.setEnabled(False)
        if hasattr(self.main_ui, "localPortALineEdit"):
            self.main_ui.localPortALineEdit.setEnabled(False)
        if hasattr(self.main_ui, "peerIpALineEdit"):
            self.main_ui.peerIpALineEdit.setEnabled(False)
        if hasattr(self.main_ui, "peerPortALineEdit"):
            self.main_ui.peerPortALineEdit.setEnabled(False)
        if hasattr(self.main_ui, "localIpBComboBox"):
            self.main_ui.localIpBComboBox.setEnabled(False)
        if hasattr(self.main_ui, "localPortBLineEdit"):
            self.main_ui.localPortBLineEdit.setEnabled(False)
        if hasattr(self.main_ui, "peerIpBLineEdit"):
            self.main_ui.peerIpBLineEdit.setEnabled(False)
        if hasattr(self.main_ui, "peerPortBLineEdit"):
            self.main_ui.peerPortBLineEdit.setEnabled(False)

        #  发送按钮置为可用
        if hasattr(self.main_ui, "sendMsgBtn"):
            self.main_ui.sendMsgBtn.setEnabled(True)
        # 选择网卡下拉框使能
        if hasattr(self.main_ui, "networkModeComboBox"):
            self.main_ui.networkModeComboBox.setEnabled(False)
        # 持续发送复选框使能
        if hasattr(self.main_ui, "keepSndCheckBox"):
            self.main_ui.keepSndCheckBox.setEnabled(True)
        # 时间字段可编辑
        if hasattr(self.main_ui, "dateTimeLineEdit"):
            self.main_ui.dateTimeLineEdit.setEnabled(False)

    '''设置ui界面为未连接状态'''
    def set_disconnect_ui_state(self):
        # 恢复UI状态
        try:
            if hasattr(self.main_ui, "connBtn"):
                self.main_ui.connBtn.setEnabled(True)
            if hasattr(self.main_ui, "disconnBtn"):
                self.main_ui.disconnBtn.setEnabled(False)
            self.update_connect_status(False)

            if hasattr(self.main_ui, "localIpAComboBox"):
                self.main_ui.localIpAComboBox.setEnabled(True)
            if hasattr(self.main_ui, "localPortALineEdit"):
                self.main_ui.localPortALineEdit.setEnabled(True)
            if hasattr(self.main_ui, "peerIpALineEdit"):
                self.main_ui.peerIpALineEdit.setEnabled(True)
            if hasattr(self.main_ui, "peerPortALineEdit"):
                self.main_ui.peerPortALineEdit.setEnabled(True)
            if hasattr(self.main_ui, "localIpBComboBox"):
                self.main_ui.localIpBComboBox.setEnabled(True)
            if hasattr(self.main_ui, "localPortBLineEdit"):
                self.main_ui.localPortBLineEdit.setEnabled(True)
            if hasattr(self.main_ui, "peerIpBLineEdit"):
                self.main_ui.peerIpBLineEdit.setEnabled(True)
            if hasattr(self.main_ui, "peerPortBLineEdit"):
                self.main_ui.peerPortBLineEdit.setEnabled(True)
            # 发送按钮置灰
            if hasattr(self.main_ui, "sendMsgBtn"):
                self.main_ui.sendMsgBtn.setEnabled(False)

            # 单双网选项表使能
            if hasattr(self.main_ui, "networkModeComboBox"):
                self.main_ui.networkModeComboBox.setEnabled(True)
            # # B网通信参数不可见
            # self.set_com_layout_visible(False)

            # 持续发送复选框使能
            if hasattr(self.main_ui, "keepSndCheckBox"):
                self.main_ui.keepSndCheckBox.setEnabled(False)
            # 时间字段可编辑
            if hasattr(self.main_ui, "dateTimeLineEdit"):
                self.main_ui.dateTimeLineEdit.setEnabled(True)

        except Exception as exc:
            print(f"恢复UI状态时出错：{exc}")

    '''接收消息区域显示处理'''
    @Slot(bytes, tuple)
    def on_udp_data_received(self, data: bytes, addr):
        # 格式化显示
        try:
            if hasattr(self.main_ui, "hexDisplayCheckBox"):
                if self.main_ui.hexDisplayCheckBox.isChecked():
                    text = data.hex(" ")
                else:
                    text = data.decode("utf-8", errors="ignore")

            current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")
            table_row_content = f"[{current_time}][接收来自:{addr}]->{text}"
            tale_row_item = QTableWidgetItem(table_row_content)

            if hasattr(self.main_ui, "recvMsgTableWidget"):
                row_count = self.main_ui.recvMsgTableWidget.rowCount()
                self.main_ui.recvMsgTableWidget.insertRow(row_count)
                self.main_ui.recvMsgTableWidget.setItem(row_count, 0, tale_row_item)
                self.main_ui.recvMsgTableWidget.resizeColumnsToContents()
            # 计数
            self.receive_count += 1
            if hasattr(self.main_ui, "revCountLineEdit"):
                self.main_ui.revCountLineEdit.setText(str(self.receive_count))
        except Exception as exc:
            # 安静失败，避免阻断接收
            print(f"处理接收数据时出错: {exc}")

    '''更新连接状态'''
    def update_connect_status(self, status: bool):
        try:
            if status:
                if hasattr(self.main_ui, "conRadioBtn") and hasattr(self.main_ui, "disconRadioBtn"):
                    self.main_ui.conRadioBtn.setChecked(True)
            else:
                if hasattr(self.main_ui, "conRadioBtn") and hasattr(self.main_ui, "disconRadioBtn"):
                    self.main_ui.disconRadioBtn.setChecked(True)
        except Exception as e:
            print(f"更新连接状态时出错: {e}")

    '''按钮点击信号槽：选择存储头部数据结构的csv文件'''
    def select_header_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self.main_ui, "选择文件", "", "所有文件 (*.csv)")
        if file_path and hasattr(self.main_ui, "headerFilePathLabel"):
            self.main_ui.headerFilePathLabel.setText(file_path)
            self.header_csv_path = file_path
            self.header_data = None
            self.header_data_diff = None
        else:
            QMessageBox.warning(self.main_ui, "注意", "请检查！未成功选择任何文件！")

    '''点击"打开"按钮关联的处理，只能打开csv文件或.py文件。选择py文件则自动跳过解析。'''
    def open_file(self):
        sender = self.sender()
        file_path, _ = QFileDialog.getOpenFileName(self.main_ui, "选择文件", "", "所有文件 (*.csv)")
        if sender.objectName() == "openMsgFilePushBtn":
            if file_path and hasattr(self.main_ui, "msgFilePathLabel"):
                self.main_ui.msgFilePathLabel.setText(file_path)
                self.send_csv_path = file_path
            else:
                QMessageBox.warning(self.main_ui, "注意", "请检查！未成功选择任何文件！")
        elif sender.objectName() == "openRecvMsgFilePushButton":
            if file_path and hasattr(self.main_ui, "recvMsgFilePathLabel"):
                self.main_ui.recvMsgFilePathLabel.setText(file_path)
                self.recv_csv_path = file_path
            else:
                QMessageBox.warning(self.main_ui, "注意", "请检查！未成功选择任何文件！")

    '''点击‘发送’按钮关联的处理'''
    def send_message(self):
        # send_interval_flag = self.main_ui.keepSndCheckBox.isChecked()
        if self.time_generator is not None:
            self.time_generator.start()
            self.change_time(self.time_generator)

        # 每次时间更新后，重新打包消息
        self.pack_msg()
        # self.msg = self.pack_action.pack_msg(self.header_data, self.send_custom_data)
        # msg = self.pack_action.pack_msg(self.header_data, self.send_custom_data)
        # 只有不在持续发送的时候，才会进行单次发送
        # if not send_interval_flag:
        self.udp_send_socket_action_a.udp_single_sender(self.send_socket_a, self.msg)
        if self.network_mode == "dual":
            self.udp_send_socket_action_b.udp_single_sender(self.send_socket_b, self.msg_diff)
        # 发送计数
        self.update_send_count()

    '''IP地址校验'''
    def is_valid_ipv4(self, ip: str):
        pattern = re.compile(
            r'^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        if pattern.match(ip):
            return True
        else:
            return False

    '''加载发送信号区，从cvs读取自定义消息结构并加载'''
    def load_snd_custom_data(self):
        if hasattr(self.main_ui, "sendMsgTree"):
            self.main_ui.sendMsgTree.clear()
            # lines = self.read_send_csv(self.send_csv_path)
            # 调整列宽
            self.main_ui.sendMsgTree.setColumnCount(5)
            self.main_ui.sendMsgTree.setColumnWidth(0, 70)
            self.main_ui.sendMsgTree.setColumnWidth(1, 100)
            self.main_ui.sendMsgTree.setColumnWidth(2, 50)
            self.main_ui.sendMsgTree.setColumnWidth(3, 50)

            self.send_custom_data = ReadCsv().read_msg_csv(self.send_csv_path)

            items = []
            for key, values in self.send_custom_data.items():
                content = [key]
                # parent_data = []
                sub_data = []

                if len(values) == 3:
                    parent_data = values
                else:
                    parent_data = values[:-1]
                    sub_data = values[-1]

                for value in parent_data:
                    content.append(value)
                item = QTreeWidgetItem(content)
                items.append(item)

                if len(sub_data) > 0:
                    for k, v in sub_data.items():
                        child_data = [k]
                        for value in v:
                            child_data.append(value)
                        child_item = QTreeWidgetItem(child_data)
                        item.addChild(child_item)

            self.main_ui.sendMsgTree.insertTopLevelItems(0, items)
            self.main_ui.sendMsgTree.doubleClicked.connect(self.double_click_edit_msg_tree)
            self.main_ui.sendMsgTree.itemChanged.connect(self.set_custom_data)
        else:
            QMessageBox.critical(self.main_ui, "错误！", "发送面板初始化失败！")

    '''
    双击发送区信号槽：双击后可编辑赋值列
    '''
    def double_click_edit_msg_tree(self):
        item = self.main_ui.sendMsgTree.currentItem()
        # parent = item.parent()
        # print("双击")
        # 第二列定义为可输入值的列
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.main_ui.sendMsgTree.editItem(item, 4)

    '''
    接收消息区，双击单个消息信号槽：解析对应的一条消息到具体字段
    '''
    def recv_msg_parse(self):
        # try:
        current_item = self.main_ui.recvMsgTableWidget.currentItem()
        recv_msg_list = current_item.text().strip().split("->")[-1].split(" ")
        print(f"recv_msg: {recv_msg_list}, length: {len(recv_msg_list)}")

        self.recv_dataset = ReadCsv().read_msg_csv(self.recv_csv_path)
        print(f"recv_dataset: {self.recv_dataset}")
        # 打开窗口
        recv_detail_ui_path = os.path.join(self.base_path, self.ui_dir_name, self.recv_detail_ui_name)
        self.recv_detail_window = self.setup_sub_window(recv_detail_ui_path)
        self.recv_detail_window.show()
        # 窗口加载数据
        self.load_recv_detail(recv_msg_list)

        # except Exception as exc:
        #     print(exc)

    '''点击设置头部按钮信号槽'''
    def set_header_btn_cilcked(self):
        header_ui_path = os.path.join(self.base_path, self.ui_dir_name, self.header_window_ui_name)
        self.sub_header_window = self.setup_sub_window(header_ui_path)
        self.sub_header_window.show()
        # 窗口加载头部数据结构
        self.load_header_structure()

    ''' 加载子窗口UI并显示窗口，返回ui对象'''
    def setup_sub_window(self, path):
        loader = QUiLoader()
        sub_ui_file = QFile(path)
        sub_ui_file.open(QFile.OpenModeFlag.ReadOnly)
        print(path)
        sub_ui = loader.load(sub_ui_file)
        sub_ui_file.close()
        return sub_ui

    '''在设置头部子窗口中从csv加载数据结构'''
    def load_header_structure(self):
        if hasattr(self.sub_header_window, "headerTreeWidget"):
            self.sub_header_window.headerTreeWidget.clear()
            # 调整界面列宽
            self.sub_header_window.headerTreeWidget.setColumnCount(5)
            self.sub_header_window.headerTreeWidget.setColumnWidth(0, 150)
            self.sub_header_window.headerTreeWidget.setColumnWidth(1, 150)
            self.sub_header_window.headerTreeWidget.setColumnWidth(2, 60)
            self.sub_header_window.headerTreeWidget.setColumnWidth(3, 200)
            self.sub_header_window.headerTreeWidget.setColumnWidth(4, 60)

            try:
                if self.header_data == None:
                    if self.header_csv_path != '':
                        self.header_data = ReadCsv().read_header_csv(self.header_csv_path)
                        print('csv_data', self.header_data)
                    # print(f"self.header_data = {self.header_data}")

                for index, (key, values) in enumerate(self.header_data.items()):
                    content = [key]
                    for value in values:
                        content.append(str(value))
                    # 头部数据结构插入一列，用于标识comboBox的索引值
                    # values.append(0)
                    # print(f"values append combo opt: {values}")

                    # 创建treewidgetitem对象并追加插入行
                    item = QTreeWidgetItem(content)
                    self.sub_header_window.headerTreeWidget.insertTopLevelItem(index, item)

                    # 创建comboBox对象
                    combo_box = QComboBox()
                    combo_box.addItems(self.header_options_text)
                    # 对comboBox当前选项按照已存的消息值进行更新
                    # print(f"key:{key},values[3]:{values[3]}")
                    combo_box.setCurrentIndex(int(values[3]))
                    # 对treewidget的第四列插入comboBox元素
                    self.sub_header_window.headerTreeWidget.setItemWidget(item, 4, combo_box)
                    # comboBox选项改变时触发信号，设置接收槽
                    combo_box.activated.connect(self.set_header_data_option)
                    # 数据长度字段名下拉列表添加字段名
                    self.sub_header_window.dataLengthComboBox.addItem(str(key))
                    # B网差异字段下拉列表添加字段名
                    if hasattr(self.sub_header_window, "fieldNameComboBox"):
                        self.sub_header_window.fieldNameComboBox.addItem(str(key))

                    # else:
                    #     for index, (key, values) in enumerate(self.header_data.items()):
                    #         content = [key]
                    #         for value in values:
                    #             content.append(str(value))
                    # # print(f"self.header_data = {self.header_data}")

                # 关联双击编辑信号槽
                self.sub_header_window.headerTreeWidget.doubleClicked.connect(self.double_click_edit_header_tree)
                # 数据改变时信号槽
                if hasattr(self.sub_header_window, "headerTreeWidget"):
                    self.sub_header_window.headerTreeWidget.itemChanged.connect(self.set_header_data)

                if hasattr(self.sub_header_window, "dataLengthComboBox"):
                    self.sub_header_window.dataLengthComboBox.currentIndexChanged.connect(self.get_msg_length_option)
                if hasattr(self.sub_header_window, "fieldValueLineEdit") and hasattr(self.sub_header_window, "fieldNameComboBox"):
                    if self.network_mode == "dual":
                        self.header_data_diff = self.header_data
                        self.sub_header_window.fieldValueLineEdit.setEnabled(True)
                        self.sub_header_window.fieldNameComboBox.setEnabled(True)
                        self.sub_header_window.fieldValueLineEdit.textChanged.connect(self.set_header_data)
                    else:
                        self.sub_header_window.fieldValueLineEdit.setEnabled(False)
                        self.sub_header_window.fieldNameComboBox.setEnabled(False)
            except Exception as exc:
                print(f"加载头部数据时发生错误：{exc}")

    def double_click_edit_header_tree(self):
        current_item = self.sub_header_window.headerTreeWidget.currentItem()
        item_row_number = self.sub_header_window.headerTreeWidget.indexOfTopLevelItem(current_item)
        cb_widget = self.sub_header_window.headerTreeWidget.itemWidget(current_item, 4)
        cb_index = cb_widget.currentIndex()
        if cb_index != 0:
            current_item.setForeground(3, QBrush(Qt.gray))
            current_item.setBackground(3, QBrush(QColor(220, 220, 220)))
            current_item.setFlags(current_item.flags() & ~Qt.ItemIsEditable)
            print(f"{item_row_number}-{cb_index} - 单元格不可编辑")
        else:
            # self.sub_header_window.headerTreeWidget.openPersistentEditor(current_item, 3)
            current_item.setForeground(3, QBrush())
            current_item.setBackground(3, QBrush())
            current_item.setFlags(current_item.flags() | Qt.ItemIsEditable)
            self.sub_header_window.headerTreeWidget.editItem(current_item, 3)
            print(f"{item_row_number}-{cb_index} - 单元格可编辑")

    def set_header_data(self, item):
        # 消息头保存数据
        if item is not None and type(item) is QTreeWidgetItem:
            row = self.sub_header_window.headerTreeWidget.indexOfTopLevelItem(item)
            value = item.text(3).strip()
            print(f"修改行{row}，更新值{value}")
            print(f"开始修改A网消息头...")

            for index, key in enumerate(self.header_data):
                if index == row:
                    self.header_data[key][2] = value
            print(f"A网消息头修改完成...")

        if self.network_mode == "dual":
            diff_value = self.sub_header_window.fieldValueLineEdit.text().strip()
            diff_row = self.sub_header_window.fieldNameComboBox.currentIndex() - 1
            print(f"已选择差异行{diff_row}，差异值{diff_value}")
            self.header_data_diff = copy.deepcopy(self.header_data)
            # 差异化数据赋值
            if diff_value != '' and diff_row is not None:
                print(f"开始修改B网消息头...")
                for index, key in enumerate(self.header_data_diff):
                    if index == diff_row:
                        self.header_data_diff[key][2] = diff_value
                print(f"B网消息头修改完成...")
            print(f"A网消息头：{self.header_data}")
            print(f"B网消息头：{self.header_data_diff}")

    def set_custom_data(self, current_item):
        # current_item = self.main_ui.sendMsgTree.currentItem()
        parent = current_item.parent()
        item_text_after_edit = current_item.text(4)

        if parent:
            # 获取当前父节点行
            parent_index = self.main_ui.sendMsgTree.indexOfTopLevelItem(parent)
            # 如果存在父节点，则获取当前子节点行
            child_index = parent.indexOfChild(current_item)
            print(f"父节点行：{parent_index}，子节点行：{child_index}，编辑后文本：{item_text_after_edit}")
        else:
            parent_index = self.main_ui.sendMsgTree.indexOfTopLevelItem(current_item)

        for index, (key, values) in enumerate(self.send_custom_data.items()):
            if index == parent_index:
                print(f"开始保存数据...")
                if parent and len(values) >4:
                    for sub_index, (sub_key, sub_values) in enumerate(values[4].items()):
                        if sub_index == child_index:
                            sub_values[3] = item_text_after_edit
                else:
                    # print("[2].", self.send_custom_data[key][3], item_text_after_edit)
                    if str(values[3]) == item_text_after_edit:
                        print("文本无变化！")
                    else:
                        values[3] = item_text_after_edit
                print(f"修改后的数据: {values}")
                break

    def set_header_data_option(self):
        # 接收传递的对象
        cb = self.sender()
        if not isinstance(cb, QComboBox):
            return

        cb_index = cb.currentIndex()
        current_item = self.sub_header_window.headerTreeWidget.currentItem()
        item_row_number = self.sub_header_window.headerTreeWidget.indexOfTopLevelItem(current_item)
        print(f"cb_index: {cb_index}, row:{item_row_number}")

        for index, (key, values) in enumerate(self.header_data.items()):
            if index == item_row_number:
                if values[3] != cb_index:
                    values[3] = cb_index
                else:
                    print("Combo Box 选项无变化！")
            # print(f"values: {values}")

    def get_msg_length_option(self):
        # index = self.sub_header_window.dataLengthComboBox.currentIndex()
        combobox_current_text = self.sub_header_window.dataLengthComboBox.currentText()
        tree_items = self.sub_header_window.headerTreeWidget.findItems(combobox_current_text, Qt.MatchFixedString, 0)
        tree_item_text = tree_items[0].text(3)
        try:
            length = int(tree_item_text) if len(tree_items)==1 else 0
            print(f"length: {length}")
            self.pack_action.set_defined_msg_length(length)
        except ValueError as e:
            QMessageBox.critical(self.sub_header_window, "错误", f"从头部数据查找消息长度发生错误：{e}")
            print(f"从头部数据查找消息长度发生错误：{e}")

    def clear_recv(self):
        if hasattr(self.main_ui, "recvMsgTableWidget"):
            row_count = self.main_ui.recvMsgTableWidget.rowCount()
            print(f"row_count: {row_count}")
            self.main_ui.recvMsgTableWidget.setRowCount(0)

    '''周期发送消息'''
    def send_msg_interval(self):
        print("开始持续发送")
        if self.time_generator is not None:
            self.time_generator.start()
            self.change_time(self.time_generator)

        self.pack_msg()

        interval_time = int(self.main_ui.intervalLineEdit.text()) * 0.001    #可以放进创建发送线程里
        print(f"发送间隔: {interval_time}")
        # if self.sender_thread and self.sender_thread.isRunning():
        #     print("发送线程已启动！")
        #     return
        if self.sender_worker_a and hasattr(self.sender_worker_a, "_running") and self.sender_worker_a._running:
            print("发送线程已启动！")
            return
        # 创建发送线程
        self.create_send_socket_worker(interval_time)

    # 更新全局计数和界面显示
    def update_send_count(self):
        count = self.send_count
        count += 1
        print(f"更新发送计数：{count}")
        if hasattr(self.main_ui, "sndCountLineEdit"):
            self.main_ui.sndCountLineEdit.setText(str(count))
            print(f"UI计数已更新为：{count}")
        self.send_count = count

    # def get_send_count(self):
    #     return self.send_count

    def stop_interval_send(self):
        '''停止发送对象'''
        if self.sender_worker_a:
            print("停止发送工作对象...")
            try:
                self.sender_worker_a.stop()
            except Exception as exc:
                print(f"停止发送工作对象时出错：{exc}")
            self.sender_worker_a = None
        '''停止发送线程'''
        if self.sender_thread_a is not None:
            print("停止发送线程...")
            try:
                self.sender_thread_a.quit()
                if not self.sender_thread_a.wait(2000):
                    self.sender_thread_a.terminate()
                    self.sender_thread_a.wait(1000)
            except Exception as exc:
                print(f"停止发送线程时出错：{exc}")
            self.sender_thread_a = None
        '''停止发送对象'''
        if self.sender_worker_b:
            print("停止发送工作对象...")
            try:
                self.sender_worker_b.stop()
            except Exception as exc:
                print(f"停止发送工作对象时出错：{exc}")
            self.sender_worker_b = None
        '''停止发送线程'''
        if self.sender_thread_b is not None:
            print("停止发送线程...")
            try:
                self.sender_thread_b.quit()
                if not self.sender_thread_b.wait(2000):
                    self.sender_thread_b.terminate()
                    self.sender_thread_b.wait(1000)
            except Exception as exc:
                print(f"停止发送线程时出错：{exc}")
            self.sender_thread_b = None

    def interval_send_check(self):
        check_state = self.main_ui.keepSndCheckBox.isChecked() if hasattr(self.main_ui, "keepSndCheckBox") else False
        if check_state:
            # pack_Action = MsgPackAction()
            # self.send_msg_interval()

            interval_time = int(self.main_ui.intervalLineEdit.text()) * 0.001  # 可以放进创建发送线程里
            print(f"发送间隔: {interval_time}")

            if self.sender_worker_a and hasattr(self.sender_worker_a, "_running") and self.sender_worker_a._running:
                print("发送线程已启动！")
            else:
                # 创建发送线程
                self.create_send_socket_worker(interval_time)
            # 单次发送按钮禁用
            if hasattr(self.main_ui, "sendMsgBtn"):
                self.main_ui.sendMsgBtn.setEnabled(False)
        else:
            self.stop_interval_send()
            if hasattr(self.main_ui, "sendMsgBtn"):
                self.main_ui.sendMsgBtn.setEnabled(True)

    def load_recv_detail(self, recv_list):
        if hasattr(self.recv_detail_window, "recvMsgTree"):
            self.recv_detail_window.recvMsgTree.clear()
            # 调整列宽
            self.recv_detail_window.recvMsgTree.setColumnCount(5)
            self.recv_detail_window.recvMsgTree.setColumnWidth(0, 100)
            self.recv_detail_window.recvMsgTree.setColumnWidth(1, 150)
            self.recv_detail_window.recvMsgTree.setColumnWidth(2, 60)
            self.recv_detail_window.recvMsgTree.setColumnWidth(3, 150)
            self.recv_detail_window.recvMsgTree.setColumnWidth(4, 60)

            print(f"recv_list: {recv_list}, length: {len(recv_list)}")
            for index, (key, values) in enumerate(self.recv_dataset.items()):
                print(f"开始处理recv_list第{index+40}个元素{recv_list[index + 40]}，填入values第{index}行")
                # if len(values) == 4:
                values[3] = recv_list[index + 40]
                content = [key]
                content.extend(values[0:4])
                print(f"开始创造主行treewidgetitem对象，填入主行内容{content}")
                # 创建treewidgetitem对象并追加插入行
                item = QTreeWidgetItem(content)
                if len(values) == 5:
                    print(f"values包含自节点，开始将recv_list第{index+40}个元素{recv_list[index + 40]}，转换为二进制{format(int(recv_list[index + 40], 16), '08b')}")
                    bit_list = list(format(int(recv_list[index + 40], 16), '08b'))
                    print(f"bit_list: {bit_list}")
                    for sub_index, (sub_key, sub_values) in enumerate(values[-1].items()):
                        # sub_values[3] = bit_list[len(bit_list) - sub_index - 1] if sub_index <= len(bit_list) else 0
                        sub_values[3] = bit_list[sub_index]
                        sub_content = [sub_key]
                        sub_content.extend(sub_values[0:4])
                        child_item = QTreeWidgetItem(sub_content)
                        item.addChild(child_item)
                # print(values)
                self.recv_detail_window.recvMsgTree.insertTopLevelItem(index, item)

    # 初始化，获取本机所有ipv4地址
    def init_local_ip_from_cards(self):
        self.ipv4_info = []
        # 获取所有网卡信息
        addrs = psutil.net_if_addrs()
        # 获取所有网卡状态
        stats = psutil.net_if_stats()

        for interface_name, addrs in addrs.items():
            for addr in addrs:
                interface_stat = stats.get(interface_name).isup
                ip_family = addr.family
                # print(f"获取到网卡：{interface_name}, 状态：{interface_stat}。ip_family: {ip_family},addr: {addr}")
                if ip_family == 2 and interface_stat: # 判断是ipv4且网卡为启用状态，显示在下拉框中
                    self.ipv4_info.append([addr.address, interface_name])
        # print(f"ipv4_info: {self.ipv4_info}")
        # return self.ipv4_info
        if hasattr(self.main_ui, "localIpAComboBox") and hasattr(self.main_ui, "localIpBComboBox"):
            for i in range(len(self.ipv4_info)):
                self.main_ui.localIpAComboBox.addItem(f"[{i}] {self.ipv4_info[i][0]}({self.ipv4_info[i][1]})")
                self.main_ui.localIpBComboBox.addItem(f"[{i}] {self.ipv4_info[i][0]}({self.ipv4_info[i][1]})")

    # 通信B网参数设置组件隐藏或显示
    def set_com_layout_visible(self, flag):
        print(f"开始设置B网参数组件显示状态...")
        if hasattr(self.main_ui, "comBHoriLayout"):
            # print(f"设置显示flag为：{flag}")
            if flag:
                for i in range(self.main_ui.comBHoriLayout.count()):
                    widget = self.main_ui.comBHoriLayout.itemAt(i).widget()
                    if widget:
                        widget.show()
            else:
                for i in range(self.main_ui.comBHoriLayout.count()):
                    widget = self.main_ui.comBHoriLayout.itemAt(i).widget()
                    if widget:
                        widget.hide()
            print(f"B网参数组件显示状态完成设置")

    def network_mode_changed_action(self):
        if hasattr(self.main_ui, "networkModeComboBox"):
            '''判断当前选择的网络模式是单网还是双网'''
            self.network_mode = "dual" if self.main_ui.networkModeComboBox.currentIndex() == 1 else "single"
            # 组件状态显示隐藏
            is_show = True if self.main_ui.networkModeComboBox.currentIndex() == 1 else False
            self.set_com_layout_visible(is_show)

    def init_network_mode_combox(self):
        if hasattr(self.main_ui, "networkModeComboBox"):
            self.main_ui.networkModeComboBox.clear()
            self.main_ui.networkModeComboBox.addItems(["单网模式", "双网模式"])

    def create_recv_socket(self, network_mode="single"):
        self.udp_recv_socket_action_a = SocketAction()
        # 读取本机IP-a与端口a
        if hasattr(self.main_ui, "localIpAComboBox") and hasattr(self.main_ui, "localPortALineEdit"):
            local_ip_a = self.main_ui.localIpAComboBox.currentText().strip().split(' ')[1].split('(')[0]
            local_port_a = self.main_ui.localPortALineEdit.text().strip()
            if self.is_valid_ipv4(local_ip_a) and local_port_a != '':
                self.local_ip_a = local_ip_a
                self.local_port_a = int(local_port_a)
                self.udp_recv_socket_action_a.set_local_ip_a(self.local_ip_a)
                self.udp_recv_socket_action_a.set_local_port_a(self.local_port_a)
            else:
                QMessageBox.critical(self.main_ui, "错误", f"本地ip地址不正确或port为空！")

        '''创建并绑定接收UDP套接字（TRDP通常基于UDP）'''
        self.recv_socket_a = self.udp_recv_socket_action_a.create_udp_recv_socket()
        # self.is_running = True
        # 启动接收线程
        self.receiver_thread_a = UdpReceiverThread(self.recv_socket_a)
        self.receiver_thread_a.data_received.connect(self.on_udp_data_received)
        self.receiver_thread_a.start()

        if network_mode == "dual":
            self.udp_recv_socket_action_b = SocketAction()
            # 读取本机IP-b与端口b
            if hasattr(self.main_ui, "localIpBComboBox") and hasattr(self.main_ui, "localPortBLineEdit"):
                local_ip_b = self.main_ui.localIpBComboBox.currentText().strip().split(' ')[1].split('(')[0]
                local_port_b = self.main_ui.localPortBLineEdit.text().strip()
                if self.is_valid_ipv4(local_ip_b) and local_port_b != '':
                    self.local_ip_b = local_ip_b
                    self.local_port_b = int(local_port_b)
                    self.udp_recv_socket_action_b.set_local_ip_a(self.local_ip_b)
                    self.udp_recv_socket_action_b.set_local_port_a(self.local_port_b)
                else:
                    QMessageBox.critical(self.main_ui, "错误", f"本地ip地址不正确或port为空！")

            '''创建并绑定接收UDP套接字（TRDP通常基于UDP）'''
            self.recv_socket_b = self.udp_recv_socket_action_b.create_udp_recv_socket()
            # 启动接收线程
            self.receiver_thread_b = UdpReceiverThread(self.recv_socket_b)
            self.receiver_thread_b.data_received.connect(self.on_udp_data_received)
            self.receiver_thread_b.start()
        self.is_running = True

    def stop_recv_socket(self, mode):
        # 停止A网接收线程
        if self.receiver_thread_a is not None:
            print("停止接收线程...")
            self.receiver_thread_a.stop()
            # 关闭socket以打断阻塞的recvfrom
            if self.udp_recv_socket_action_a is not None:
                try:
                    self.udp_recv_socket_action_a.safe_close_socket()
                except Exception as exc:
                    print(f"关闭接收socket时出错：{exc}")
            # 等待线程结束，但不强制等待
            if not self.receiver_thread_a.wait(1000):
                print("接收线程未在2s内结束，强制终止")
                self.receiver_thread_a.terminate()
                self.receiver_thread_a.wait(1000)
            self.receiver_thread_a = None
        # 关闭接收socket_action
        if self.udp_recv_socket_action_a is not None:
            try:
                # 若线程已关闭仍未关闭socket，则关闭
                self.udp_recv_socket_action_a.safe_close_socket()
            except Exception as exc:
                print(f"关闭接收socket action时出错：{exc}")
            self.udp_recv_socket_action_a = None

        if mode == "dual":
            # 停止接收线程
            if self.receiver_thread_b is not None:
                print("停止接收线程...")
                self.receiver_thread_b.stop()
                # 关闭socket以打断阻塞的recvfrom
                if self.udp_recv_socket_action_b is not None:
                    try:
                        self.udp_recv_socket_action_b.safe_close_socket()
                    except Exception as exc:
                        print(f"关闭接收socket时出错：{exc}")
                # 等待线程结束，但不强制等待
                if not self.receiver_thread_b.wait(2000):
                    print("接收线程未在2s内结束，强制终止")
                    self.receiver_thread_b.terminate()
                    self.receiver_thread_b.wait(1000)
                self.receiver_thread_b = None
            # 关闭接收socket_action
            if self.udp_recv_socket_action_b is not None:
                try:
                    # 若线程已关闭仍未关闭socket，则关闭
                    self.udp_recv_socket_action_b.safe_close_socket()
                except Exception as exc:
                    print(f"关闭接收socket action时出错：{exc}")
                self.udp_recv_socket_action_b = None

    def create_send_socket(self, mode):
        '''创建并绑定A网发送UDP'''
        self.udp_send_socket_action_a = SocketAction()
        # 读取对端IP与端口
        if hasattr(self.main_ui, "peerIpALineEdit") and hasattr(self.main_ui, "peerPortALineEdit"):
            peer_ip = self.main_ui.peerIpALineEdit.text().strip()
            peer_port = self.main_ui.peerPortALineEdit.text().strip()
            if self.is_valid_ipv4(peer_ip) and peer_port != '':
                # self.peer_ip_a = peer_ip
                # self.peer_port_a = int(peer_port)
                self.udp_send_socket_action_a.set_peer_ip_a(peer_ip)
                self.udp_send_socket_action_a.set_peer_port_a(int(peer_port))
            else:
                QMessageBox.critical(self.main_ui, "错误", f"对端ip地址不正确或port为空！")
        self.send_socket_a = self.udp_send_socket_action_a.create_udp_sender_socket()

        if mode == "dual":
            '''创建并绑定B网发送UDP'''
            self.udp_send_socket_action_b = SocketAction()
            # 读取对端IP与端口
            if hasattr(self.main_ui, "peerIpBLineEdit") and hasattr(self.main_ui, "peerPortBLineEdit"):
                peer_ip = self.main_ui.peerIpBLineEdit.text().strip()
                peer_port = self.main_ui.peerPortBLineEdit.text().strip()
                if self.is_valid_ipv4(peer_ip) and peer_port != '':
                    # self.peer_ip_b = peer_ip
                    # self.peer_port_b = int(peer_port)
                    self.udp_send_socket_action_b.set_peer_ip_a(peer_ip)
                    self.udp_send_socket_action_b.set_peer_port_a(int(peer_port))
                else:
                    QMessageBox.critical(self.main_ui, "错误", f"对端ip地址不正确或port为空！")
            self.send_socket_b = self.udp_send_socket_action_b.create_udp_sender_socket()

    def create_send_socket_worker(self, interval):
        try:
            # 创建A网发送的socket
            # self.send_socket_a = self.udp_send_socket_action_a.create_udp_sender_socket()
            # print(f"创建发送socket：{self.send_socket_a}")
            # 创建发送工作对象
            # self.sender_worker_a = UdpSenderWorker([self.send_socket_a, self.peer_ip_a, self.peer_port_a], self.msg, self.send_count,
            #                                        interval)
            self.pack_msg()
            self.sender_worker_a = UdpSenderWorker(self.udp_send_socket_action_a, self.send_socket_a, self.msg, interval)

            print(f"创建发送工作对象：{self.sender_worker_a}")
            # 创建新线程
            self.sender_thread_a = QThread()
            print(f"创建发送线程：{self.sender_thread_a}")
            # 将工作对象移送到线程中
            self.sender_worker_a.moveToThread(self.sender_thread_a)
            # 连接信号槽
            self.sender_thread_a.started.connect(self.sender_worker_a.run)
            if self.time_generator is not None:
                self.sender_thread_a.started.connect(self.time_generator.start)
                # 发送消息前信号接收槽
                self.sender_worker_a.data_send_before.connect(partial(self.change_time, self.time_generator))
                self.sender_worker_a.data_send_before.connect(self.pack_msg)
                # self.sender_worker_a.data_send_before.connect(partial(self.sender_worker_a.update_msg, self.msg))
                self.sender_worker_a.data_send_before.connect(lambda: self.sender_worker_a.update_msg(self.msg))

            # 发送消息后更新计数信号接收槽
            self.sender_worker_a.data_send.connect(self.update_send_count)
            # 线程结束信号槽
            self.sender_worker_a.finished.connect(self.sender_thread_a.quit)
            self.sender_worker_a.finished.connect(self.sender_worker_a.deleteLater)
            self.sender_thread_a.finished.connect(self.sender_thread_a.deleteLater)
            print("准备启动A网发送线程...")
            # 启动线程
            self.sender_thread_a.start()
            print("A网发送线程已启动...")

            if self.network_mode == "dual":
                # 创建A网发送的socket
                # self.send_socket_b = self.udp_send_socket_action_a.create_udp_sender_socket()
                # print(f"创建发送socket：{self.send_socket_a}")
                # 创建发送工作对象
                self.sender_worker_b = UdpSenderWorker(self.udp_send_socket_action_b, self.send_socket_b, self.msg_diff, interval)
                print(f"创建发送工作对象：{self.sender_worker_b}")
                # 创建新线程
                self.sender_thread_b = QThread()
                print(f"创建发送线程：{self.sender_thread_b}")
                # 将工作对象移送到线程中
                self.sender_worker_b.moveToThread(self.sender_thread_b)
                # 连接信号槽
                self.sender_thread_b.started.connect(self.sender_worker_b.run)
                # self.sender_thread_b.started.connect(self.time_generator.start)
                if self.time_generator is not None:
                    # 发送消息前信号接收槽
                    self.sender_worker_b.data_send_before.connect(partial(self.change_time, self.time_generator))
                    # self.sender_worker_b.data_send_before.connect(self.pack_msg)
                    # self.sender_worker_b.data_send_before.connect(partial(self.sender_worker_a.update_msg, self.msg))
                    # 上边这个方法partial传参会在partial写下的时候就将self.msg值固定，后续connect不会再读取新的msg内容
                    self.sender_worker_b.data_send_before.connect(lambda: self.sender_worker_b.update_msg(self.msg_diff))

                # self.sender_worker_b.data_send.connect(self.update_send_count)
                self.sender_worker_b.finished.connect(self.sender_thread_b.quit)
                self.sender_worker_b.finished.connect(self.sender_worker_b.deleteLater)
                self.sender_thread_b.finished.connect(self.sender_thread_b.deleteLater)
                print("准备启动B网发送线程...")
                # 启动线程
                self.sender_thread_b.start()
                print("B网发送线程已启动...")
        except Exception as e:
            QMessageBox.critical(self.main_ui,"错误", f"启动发送线程时发生错误：{e}")

    def get_start_datetime(self):
        self.start_datetime = [0] * 6
        self.time_offset = self.main_ui.dateTimeLineEdit.text().split(',')
        if len(self.time_offset) == 2 and (int(self.time_offset[1]) - int(self.time_offset[0]) == 5):
            i = 0
            for key, value in self.send_custom_data.items():
                if int(key) - int(self.time_offset[0]) - i == 0 and int(key) <= int(self.time_offset[1]):
                    if value[3] != '':
                        self.start_datetime[i] = int(value[3])
                        i += 1
                    else:
                        self.start_datetime = [datetime.datetime.now().year%2000, datetime.datetime.now().month, datetime.datetime.now().day
                            , datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second]
                        break
                elif int(key) > int(self.time_offset[1]):
                    break
            self.time_generator = AutoTimeGenerator(1, self.start_datetime)
        print(f"获取起始时间为：{self.start_datetime}")

    # @Slot(AutoTimeGenerator)
    def change_time(self, timer):
        if hasattr(self.main_ui, "sendMsgTree"):
            timelist = timer.get_time_list()
            for i in range(int(self.time_offset[0]), int(self.time_offset[1])+1):
                item = QTreeWidget.topLevelItem(self.main_ui.sendMsgTree, i)
                # item.setFlags(item.flags() | Qt.ItemIsEditable)
                # self.main_ui.sendMsgTree.itemChanged.disconnect(self.set_custom_data)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                # self.main_ui.sendMsgTree.double_click_edit_msg_tree
                item.setText(4, str(timelist[i - 6]))
                # self.main_ui.sendMsgTree.itemChanged.connect(self.set_custom_data)

        # # 如果持续发送
        # if hasattr(self.main_ui, "keepSndCheckBox") and self.main_ui.keepSndCheckBox.isChecked():
        #     # 打包消息完成后，发出信号，更新发送线程里的消息
        #     self.pack_action.msg_ready.connect(self.sender_worker_a.update_msg)
        #     # 如果是双网模式的话，更新B网发送线程里的消息
        #     if self.network_mode == "dual":
        #         self.pack_action.msg_ready.connect(self.sender_worker_b.update_msg)

    # def set_head_diff_fieldvalue(self):
        # value = self.sub_header_window.fieldValueLineEdit.text().strip()
        # row = self.sub_header_window.fieldNameComboBox.CurrentIndex()
        # if value is not None or row is not None:
        #     if value <= 255:
        # self.set_header_data(self.sub_header_window.fieldValueLineEdit)
        #     else:
        #         QMessageBox.critical(self.sub_header_window, "Error", "输入值不可大于256！")
        # else:
        #     QMessageBox.critical(self.sub_header_window, "Error", "差异字段不可为空且输入值不可为空！")

    def pack_msg(self):
        print(f"信号触发打包数据")
        print(f"开始打包数据...")
        self.msg, self.msg_diff = self.pack_action.pack_msg(self.header_data, self.send_custom_data, self.header_data_diff)
        # seq打包完成信号接收槽
        self.pack_action.seq_ready.connect(self.set_head_seq)
        print(f"开始数据打包结束...")
        # if self.network_mode == "dual":
        #     print(f"开始打包B网数据...")
        #     self.msg_diff = self.pack_action.pack_msg(self.header_data_diff, self.send_custom_data)
        #     print(f"B网数据打包结束...")
        print(f"A网数据：{self.msg}")
        print(f"B网数据：{self.msg_diff}")

    def set_head_seq(self, seq, row):
        if hasattr(self.sub_header_window, "headerTreeWidget"):
            item = self.sub_header_window.headerTreeWidget.topLevelItem(row)
            # 对value列进行更新
            item.setText(3, str(seq))
