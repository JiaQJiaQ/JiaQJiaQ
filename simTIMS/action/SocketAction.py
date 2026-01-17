import socket
from argparse import Action
from typing import Optional
import socket
import netifaces

from action.MsgPackAction import MsgPackAction


class SocketAction():
    def __init__(self):
        super().__init__()

    def create_udp_recv_socket(self):
        """
        创建并绑定一个UDP套接字到指定的本地地址与端口。
        返回已绑定的socket对象，调用方负责关闭。
        """
        self.udp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 某些平台不支持或语义不同，仅在存在该选项时设置
        reuseport_opt = getattr(socket, "SO_REUSEPORT", None)
        if reuseport_opt is not None:
            try:
                self.udp_recv_socket.setsockopt(socket.SOL_SOCKET, reuseport_opt, 1)
            except Exception:
                # 忽略设置失败
                pass
        self.udp_recv_socket.bind((self.local_ip_a, self.local_port_a))
        return self.udp_recv_socket

    def create_udp_sender_socket(self):
        self.udp_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        return self.udp_send_socket

    def safe_close_socket(self) -> None:
        """安全关闭socket，忽略关闭过程中的异常。"""
        if hasattr(self, 'udp_recv_socket') and self.udp_recv_socket is None:
            try:
                self.udp_recv_socket.close()
                self.udp_recv_socket = None
            except Exception as e:
                print(f"关闭socket时出错：{e}")

    # 根据选择的网卡，设置绑定发送的IP地址
    def set_local_ip_a(self, ip):
        self.local_ip_a = ip

    def set_local_port_a(self, port):
        self.local_port_a = port

    def set_local_ip_b(self, ip):
        self.local_ip_b = ip

    def set_local_port_b(self, port):
        self.local_port_b = port

    def set_peer_ip_a(self, ip):
        self.peer_ip_a = ip

    def set_peer_port_a(self, port):
        self.peer_port_a = port

    def set_peer_ip_b(self, ip):
        self.peer_ip_b = ip

    def set_peer_port_b(self, port):
        self.peer_port_b = port

    def set_comid(self, comid):
        self.comid = comid

    # def set_send_interval(self, send_interval):
    #     self.send_interval = send_interval

    # 设置选定的网卡，并设置ip地址
    def set_network_interface(self, selected_interface):
        self.network_interface = selected_interface
        ip_addresses = netifaces.ifaddresses(self.network_interface)
        self.local_ip_a = ip_addresses[netifaces.AF_INET][0]['addr']

    # 发送一次数据
    def udp_single_sender(self, socket, msg):
        # msg = "010203040506070809111213141516171819212223242526272829"
        socket.sendto(msg, (self.peer_ip_a, self.peer_port_a))
        print(f"发送一次消息:{self.peer_ip_a}[{self.peer_port_a}]!")
