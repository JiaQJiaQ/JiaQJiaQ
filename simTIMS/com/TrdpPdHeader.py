#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRDP PD数据包头结构
基于图片中的字段定义创建Python类
"""

import struct
from typing import List
from enum import IntEnum
try:
    from action.Fcs32Calculator import Fcs32Calculator
except ImportError:
    from action.Fcs32Calculator import Fcs32Calculator


class MessageType(IntEnum):
    """消息类型枚举 - 基于TRDP协议规范"""
    # 使用ASCII编码，便于协议分析工具（如Wireshark）读取
    PD_REQUEST = 0x5072  # 'Pr' - PD Request
    PD_REPLY = 0x5070    # 'Pp' - PD Reply  
    PD_DATA = 0x5064     # 'Pd' - PD Data
    PD_DATA_ERROR = 0x5065  # 'Pe' - PD Data (Error) - 仅用于通知，不应在总线上发送


class TRDPPdHeader:
    """
    TRDP PD数据包头类
    包含协议版本、序列计数器、消息类型、通信ID等信息
    """
    
    def __init__(self):
        """初始化TRDP PD数据包头，设置默认值"""

        # 序列计数器 (字节0-3) - 32位无符号整数
        self.sequence_counter = [0] * 4  # Sequence Counter

        # 协议版本 (字节4-5) - 16位无符号整数
        self.protocol_version = [0] * 2  # Protocol Version

        # 消息类型 (字节6-7) - 16位无符号整数
        self.msg_type = MessageType.PD_DATA  # Message Type - 默认为PD Data

        # 通信ID (字节8-11) - 32位无符号整数
        self.com_id = [0] * 4  # Communication ID
        
        # ETB拓扑计数器 (字节12-15) - 32位无符号整数
        self.etb_topocnt = [0] * 4  # ETB Topology Counter
        
        # 操作列车拓扑计数器 (字节16-19) - 32位无符号整数
        self.op_trn_topocnt = [0] * 4  # Operational Train Topology Counter
        
        # 数据集长度 (字节20-23) - 32位无符号整数
        self.dataset_length = [0] * 4  # Dataset Length
        
        # 保留字节 (字节24-27) - 32位无符号整数
        self.reserved_bytes_20_23 = [0] * 4  # Reserved
        
        # 回复通信ID (字节28-31) - 32位无符号整数
        self.reply_com_id = [0] * 4  # Reply Communication ID
        
        # 回复IP地址 (字节32-35) - 32位无符号整数
        self.reply_ip_address = [0] * 4  # Reply IP Address
        
        # 头部FCS (字节36-39) - 32位无符号整数
        self.header_fcs = [0] * 4  # Header FCS (Frame Check Sequence)

    
    # ==================== GET方法 ====================
    
    def get_protocol_version(self) -> List[int]:
        """获取协议版本"""
        return self.protocol_version
    
    def get_sequence_counter(self) -> List[int]:
        """获取序列计数器"""
        return self.sequence_counter
    
    def get_msg_type(self) -> MessageType:
        """获取消息类型"""
        return self.msg_type
    
    def get_com_id(self) -> List[int]:
        """获取通信ID"""
        return self.com_id
    
    def get_etb_topocnt(self) -> List[int]:
        """获取ETB拓扑计数器"""
        return self.etb_topocnt
    
    def get_op_trn_topocnt(self) -> List[int]:
        """获取操作列车拓扑计数器"""
        return self.op_trn_topocnt
    
    def get_dataset_length(self) -> List[int]:
        """获取数据集长度"""
        return self.dataset_length
    
    def get_reserved_bytes_20_23(self) -> List[int]:
        """获取保留字节20-23"""
        return self.reserved_bytes_20_23
    
    def get_reply_com_id(self) -> List[int]:
        """获取回复通信ID"""
        return self.reply_com_id
    
    def get_reply_ip_address(self) -> List[int]:
        """获取回复IP地址"""
        return self.reply_ip_address
    
    def get_header_fcs(self) -> List[int]:
        """获取头部FCS"""
        return self.header_fcs
    
    # ==================== 辅助方法 ====================
    
    def get_protocol_version_str(self) -> str:
        """获取协议版本字符串表示"""
        return f"{self.protocol_version[1]}.{self.protocol_version[0]}"  # 主版本.子版本
    
    def get_sequence_counter_value(self) -> int:
        """获取序列计数器数值"""
        return (self.sequence_counter[0] + 
                (self.sequence_counter[1] << 8) + 
                (self.sequence_counter[2] << 16) + 
                (self.sequence_counter[3] << 24))
    
    def set_sequence_counter_value(self, value: int):
        """设置序列计数器数值"""
        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError(f"序列计数器值必须在0-4294967295范围内，当前值: {value}")
        self.sequence_counter[0] = value & 0xFF
        self.sequence_counter[1] = (value >> 8) & 0xFF
        self.sequence_counter[2] = (value >> 16) & 0xFF
        self.sequence_counter[3] = (value >> 24) & 0xFF
    
    def increment_sequence_counter(self):
        """递增序列计数器"""
        current_value = self.get_sequence_counter_value()
        self.set_sequence_counter_value((current_value + 1) % 0x100000000)
    
    def get_msg_type_ascii(self) -> str:
        """获取消息类型的ASCII表示"""
        return chr(self.msg_type >> 8) + chr(self.msg_type & 0xFF)
    
    # ==================== SET方法 ====================
    
    def set_protocol_version(self, value: List[int]):
        """设置协议版本"""
        if len(value) != 2:
            raise ValueError(f"协议版本长度必须为2，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"协议版本[{i}]必须在0-255范围内，当前值: {val}")
        self.protocol_version = value
    
    def set_sequence_counter(self, value: List[int]):
        """设置序列计数器"""
        if len(value) != 4:
            raise ValueError(f"序列计数器长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"序列计数器[{i}]必须在0-255范围内，当前值: {val}")
        self.sequence_counter = value
    
    def set_msg_type(self, value: MessageType):
        """设置消息类型"""
        self.msg_type = value
    
    def set_com_id(self, value: List[int]):
        """设置通信ID"""
        if len(value) != 4:
            raise ValueError(f"通信ID长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"通信ID[{i}]必须在0-255范围内，当前值: {val}")
        self.com_id = value
    
    def set_etb_topocnt(self, value: List[int]):
        """设置ETB拓扑计数器"""
        if len(value) != 4:
            raise ValueError(f"ETB拓扑计数器长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"ETB拓扑计数器[{i}]必须在0-255范围内，当前值: {val}")
        self.etb_topocnt = value
    
    def set_op_trn_topocnt(self, value: List[int]):
        """设置操作列车拓扑计数器"""
        if len(value) != 4:
            raise ValueError(f"操作列车拓扑计数器长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"操作列车拓扑计数器[{i}]必须在0-255范围内，当前值: {val}")
        self.op_trn_topocnt = value
    
    def set_dataset_length(self, value: List[int]):
        """设置数据集长度"""
        if len(value) != 4:
            raise ValueError(f"数据集长度字段长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"数据集长度[{i}]必须在0-255范围内，当前值: {val}")
        self.dataset_length = value
    
    def set_reserved_bytes_20_23(self, value: List[int]):
        """设置保留字节20-23"""
        if len(value) != 4:
            raise ValueError(f"保留字节20-23长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"保留字节20-23[{i}]必须在0-255范围内，当前值: {val}")
        self.reserved_bytes_20_23 = value
    
    def set_reply_com_id(self, value: List[int]):
        """设置回复通信ID"""
        if len(value) != 4:
            raise ValueError(f"回复通信ID长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"回复通信ID[{i}]必须在0-255范围内，当前值: {val}")
        self.reply_com_id = value
    
    def set_reply_ip_address(self, value: List[int]):
        """设置回复IP地址"""
        if len(value) != 4:
            raise ValueError(f"回复IP地址长度必须为4，当前长度: {len(value)}")
        for i, val in enumerate(value):
            if not 0 <= val <= 255:
                raise ValueError(f"回复IP地址[{i}]必须在0-255范围内，当前值: {val}")
        self.reply_ip_address = value
    
    def set_header_fcs(self):
        """设置头部FCS"""
        self.header_fcs = self.calculate_fcs()
    
    def to_bytes(self) -> bytes:
        """将数据包头转换为字节数组"""
        data = bytearray(40)  # 40字节的数据包头
        
        # 序列计数器 (字节0-3) - 4字节
        data[0:4] = self.sequence_counter
        
        # 协议版本 (字节4-5) - 2字节
        data[4:6] = self.protocol_version
        
        # 消息类型 (字节6-7) - 16位
        struct.pack_into('<H', data, 6, self.msg_type)
        
        # 通信ID (字节8-11) - 4字节
        data[8:12] = self.com_id
        
        # ETB拓扑计数器 (字节12-15) - 4字节
        data[12:16] = self.etb_topocnt
        
        # 操作列车拓扑计数器 (字节16-19) - 4字节
        data[16:20] = self.op_trn_topocnt
        
        # 数据集长度 (字节20-23) - 4字节
        data[20:24] = self.dataset_length
        
        # 保留字节 (字节24-27) - 4字节
        data[24:28] = self.reserved_bytes_20_23
        
        # 回复通信ID (字节28-31) - 4字节
        data[28:32] = self.reply_com_id
        
        # 回复IP地址 (字节32-35) - 4字节
        data[32:36] = self.reply_ip_address
        
        # 头部FCS (字节36-39) - 4字节
        data[36:40] = self.header_fcs
        
        return bytes(data)
    
    def from_bytes(self, data: bytes):
        """从字节数组解析数据包头"""
        if len(data) < 40:
            raise ValueError("Header数据长度不足40字节")
        
        # 序列计数器 (字节0-3) - 4字节
        self.sequence_counter = list(data[0:4])
        
        # 协议版本 (字节4-5) - 2字节
        self.protocol_version = list(data[4:6])
        
        # 消息类型 (字节6-7) - 16位
        self.msg_type = MessageType(struct.unpack('<H', data[6:8])[0])
        
        # 通信ID (字节8-11) - 4字节
        self.com_id = list(data[8:12])
        
        # ETB拓扑计数器 (字节12-15) - 4字节
        self.etb_topocnt = list(data[12:16])
        
        # 操作列车拓扑计数器 (字节16-19) - 4字节
        self.op_trn_topocnt = list(data[16:20])
        
        # 数据集长度 (字节20-23) - 4字节
        self.dataset_length = list(data[20:24])
        
        # 保留字节 (字节24-27) - 4字节
        self.reserved_bytes_20_23 = list(data[24:28])
        
        # 回复通信ID (字节28-31) - 4字节
        self.reply_com_id = list(data[28:32])
        
        # 回复IP地址 (字节32-35) - 4字节
        self.reply_ip_address = list(data[32:36])
        
        # 头部FCS (字节36-39) - 4字节
        self.header_fcs = list(data[36:40])
    
    def calculate_fcs(self) -> List[int]:
        """计算头部FCS (Frame Check Sequence)"""
        # 创建临时数据包头，FCS字段设为0
        temp_header = TRDPPdHeader()
        temp_header.protocol_version = self.protocol_version.copy()
        temp_header.sequence_counter = self.sequence_counter.copy()
        temp_header.msg_type = self.msg_type
        temp_header.com_id = self.com_id.copy()
        temp_header.etb_topocnt = self.etb_topocnt.copy()
        temp_header.op_trn_topocnt = self.op_trn_topocnt.copy()
        temp_header.dataset_length = self.dataset_length.copy()
        temp_header.reserved_bytes_20_23 = self.reserved_bytes_20_23.copy()
        temp_header.reply_com_id = self.reply_com_id.copy()
        temp_header.reply_ip_address = self.reply_ip_address.copy()
        temp_header.header_fcs = [0, 0, 0, 0]  # 设为0用于计算
        
        # 获取字节数据（前36字节，不包括FCS字段）
        header_bytes = temp_header.to_bytes()[:36]
        
        # 使用Fcs32Calculator计算FCS
        fcs_calculator = Fcs32Calculator()
        fcs_value = fcs_calculator.fcs32(header_bytes)
        
        # 将32位FCS值转换为4字节列表（小端序）
        fcs_bytes = list(struct.pack('<I', fcs_value))
        return fcs_bytes
    
    def update_fcs(self):
        """更新头部FCS"""
        self.header_fcs = self.calculate_fcs()
    
    def verify_fcs(self) -> bool:
        """验证头部FCS"""
        calculated_fcs = self.calculate_fcs()
        print("calculated_fcs:", calculated_fcs)
        print("header_fcs:", self.header_fcs)
        return calculated_fcs == self.header_fcs
    
    def __str__(self) -> str:
        """返回数据包头的字符串表示"""
        return f"""TRDP PD数据包头:
            协议版本: {self.get_protocol_version_str()} ({self.protocol_version})
            序列计数器: {self.get_sequence_counter_value()} ({self.sequence_counter})
            消息类型: {self.get_msg_type_ascii()} ({self.msg_type.name}, 0x{self.msg_type:04X})
            通信ID: {self.com_id}
            ETB拓扑计数器: {self.etb_topocnt}
            操作列车拓扑计数器: {self.op_trn_topocnt}
            数据集长度: {self.dataset_length} 字节
            回复通信ID: {self.reply_com_id}
            回复IP地址: {self.reply_ip_address}
            头部FCS: {self.header_fcs}
            FCS验证: {'通过' if self.verify_fcs() else '失败'}"""
