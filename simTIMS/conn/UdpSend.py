#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UDP发送器 - TRDP PD数据包发送
实现实时读取配置文件，打包TrdpPdHeader和TrdpDatasetFromOCRMS数据，通过UDP组播发送
"""

import socket
import json
import time
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from com.TrdpPdHeader import TRDPPdHeader, MessageType
from com.TrdpDatasetFromOCRMS import TRDPDatasetFromOCRMS, SelfTestResult, AlarmSeverity



class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # 使用相对路径，从conn目录开始
            self.config_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'ocrms_config.json')
        else:
            self.config_file = config_file
        self.config = {}
        self.last_modified = 0
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
            
            current_modified = os.path.getmtime(self.config_file)
            if current_modified > self.last_modified:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.last_modified = current_modified
                logging.info(f"配置文件已重新加载: {self.config_file}")
            
            return self.config
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            raise
    
    def get_network_config(self) -> Dict[str, Any]:
        return self.config.get('network', {})
    
    def get_trdp_header_config(self) -> Dict[str, Any]:
        return self.config.get('trdp_header', {})
    
    def get_ocrms_dataset_config(self) -> Dict[str, Any]:
        return self.config.get('ocrms_dataset', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        return self.config.get('logging', {})


class TRDPPacketBuilder:
    """TRDP数据包构建器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.sequence_counter = 0
    
    def build_trdp_header(self) -> TRDPPdHeader:
        """构建TRDP PD头部"""
        header_config = self.config_manager.get_trdp_header_config()
        
        header = TRDPPdHeader()
        
        # 设置协议版本
        protocol_version = header_config.get('protocol_version', [1, 0])
        header.set_protocol_version(protocol_version)
        
        # 设置序列计数器
        self.sequence_counter += 1
        header.set_sequence_counter_value(self.sequence_counter)
        
        # 设置消息类型
        msg_type_str = header_config.get('msg_type', 'PD_DATA')
        msg_type_map = {
            'PD_REQUEST': MessageType.PD_REQUEST,
            'PD_REPLY': MessageType.PD_REPLY,
            'PD_DATA': MessageType.PD_DATA,
            'PD_DATA_ERROR': MessageType.PD_DATA_ERROR
        }
        header.set_msg_type(msg_type_map.get(msg_type_str, MessageType.PD_DATA))
        
        # 设置其他字段
        header.set_com_id(header_config.get('com_id', [0x78, 0x56, 0x34, 0x12]))
        header.set_etb_topocnt(header_config.get('etb_topocnt', [1, 0, 0, 0]))
        header.set_op_trn_topocnt(header_config.get('op_trn_topocnt', [2, 0, 0, 0]))
        header.set_reply_com_id(header_config.get('reply_com_id', [0x21, 0x43, 0x65, 0x87]))
        header.set_reply_ip_address(header_config.get('reply_ip_address', [1, 1, 168, 192]))
        
        # 设置数据集长度（100字节）
        header.set_dataset_length([100, 0, 0, 0])
        
        # 计算并设置FCS
        header.update_fcs()
        
        return header
    
    def build_ocrms_dataset(self) -> TRDPDatasetFromOCRMS:
        """构建OCRMS数据集"""
        dataset_config = self.config_manager.get_ocrms_dataset_config()
        
        dataset = TRDPDatasetFromOCRMS()
        
        # 设置生命信号
        life_signals = dataset_config.get('life_signals', {})
        dataset.life_signal_hh = life_signals.get('life_signal_hh', 123)
        dataset.life_signal_hl = life_signals.get('life_signal_hl', 45)
        dataset.life_signal_lh = life_signals.get('life_signal_lh', 67)
        dataset.life_signal_ll = life_signals.get('life_signal_ll', 89)
        
        # 设置系统状态
        system_status = dataset_config.get('system_status', {})
        dataset.power_on_request_received = system_status.get('power_on_request_received', True)
        dataset.ocrms_on_system_state = system_status.get('ocrms_on_system_state', True)
        dataset.power_off_request_received = system_status.get('power_off_request_received', False)
        dataset.ocrms_off_system_state = system_status.get('ocrms_off_system_state', False)
        
        # 设置自检结果
        self_test = dataset_config.get('self_test', {})
        test_result_str = self_test.get('self_test_result', 'SELF_TEST_SUCCESSFUL')
        test_result_map = {
            'NOT_SELF_TESTED': SelfTestResult.NOT_SELF_TESTED,
            'SELF_TESTING': SelfTestResult.SELF_TESTING,
            'SELF_TEST_SUCCESSFUL': SelfTestResult.SELF_TEST_SUCCESSFUL,
            'SELF_TEST_FAILURE': SelfTestResult.SELF_TEST_FAILURE
        }
        dataset.self_test_result = test_result_map.get(test_result_str, SelfTestResult.SELF_TEST_SUCCESSFUL)
        
        # 设置模块故障标志
        module_failures = dataset_config.get('module_failures', {})
        dataset.arcing_detection_failure = module_failures.get('arcing_detection_failure', False)
        dataset.video_surveillance_failure = module_failures.get('video_surveillance_failure', False)
        dataset.temperature_detection_failure = module_failures.get('temperature_detection_failure', False)
        dataset.geometric_parameters_failure = module_failures.get('geometric_parameters_failure', False)
        dataset.left_vibration_compensation_failure = module_failures.get('left_vibration_compensation_failure', False)
        dataset.right_vibration_compensation_failure = module_failures.get('right_vibration_compensation_failure', False)
        dataset.ocrms_software_failure = module_failures.get('ocrms_software_failure', False)
        
        # 设置序列号
        serial_numbers = dataset_config.get('serial_numbers', {})
        dataset.arcing_detection_sn = serial_numbers.get('arcing_detection_sn', [65, 82, 67, 48, 49])
        dataset.video_surveillance_sn = serial_numbers.get('video_surveillance_sn', [86, 73, 68, 48, 49])
        dataset.temperature_detection_sn = serial_numbers.get('temperature_detection_sn', [84, 69, 77, 48, 49])
        dataset.geometric_parameters_sn = serial_numbers.get('geometric_parameters_sn', [71, 69, 79, 48, 49])
        dataset.left_vibration_compensation_sn = serial_numbers.get('left_vibration_compensation_sn', [76, 86, 67, 48, 49])
        dataset.right_vibration_compensation_sn = serial_numbers.get('right_vibration_compensation_sn', [82, 86, 67, 48, 49])
        
        # 设置告警信息
        alarm_info = dataset_config.get('alarm_info', {})
        dataset.defect_class_id = alarm_info.get('defect_class_id', [0x39, 0x30])
        
        alarm_severity_str = alarm_info.get('alarm_severity', 'MEDIUM')
        severity_map = {
            'HIGH': AlarmSeverity.HIGH,
            'MEDIUM': AlarmSeverity.MEDIUM,
            'LOW': AlarmSeverity.LOW
        }
        dataset.alarm_severity = severity_map.get(alarm_severity_str, AlarmSeverity.MEDIUM)
        
        dataset.alarm_location = alarm_info.get('alarm_location', [0x40, 0x42, 0x0F, 0x00])
        dataset.track_circuit = alarm_info.get('track_circuit', [84, 67, 48, 48, 49, 65])
        dataset.wearing_value = alarm_info.get('wearing_value', [0xF4, 0x01])
        dataset.alarm_location_pmd = alarm_info.get('alarm_location_pmd', 2000000)
        dataset.track_circuit_pmd = alarm_info.get('track_circuit_pmd', [84, 67, 48, 48, 49, 66])
        
        # 设置软件版本
        software_version = dataset_config.get('software_version', {})
        dataset.software_version_high = software_version.get('software_version_high', 1)
        dataset.software_version_low = software_version.get('software_version_low', 23)
        
        return dataset
    
    def build_packet(self) -> bytes:
        """构建完整的TRDP数据包"""
        # 构建头部
        header = self.build_trdp_header()
        header_bytes = header.to_bytes()
        
        # 构建数据集
        dataset = self.build_ocrms_dataset()
        dataset_bytes = dataset.to_bytes()
        
        # 组合完整数据包
        packet = header_bytes + dataset_bytes
        
        logging.debug(f"数据包构建完成: 头部{len(header_bytes)}字节 + 数据集{len(dataset_bytes)}字节 = 总计{len(packet)}字节")
        
        return packet


class UDPSender:
    """UDP发送器"""
    
    def __init__(self, config_manager: ConfigManager):
        print("   - 初始化UDP发送器...")
        self.config_manager = config_manager
        self.socket = None
        self.packet_builder = TRDPPacketBuilder(config_manager)
        print("   - 数据包构建器创建成功")
        self.running = False
        print("   - UDP发送器初始化完成")
    
    def setup_socket(self):
        """设置UDP套接字"""
        try:
            network_config = self.config_manager.get_network_config()
            local_ip = network_config.get('local_ip', '0.0.0.0')
            
            logging.debug("开始创建UDP套接字...")
            
            # 创建UDP套接字
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            logging.debug("UDP套接字创建成功")
            
            # 设置套接字选项
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.debug("设置SO_REUSEADDR选项成功")
            
            # 绑定本地地址和端口 - 使用0.0.0.0避免绑定错误
            self.socket.bind(('0.0.0.0', 0))
            logging.debug("绑定到0.0.0.0:0成功")
            
            # 设置组播TTL
            self.socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
            logging.debug("设置组播TTL为2成功")
            
            # 获取绑定的端口
            bound_port = self.socket.getsockname()[1]
            logging.info(f"UDP套接字设置完成，绑定地址: 0.0.0.0:{bound_port}")
            
        except Exception as e:
            logging.error(f"设置UDP套接字失败: {e}")
            raise
    
    def send_packet(self, packet: bytes) -> bool:
        """发送数据包"""
        try:
            network_config = self.config_manager.get_network_config()
            target_ip = network_config.get('target_ip', '192.168.0.20')
            target_port = network_config.get('target_port', 17224)
            
            logging.debug(f"准备发送数据包到 {target_ip}:{target_port}")
            
            # 发送数据包
            bytes_sent = self.socket.sendto(packet, (target_ip, target_port))
            
            logging.debug(f"UDP sendto() 返回: {bytes_sent} 字节")
            logging.info(f"数据包已发送到 {target_ip}:{target_port}, 大小: {len(packet)}字节, 实际发送: {bytes_sent}字节")
            return True
            
        except Exception as e:
            logging.error(f"发送数据包失败: {e}")
            return False
    
    def start_sending(self):
        """开始发送循环"""
        try:
            print("   - 设置UDP套接字...")
            self.setup_socket()
            print("   - UDP套接字设置成功")
            self.running = True
            
            network_config = self.config_manager.get_network_config()
            send_interval = network_config.get('send_interval', 1.0)
            
            print(f"   - 开始UDP发送循环，发送间隔: {send_interval}秒")
            logging.info(f"开始UDP发送循环，发送间隔: {send_interval}秒")
            
            while self.running:
                try:
                    # 重新加载配置（检查是否有更新）
                    self.config_manager.load_config()
                    logging.debug("配置文件重新加载完成")
                    
                    # 构建数据包
                    logging.debug("开始构建数据包...")
                    packet = self.packet_builder.build_packet()
                    logging.debug(f"数据包构建完成，长度: {len(packet)} 字节")
                    
                    # 记录数据包原始数据
                    packet_hex = ' '.join([f'{b:02X}' for b in packet])
                    logging.debug(f"数据包原始数据 (HEX): {packet_hex}")
                    
                    # 记录数据包前32字节的详细信息
                    if len(packet) >= 32:
                        header_hex = ' '.join([f'{b:02X}' for b in packet[:32]])
                        logging.debug(f"数据包头部 (前32字节): {header_hex}")
                    
                    # 发送数据包
                    logging.debug("开始发送数据包...")
                    if self.send_packet(packet):
                        logging.info(f"数据包发送成功，发送了 {len(packet)} 字节")
                    else:
                        logging.warning("数据包发送失败")
                    
                    # 等待下次发送
                    logging.debug(f"等待 {send_interval} 秒后发送下一个数据包...")
                    time.sleep(send_interval)
                    
                except KeyboardInterrupt:
                    logging.info("收到中断信号，停止发送")
                    break
                except Exception as e:
                    logging.error(f"发送循环中发生错误: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logging.error(f"启动发送循环失败: {e}")
        finally:
            self.stop_sending()
    
    def stop_sending(self):
        """停止发送"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        logging.info("UDP发送器已停止")


def setup_logging(config_manager: ConfigManager):
    """设置日志"""
    logging_config = config_manager.get_logging_config()
    log_level = getattr(logging, logging_config.get('level', 'INFO'))
    log_file = logging_config.get('file', 'logs/udp_send.log')
    console_output = logging_config.get('console_output', True)
    
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() if console_output else logging.NullHandler()
        ]
    )


def main():
    """主函数"""
    try:
        print("=== TRDP UDP发送器启动 ===")
        
        # 创建配置管理器
        print("1. 创建配置管理器...")
        config_manager = ConfigManager()
        print("   ✅ 配置管理器创建成功")
        
        # 设置日志
        print("2. 设置日志系统...")
        setup_logging(config_manager)
        print("   ✅ 日志系统设置成功")
        
        logging.info("TRDP UDP发送器启动")
        
        # 创建UDP发送器
        print("3. 创建UDP发送器...")
        sender = UDPSender(config_manager)
        print("   ✅ UDP发送器创建成功")
        
        # 开始发送
        print("4. 开始发送循环...")
        sender.start_sending()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        logging.error(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
