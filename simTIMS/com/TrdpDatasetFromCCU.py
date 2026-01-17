#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRDP协议数据集结构
基于图片中的字段定义创建Python类
"""

import struct
from datetime import datetime
from typing import List, Optional


class TRDPDatasetFromCCU:
    """
    TRDP协议数据集类
    包含列车状态、时间、速度、乘客负载等信息
    """
    
    def __init__(self):
        """初始化TRDP数据集，设置默认值"""
        
        # Lifesign (字节 0-3) - 32位无符号整数
        self.lifesign = 0  # 生命信号，每100ms加1
        
        # 保留字节 (字节 4-5)
        self.reserved_byte_4 = 0
        self.reserved_byte_5 = 0
        
        # 日期时间 (字节 6-11)
        current_time = datetime.now()
        self.year = current_time.year - 2000  # 0=2000, 20-99
        self.month = current_time.month  # 1-12
        self.day = current_time.day  # 1-31
        self.hour = current_time.hour  # 0-23
        self.minute = current_time.minute  # 0-59
        self.second = current_time.second  # 0-59
        
        # 状态标志 (字节 12) - 位级别定义
        self.dt1_cab_activated = False  # b7: DT1驾驶室激活
        self.dt2_cab_activated = False  # b6: DT2驾驶室激活
        self.reserved_byte_12_bit_5 = False  # b5: 保留
        self.reserved_byte_12_bit_4 = False  # b4: 保留
        self.train_speed_valid = False  # b3: 列车速度有效 (1=有效, 0=无效)
        self.wheel_diameter_valid = False  # b2: 轮径有效 (1=有效, 0=无效)
        self.time_setting = False  # b1: 时间设置 (1=有效, 0=无效 3s脉冲)
        self.time_valid = False  # b0: 时间有效 (1=有效, 0=无效)

        # 车门命令 (字节 13) - 位级别定义
        self.backward = False  # b7: 向后
        self.forward = False  # b6: 向前
        self.reserved_byte_13_bit_5 = False  # b5: 保留
        self.left_door_open_command = False  # b4: 左门开启命令
        self.right_door_open_command = False  # b3: 右门开启命令
        self.left_door_close_command = False  # b2: 左门关闭命令
        self.right_door_close_command = False  # b1: 右门关闭命令
        self.all_door_closed = False  # b0: 所有门关闭

        # 列车ID (字节 14)
        self.train_id = 0

        # 保留字节 (字节 15)
        self.reserved_bytes_15 = [0]

        # 轮径 (字节 16-17) - 16位无符号整数
        self.wheel_diameter = 0  # 轮径值
        
        # 保留字节 (字节 18-21)
        self.reserved_bytes_18_21 = [0] * 4
        
        # 状态标志2 (字节 22) - 位级别定义
        self.reserved_bits_22 = [False] * 8  # b7-b0: 保留

        # 保留字节（字节23-31）
        self.reserved_bytes_23_31 = [0] * 9

        # 列车速度 (字节 32-33) - 16位无符号整数
        self.train_speed = 0  # 列车速度 (1=0.1km/h, 0~2000 = 0-200km/h)
        
        # 受电弓状态 (字节 34) - 位级别定义
        self.reserved_byte_34_bits_7_3 = [False] * 5  # b7-b3: 保留
        self.mp1_pantograph_status = False  # b2: Mp1受电弓状态 (0:降下 1:升起)
        self.mp2_pantograph_status = False  # b1: Mp2受电弓状态 (0:降下 1:升起)
        self.reserved_byte_34_bit_0 = False  # b0: 保留

        # 列车事件 (字节 35) - 位级别定义
        self.train_arrived = False  # b7: 列车到达
        self.skip_stop_announcement = False  # b6: 跳过停站广播
        self.reserved_byte_34_bits_5_0 = [False] * 6  # b5-b0: 保留
        
        # 保留字节 (字节 36-37)
        self.reserved_bytes_36_37 = [0] * 2
        
        # 乘客负载 (字节 38-43) - 6个车厢
        self.passenger_loading = [1] * 6  # 乘客负载 (1-6, 对应AW0-AW5)
        
        # 保留字节 (字节 44-47)
        self.reserved_bytes_44_47 = [0] * 4
        
        # 线路电压 (字节 48-49) - 16位无符号整数
        self.line_voltage = 0  # 线路电压 (1=1V, 0-65535V)
        
        # 线路电流 (字节 50-51) - 16位有符号整数
        self.line_current = 0  # 线路电流 (1=1A, -32768A~32767A)
        
        # 通用站台代码 (字节 52-53) - 16位无符号整数
        self.generic_station_code = 0  # 通用站台代码，(1010-1241)
        
        # 最终目的地代码 (字节 54-55) - 16位无符号整数
        self.final_destination_code = 0  # 最终目的地代码，(1010-1241)

        # 下一站代码 (字节 56-57) - 16位无符号整数
        self.next_station_code = 0  # 下一站代码，(1010-1241)

        # 保留字节（字节58-67）
        self.reserved_bytes_58_67 = [0] * 10

        # ocrms电源命令 (字节 68) - 位级别定义
        self.power_on_ocrm_request = False  # b7: 开启OCRMS请求 (0:无命令, 1:开启OCRMS)
        self.reserved_byte_68_bits_6_5 = [False] * 2
        self.power_off_ocrm_request = False  # b4: 关闭OCRMS请求 (0:无命令, 1:关闭OCRMS)
        self.reserved_byte_68_bits_3_0 = [False] * 4  # b3-b0: 保留
        
        # thms电源命令 (字节 69) - 位级别定义
        self.power_on_thms_request = False  # b7: 开启THMS请求 (0:无命令, 1:开启THMS)
        self.reserved_byte_69_bits_6_5 = [False] * 2
        self.power_off_thms_request = False  # b4: 关闭THMS请求 (0:无命令, 1:关闭THMS)
        self.reserved_byte_69_bits_0_3 = [False] * 4

        # 测试命令（字节70）
        self.reserved_byte_70_bits_7_2 = [False] * 6  # 其他保留位
        self.ocrm_test = False  # b1: OCRMS测试
        self.thms_static_test = False  # b0: THMS静态测试

        # 保留字节 (字节 71) - bool类型
        self.reserved_bytes_71 = [False]

        # 保留字节 (字节 72-99)
        self.reserved_bytes_72_99 = [0] * 28
    
    # ==================== GET方法 ====================
    
    def get_lifesign(self) -> int:
        """获取生命信号"""
        return self.lifesign
    
    def get_reserved_byte_4(self) -> int:
        """获取保留字节4"""
        return self.reserved_byte_4
    
    def get_reserved_byte_5(self) -> int:
        """获取保留字节5"""
        return self.reserved_byte_5
    
    def get_year(self) -> int:
        """获取年份 (0=2000, 20-99)"""
        return self.year
    
    def get_month(self) -> int:
        """获取月份 (1-12)"""
        return self.month
    
    def get_day(self) -> int:
        """获取日期 (1-31)"""
        return self.day
    
    def get_hour(self) -> int:
        """获取小时 (0-23)"""
        return self.hour
    
    def get_minute(self) -> int:
        """获取分钟 (0-59)"""
        return self.minute
    
    def get_second(self) -> int:
        """获取秒数 (0-59)"""
        return self.second
    
    def get_dt1_cab_activated(self) -> bool:
        """获取DT1驾驶室激活状态"""
        return self.dt1_cab_activated
    
    def get_dt2_cab_activated(self) -> bool:
        """获取DT2驾驶室激活状态"""
        return self.dt2_cab_activated
    
    def get_reserved_bit_5(self) -> bool:
        """获取保留位5"""
        return self.reserved_bit_5
    
    def get_reserved_bit_4(self) -> bool:
        """获取保留位4"""
        return self.reserved_bit_4
    
    def get_train_speed_valid(self) -> bool:
        """获取列车速度有效状态"""
        return self.train_speed_valid
    
    def get_wheel_diameter_valid(self) -> bool:
        """获取轮径有效状态"""
        return self.wheel_diameter_valid
    
    def get_time_setting(self) -> bool:
        """获取时间设置状态"""
        return self.time_setting
    
    def get_time_valid(self) -> bool:
        """获取时间有效状态"""
        return self.time_valid
    
    def get_backward(self) -> bool:
        """获取向后状态"""
        return self.backward
    
    def get_forward(self) -> bool:
        """获取向前状态"""
        return self.forward
    
    def get_reserved_bit_0(self) -> bool:
        """获取保留位0"""
        return self.reserved_bit_0
    
    def get_left_door_open_command(self) -> bool:
        """获取左门开启命令"""
        return self.left_door_open_command
    
    def get_right_door_open_command(self) -> bool:
        """获取右门开启命令"""
        return self.right_door_open_command
    
    def get_left_door_close_command(self) -> bool:
        """获取左门关闭命令"""
        return self.left_door_close_command
    
    def get_right_door_close_command(self) -> bool:
        """获取右门关闭命令"""
        return self.right_door_close_command
    
    def get_all_door_closed(self) -> bool:
        """获取所有门关闭状态"""
        return self.all_door_closed
    
    def get_train_id(self) -> int:
        """获取列车ID"""
        return self.train_id
    
    def get_reserved_bytes_15(self) -> List[int]:
        """获取保留字节15"""
        return self.reserved_bytes_15
    
    def get_wheel_diameter(self) -> int:
        """获取轮径值"""
        return self.wheel_diameter
    
    def get_reserved_bytes_18_21(self) -> List[int]:
        """获取保留字节18-21"""
        return self.reserved_bytes_18_21
    
    def get_reserved_bits_22(self) -> List[bool]:
        """获取保留位22"""
        return self.reserved_bits_22
    
    def get_reserved_bytes_23_31(self) -> List[int]:
        """获取保留字节23-31"""
        return self.reserved_bytes_23_31
    
    def get_train_speed(self) -> int:
        """获取列车速度 (1=0.1km/h, 0~2000 = 0-200km/h)"""
        return self.train_speed
    
    def get_reserved_bits_34(self) -> List[bool]:
        """获取保留位34"""
        return self.reserved_bits_34
    
    def get_mp1_pantograph_status(self) -> bool:
        """获取Mp1受电弓状态 (0:降下 1:升起)"""
        return self.mp1_pantograph_status
    
    def get_mp2_pantograph_status(self) -> bool:
        """获取Mp2受电弓状态 (0:降下 1:升起)"""
        return self.mp2_pantograph_status
    
    def get_reserved_bit_34_0(self) -> bool:
        """获取保留位34_0"""
        return self.reserved_bit_34_0
    
    def get_train_arrived(self) -> bool:
        """获取列车到达状态"""
        return self.train_arrived
    
    def get_skip_stop_announcement(self) -> bool:
        """获取跳过停站广播状态"""
        return self.skip_stop_announcement
    
    def get_reserved_bits_35(self) -> List[bool]:
        """获取保留位35"""
        return self.reserved_bits_35
    
    def get_reserved_bytes_36_37(self) -> List[int]:
        """获取保留字节36-37"""
        return self.reserved_bytes_36_37
    
    def get_passenger_loading(self) -> List[int]:
        """获取乘客负载 (1-6, 对应AW0-AW5)"""
        return self.passenger_loading
    
    def get_reserved_bytes_44_47(self) -> List[int]:
        """获取保留字节44-47"""
        return self.reserved_bytes_44_47
    
    def get_line_voltage(self) -> int:
        """获取线路电压 (1=1V, 0-65535V)"""
        return self.line_voltage
    
    def get_line_current(self) -> int:
        """获取线路电流 (1=1A, -32768A~32767A)"""
        return self.line_current
    
    def get_generic_station_code(self) -> int:
        """获取通用站台代码 (1010-1241)"""
        return self.generic_station_code
    
    def get_final_destination_code(self) -> int:
        """获取最终目的地代码 (1010-1241)"""
        return self.final_destination_code
    
    def get_next_station_code(self) -> int:
        """获取下一站代码 (1010-1241)"""
        return self.next_station_code
    
    def get_reserved_bytes_58_67(self) -> List[int]:
        """获取保留字节58-67"""
        return self.reserved_bytes_58_67
    
    def get_power_on_ocrm_request(self) -> bool:
        """获取开启OCRMS请求状态"""
        return self.power_on_ocrm_request
    
    def get_reserved_68_bits_6_6(self) -> List[bool]:
        """获取保留位68_6_6"""
        return self.reserved_68_bits_6_6
    
    def get_power_off_ocrm_request(self) -> bool:
        """获取关闭OCRMS请求状态"""
        return self.power_off_ocrm_request
    
    def get_reserved_bits_68(self) -> List[bool]:
        """获取保留位68"""
        return self.reserved_bits_68
    
    def get_power_on_thms_request(self) -> bool:
        """获取开启THMS请求状态"""
        return self.power_on_thms_request
    
    def get_reserved_69_bits_6_5(self) -> List[bool]:
        """获取保留位69_6_5"""
        return self.reserved_69_bits_6_5
    
    def get_power_off_thms_request(self) -> bool:
        """获取关闭THMS请求状态"""
        return self.power_off_thms_request
    
    def get_reserved_69_bits_0_3(self) -> List[bool]:
        """获取保留位69_0_3"""
        return self.reserved_69_bits_0_3
    
    def get_reserved_70_bits_7_2(self) -> List[bool]:
        """获取保留位70_7_2"""
        return self.reserved_70_bits_7_2
    
    def get_ocrm_test(self) -> bool:
        """获取OCRMS测试状态"""
        return self.ocrm_test
    
    def get_thms_static_test(self) -> bool:
        """获取THMS静态测试状态"""
        return self.thms_static_test
    
    def get_reserved_bytes_71(self) -> List[bool]:
        """获取保留字节71"""
        return self.reserved_bytes_71
    
    def get_reserved_bytes_72_99(self) -> List[int]:
        """获取保留字节72-99"""
        return self.reserved_bytes_72_99
    
    # ==================== SET方法 ====================
    
    def set_lifesign(self, value: int):
        """设置生命信号"""
        self.lifesign = value
    
    def set_reserved_byte_4(self, value: int):
        """设置保留字节4"""
        self.reserved_byte_4 = value
    
    def set_reserved_byte_5(self, value: int):
        """设置保留字节5"""
        self.reserved_byte_5 = value
    
    def set_year(self, value: int):
        """设置年份 (0=2000, 20-99)"""
        if not 0 <= value <= 99:
            raise ValueError(f"年份必须在0-99范围内，当前值: {value}")
        self.year = value
    
    def set_month(self, value: int):
        """设置月份 (1-12)"""
        if not 1 <= value <= 12:
            raise ValueError(f"月份必须在1-12范围内，当前值: {value}")
        self.month = value
    
    def set_day(self, value: int):
        """设置日期 (1-31)"""
        if not 1 <= value <= 31:
            raise ValueError(f"日期必须在1-31范围内，当前值: {value}")
        self.day = value
    
    def set_hour(self, value: int):
        """设置小时 (0-23)"""
        if not 0 <= value <= 23:
            raise ValueError(f"小时必须在0-23范围内，当前值: {value}")
        self.hour = value
    
    def set_minute(self, value: int):
        """设置分钟 (0-59)"""
        if not 0 <= value <= 59:
            raise ValueError(f"分钟必须在0-59范围内，当前值: {value}")
        self.minute = value
    
    def set_second(self, value: int):
        """设置秒数 (0-59)"""
        if not 0 <= value <= 59:
            raise ValueError(f"秒数必须在0-59范围内，当前值: {value}")
        self.second = value
    
    def set_dt1_cab_activated(self, value: bool):
        """设置DT1驾驶室激活状态"""
        self.dt1_cab_activated = bool(value)
    
    def set_dt2_cab_activated(self, value: bool):
        """设置DT2驾驶室激活状态"""
        self.dt2_cab_activated = bool(value)
    
    def set_reserved_bit_5(self, value: bool):
        """设置保留位5"""
        self.reserved_bit_5 = bool(value)
    
    def set_reserved_bit_4(self, value: bool):
        """设置保留位4"""
        self.reserved_bit_4 = bool(value)
    
    def set_train_speed_valid(self, value: bool):
        """设置列车速度有效状态"""
        self.train_speed_valid = bool(value)
    
    def set_wheel_diameter_valid(self, value: bool):
        """设置轮径有效状态"""
        self.wheel_diameter_valid = bool(value)
    
    def set_time_setting(self, value: bool):
        """设置时间设置状态"""
        self.time_setting = bool(value)
    
    def set_time_valid(self, value: bool):
        """设置时间有效状态"""
        self.time_valid = bool(value)
    
    def set_backward(self, value: bool):
        """设置向后状态"""
        self.backward = bool(value)
    
    def set_forward(self, value: bool):
        """设置向前状态"""
        self.forward = bool(value)
    
    def set_reserved_bit_0(self, value: bool):
        """设置保留位0"""
        self.reserved_bit_0 = bool(value)
    
    def set_left_door_open_command(self, value: bool):
        """设置左门开启命令"""
        self.left_door_open_command = bool(value)
    
    def set_right_door_open_command(self, value: bool):
        """设置右门开启命令"""
        self.right_door_open_command = bool(value)
    
    def set_left_door_close_command(self, value: bool):
        """设置左门关闭命令"""
        self.left_door_close_command = bool(value)
    
    def set_right_door_close_command(self, value: bool):
        """设置右门关闭命令"""
        self.right_door_close_command = bool(value)
    
    def set_all_door_closed(self, value: bool):
        """设置所有门关闭状态"""
        self.all_door_closed = bool(value)
    
    def set_train_id(self, value: int):
        """设置列车ID"""
        if not 0 <= value <= 255:
            raise ValueError(f"列车ID必须在0-255范围内，当前值: {value}")
        self.train_id = value
    
    def set_reserved_bytes_15(self, value: List[int]):
        """设置保留字节15"""
        if len(value) != 1:
            raise ValueError(f"保留字节15长度必须为1，当前长度: {len(value)}")
        self.reserved_bytes_15 = value
    
    def set_wheel_diameter(self, value: int):
        """设置轮径值"""
        self.wheel_diameter = value
    
    def set_reserved_bytes_18_21(self, value: List[int]):
        """设置保留字节18-21"""
        if len(value) != 4:
            raise ValueError(f"保留字节18-21长度必须为4，当前长度: {len(value)}")
        self.reserved_bytes_18_21 = value
    
    def set_reserved_bits_22(self, value: List[bool]):
        """设置保留位22"""
        if len(value) != 8:
            raise ValueError(f"保留位22长度必须为8，当前长度: {len(value)}")
        self.reserved_bits_22 = [bool(v) for v in value]
    
    def set_reserved_bytes_23_31(self, value: List[int]):
        """设置保留字节23-31"""
        if len(value) != 9:
            raise ValueError(f"保留字节23-31长度必须为9，当前长度: {len(value)}")
        self.reserved_bytes_23_31 = value
    
    def set_train_speed(self, value: int):
        """设置列车速度 (1=0.1km/h, 0~2000 = 0-200km/h)"""
        if not 0 <= value <= 2000:
            raise ValueError(f"列车速度必须在0-2000范围内，当前值: {value}")
        self.train_speed = value
    
    def set_reserved_bits_34(self, value: List[bool]):
        """设置保留位34"""
        if len(value) != 5:
            raise ValueError(f"保留位34长度必须为5，当前长度: {len(value)}")
        self.reserved_bits_34 = [bool(v) for v in value]
    
    def set_mp1_pantograph_status(self, value: bool):
        """设置Mp1受电弓状态 (0:降下 1:升起)"""
        self.mp1_pantograph_status = bool(value)
    
    def set_mp2_pantograph_status(self, value: bool):
        """设置Mp2受电弓状态 (0:降下 1:升起)"""
        self.mp2_pantograph_status = bool(value)
    
    def set_reserved_bit_34_0(self, value: bool):
        """设置保留位34_0"""
        self.reserved_bit_34_0 = bool(value)
    
    def set_train_arrived(self, value: bool):
        """设置列车到达状态"""
        self.train_arrived = bool(value)
    
    def set_skip_stop_announcement(self, value: bool):
        """设置跳过停站广播状态"""
        self.skip_stop_announcement = bool(value)
    
    def set_reserved_bits_35(self, value: List[bool]):
        """设置保留位35"""
        if len(value) != 6:
            raise ValueError(f"保留位35长度必须为6，当前长度: {len(value)}")
        self.reserved_bits_35 = [bool(v) for v in value]
    
    def set_reserved_bytes_36_37(self, value: List[int]):
        """设置保留字节36-37"""
        if len(value) != 2:
            raise ValueError(f"保留字节36-37长度必须为2，当前长度: {len(value)}")
        self.reserved_bytes_36_37 = value
    
    def set_passenger_loading(self, value: List[int]):
        """设置乘客负载 (1-6, 对应AW0-AW5)"""
        if len(value) != 6:
            raise ValueError(f"乘客负载长度必须为6，当前长度: {len(value)}")
        for i, loading in enumerate(value):
            if not 1 <= loading <= 6:
                raise ValueError(f"乘客负载必须在1-6范围内，车厢{i+1}的值: {loading}")
        self.passenger_loading = value
    
    def set_reserved_bytes_44_47(self, value: List[int]):
        """设置保留字节44-47"""
        if len(value) != 4:
            raise ValueError(f"保留字节44-47长度必须为4，当前长度: {len(value)}")
        self.reserved_bytes_44_47 = value
    
    def set_line_voltage(self, value: int):
        """设置线路电压 (1=1V, 0-65535V)"""
        if not 0 <= value <= 65535:
            raise ValueError(f"线路电压必须在0-65535范围内，当前值: {value}")
        self.line_voltage = value
    
    def set_line_current(self, value: int):
        """设置线路电流 (1=1A, -32768A~32767A)"""
        if not -32768 <= value <= 32767:
            raise ValueError(f"线路电流必须在-32768到32767范围内，当前值: {value}")
        self.line_current = value
    
    def set_generic_station_code(self, value: int):
        """设置通用站台代码 (1010-1241)"""
        if not 1010 <= value <= 1241:
            raise ValueError(f"通用站台代码必须在1010-1241范围内，当前值: {value}")
        self.generic_station_code = value
    
    def set_final_destination_code(self, value: int):
        """设置最终目的地代码 (1010-1241)"""
        if not 1010 <= value <= 1241:
            raise ValueError(f"最终目的地代码必须在1010-1241范围内，当前值: {value}")
        self.final_destination_code = value
    
    def set_next_station_code(self, value: int):
        """设置下一站代码 (1010-1241)"""
        if not 1010 <= value <= 1241:
            raise ValueError(f"下一站代码必须在1010-1241范围内，当前值: {value}")
        self.next_station_code = value
    
    def set_reserved_bytes_58_67(self, value: List[int]):
        """设置保留字节58-67"""
        if len(value) != 10:
            raise ValueError(f"保留字节58-67长度必须为10，当前长度: {len(value)}")
        self.reserved_bytes_58_67 = value
    
    def set_power_on_ocrm_request(self, value: bool):
        """设置开启OCRMS请求状态"""
        self.power_on_ocrm_request = bool(value)
    
    def set_reserved_68_bits_6_6(self, value: List[bool]):
        """设置保留位68_6_6"""
        if len(value) != 2:
            raise ValueError(f"保留位68_6_6长度必须为2，当前长度: {len(value)}")
        self.reserved_68_bits_6_6 = [bool(v) for v in value]
    
    def set_power_off_ocrm_request(self, value: bool):
        """设置关闭OCRMS请求状态"""
        self.power_off_ocrm_request = bool(value)
    
    def set_reserved_bits_68(self, value: List[bool]):
        """设置保留位68"""
        if len(value) != 4:
            raise ValueError(f"保留位68长度必须为4，当前长度: {len(value)}")
        self.reserved_bits_68 = [bool(v) for v in value]
    
    def set_power_on_thms_request(self, value: bool):
        """设置开启THMS请求状态"""
        self.power_on_thms_request = bool(value)
    
    def set_reserved_69_bits_6_5(self, value: List[bool]):
        """设置保留位69_6_5"""
        if len(value) != 2:
            raise ValueError(f"保留位69_6_5长度必须为2，当前长度: {len(value)}")
        self.reserved_69_bits_6_5 = [bool(v) for v in value]
    
    def set_power_off_thms_request(self, value: bool):
        """设置关闭THMS请求状态"""
        self.power_off_thms_request = bool(value)
    
    def set_reserved_69_bits_0_3(self, value: List[bool]):
        """设置保留位69_0_3"""
        if len(value) != 4:
            raise ValueError(f"保留位69_0_3长度必须为4，当前长度: {len(value)}")
        self.reserved_69_bits_0_3 = [bool(v) for v in value]
    
    def set_reserved_70_bits_7_2(self, value: List[bool]):
        """设置保留位70_7_2"""
        if len(value) != 6:
            raise ValueError(f"保留位70_7_2长度必须为6，当前长度: {len(value)}")
        self.reserved_70_bits_7_2 = [bool(v) for v in value]
    
    def set_ocrm_test(self, value: bool):
        """设置OCRMS测试状态"""
        self.ocrm_test = bool(value)
    
    def set_thms_static_test(self, value: bool):
        """设置THMS静态测试状态"""
        self.thms_static_test = bool(value)
    
    def set_reserved_bytes_71(self, value: List[bool]):
        """设置保留字节71"""
        if len(value) != 1:
            raise ValueError(f"保留字节71长度必须为1，当前长度: {len(value)}")
        self.reserved_bytes_71 = [bool(v) for v in value]
    
    def set_reserved_bytes_72_99(self, value: List[int]):
        """设置保留字节72-99"""
        if len(value) != 28:
            raise ValueError(f"保留字节72-99长度必须为28，当前长度: {len(value)}")
        self.reserved_bytes_72_99 = value
    
    def get_byte_12_flags(self) -> int:
        """获取字节12的状态标志"""
        flags = 0
        if self.dt1_cab_activated:
            flags |= 0x80  # b7
        if self.dt2_cab_activated:
            flags |= 0x40  # b6
        if self.reserved_bit_5:
            flags |= 0x20  # b5
        if self.reserved_bit_4:
            flags |= 0x10  # b4
        if self.train_speed_valid:
            flags |= 0x08  # b3
        if self.wheel_diameter_valid:
            flags |= 0x04  # b2
        if self.time_setting:
            flags |= 0x02  # b1
        if self.time_valid:
            flags |= 0x01  # b0
        return flags
    
    def get_byte_13_flags(self) -> int:
        """获取字节13的车门命令标志"""
        flags = 0
        if self.backward:
            flags |= 0x80  # b7
        if self.forward:
            flags |= 0x40  # b6
        if self.reserved_bit_0:
            flags |= 0x20  # b5
        if self.left_door_open_command:
            flags |= 0x10  # b4
        if self.right_door_open_command:
            flags |= 0x08  # b3
        if self.left_door_close_command:
            flags |= 0x04  # b2
        if self.right_door_close_command:
            flags |= 0x02  # b1
        if self.all_door_closed:
            flags |= 0x01  # b0
        return flags
    
    def get_byte_34_flags(self) -> int:
        """获取字节34的受电弓状态标志"""
        flags = 0
        for i, bit in enumerate(self.reserved_bits_34):
            if bit:
                flags |= (0x80 >> i)  # b7-b3
        if self.mp1_pantograph_status:
            flags |= 0x04  # b2
        if self.mp2_pantograph_status:
            flags |= 0x02  # b1
        if self.reserved_bit_34_0:
            flags |= 0x01  # b0
        return flags
    
    def get_byte_35_flags(self) -> int:
        """获取字节35的列车事件标志"""
        flags = 0
        if self.train_arrived:
            flags |= 0x80  # b7
        if self.skip_stop_announcement:
            flags |= 0x40  # b6
        for i, bit in enumerate(self.reserved_bits_35):
            if bit:
                flags |= (0x20 >> i)  # b5-b0
        return flags
    
    def get_byte_68_flags(self) -> int:
        """获取字节68的OCRMS电源命令标志"""
        flags = 0
        if self.power_on_ocrm_request:
            flags |= 0x80  # b7
        for i, bit in enumerate(self.reserved_68_bits_6_6):
            if bit:
                flags |= (0x40 >> i)  # b6-b5
        if self.power_off_ocrm_request:
            flags |= 0x10  # b4
        for i, bit in enumerate(self.reserved_bits_68):
            if bit:
                flags |= (0x08 >> i)  # b3-b0
        return flags
    
    def get_byte_69_flags(self) -> int:
        """获取字节69的THMS电源命令标志"""
        flags = 0
        if self.power_on_thms_request:
            flags |= 0x80  # b7
        for i, bit in enumerate(self.reserved_69_bits_6_5):
            if bit:
                flags |= (0x40 >> i)  # b6-b5
        if self.power_off_thms_request:
            flags |= 0x10  # b4
        for i, bit in enumerate(self.reserved_69_bits_0_3):
            if bit:
                flags |= (0x08 >> i)  # b3-b0
        return flags
    
    def get_byte_70_flags(self) -> int:
        """获取字节70的测试命令标志"""
        flags = 0
        for i, bit in enumerate(self.reserved_70_bits_7_2):
            if bit:
                flags |= (0x80 >> i)  # b7-b2
        if self.ocrm_test:
            flags |= 0x02  # b1
        if self.thms_static_test:
            flags |= 0x01  # b0
        return flags
    
    def to_bytes(self) -> bytes:
        """将数据集转换为字节数组"""
        data = bytearray(100)  # 100字节的数据集
        
        # Lifesign (字节 0-3)
        struct.pack_into('<I', data, 0, self.lifesign)
        
        # 保留字节 (字节 4-5)
        data[4] = self.reserved_byte_4
        data[5] = self.reserved_byte_5
        
        # 日期时间 (字节 6-11)
        # 验证日期时间字段范围
        if not 0 <= self.year <= 99:
            raise ValueError(f"年份必须在0-99范围内，当前值: {self.year}")
        if not 1 <= self.month <= 12:
            raise ValueError(f"月份必须在1-12范围内，当前值: {self.month}")
        if not 1 <= self.day <= 31:
            raise ValueError(f"日期必须在1-31范围内，当前值: {self.day}")
        if not 0 <= self.hour <= 23:
            raise ValueError(f"小时必须在0-23范围内，当前值: {self.hour}")
        if not 0 <= self.minute <= 59:
            raise ValueError(f"分钟必须在0-59范围内，当前值: {self.minute}")
        if not 0 <= self.second <= 59:
            raise ValueError(f"秒数必须在0-59范围内，当前值: {self.second}")
        
        data[6] = self.year
        data[7] = self.month
        data[8] = self.day
        data[9] = self.hour
        data[10] = self.minute
        data[11] = self.second
        
        # 状态标志 (字节 12)
        data[12] = self.get_byte_12_flags()
        
        # 车门命令 (字节 13)
        data[13] = self.get_byte_13_flags()
        
        # 列车ID (字节 14)
        if not 0 <= self.train_id <= 255:
            raise ValueError(f"列车ID必须在0-255范围内，当前值: {self.train_id}")
        data[14] = self.train_id
        
        # 保留字节 (字节 15)
        data[15] = self.reserved_bytes_15[0]
        
        # 轮径 (字节 16-17)
        struct.pack_into('<H', data, 16, self.wheel_diameter)
        
        # 保留字节 (字节 18-21)
        for i, val in enumerate(self.reserved_bytes_18_21):
            data[18 + i] = val
        
        # 状态标志2 (字节 22)
        flags_22 = 0
        for i, bit in enumerate(self.reserved_bits_22):
            if bit:
                flags_22 |= (0x80 >> i)  # b7-b0
        data[22] = flags_22
        
        # 保留字节 (字节 23-31)
        for i, val in enumerate(self.reserved_bytes_23_31):
            data[23 + i] = val
        
        # 列车速度 (字节 32-33)
        struct.pack_into('<H', data, 32, self.train_speed)
        
        # 受电弓状态 (字节 34)
        data[34] = self.get_byte_34_flags()
        
        # 列车事件 (字节 35)
        data[35] = self.get_byte_35_flags()
        
        # 保留字节 (字节 36-37)
        for i, val in enumerate(self.reserved_bytes_36_37):
            data[36 + i] = val
        
        # 乘客负载 (字节 38-43)
        for i, loading in enumerate(self.passenger_loading):
            if not 1 <= loading <= 6:
                raise ValueError(f"乘客负载必须在1-6范围内，车厢{i+1}的值: {loading}")
            data[38 + i] = loading
        
        # 保留字节 (字节 44-47)
        for i, val in enumerate(self.reserved_bytes_44_47):
            data[44 + i] = val
        
        # 线路电压 (字节 48-49)
        struct.pack_into('<H', data, 48, self.line_voltage)
        
        # 线路电流 (字节 50-51)
        struct.pack_into('<h', data, 50, self.line_current)
        
        # 通用站台代码 (字节 52-53)
        struct.pack_into('<H', data, 52, self.generic_station_code)
        
        # 最终目的地代码 (字节 54-55)
        struct.pack_into('<H', data, 54, self.final_destination_code)
        
        # 下一站代码 (字节 56-57)
        struct.pack_into('<H', data, 56, self.next_station_code)
        
        # 保留字节 (字节 58-67)
        for i, val in enumerate(self.reserved_bytes_58_67):
            data[58 + i] = val
        
        # OCRMS电源命令 (字节 68)
        data[68] = self.get_byte_68_flags()
        
        # THMS电源命令 (字节 69)
        data[69] = self.get_byte_69_flags()
        
        # 测试命令 (字节 70)
        data[70] = self.get_byte_70_flags()
        
        # 保留字节 (字节 71)
        data[71] = self.reserved_bytes_71[0]
        
        # 保留字节 (字节 72-99)
        for i, val in enumerate(self.reserved_bytes_72_99):
            data[72 + i] = val
        
        return bytes(data)
    
    def from_bytes(self, data: bytes):
        """从字节数组解析数据集"""
        if len(data) < 100:
            raise ValueError("数据长度不足100字节")
        
        # Lifesign (字节 0-3)
        self.lifesign = struct.unpack('<I', data[0:4])[0]
        
        # 保留字节 (字节 4-5)
        self.reserved_byte_4 = data[4]
        self.reserved_byte_5 = data[5]
        
        # 日期时间 (字节 6-11)
        self.year = data[6]
        self.month = data[7]
        self.day = data[8]
        self.hour = data[9]
        self.minute = data[10]
        self.second = data[11]
        
        # 状态标志 (字节 12)
        flags_12 = data[12]
        self.dt1_cab_activated = bool(flags_12 & 0x80)
        self.dt2_cab_activated = bool(flags_12 & 0x40)
        self.reserved_bit_5 = bool(flags_12 & 0x20)
        self.reserved_bit_4 = bool(flags_12 & 0x10)
        self.train_speed_valid = bool(flags_12 & 0x08)
        self.wheel_diameter_valid = bool(flags_12 & 0x04)
        self.time_setting = bool(flags_12 & 0x02)
        self.time_valid = bool(flags_12 & 0x01)
        
        # 车门命令 (字节 13)
        flags_13 = data[13]
        self.backward = bool(flags_13 & 0x80)
        self.forward = bool(flags_13 & 0x40)
        self.reserved_bit_0 = bool(flags_13 & 0x20)
        self.left_door_open_command = bool(flags_13 & 0x10)
        self.right_door_open_command = bool(flags_13 & 0x08)
        self.left_door_close_command = bool(flags_13 & 0x04)
        self.right_door_close_command = bool(flags_13 & 0x02)
        self.all_door_closed = bool(flags_13 & 0x01)
        
        # 列车ID (字节 14)
        self.train_id = data[14]
        
        # 保留字节 (字节 15)
        self.reserved_bytes_15 = [data[15]]
        
        # 轮径 (字节 16-17)
        self.wheel_diameter = struct.unpack('<H', data[16:18])[0]
        
        # 保留字节 (字节 18-21)
        self.reserved_bytes_18_21 = list(data[18:22])
        
        # 状态标志2 (字节 22)
        flags_22 = data[22]
        self.reserved_bits_22 = [bool(flags_22 & (0x80 >> i)) for i in range(8)]
        
        # 保留字节 (字节 23-31)
        self.reserved_bytes_23_31 = list(data[23:32])
        
        # 列车速度 (字节 32-33)
        self.train_speed = struct.unpack('<H', data[32:34])[0]
        
        # 受电弓状态 (字节 34)
        flags_34 = data[34]
        self.reserved_bits_34 = [bool(flags_34 & (0x80 >> i)) for i in range(5)]
        self.mp1_pantograph_status = bool(flags_34 & 0x04)
        self.mp2_pantograph_status = bool(flags_34 & 0x02)
        self.reserved_bit_34_0 = bool(flags_34 & 0x01)
        
        # 列车事件 (字节 35)
        flags_35 = data[35]
        self.train_arrived = bool(flags_35 & 0x80)
        self.skip_stop_announcement = bool(flags_35 & 0x40)
        self.reserved_bits_35 = [bool(flags_35 & (0x20 >> i)) for i in range(6)]
        
        # 乘客负载 (字节 38-43)
        self.passenger_loading = list(data[38:44])
        
        # 线路电压 (字节 48-49)
        self.line_voltage = struct.unpack('<H', data[48:50])[0]
        
        # 线路电流 (字节 50-51)
        self.line_current = struct.unpack('<h', data[50:52])[0]
        
        # 通用站台代码 (字节 52-53)
        self.generic_station_code = struct.unpack('<H', data[52:54])[0]
        
        # 最终目的地代码 (字节 54-55)
        self.final_destination_code = struct.unpack('<H', data[54:56])[0]
        
        # 下一站代码 (字节 56-57)
        self.next_station_code = struct.unpack('<H', data[56:58])[0]
        
        # 保留字节 (字节 58-67)
        self.reserved_bytes_58_67 = list(data[58:68])
        
        # OCRMS电源命令 (字节 68)
        flags_68 = data[68]
        self.power_on_ocrm_request = bool(flags_68 & 0x80)
        self.reserved_68_bits_6_6 = [bool(flags_68 & (0x40 >> i)) for i in range(2)]
        self.power_off_ocrm_request = bool(flags_68 & 0x10)
        self.reserved_bits_68 = [bool(flags_68 & (0x08 >> i)) for i in range(4)]
        
        # THMS电源命令 (字节 69)
        flags_69 = data[69]
        self.power_on_thms_request = bool(flags_69 & 0x80)
        self.reserved_69_bits_6_5 = [bool(flags_69 & (0x40 >> i)) for i in range(2)]
        self.power_off_thms_request = bool(flags_69 & 0x10)
        self.reserved_69_bits_0_3 = [bool(flags_69 & (0x08 >> i)) for i in range(4)]
        
        # 测试命令 (字节 70)
        flags_70 = data[70]
        self.reserved_70_bits_7_2 = [bool(flags_70 & (0x80 >> i)) for i in range(6)]
        self.ocrm_test = bool(flags_70 & 0x02)
        self.thms_static_test = bool(flags_70 & 0x01)
        
        # 保留字节 (字节 71)
        self.reserved_bytes_71 = [bool(data[71])]
        
        # 保留字节 (字节 72-99)
        self.reserved_bytes_72_99 = list(data[72:100])
    
    def __str__(self) -> str:
        """返回数据集的字符串表示"""
        return f"""TRDP数据集:
            生命信号: {self.lifesign}
            时间: {2000 + self.year}-{self.month:02d}-{self.day:02d} {self.hour:02d}:{self.minute:02d}:{self.second:02d}
            列车ID: {self.train_id}
            列车速度: {self.train_speed * 0.1:.1f} km/h
            线路电压: {self.line_voltage} V
            线路电流: {self.line_current} A
            乘客负载: {self.passenger_loading}
            DT1驾驶室激活: {self.dt1_cab_activated}
            DT2驾驶室激活: {self.dt2_cab_activated}
            列车速度有效: {self.train_speed_valid}
            时间有效: {self.time_valid}"""

