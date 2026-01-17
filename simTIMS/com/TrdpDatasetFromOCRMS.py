#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCRMS到CCU的TRDP数据集结构
基于图片中的字段定义创建Python类
"""

import struct
from typing import List
from enum import IntEnum


class SelfTestResult(IntEnum):
    """自检结果枚举"""
    NOT_SELF_TESTED = 1
    SELF_TESTING = 2
    SELF_TEST_SUCCESSFUL = 3
    SELF_TEST_FAILURE = 4


class AlarmSeverity(IntEnum):
    """告警严重程度枚举"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TRDPDatasetFromOCRMS:
    """
    OCRMS到CCU的TRDP数据集类
    包含OCRMS生命信号、系统状态、自检结果、模块故障标志、序列号等信息
    """
    
    def __init__(self):
        """初始化TRDP数据集，设置默认值"""
        
        # OCRMS生命信号 (字节0-3) - 4个8位无符号整数
        self.life_signal_hh = 0  # OCRMS Life Signal HH (High High)
        self.life_signal_hl = 0  # OCRMS Life Signal HL (High Low)
        self.life_signal_lh = 0  # OCRMS Life Signal LH (Low High)
        self.life_signal_ll = 0  # OCRMS Life Signal LL (Low Low)
        
        # OCRMS请求和系统状态信号 (字节4) - 位级别定义
        self.power_on_request_received = False  # b7: Power ON OCRMS request received
        self.ocrms_on_system_state = False      # b6: OCRMS ON system state
        self.power_off_request_received = False # b5: Power OFF OCRMS request received
        self.ocrms_off_system_state = False     # b4: OCRMS OFF system state
        self.reserved_b3 = False                # b3: 保留位
        self.reserved_b2 = False                # b2: 保留位
        self.reserved_b1 = False                # b1: 保留位
        self.reserved_b0 = False                # b0: 保留位
        
        # 保留字节 (字节5)
        self.reserved_byte_5 = 0
        
        # 自检结果 (字节6)
        self.self_test_result = SelfTestResult.NOT_SELF_TESTED
        
        # 模块故障标志 (字节7) - 位级别定义
        self.reserved_b7 = False                # b7: 保留位
        self.arcing_detection_failure = False   # b6: E002 - Arcing detection module failure
        self.video_surveillance_failure = False # b5: E003 - Video surveillance module failure
        self.temperature_detection_failure = False # b4: E004 - Temperature detection module failure
        self.geometric_parameters_failure = False # b3: E005 - Geometric parameters module failure
        self.left_vibration_compensation_failure = False # b2: E006 - Left vibration compensation device failure
        self.right_vibration_compensation_failure = False # b1: E007 - Right vibration compensation device failure
        self.ocrms_software_failure = False     # b0: E008 - OCRMS software failure
        
        # 序列号 (字节8-37)
        self.arcing_detection_sn = [0] * 5      # 字节8-12: 电弧检测模块序列号
        self.video_surveillance_sn = [0] * 5    # 字节13-17: 视频监控模块序列号
        self.temperature_detection_sn = [0] * 5 # 字节18-22: 温度检测模块序列号
        self.geometric_parameters_sn = [0] * 5  # 字节23-27: 几何参数模块序列号
        self.left_vibration_compensation_sn = [0] * 5  # 字节28-32: 左振动补偿设备序列号
        self.right_vibration_compensation_sn = [0] * 5 # 字节33-37: 右振动补偿设备序列号
        
        # 缺陷类ID (字节38-39) - 16位无符号整数
        self.defect_class_id = [0] * 2
        
        # 告警严重程度 (字节40)
        self.alarm_severity = AlarmSeverity.LOW

        # 保留字节 (字节41)
        self.reserved_byte_41 = 0
        
        # 保留字节 (字节38-40)
        self.reserved_bytes_38_40 = [0] * 3
        
        # 告警位置 (字节42-45) - 32位无符号整数，单位mm
        self.alarm_location = [0] * 4
        
        # 轨道电路 (字节46-51) - 6字节ASCII字符串
        self.track_circuit = [0] * 6
        
        # 磨损值 (字节52-53) - 16位无符号整数，100=1
        self.wearing_value = [0] * 2
        
        # 告警位置PMD (字节54-56) - 24位无符号整数，单位mm
        self.alarm_location_pmd = 0
        
        # 轨道电路PMD (字节57-62) - 6字节ASCII字符串
        self.track_circuit_pmd = [0] * 6
        
        # 软件版本 (字节63-64)
        self.software_version_high = 0  # Software Version H: 1~99
        self.software_version_low = 0   # Software Version L: 1~99
        
        # 保留字节 (字节65-99)
        self.reserved_bytes_65_99 = [0] * 35
    
    def get_byte_4_flags(self) -> int:
        """获取字节4的OCRMS请求和系统状态标志"""
        flags = 0
        if self.power_on_request_received:
            flags |= 0x80  # b7
        if self.ocrms_on_system_state:
            flags |= 0x40  # b6
        if self.power_off_request_received:
            flags |= 0x20  # b5
        if self.ocrms_off_system_state:
            flags |= 0x10  # b4
        if self.reserved_b3:
            flags |= 0x08  # b3
        if self.reserved_b2:
            flags |= 0x04  # b2
        if self.reserved_b1:
            flags |= 0x02  # b1
        if self.reserved_b0:
            flags |= 0x01  # b0
        return flags
    
    def get_byte_7_flags(self) -> int:
        """获取字节7的模块故障标志"""
        flags = 0
        if self.reserved_b7:
            flags |= 0x80  # b7
        if self.arcing_detection_failure:
            flags |= 0x40  # b6
        if self.video_surveillance_failure:
            flags |= 0x20  # b5
        if self.temperature_detection_failure:
            flags |= 0x10  # b4
        if self.geometric_parameters_failure:
            flags |= 0x08  # b3
        if self.left_vibration_compensation_failure:
            flags |= 0x04  # b2
        if self.right_vibration_compensation_failure:
            flags |= 0x02  # b1
        if self.ocrms_software_failure:
            flags |= 0x01  # b0
        return flags
    
    def to_bytes(self) -> bytes:
        """将数据集转换为字节数组"""
        data = bytearray(100)  # 100字节的数据集
        
        # OCRMS生命信号 (字节0-3)
        data[0] = self.life_signal_hh
        data[1] = self.life_signal_hl
        data[2] = self.life_signal_lh
        data[3] = self.life_signal_ll
        
        # OCRMS请求和系统状态 (字节4)
        data[4] = self.get_byte_4_flags()
        
        # 保留字节 (字节5)
        data[5] = self.reserved_byte_5
        
        # 自检结果 (字节6)
        data[6] = self.self_test_result
        
        # 模块故障标志 (字节7)
        data[7] = self.get_byte_7_flags()
        
        # 电弧检测模块序列号 (字节8-12)
        for i, val in enumerate(self.arcing_detection_sn):
            data[8 + i] = val
        
        # 视频监控模块序列号 (字节13-17)
        for i, val in enumerate(self.video_surveillance_sn):
            data[13 + i] = val
        
        # 温度检测模块序列号 (字节18-19)
        for i, val in enumerate(self.temperature_detection_sn):
            data[18 + i] = val
        
        # 几何参数模块序列号 (字节20-24)
        for i, val in enumerate(self.geometric_parameters_sn):
            data[20 + i] = val
        
        # 左振动补偿设备序列号 (字节25-29)
        for i, val in enumerate(self.left_vibration_compensation_sn):
            data[25 + i] = val
        
        # 右振动补偿设备序列号 (字节30-34)
        for i, val in enumerate(self.right_vibration_compensation_sn):
            data[30 + i] = val
        
        # 缺陷类ID (字节35-36)
        for i, val in enumerate(self.defect_class_id):
            data[35 + i] = val
        
        # 告警严重程度 (字节37)
        data[37] = self.alarm_severity
        
        # 保留字节 (字节38-40)
        for i, val in enumerate(self.reserved_bytes_38_40):
            data[38 + i] = val
        
        # 保留字节 (字节41)
        data[41] = self.reserved_byte_41
        
        # 告警位置 (字节42-45)
        for i, val in enumerate(self.alarm_location):
            data[42 + i] = val
        
        # 轨道电路 (字节46-51)
        for i, val in enumerate(self.track_circuit):
            data[46 + i] = val
        
        # 磨损值 (字节52-53)
        for i, val in enumerate(self.wearing_value):
            data[52 + i] = val
        
        # 告警位置PMD (字节54-56) - 24位无符号整数
        # 使用3字节存储24位无符号整数
        alarm_location_bytes = struct.pack('<I', self.alarm_location_pmd)[:3]
        for i, val in enumerate(alarm_location_bytes):
            data[54 + i] = val
        
        # 轨道电路PMD (字节57-62)
        for i, val in enumerate(self.track_circuit_pmd):
            data[57 + i] = val
        
        # 软件版本 (字节63-64)
        data[63] = self.software_version_high
        data[64] = self.software_version_low
        
        # 保留字节 (字节65-99)
        for i, val in enumerate(self.reserved_bytes_65_99):
            data[65 + i] = val
        
        return bytes(data)
    
    def from_bytes(self, data: bytes):
        """从字节数组解析数据集"""
        if len(data) < 100:
            raise ValueError("数据长度不足100字节")
        
        # OCRMS生命信号 (字节0-3)
        self.life_signal_hh = data[0]
        self.life_signal_hl = data[1]
        self.life_signal_lh = data[2]
        self.life_signal_ll = data[3]
        
        # OCRMS请求和系统状态 (字节4)
        flags_4 = data[4]
        self.power_on_request_received = bool(flags_4 & 0x80)
        self.ocrms_on_system_state = bool(flags_4 & 0x40)
        self.power_off_request_received = bool(flags_4 & 0x20)
        self.ocrms_off_system_state = bool(flags_4 & 0x10)
        self.reserved_b3 = bool(flags_4 & 0x08)
        self.reserved_b2 = bool(flags_4 & 0x04)
        self.reserved_b1 = bool(flags_4 & 0x02)
        self.reserved_b0 = bool(flags_4 & 0x01)
        
        # 保留字节 (字节5)
        self.reserved_byte_5 = data[5]
        
        # 自检结果 (字节6)
        self.self_test_result = SelfTestResult(data[6])
        
        # 模块故障标志 (字节7)
        flags_7 = data[7]
        self.reserved_b7 = bool(flags_7 & 0x80)
        self.arcing_detection_failure = bool(flags_7 & 0x40)
        self.video_surveillance_failure = bool(flags_7 & 0x20)
        self.temperature_detection_failure = bool(flags_7 & 0x10)
        self.geometric_parameters_failure = bool(flags_7 & 0x08)
        self.left_vibration_compensation_failure = bool(flags_7 & 0x04)
        self.right_vibration_compensation_failure = bool(flags_7 & 0x02)
        self.ocrms_software_failure = bool(flags_7 & 0x01)
        
        # 电弧检测模块序列号 (字节8-12)
        self.arcing_detection_sn = list(data[8:13])
        
        # 视频监控模块序列号 (字节13-17)
        self.video_surveillance_sn = list(data[13:18])
        
        # 温度检测模块序列号 (字节18-19)
        self.temperature_detection_sn = list(data[18:20])
        
        # 几何参数模块序列号 (字节20-24)
        self.geometric_parameters_sn = list(data[20:25])
        
        # 左振动补偿设备序列号 (字节25-29)
        self.left_vibration_compensation_sn = list(data[25:30])
        
        # 右振动补偿设备序列号 (字节30-34)
        self.right_vibration_compensation_sn = list(data[30:35])
        
        # 缺陷类ID (字节35-36)
        self.defect_class_id = list(data[35:37])
        
        # 告警严重程度 (字节37)
        self.alarm_severity = AlarmSeverity(data[37])
        
        # 保留字节 (字节38-40)
        self.reserved_bytes_38_40 = list(data[38:41])
        
        # 保留字节 (字节41)
        self.reserved_byte_41 = data[41]
        
        # 告警位置 (字节42-45)
        self.alarm_location = list(data[42:46])
        
        # 轨道电路 (字节46-51)
        self.track_circuit = list(data[46:52])
        
        # 磨损值 (字节52-53)
        self.wearing_value = list(data[52:54])
        
        # 告警位置PMD (字节54-56) - 24位无符号整数
        alarm_location_pmd_bytes = data[54:57] + b'\x00'
        self.alarm_location_pmd = struct.unpack('<I', alarm_location_pmd_bytes)[0]
        
        # 轨道电路PMD (字节57-62)
        self.track_circuit_pmd = list(data[57:63])
        
        # 软件版本 (字节63-64)
        self.software_version_high = data[63]
        self.software_version_low = data[64]
        
        # 保留字节 (字节65-99)
        self.reserved_bytes_65_99 = list(data[65:100])
    
    def __str__(self) -> str:
        """返回数据集的字符串表示"""
        return f"""OCRMS到CCU的TRDP数据集:
            生命信号: HH={self.life_signal_hh}, HL={self.life_signal_hl}, LH={self.life_signal_lh}, LL={self.life_signal_ll}
            系统状态: 开启请求={self.power_on_request_received}, 开启状态={self.ocrms_on_system_state}
            自检结果: {self.self_test_result.name}
            缺陷类ID: {self.defect_class_id}
            告警严重程度: {self.alarm_severity.name}
            告警位置: {self.alarm_location}mm
            磨损值: {self.wearing_value}
            软件版本: {self.software_version_high}.{self.software_version_low}
            模块故障: 电弧检测={self.arcing_detection_failure}, 视频监控={self.video_surveillance_failure}, 温度检测={self.temperature_detection_failure}"""


def create_sample_dataset() -> TRDPDatasetFromOCRMS:
    """创建示例数据集"""
    dataset = TRDPDatasetFromOCRMS()
    
    # 设置示例值
    dataset.life_signal_hh = 123
    dataset.life_signal_hl = 45
    dataset.life_signal_lh = 67
    dataset.life_signal_ll = 89
    
    dataset.power_on_request_received = True
    dataset.ocrms_on_system_state = True
    
    dataset.self_test_result = SelfTestResult.SELF_TEST_SUCCESSFUL
    
    dataset.defect_class_id = 12345
    dataset.alarm_severity = AlarmSeverity.MEDIUM
    dataset.alarm_location = 1000000  # 1000米
    
    dataset.wearing_value = 500  # 5.0
    dataset.alarm_location_pmd = 2000000  # 2000米
    
    dataset.software_version_high = 1
    dataset.software_version_low = 23
    
    return dataset


if __name__ == "__main__":
    # 测试代码
    print("创建示例数据集...")
    sample_dataset = create_sample_dataset()
    print(sample_dataset)
    
    print("\n打包数据集...")
    packed_data = sample_dataset.to_bytes()
    print(f"打包后数据大小: {len(packed_data)} 字节")
    print(f"打包后数据: {packed_data.hex()}")
    
    print("\n解包数据集...")
    unpacked_dataset = TRDPDatasetFromOCRMS()
    unpacked_dataset.from_bytes(packed_data)
    print(unpacked_dataset)
    
    print("\n验证数据完整性...")
    print(f"数据大小正确: {len(packed_data) == 100}")
    print(f"数据内容一致: {sample_dataset.life_signal_hh == unpacked_dataset.life_signal_hh}")
