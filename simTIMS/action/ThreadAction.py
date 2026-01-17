import socket
import time
from PySide6.QtCore import QThread, Signal, QObject, Slot


class UdpReceiverThread(QThread):
    data_received = Signal(bytes, str, int)

    def __init__(self, udp_socket, parent = None, buffer_size=65535):
        super().__init__(parent)
        self._socket = udp_socket
        self.buffer_size = buffer_size
        self._running = True

    def run(self):
        while self._running:
            try:
                data, addr = self._socket.recvfrom(self.buffer_size)
                self.data_received.emit(data, addr[0], addr[1])
            except socket.timeout:
                continue
            except Exception:
                if not self._running:
                    break
                continue
        self._socket.close()
        print(f"UDP 接收线程已停止")

    def stop(self):
        self._running = False


class UdpSenderWorker(QObject):
    data_send_before = Signal()
    data_send = Signal()
    finished = Signal()
    def __init__(self, socket_action, socket_sender, msg, interval=1):
        super().__init__()
        # self._socket = socket_list[0]
        # self._ip = socket_list[1]
        # self._port = socket_list[2]
        self._socket_action = socket_action
        self._socket_sender = socket_sender

        self._msg = msg
        # self._send_cnt = send_cnt
        self._interval = interval
        self._running = True

    # 持续发送报文
    def run(self):
        print("UdpSenderWorker 开始运行")
        while self._running:
            try:
                # self.data_send.emit()
                # self._socket.sendto(self._msg, (self._ip, self._port))
                # self._send_cnt += 1
                #
                self.data_send_before.emit()
                print(f"线程{self._socket_sender} 发送数据：{self._msg}")
                self._socket_action.udp_single_sender(self._socket_sender, self._msg)
                self.data_send.emit()
                time.sleep(self._interval)
            except OSError as e:
                print(f"发送错误：{e}")
                break
            except Exception as e:
                print(f"其他错误：{e}")
                if not self._running:
                    break
                continue
        print("UdpSenderWorker 结束运行")
        self.finished.emit()

    def stop(self):
        print("停止UdpSenderWorker")
        self._running = False

    # @Slot(bytes)
    def update_msg(self, msg):
        # print(f"线程更新前的发送数据：{msg}")
        self._msg = msg
        print(f"线程更新后的发送数据：{self._msg}")
