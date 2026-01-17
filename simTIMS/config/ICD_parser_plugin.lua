-- TRDP协议Wireshark Dissector
-- 描述: 基于新加坡项目ICD协议结构的解析器

-- 创建协议对象
local trdp_proto = Proto("TRDP_Real", "Train Real-time Data Protocol (Real)")

-- 定义HEADER部分
local f_sequence_counter = ProtoField.uint32("trdp.sequence_counter", "Sequence Counter", base.DEC, nil, 0, "Network Byte Order")
local f_protocol_version_high = ProtoField.uint8("trdp.protocol_version_high", "Protocol Version High", base.DEC)
local f_protocol_version_low = ProtoField.uint8("trdp.protocol_version_low", "Protocol Version Low", base.DEC)
local f_message_type = ProtoField.uint16("trdp.message_type", "Message Type", base.HEX, {
    [0x5072] = "Pr - Publisher Request",
    [0x5070] = "Pp - Publisher Publish", 
    [0x5064] = "Pd - Publisher Data",
    [0x5065] = "Pe - Publisher Event"
}, 0, "Network Byte Order")
local f_com_id = ProtoField.uint32("trdp.com_id", "Communication ID", base.DEC, {
    [10000] = "NetworkA - CCU",
    [10001] = "NetworkB - CCU",
    [22150] = "NetworkA - OCRMS",
    [22151] = "NetworkB - OCRMS",
    [21120] = "NetworkA - THMS",
    [21121] = "NetworkB - THMS"
}, 0, "Network Byte Order")
local f_etb_topo_cnt = ProtoField.uint32("trdp.etb_topo_cnt", "ETB Topology Counter", base.DEC, nil, 0, "Network Byte Order")
local f_op_trn_topo_cnt = ProtoField.uint32("trdp.op_trn_topo_cnt", "Operating Train Topology Counter", base.DEC, nil, 0, "Network Byte Order")
local f_dataset_length = ProtoField.uint32("trdp.dataset_length", "Dataset Length", base.DEC, nil, 0, "Network Byte Order")
local f_reserved = ProtoField.uint32("trdp.reserved", "Reserved", base.HEX, nil, 0, "Network Byte Order")
local f_reply_comid = ProtoField.uint32("trdp.reply_comid", "Reply Communication ID", base.DEC, nil, 0, "Network Byte Order")
local f_reply_ipaddress = ProtoField.ipv4("trdp.reply_ipaddress", "Reply IP Address")
local f_header_fcs = ProtoField.uint32("trdp.header_fcs", "Header FCS", base.HEX)

-- 定义dataset部分
-- 来自CCU
local f_dataset_ccu_lifesign = ProtoField.uint32("trdp.dataset.ccu_lifesign", "Lifesign", base.DEC)

local f_dataset_ccu_reserved_byte4_5 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte4_5", "Reserved (4-5)")

local f_dataset_ccu_year = ProtoField.uint8("trdp.dataset.ccu_year", "Year (2000+)", base.DEC)
local f_dataset_ccu_month = ProtoField.uint8("trdp.dataset.ccu_month", "Month", base.DEC)
local f_dataset_ccu_day = ProtoField.uint8("trdp.dataset.ccu_day", "Day", base.DEC)
local f_dataset_ccu_hour = ProtoField.uint8("trdp.dataset.ccu_hour", "Hour", base.DEC)
local f_dataset_ccu_minute = ProtoField.uint8("trdp.dataset.ccu_minute", "Minute", base.DEC)
local f_dataset_ccu_second = ProtoField.uint8("trdp.dataset.ccu_second", "Second", base.DEC)
-- 字节12
local f_dataset_ccu_dt1_cab_activated = ProtoField.bool("trdp.dataset.ccu_dt1_cab_activated", "DT1 Cab Activated", 8, nil, 0x80)
local f_dataset_ccu_dt2_cab_activated = ProtoField.bool("trdp.dataset.ccu_dt2_cab_activated", "DT2 Cab Activated", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte12_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte12_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_reserved_byte12_b4 = ProtoField.bool("trdp.dataset.ccu_reserved_byte12_b4", "reserved b4", 8, nil, 0x10)
local f_dataset_ccu_train_speed_valid = ProtoField.bool("trdp.dataset.ccu_train_speed_valid", "Train Speed Valid", 8, nil, 0x08)
local f_dataset_ccu_wheel_diameter_valid = ProtoField.bool("trdp.dataset.ccu_wheel_diameter_valid", "Wheel Diameter Valid", 8, nil, 0x04)
local f_dataset_ccu_time_setting = ProtoField.bool("trdp.dataset.ccu_time_setting", "Time Setting", 8, nil, 0x02)
local f_dataset_ccu_time_valid = ProtoField.bool("trdp.dataset.ccu_time_valid", "Time Valid", 8, nil, 0x01)
-- 字节13
local f_dataset_ccu_backward = ProtoField.bool("trdp.dataset.ccu_backward", "Backward", 8, nil, 0x80)
local f_dataset_ccu_forward = ProtoField.bool("trdp.dataset.ccu_forward", "Forward", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte13_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte13_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_left_door_open = ProtoField.bool("trdp.dataset.ccu_left_door_open", "Left Door Open", 8, nil, 0x10)
local f_dataset_ccu_right_door_open = ProtoField.bool("trdp.dataset.ccu_right_door_open", "Right Door Open", 8, nil, 0x08)
local f_dataset_ccu_left_door_close = ProtoField.bool("trdp.dataset.ccu_left_door_close", "Left Door Close", 8, nil, 0x04)
local f_dataset_ccu_right_door_close = ProtoField.bool("trdp.dataset.ccu_right_door_close", "Right Door Close", 8, nil, 0x02)
local f_dataset_ccu_all_door_closed = ProtoField.bool("trdp.dataset.ccu_all_door_closed", "All Door Closed", 8, nil, 0x01)

local f_dataset_ccu_train_id = ProtoField.uint8("trdp.dataset.ccu_train_id", "Train ID", base.DEC)

local f_dataset_ccu_reserved_byte15 = ProtoField.uint8("trdp.dataset.ccu_reserved_byte15", "Reserved (15)")

local f_dataset_ccu_wheel_diameter = ProtoField.uint16("trdp.dataset.ccu_wheel_diameter", "Wheel Diameter (mm)", base.DEC)

local f_dataset_ccu_reserved_byte18_21 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte18_21", "Reserved (18-21)")
local f_dataset_ccu_reserved_byte22 = ProtoField.uint8("trdp.dataset.ccu_reserved_byte22", "Reserved (22)")
local f_dataset_ccu_reserved_byte23_31 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte23_31", "Reserved (23-31)")

local f_dataset_ccu_train_speed = ProtoField.uint16("trdp.dataset.ccu_train_speed", "Train Speed (0.1 km/h)", base.DEC)
-- 字节34
local f_dataset_ccu_reserved_byte34_b7 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b7", "reserved b7", 8, nil, 0x80)
local f_dataset_ccu_reserved_byte34_b6 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b6", "reserved b6", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte34_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_reserved_byte34_b4 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b4", "reserved b4", 8, nil, 0x10)
local f_dataset_ccu_reserved_byte34_b3 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b3", "reserved b3", 8, nil, 0x08)
local f_dataset_ccu_mp1_pantograph = ProtoField.bool("trdp.dataset.ccu_mp1_pantograph", "MP1 Pantograph", 8, nil, 0x04)
local f_dataset_ccu_mp2_pantograph = ProtoField.bool("trdp.dataset.ccu_mp2_pantograph", "MP2 Pantograph", 8, nil, 0x02)
local f_dataset_ccu_reserved_byte34_b0 = ProtoField.bool("trdp.dataset.ccu_reserved_byte34_b0", "reserved b0", 8, nil, 0x01)

-- 字节35
local f_dataset_ccu_train_arrived = ProtoField.bool("trdp.dataset.ccu_train_arrived", "Train Arrived", 8, nil, 0x80)
local f_dataset_ccu_skip_stop_announcement = ProtoField.bool("trdp.dataset.ccu_skip_stop_announcement", "Skip Stop Announcement", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte35_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_reserved_byte35_b4 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b4", "reserved b4", 8, nil, 0x10)
local f_dataset_ccu_reserved_byte35_b3 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b3", "reserved b3", 8, nil, 0x08)
local f_dataset_ccu_reserved_byte35_b2 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b2", "reserved b2", 8, nil, 0x04)
local f_dataset_ccu_reserved_byte35_b1 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b1", "reserved b1", 8, nil, 0x02)
local f_dataset_ccu_reserved_byte35_b0 = ProtoField.bool("trdp.dataset.ccu_reserved_byte35_b0", "reserved b0", 8, nil, 0x01)

-- 字节36-37保留
local f_dataset_ccu_reserved_byte36_37 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte36_37", "Reserved (36-37)")

-- 字节38-43，乘客负载字段
local f_dataset_ccu_car_1_load = ProtoField.uint8("trdp.dataset.ccu_car_1_load", "Car 1 Load", base.DEC)
local f_dataset_ccu_car_2_load = ProtoField.uint8("trdp.dataset.ccu_car_2_load", "Car 2 Load", base.DEC)
local f_dataset_ccu_car_3_load = ProtoField.uint8("trdp.dataset.ccu_car_3_load", "Car 3 Load", base.DEC)
local f_dataset_ccu_car_4_load = ProtoField.uint8("trdp.dataset.ccu_car_4_load", "Car 4 Load", base.DEC)
local f_dataset_ccu_car_5_load = ProtoField.uint8("trdp.dataset.ccu_car_5_load", "Car 5 Load", base.DEC)
local f_dataset_ccu_car_6_load = ProtoField.uint8("trdp.dataset.ccu_car_6_load", "Car 6 Load", base.DEC)
-- 字节44-47保留
local f_dataset_ccu_reserved_byte44_47 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte44_47", "Reserved (44-47)")
-- 字节48-51电流电压
local f_dataset_ccu_line_voltage = ProtoField.uint16("trdp.dataset.ccu_line_voltage", "Line Voltage (V)", base.DEC)
local f_dataset_ccu_line_current = ProtoField.int16("trdp.dataset.ccu_line_current", "Line Current (A)", base.DEC)
-- 字节52-53下一车站号
local f_dataset_ccu_generic_station = ProtoField.uint16("trdp.dataset.ccu_generic_station", "Generic Station Code", base.DEC)
-- 字节54-55终到站号
local f_dataset_ccu_final_destination = ProtoField.uint16("trdp.dataset.ccu_final_destination", "Final Destination Code", base.DEC)
-- 字节56-57下一车站号
local f_dataset_ccu_next_station = ProtoField.uint16("trdp.dataset.ccu_next_station", "Next Station Code", base.DEC)
-- 字节58-67保留
local f_dataset_ccu_reserved_byte58_67 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte58_67", "Reserved (58-67)")

-- 字节68 OCRMS上电命令
local f_dataset_ccu_power_on_ocrm = ProtoField.bool("trdp.dataset.ccu_power_on_ocrm", "Power On OCRMS", 8, nil, 0x80)
local f_dataset_ccu_reserved_byte68_b6 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b6", "reserved b6", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte68_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_power_off_ocrm = ProtoField.bool("trdp.dataset.ccu_power_off_ocrm", "Power Off OCRMS", 8, nil, 0x10)
local f_dataset_ccu_reserved_byte68_b3 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b3", "reserved b3", 8, nil, 0x08)
local f_dataset_ccu_reserved_byte68_b2 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b2", "reserved b2", 8, nil, 0x04)
local f_dataset_ccu_reserved_byte68_b1 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b1", "reserved b1", 8, nil, 0x02)
local f_dataset_ccu_reserved_byte68_b0 = ProtoField.bool("trdp.dataset.ccu_reserved_byte68_b0", "reserved b0", 8, nil, 0x01)
-- 字节69 THMS上电
local f_dataset_ccu_power_on_thms = ProtoField.bool("trdp.dataset.ccu_power_on_thms", "Power On THMS", 8, nil, 0x80)
local f_dataset_ccu_reserved_byte69_b6 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b6", "reserved b6", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte69_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_power_off_thms = ProtoField.bool("trdp.dataset.ccu_power_off_thms", "Power Off THMS", 8, nil, 0x10)
local f_dataset_ccu_reserved_byte69_b3 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b3", "reserved b3", 8, nil, 0x08)
local f_dataset_ccu_reserved_byte69_b2 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b2", "reserved b2", 8, nil, 0x04)
local f_dataset_ccu_reserved_byte69_b1 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b1", "reserved b1", 8, nil, 0x02)
local f_dataset_ccu_reserved_byte69_b0 = ProtoField.bool("trdp.dataset.ccu_reserved_byte69_b0", "reserved b0", 8, nil, 0x01)

-- 字节70 测试命令
local f_dataset_ccu_reserved_byte70_b7 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b7", "reserved b7", 8, nil, 0x80)
local f_dataset_ccu_reserved_byte70_b6 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b6", "reserved b6", 8, nil, 0x40)
local f_dataset_ccu_reserved_byte70_b5 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b5", "reserved b5", 8, nil, 0x20)
local f_dataset_ccu_reserved_byte70_b4 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b4", "reserved b4", 8, nil, 0x10)
local f_dataset_ccu_reserved_byte70_b3 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b3", "reserved b3", 8, nil, 0x08)
local f_dataset_ccu_reserved_byte70_b2 = ProtoField.bool("trdp.dataset.ccu_reserved_byte70_b2", "reserved b2", 8, nil, 0x04)
local f_dataset_ccu_ocrm_test = ProtoField.bool("trdp.dataset.ccu_ocrm_test", "OCRMS Test", 8, nil, 0x02)
local f_dataset_ccu_thms_static_test = ProtoField.bool("trdp.dataset.ccu_thms_static_test", "THMS Static Test", 8, nil, 0x01)

-- 保留字节字段
local f_dataset_ccu_reserved_byte71 = ProtoField.uint8("trdp.dataset.ccu_reserved_byte71", "Reserved (71)")
local f_dataset_ccu_reserved_byte72_99 = ProtoField.bytes("trdp.dataset.ccu_reserved_byte72_99", "Reserved (72-99)")


-- 定义枚举
local SelfTestResult = {
    NOT_SELF_TESTED = 0,
    SELF_TEST_PASSED = 1,
    SELF_TEST_FAILED = 2,
    SELF_TEST_IN_PROGRESS = 3
}

local AlarmSeverity = {
    LOW = 0,
    MEDIUM = 1,
    HIGH = 2,
    CRITICAL = 3
}

-- 来自OCRMS
-- OCRMS生命信号字段 (字节0-3)
local f_dataset_ocrms_life_signal_hh = ProtoField.uint8("trdp.dataset.ocrms_life_signal_hh", "OCRMS Life Signal HH", base.DEC)
local f_dataset_ocrms_life_signal_hl = ProtoField.uint8("trdp.dataset.ocrms_life_signal_hl", "OCRMS Life Signal HL", base.DEC)
local f_dataset_ocrms_life_signal_lh = ProtoField.uint8("trdp.dataset.ocrms_life_signal_lh", "OCRMS Life Signal LH", base.DEC)
local f_dataset_ocrms_life_signal_ll = ProtoField.uint8("trdp.dataset.ocrms_life_signal_ll", "OCRMS Life Signal LL", base.DEC)

-- OCRMS请求和系统状态信号字段 (字节4)
local f_dataset_ocrms_power_on_request_received = ProtoField.bool("trdp.dataset.ocrms_power_on_request_received", "Power ON OCRMS request received", 8, nil, 0x80)
local f_dataset_ocrms_ocrms_on_system_state = ProtoField.bool("trdp.dataset.ocrms_ocrms_on_system_state", "OCRMS ON system state", 8, nil, 0x40)
local f_dataset_ocrms_power_off_request_received = ProtoField.bool("trdp.dataset.ocrms_power_off_request_received", "Power OFF OCRMS request received", 8, nil, 0x20)
local f_dataset_ocrms_ocrms_off_system_state = ProtoField.bool("trdp.dataset.ocrms_ocrms_off_system_state", "OCRMS OFF system state", 8, nil, 0x10)
local f_dataset_ocrms_reserved_byte4_b3 = ProtoField.bool("trdp.dataset.ocrms_reserved_byte4_b3", "Reserved b3", 8, nil, 0x08)
local f_dataset_ocrms_reserved_byte4_b2 = ProtoField.bool("trdp.dataset.ocrms_reserved_byte4_b2", "Reserved b2", 8, nil, 0x04)
local f_dataset_ocrms_reserved_byte4_b1 = ProtoField.bool("trdp.dataset.ocrms_reserved_byte4_b1", "Reserved b1", 8, nil, 0x02)
local f_dataset_ocrms_reserved_byte4_b0 = ProtoField.bool("trdp.dataset.ocrms_reserved_byte4_b0", "Reserved b0", 8, nil, 0x01)

-- 保留字节字段 (字节5)
local f_dataset_ocrms_reserved_byte5 = ProtoField.uint8("trdp.dataset.ocrms_reserved_byte5", "Reserved Byte 5", base.HEX)

-- 自检结果字段 (字节6)
local f_dataset_ocrms_self_test_result = ProtoField.uint8("trdp.dataset.ocrms_self_test_result", "Self Test Result", base.DEC, {
    [0] = "Not Self Tested",
    [1] = "Self Test Passed",
    [2] = "Self Test Failed",
    [3] = "Self Test In Progress"
})

-- 模块故障标志字段 (字节7)
local f_dataset_ocrms_reserved_byte7_b7 = ProtoField.bool("trdp.dataset.ocrms_reserved_byte7_b7", "Reserved b7", 8, nil, 0x80)
local f_dataset_ocrms_arcing_detection_failure = ProtoField.bool("trdp.dataset.ocrms_arcing_detection_failure", "E002 - Arcing detection module failure", 8, nil, 0x40)
local f_dataset_ocrms_video_surveillance_failure = ProtoField.bool("trdp.dataset.ocrms_video_surveillance_failure", "E003 - Video surveillance module failure", 8, nil, 0x20)
local f_dataset_ocrms_temperature_detection_failure = ProtoField.bool("trdp.dataset.ocrms_temperature_detection_failure", "E004 - Temperature detection module failure", 8, nil, 0x10)
local f_dataset_ocrms_geometric_parameters_failure = ProtoField.bool("trdp.dataset.ocrms_geometric_parameters_failure", "E005 - Geometric parameters module failure", 8, nil, 0x08)
local f_dataset_ocrms_left_vibration_compensation_failure = ProtoField.bool("trdp.dataset.ocrms_left_vibration_compensation_failure", "E006 - Left vibration compensation device failure", 8, nil, 0x04)
local f_dataset_ocrms_right_vibration_compensation_failure = ProtoField.bool("trdp.dataset.ocrms_right_vibration_compensation_failure", "E007 - Right vibration compensation device failure", 8, nil, 0x02)
local f_dataset_ocrms_software_failure = ProtoField.bool("trdp.dataset.ocrms_software_failure", "E008 - OCRMS software failure", 8, nil, 0x01)

-- 序列号字段 (字节8-37)
local f_dataset_ocrms_arcing_detection_sn = ProtoField.bytes("trdp.dataset.ocrms_arcing_detection_sn", "Arcing Detection Module SN", 5, base.SPACE)
local f_dataset_ocrms_video_surveillance_sn = ProtoField.bytes("trdp.dataset.ocrms_video_surveillance_sn", "Video Surveillance Module SN", 5, base.SPACE)
local f_dataset_ocrms_temperature_detection_sn = ProtoField.bytes("trdp.dataset.ocrms_temperature_detection_sn", "Temperature Detection Module SN", 5, base.SPACE)
local f_dataset_ocrms_geometric_parameters_sn = ProtoField.bytes("trdp.dataset.ocrms_geometric_parameters_sn", "Geometric Parameters Module SN", 5, base.SPACE)
local f_dataset_ocrms_left_vibration_compensation_sn = ProtoField.bytes("trdp.dataset.ocrms_left_vibration_compensation_sn", "Left Vibration Compensation Device SN", 5, base.SPACE)
local f_dataset_ocrms_right_vibration_compensation_sn = ProtoField.bytes("trdp.dataset.ocrms_right_vibration_compensation_sn", "Right Vibration Compensation Device SN", 5, base.SPACE)

-- 缺陷类ID字段 (字节38-39)
local f_dataset_ocrms_defect_class_id = ProtoField.uint16("trdp.dataset.ocrms_defect_class_id", "Defect Class ID", base.DEC, nil, 0, "Network Byte Order")

-- 告警严重程度字段 (字节40)
local f_dataset_ocrms_alarm_severity = ProtoField.uint8("trdp.dataset.ocrms_alarm_severity", "Alarm Severity", base.DEC, {
    [0] = "Low",
    [1] = "Medium",
    [2] = "High",
    [3] = "Critical"
})

-- 保留字节字段 (字节41)
local f_dataset_ocrms_reserved_byte41 = ProtoField.uint8("trdp.dataset.ocrms_reserved_byte41", "Reserved Byte 41", base.HEX)

-- 告警位置字段 (字节42-45)
local f_dataset_ocrms_alarm_location = ProtoField.uint32("trdp.dataset.ocrms_alarm_location", "Alarm Location (mm)", base.DEC, nil, 0, "Network Byte Order")

-- 轨道电路字段 (字节46-51)
local f_dataset_ocrms_track_circuit = ProtoField.string("trdp.dataset.ocrms_track_circuit", "Track Circuit", 6, base.ASCII)

-- 磨损值字段 (字节52-53)
local f_dataset_ocrms_wearing_value = ProtoField.uint16("trdp.dataset.ocrms_wearing_value", "Wearing Value (100=1)", base.DEC, nil, 0, "Network Byte Order")

-- 告警位置PMD字段 (字节54-56)
local f_dataset_ocrms_alarm_location_pmd = ProtoField.uint24("trdp.dataset.ocrms_alarm_location_pmd", "Alarm Location PMD (mm)", base.DEC, nil, 0, "Network Byte Order")

-- 轨道电路PMD字段 (字节57-62)
local f_dataset_ocrms_track_circuit_pmd = ProtoField.string("trdp.dataset.ocrms_track_circuit_pmd", "Track Circuit PMD", 6, base.ASCII)

-- 软件版本字段 (字节63-64)
local f_dataset_ocrms_software_version_high = ProtoField.uint8("trdp.dataset.ocrms_software_version_high", "Software Version H (1-99)", base.DEC)
local f_dataset_ocrms_software_version_low = ProtoField.uint8("trdp.dataset.ocrms_software_version_low", "Software Version L (1-99)", base.DEC)

-- 保留字节字段 (字节65-99)
local f_dataset_ocrms_reserved_byte65_99 = ProtoField.bytes("trdp.dataset.ocrms_reserved_byte65_99", "Reserved Bytes 65-99", 35, base.SPACE)

-- 来自THMS
-- THMS生命信号字段 (字节0-3)
local f_dataset_thms_life_signal_hh = ProtoField.uint8("trdp.dataset.thms_life_signal_hh", "THMS Life Signal HH", base.DEC)
local f_dataset_thms_life_signal_hl = ProtoField.uint8("trdp.dataset.thms_life_signal_hl", "THMS Life Signal HL", base.DEC)
local f_dataset_thms_life_signal_lh = ProtoField.uint8("trdp.dataset.thms_life_signal_lh", "THMS Life Signal LH", base.DEC)
local f_dataset_thms_life_signal_ll = ProtoField.uint8("trdp.dataset.thms_life_signal_ll", "THMS Life Signal LL", base.DEC)

-- THMS请求和系统状态信号字段 (字节4)
local f_dataset_thms_power_on_request_received = ProtoField.bool("trdp.dataset.thms_power_on_request_received", "Power ON THMS request received", 8, nil, 0x80)
local f_dataset_thms_on_system_state = ProtoField.bool("trdp.dataset.thms_on_system_state", "THMS ON system state", 8, nil, 0x40)
local f_dataset_thms_power_off_request_received = ProtoField.bool("trdp.dataset.thms_power_off_request_received", "Power OFF THMS request received", 8, nil, 0x20)
local f_dataset_thms_off_system_state = ProtoField.bool("trdp.dataset.thms_off_system_state", "THMS OFF system state", 8, nil, 0x10)
local f_dataset_thms_reserved_byte4_b3 = ProtoField.bool("trdp.dataset.thms_reserved_byte4_b3", "Reserved b3", 8, nil, 0x08)
local f_dataset_thms_reserved_byte4_b2 = ProtoField.bool("trdp.dataset.thms_reserved_byte4_b2", "Reserved b2", 8, nil, 0x04)
local f_dataset_thms_reserved_byte4_b1 = ProtoField.bool("trdp.dataset.thms_reserved_byte4_b1", "Reserved b1", 8, nil, 0x02)
local f_dataset_thms_reserved_byte4_b0 = ProtoField.bool("trdp.dataset.thms_reserved_byte4_b0", "Reserved b0", 8, nil, 0x01)

-- THMS保留字节字段 (字节5)
local f_dataset_thms_reserved_byte5 = ProtoField.uint8("trdp.dataset.thms_reserved_byte5", "Reserved Byte 5", base.HEX)

-- THMS自检结果字段 (字节6)
local f_dataset_thms_self_test_result = ProtoField.uint8("trdp.dataset.thms_self_test_result", "THMS Self Test Result", base.DEC, {
    [0] = "THMS Not Self Tested",
    [1] = "THMS Self Test Passed",
    [2] = "THMS Self Test Failed",
    [3] = "THMS Self Test In Progress"
})

-- THMS模块故障标志字段 (字节7)
local f_dataset_left_3D_module_failure = ProtoField.bool("trdp.dataset.left_3D_module_failure","Left 3D module failure", 8, nil, 0x80)
local f_dataset_middle_3D_module_failure = ProtoField.bool("trdp.dataset.middle_3D_module_failure","Middle 3D module failure", 8, nil, 0x40)
local f_dataset_right_3D_module_failure = ProtoField.bool("trdp.dataset.right_3D_module_failure","Right 3D module failure", 8, nil, 0x20)
local f_dataset_left_2D_module_failure = ProtoField.bool("trdp.dataset.left_2D_module_failure","Left 2D module failure", 8, nil, 0x10)
local f_dataset_middle_2D_module_failure = ProtoField.bool("trdp.dataset.middle_2D_module_failure","Middle 2D module failure", 8, nil, 0x08)
local f_dataset_right_2D_module_failure = ProtoField.bool("trdp.dataset.right_2D_module_failure","Right 2D module failure", 8, nil, 0x04)
local f_dataset_thms_software_failure = ProtoField.bool("trdp.dataset.thms_software_failure","THMS software failure", 8, nil, 0x02)
local f_dataset_thms_reserved_byte7_b7 = ProtoField.bool("trdp.dataset.thms_reserved_byte7_b7","Reserved byte7 b7", 8, nil, 0x01)

-- THMS序列号字段 (字节8-37)
local f_dataset_left_3D_module_sn = ProtoField.bytes("trdp.dataset.left_3D_module_sn", "Left 3D Module SN", 5, base.SPACE)
local f_dataset_middle_3D_module_sn = ProtoField.bytes("trdp.dataset.middle_3D_module_sn", "Middle 3D Module SN", 5, base.SPACE)
local f_dataset_right_3D_module_sn = ProtoField.bytes("trdp.dataset.right_3D_module_sn", "Right 3D Module SN", 5, base.SPACE)
local f_dataset_left_2D_module_sn = ProtoField.bytes("trdp.dataset.left_2D_module_sn", "Left 2D Module SN", 5, base.SPACE)
local f_dataset_middle_2D_module_sn = ProtoField.bytes("trdp.dataset.middle_2D_module_sn", "Middle 2D Module SN", 5, base.SPACE)
local f_dataset_right_2D_module_sn = ProtoField.bytes("trdp.dataset.right_2D_module_sn", "Right 2D Module SN", 5, base.SPACE)

-- THMS缺陷类ID字段 (字节38-39)
local f_dataset_thms_defect_class_id = ProtoField.uint16("trdp.dataset.thms_defect_class_id", "THMS Defect Class ID", base.DEC, nil, 0, "Network Byte Order")

-- THMS告警严重程度字段 (字节40)
local f_dataset_thms_alarm_severity = ProtoField.uint8("trdp.dataset.thms_alarm_severity", "THMS Alarm Severity", base.DEC, {
    [0] = "Low",
    [1] = "Medium",
    [2] = "High",
    [3] = "Critical"
})

-- THMS缺陷轨道侧字段 (字节41)
local f_dataset_defect_track_side = ProtoField.uint8("trdp.dataset.defect_track_side", "Defect Track Side", base.HEX, {
    [0x01] = "Left Side Left",
    [0x02] = "Left Side Right",
    [0x04] = "Right Side Left",
    [0x08] = "Right Side Right",
    [0x10] = "Middle"
})

-- THMS告警位置字段 (字节42-45)
local f_dataset_thms_alarm_location = ProtoField.uint32("trdp.dataset.thms_alarm_location", "THMS Alarm Location (mm)", base.DEC, nil, 0, "Network Byte Order")

-- THMS轨道电路字段 (字节46-51)
local f_dataset_thms_track_circuit = ProtoField.string("trdp.dataset.thms_track_circuit", "THMS Track Circuit", 6, base.ASCII)

-- THMS软件版本字段 (字节52-53)
local f_dataset_thms_software_version_high = ProtoField.uint8("trdp.dataset.thms_software_version_high", "THMS Software Version H (1-99)", base.DEC)
local f_dataset_thms_software_version_low = ProtoField.uint8("trdp.dataset.thms_software_version_low", "THMS Software Version L (1-99)", base.DEC)

-- THMS保留字节字段 (字节54-99)
local f_dataset_thms_reserved_byte54_99 = ProtoField.bytes("trdp.dataset.thms_reserved_byte54_99", "THMS Reserved Bytes 54-99",
46, base.SPACE)


-- 将字段添加到协议
trdp_proto.fields = {
    f_sequence_counter, f_protocol_version_high, f_protocol_version_low, f_message_type, f_com_id,
    f_etb_topo_cnt, f_op_trn_topo_cnt, f_dataset_length, f_reply_comid,
    f_reserved, f_reply_ipaddress, f_header_fcs,
    -- CCU数据集字段
    f_dataset_ccu_lifesign, f_dataset_ccu_year, f_dataset_ccu_month, f_dataset_ccu_day,
    f_dataset_ccu_hour, f_dataset_ccu_minute, f_dataset_ccu_second,
    f_dataset_ccu_dt1_cab_activated, f_dataset_ccu_dt2_cab_activated,
    f_dataset_ccu_train_speed_valid, f_dataset_ccu_wheel_diameter_valid,
    f_dataset_ccu_time_setting, f_dataset_ccu_time_valid,
    f_dataset_ccu_backward, f_dataset_ccu_forward, f_dataset_ccu_left_door_open,
    f_dataset_ccu_right_door_open, f_dataset_ccu_left_door_close,
    f_dataset_ccu_right_door_close, f_dataset_ccu_all_door_closed,
    f_dataset_ccu_train_id, f_dataset_ccu_wheel_diameter, f_dataset_ccu_train_speed,
    f_dataset_ccu_mp1_pantograph, f_dataset_ccu_mp2_pantograph,
    f_dataset_ccu_train_arrived, f_dataset_ccu_skip_stop_announcement,
    f_dataset_ccu_line_voltage, f_dataset_ccu_line_current,
    f_dataset_ccu_generic_station, f_dataset_ccu_final_destination, f_dataset_ccu_next_station,
    f_dataset_ccu_power_on_ocrm, f_dataset_ccu_power_off_ocrm,
    f_dataset_ccu_power_on_thms, f_dataset_ccu_power_off_thms,
    f_dataset_ccu_ocrm_test, f_dataset_ccu_thms_static_test,
    f_dataset_ccu_reserved_byte4_5, f_dataset_ccu_reserved_byte15, f_dataset_ccu_reserved_byte18_21,
    f_dataset_ccu_reserved_byte22, f_dataset_ccu_reserved_byte23_31, f_dataset_ccu_reserved_byte36_37,
    f_dataset_ccu_reserved_byte44_47, f_dataset_ccu_reserved_byte58_67, f_dataset_ccu_reserved_byte71,
    f_dataset_ccu_reserved_byte72_99,
    f_dataset_ccu_car_1_load, f_dataset_ccu_car_2_load, f_dataset_ccu_car_3_load,
    f_dataset_ccu_car_4_load, f_dataset_ccu_car_5_load, f_dataset_ccu_car_6_load,
    -- OCRMS数据集字段
    f_dataset_ocrms_life_signal_hh, f_dataset_ocrms_life_signal_hl, f_dataset_ocrms_life_signal_lh, f_dataset_ocrms_life_signal_ll,
    f_dataset_ocrms_power_on_request_received, f_dataset_ocrms_ocrms_on_system_state,
    f_dataset_ocrms_power_off_request_received, f_dataset_ocrms_ocrms_off_system_state,
    f_dataset_ocrms_reserved_byte4_b3, f_dataset_ocrms_reserved_byte4_b2, f_dataset_ocrms_reserved_byte4_b1, f_dataset_ocrms_reserved_byte4_b0,
    f_dataset_ocrms_reserved_byte5, f_dataset_ocrms_self_test_result,
    f_dataset_ocrms_reserved_byte7_b7, f_dataset_ocrms_arcing_detection_failure, f_dataset_ocrms_video_surveillance_failure,
    f_dataset_ocrms_temperature_detection_failure, f_dataset_ocrms_geometric_parameters_failure,
    f_dataset_ocrms_left_vibration_compensation_failure, f_dataset_ocrms_right_vibration_compensation_failure,
    f_dataset_ocrms_software_failure,
    f_dataset_ocrms_arcing_detection_sn, f_dataset_ocrms_video_surveillance_sn, f_dataset_ocrms_temperature_detection_sn,
    f_dataset_ocrms_geometric_parameters_sn, f_dataset_ocrms_left_vibration_compensation_sn, f_dataset_ocrms_right_vibration_compensation_sn,
    f_dataset_ocrms_defect_class_id, f_dataset_ocrms_alarm_severity, f_dataset_ocrms_reserved_byte41,
    f_dataset_ocrms_alarm_location, f_dataset_ocrms_track_circuit, f_dataset_ocrms_wearing_value,
    f_dataset_ocrms_alarm_location_pmd, f_dataset_ocrms_track_circuit_pmd,
    f_dataset_ocrms_software_version_high, f_dataset_ocrms_software_version_low,
    f_dataset_ocrms_reserved_byte65_99,
    -- THMS数据集字段
    f_dataset_thms_life_signal_hh, f_dataset_thms_life_signal_hl, f_dataset_thms_life_signal_lh, f_dataset_thms_life_signal_ll,
    f_dataset_thms_power_on_request_received, f_dataset_thms_on_system_state,
    f_dataset_thms_power_off_request_received, f_dataset_thms_off_system_state,
    f_dataset_thms_reserved_byte4_b3, f_dataset_thms_reserved_byte4_b2, f_dataset_thms_reserved_byte4_b1, f_dataset_thms_reserved_byte4_b0,
    f_dataset_thms_reserved_byte5, f_dataset_thms_self_test_result,
    f_dataset_left_3D_module_failure, f_dataset_middle_3D_module_failure, f_dataset_right_3D_module_failure,
    f_dataset_left_2D_module_failure, f_dataset_middle_2D_module_failure, f_dataset_right_2D_module_failure,
    f_dataset_thms_software_failure, f_dataset_thms_reserved_byte7_b7,
    f_dataset_left_3D_module_sn, f_dataset_middle_3D_module_sn, f_dataset_right_3D_module_sn,
    f_dataset_left_2D_module_sn, f_dataset_middle_2D_module_sn, f_dataset_right_2D_module_sn,
    f_dataset_thms_defect_class_id, f_dataset_thms_alarm_severity, f_dataset_defect_track_side,
    f_dataset_thms_alarm_location, f_dataset_thms_track_circuit,
    f_dataset_thms_software_version_high, f_dataset_thms_software_version_low,
    f_dataset_thms_reserved_byte54_99
}

-- 解析CCU数据集的函数
local function parse_ccu_dataset(buffer, offset, dataset_subtree)
    -- 解析生命信号 (字节 0-3) - 32位无符号整数
    local lifesign = buffer(offset, 4):uint()
    dataset_subtree:add(f_dataset_ccu_lifesign, buffer(offset, 4))
    offset = offset + 4
    
    -- 保留字节 (字节 4-5)
    dataset_subtree:add(f_dataset_ccu_reserved_byte4_5, buffer(offset, 2))
    offset = offset + 2
    
    -- 日期时间 (字节 6-11)
    local year = buffer(offset, 1):uint()
    local month = buffer(offset + 1, 1):uint()
    local day = buffer(offset + 2, 1):uint()
    local hour = buffer(offset + 3, 1):uint()
    local minute = buffer(offset + 4, 1):uint()
    local second = buffer(offset + 5, 1):uint()
    dataset_subtree:add(f_dataset_ccu_year, buffer(offset, 1))
    dataset_subtree:add(f_dataset_ccu_month, buffer(offset + 1, 1))
    dataset_subtree:add(f_dataset_ccu_day, buffer(offset + 2, 1))
    dataset_subtree:add(f_dataset_ccu_hour, buffer(offset + 3, 1))
    dataset_subtree:add(f_dataset_ccu_minute, buffer(offset + 4, 1))
    dataset_subtree:add(f_dataset_ccu_second, buffer(offset + 5, 1))
    offset = offset + 6
    
    -- 状态标志 (字节 12)
    local status_flags = buffer(offset, 1):uint()
    local status_subtree = dataset_subtree:add(buffer(offset, 1), "Status Flags")
    status_subtree:add(f_dataset_ccu_dt1_cab_activated, buffer(offset, 1))
    status_subtree:add(f_dataset_ccu_dt2_cab_activated, buffer(offset, 1))
    status_subtree:add(f_dataset_ccu_train_speed_valid, buffer(offset, 1))
    status_subtree:add(f_dataset_ccu_wheel_diameter_valid, buffer(offset, 1))
    status_subtree:add(f_dataset_ccu_time_setting, buffer(offset, 1))
    status_subtree:add(f_dataset_ccu_time_valid, buffer(offset, 1))
    offset = offset + 1
    
    -- 车门命令 (字节 13)
    local door_commands = buffer(offset, 1):uint()
    local door_subtree = dataset_subtree:add(buffer(offset, 1), "Door Commands")
    door_subtree:add(f_dataset_ccu_backward, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_forward, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_left_door_open, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_right_door_open, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_left_door_close, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_right_door_close, buffer(offset, 1))
    door_subtree:add(f_dataset_ccu_all_door_closed, buffer(offset, 1))
    offset = offset + 1
    
    -- 列车ID (字节 14)
    local train_id = buffer(offset, 1):uint()
    dataset_subtree:add(f_dataset_ccu_train_id, buffer(offset, 1))
    offset = offset + 1
    
    -- 保留字节 (字节 15)
    dataset_subtree:add(f_dataset_ccu_reserved_byte15, buffer(offset, 1))
    offset = offset + 1
    
    -- 轮径 (字节 16-17) - 16位无符号整数
    local wheel_diameter = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_wheel_diameter, buffer(offset, 2))
    offset = offset + 2
    
    -- 保留字节 (字节 18-21)
    dataset_subtree:add(f_dataset_ccu_reserved_byte18_21, buffer(offset, 4))
    offset = offset + 4
    
    -- 状态标志2 (字节 22) - 保留
    dataset_subtree:add(f_dataset_ccu_reserved_byte22, buffer(offset, 1))
    offset = offset + 1
    
    -- 保留字节 (字节 23-31)
    dataset_subtree:add(f_dataset_ccu_reserved_byte23_31, buffer(offset, 9))
    offset = offset + 9
    
    -- 列车速度 (字节 32-33) - 16位无符号整数
    local train_speed = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_train_speed, buffer(offset, 2))
    offset = offset + 2
    
    -- 受电弓状态 (字节 34)
    local pantograph_status = buffer(offset, 1):uint()
    local pantograph_subtree = dataset_subtree:add(buffer(offset, 1), "Pantograph Status")
    pantograph_subtree:add(f_dataset_ccu_mp1_pantograph, buffer(offset, 1))
    pantograph_subtree:add(f_dataset_ccu_mp2_pantograph, buffer(offset, 1))
    offset = offset + 1
    
    -- 列车事件 (字节 35)
    local train_events = buffer(offset, 1):uint()
    local events_subtree = dataset_subtree:add(buffer(offset, 1), "Train Events")
    events_subtree:add(f_dataset_ccu_train_arrived, buffer(offset, 1))
    events_subtree:add(f_dataset_ccu_skip_stop_announcement, buffer(offset, 1))
    offset = offset + 1
    
    -- 保留字节 (字节 36-37)
    dataset_subtree:add(f_dataset_ccu_reserved_byte36_37, buffer(offset, 2))
    offset = offset + 2
    
    -- 乘客负载 (字节 38-43) - 6个车厢
    local passenger_subtree = dataset_subtree:add(buffer(offset, 6), "Passenger Loading")
    passenger_subtree:add(f_dataset_ccu_car_1_load, buffer(offset, 1))
    passenger_subtree:add(f_dataset_ccu_car_2_load, buffer(offset + 1, 1))
    passenger_subtree:add(f_dataset_ccu_car_3_load, buffer(offset + 2, 1))
    passenger_subtree:add(f_dataset_ccu_car_4_load, buffer(offset + 3, 1))
    passenger_subtree:add(f_dataset_ccu_car_5_load, buffer(offset + 4, 1))
    passenger_subtree:add(f_dataset_ccu_car_6_load, buffer(offset + 5, 1))
    offset = offset + 6
    
    -- 保留字节 (字节 44-47)
    dataset_subtree:add(f_dataset_ccu_reserved_byte44_47, buffer(offset, 4))
    offset = offset + 4
    
    -- 线路电压 (字节 48-49) - 16位无符号整数
    local line_voltage = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_line_voltage, buffer(offset, 2))
    offset = offset + 2
    
    -- 线路电流 (字节 50-51) - 16位有符号整数
    local line_current = buffer(offset, 2):int()
    dataset_subtree:add(f_dataset_ccu_line_current, buffer(offset, 2))
    offset = offset + 2
    
    -- 通用站台代码 (字节 52-53) - 16位无符号整数
    local generic_station = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_generic_station, buffer(offset, 2))
    offset = offset + 2
    
    -- 最终目的地代码 (字节 54-55) - 16位无符号整数
    local final_destination = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_final_destination, buffer(offset, 2))
    offset = offset + 2
    
    -- 下一站代码 (字节 56-57) - 16位无符号整数
    local next_station = buffer(offset, 2):uint()
    dataset_subtree:add(f_dataset_ccu_next_station, buffer(offset, 2))
    offset = offset + 2
    
    -- 保留字节 (字节 58-67)
    dataset_subtree:add(f_dataset_ccu_reserved_byte58_67, buffer(offset, 10))
    offset = offset + 10
    
    -- OCRMS电源命令 (字节 68)
    local ocrm_commands = buffer(offset, 1):uint()
    local ocrm_subtree = dataset_subtree:add(buffer(offset, 1), "OCRMS Commands")
    ocrm_subtree:add(f_dataset_ccu_power_on_ocrm, buffer(offset, 1))
    ocrm_subtree:add(f_dataset_ccu_power_off_ocrm, buffer(offset, 1))
    offset = offset + 1
    
    -- THMS电源命令 (字节 69)
    local thms_commands = buffer(offset, 1):uint()
    local thms_subtree = dataset_subtree:add(buffer(offset, 1), "THMS Commands")
    thms_subtree:add(f_dataset_ccu_power_on_thms, buffer(offset, 1))
    thms_subtree:add(f_dataset_ccu_power_off_thms, buffer(offset, 1))
    offset = offset + 1
    
    -- 测试命令 (字节 70)
    local test_commands = buffer(offset, 1):uint()
    local test_subtree = dataset_subtree:add(buffer(offset, 1), "Test Commands")
    test_subtree:add(f_dataset_ccu_ocrm_test, buffer(offset, 1))
    test_subtree:add(f_dataset_ccu_thms_static_test, buffer(offset, 1))
    offset = offset + 1
    
    -- 保留字节 (字节 71)
    dataset_subtree:add(f_dataset_ccu_reserved_byte71, buffer(offset, 1))
    offset = offset + 1
    
    -- 保留字节 (字节 72-99)
    dataset_subtree:add(f_dataset_ccu_reserved_byte72_99, buffer(offset, 28))
    offset = offset + 28
    
    return offset
end

-- 解析OCRMS数据集的函数
local function parse_ocrms_dataset(buffer, offset, dataset_subtree)
    -- 解析OCRMS生命信号 (字节 0-3) - 4个8位无符号整数
    local life_signal_subtree = dataset_subtree:add(buffer(offset, 4), "OCRMS Life Signal")
    life_signal_subtree:add(f_dataset_ocrms_life_signal_hh, buffer(offset, 1))
    life_signal_subtree:add(f_dataset_ocrms_life_signal_hl, buffer(offset + 1, 1))
    life_signal_subtree:add(f_dataset_ocrms_life_signal_lh, buffer(offset + 2, 1))
    life_signal_subtree:add(f_dataset_ocrms_life_signal_ll, buffer(offset + 3, 1))
    offset = offset + 4
    
    -- 解析OCRMS请求和系统状态信号 (字节 4) - 位级别定义
    local ocrms_status = buffer(offset, 1):uint()
    local ocrms_status_subtree = dataset_subtree:add(buffer(offset, 1), "OCRMS Request and System Status")
    ocrms_status_subtree:add(f_dataset_ocrms_power_on_request_received, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_ocrms_on_system_state, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_power_off_request_received, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_ocrms_off_system_state, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_reserved_byte4_b3, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_reserved_byte4_b2, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_reserved_byte4_b1, buffer(offset, 1))
    ocrms_status_subtree:add(f_dataset_ocrms_reserved_byte4_b0, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析保留字节 (字节 5)
    dataset_subtree:add(f_dataset_ocrms_reserved_byte5, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析自检结果 (字节 6)
    dataset_subtree:add(f_dataset_ocrms_self_test_result, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析模块故障标志 (字节 7) - 位级别定义
    local failure_flags = buffer(offset, 1):uint()
    local failure_subtree = dataset_subtree:add(buffer(offset, 1), "Module Failure Flags")
    failure_subtree:add(f_dataset_ocrms_reserved_byte7_b7, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_arcing_detection_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_video_surveillance_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_temperature_detection_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_geometric_parameters_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_left_vibration_compensation_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_right_vibration_compensation_failure, buffer(offset, 1))
    failure_subtree:add(f_dataset_ocrms_software_failure, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析序列号 (字节 8-37)
    local sn_subtree = dataset_subtree:add(buffer(offset, 30), "Module Serial Numbers")
    sn_subtree:add(f_dataset_ocrms_arcing_detection_sn, buffer(offset, 5))
    sn_subtree:add(f_dataset_ocrms_video_surveillance_sn, buffer(offset + 5, 5))
    sn_subtree:add(f_dataset_ocrms_temperature_detection_sn, buffer(offset + 10, 5))
    sn_subtree:add(f_dataset_ocrms_geometric_parameters_sn, buffer(offset + 15, 5))
    sn_subtree:add(f_dataset_ocrms_left_vibration_compensation_sn, buffer(offset + 20, 5))
    sn_subtree:add(f_dataset_ocrms_right_vibration_compensation_sn, buffer(offset + 25, 5))
    offset = offset + 30
    
    -- 解析缺陷类ID (字节 38-39) - 16位无符号整数
    dataset_subtree:add(f_dataset_ocrms_defect_class_id, buffer(offset, 2))
    offset = offset + 2
    
    -- 解析告警严重程度 (字节 40)
    dataset_subtree:add(f_dataset_ocrms_alarm_severity, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析保留字节 (字节 41)
    dataset_subtree:add(f_dataset_ocrms_reserved_byte41, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析告警位置 (字节 42-45) - 32位无符号整数，单位mm
    dataset_subtree:add(f_dataset_ocrms_alarm_location, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析轨道电路 (字节 46-51) - 6字节ASCII字符串
    dataset_subtree:add(f_dataset_ocrms_track_circuit, buffer(offset, 6))
    offset = offset + 6
    
    -- 解析磨损值 (字节 52-53) - 16位无符号整数，100=1
    dataset_subtree:add(f_dataset_ocrms_wearing_value, buffer(offset, 2))
    offset = offset + 2
    
    -- 解析告警位置PMD (字节 54-56) - 24位无符号整数，单位mm
    dataset_subtree:add(f_dataset_ocrms_alarm_location_pmd, buffer(offset, 3))
    offset = offset + 3
    
    -- 解析轨道电路PMD (字节 57-62) - 6字节ASCII字符串
    dataset_subtree:add(f_dataset_ocrms_track_circuit_pmd, buffer(offset, 6))
    offset = offset + 6
    
    -- 解析软件版本 (字节 63-64)
    local version_subtree = dataset_subtree:add(buffer(offset, 2), "Software Version")
    version_subtree:add(f_dataset_ocrms_software_version_high, buffer(offset, 1))
    version_subtree:add(f_dataset_ocrms_software_version_low, buffer(offset + 1, 1))
    offset = offset + 2
    
    -- 解析保留字节 (字节 65-99)
    dataset_subtree:add(f_dataset_ocrms_reserved_byte65_99, buffer(offset, 35))
    offset = offset + 35
    
    return offset
end

-- 解析THMS数据集的函数
local function parse_thms_dataset(buffer, offset, dataset_subtree)
    -- 解析THMS生命信号 (字节 0-3) - 4个8位无符号整数
    local thms_life_signal_subtree = dataset_subtree:add(buffer(offset, 4), "THMS Life Signal")
    thms_life_signal_subtree:add(f_dataset_thms_life_signal_hh, buffer(offset, 1))
    thms_life_signal_subtree:add(f_dataset_thms_life_signal_hl, buffer(offset + 1, 1))
    thms_life_signal_subtree:add(f_dataset_thms_life_signal_lh, buffer(offset + 2, 1))
    thms_life_signal_subtree:add(f_dataset_thms_life_signal_ll, buffer(offset + 3, 1))
    offset = offset + 4
    
    -- 解析THMS请求和系统状态信号 (字节 4) - 位级别定义
    local thms_status = buffer(offset, 1):uint()
    local thms_status_subtree = dataset_subtree:add(buffer(offset, 1), "THMS Request and System Status")
    thms_status_subtree:add(f_dataset_thms_power_on_request_received, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_on_system_state, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_power_off_request_received, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_off_system_state, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_reserved_byte4_b3, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_reserved_byte4_b2, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_reserved_byte4_b1, buffer(offset, 1))
    thms_status_subtree:add(f_dataset_thms_reserved_byte4_b0, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS保留字节 (字节 5)
    dataset_subtree:add(f_dataset_thms_reserved_byte5, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS自检结果 (字节 6)
    dataset_subtree:add(f_dataset_thms_self_test_result, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS模块故障标志 (字节 7) - 位级别定义
    local thms_failure_flags = buffer(offset, 1):uint()
    local thms_failure_subtree = dataset_subtree:add(buffer(offset, 1), "THMS Module Failure Flags")
    thms_failure_subtree:add(f_dataset_left_3D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_middle_3D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_right_3D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_left_2D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_middle_2D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_right_2D_module_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_thms_software_failure, buffer(offset, 1))
    thms_failure_subtree:add(f_dataset_thms_reserved_byte7_b7, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS序列号 (字节 8-37)
    local thms_sn_subtree = dataset_subtree:add(buffer(offset, 30), "THMS Module Serial Numbers")
    thms_sn_subtree:add(f_dataset_left_3D_module_sn, buffer(offset, 5))
    thms_sn_subtree:add(f_dataset_middle_3D_module_sn, buffer(offset + 5, 5))
    thms_sn_subtree:add(f_dataset_right_3D_module_sn, buffer(offset + 10, 5))
    thms_sn_subtree:add(f_dataset_left_2D_module_sn, buffer(offset + 15, 5))
    thms_sn_subtree:add(f_dataset_middle_2D_module_sn, buffer(offset + 20, 5))
    thms_sn_subtree:add(f_dataset_right_2D_module_sn, buffer(offset + 25, 5))
    offset = offset + 30
    
    -- 解析THMS缺陷类ID (字节 38-39) - 16位无符号整数
    dataset_subtree:add(f_dataset_thms_defect_class_id, buffer(offset, 2))
    offset = offset + 2
    
    -- 解析THMS告警严重程度 (字节 40)
    dataset_subtree:add(f_dataset_thms_alarm_severity, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS缺陷轨道侧 (字节 41)
    dataset_subtree:add(f_dataset_defect_track_side, buffer(offset, 1))
    offset = offset + 1
    
    -- 解析THMS告警位置 (字节 42-45) - 32位无符号整数，单位mm
    dataset_subtree:add(f_dataset_thms_alarm_location, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析THMS轨道电路 (字节 46-51) - 6字节ASCII字符串
    dataset_subtree:add(f_dataset_thms_track_circuit, buffer(offset, 6))
    offset = offset + 6
    
    -- 解析THMS软件版本 (字节 52-53)
    local thms_version_subtree = dataset_subtree:add(buffer(offset, 2), "THMS Software Version")
    thms_version_subtree:add(f_dataset_thms_software_version_high, buffer(offset, 1))
    thms_version_subtree:add(f_dataset_thms_software_version_low, buffer(offset + 1, 1))
    offset = offset + 2
    
    -- 解析THMS保留字节 (字节 54-99)
    dataset_subtree:add(f_dataset_thms_reserved_byte54_99, buffer(offset, 46))
    offset = offset + 46
    
    return offset
end

-- 协议解析函数
function trdp_proto.dissector(buffer, pinfo, tree)
    local length = buffer:len()
    if length < 140 then 
        pinfo.cols.info = "TRDP: Invalid packet (too short)"
        return 
    end
    
    pinfo.cols.protocol = "TRDP"
    
    -- 创建协议树
    local subtree = tree:add(trdp_proto, buffer(), "TRDP Protocol")
    
    local offset = 0
    
    -- 解析序列计数器 (4字节)
    local sequence_counter = buffer(offset, 4):uint()
    subtree:add(f_sequence_counter, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析协议版本和消息类型 (4字节)
    local version_type = buffer(offset, 4):uint()
    local protocol_version = bit.rshift(version_type, 16)
    local message_type = bit.band(version_type, 0xFFFF)
    
    local version_type_subtree = subtree:add(buffer(offset, 4), "Protocol Version + Message Type")
    -- 解析协议版本高字节和低字节
    local protocol_version_high = bit.rshift(protocol_version, 8)
    local protocol_version_low = bit.band(protocol_version, 0xFF)
    version_type_subtree:add(f_protocol_version_high, buffer(offset, 1))
    version_type_subtree:add(f_protocol_version_low, buffer(offset + 1, 1))
    version_type_subtree:add(f_message_type, buffer(offset + 2, 2))
    offset = offset + 4
    
    -- 解析通信ID (4字节)
    local com_id = buffer(offset, 4):uint()
    subtree:add(f_com_id, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析ETB拓扑计数器 (4字节)
    local etb_topo_cnt = buffer(offset, 4):uint()
    subtree:add(f_etb_topo_cnt, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析操作列车拓扑计数器 (4字节)
    local op_trn_topo_cnt = buffer(offset, 4):uint()
    subtree:add(f_op_trn_topo_cnt, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析数据集长度 (4字节)
    local dataset_length = buffer(offset, 4):uint()
    subtree:add(f_dataset_length, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析回复通信ID (4字节)
    local reply_comid = buffer(offset, 4):uint()
    subtree:add(f_reply_comid, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析保留字段 (4字节)
    local reserved = buffer(offset, 4):uint()
    subtree:add(f_reserved, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析回复IP地址 (4字节)
    local reply_ip = buffer(offset, 4):uint()
    subtree:add(f_reply_ipaddress, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析头部校验码 (4字节) - 小端序
    local header_fcs = buffer(offset, 4):le_uint()
    subtree:add(f_header_fcs, buffer(offset, 4))
    offset = offset + 4
    
    -- 解析数据集部分 (100字节)
    if length >= 140 then
        local dataset_subtree = subtree:add(buffer(offset, 100), "TRDP Dataset")
        
        -- 根据comid选择不同的数据集解析逻辑
        if com_id == 22150 or com_id == 22151 then
            -- OCRMS数据集解析
            dataset_subtree:set_text("TRDP Dataset (OCRMS)")
            offset = parse_ocrms_dataset(buffer, offset, dataset_subtree)
        elseif com_id == 21120 or com_id == 21121 then
            -- THMS数据集解析
            dataset_subtree:set_text("TRDP Dataset (THMS)")
            offset = parse_thms_dataset(buffer, offset, dataset_subtree)
        elseif com_id == 10000 or com_id == 10001 then
            -- CCU数据集解析 (默认)
            dataset_subtree:set_text("TRDP Dataset (CCU)")
            offset = parse_ccu_dataset(buffer, offset, dataset_subtree)
        else
            -- 未知数据集类型，使用CCU解析作为默认
            dataset_subtree:set_text("TRDP Dataset (Unknown - Using CCU)")
            offset = parse_ccu_dataset(buffer, offset, dataset_subtree)
        end
    end
    
    -- 设置信息列显示
    local msg_type_str = ""
    if message_type == 0x5072 then
        msg_type_str = "Pr"
    elseif message_type == 0x5070 then
        msg_type_str = "Pp"
    elseif message_type == 0x5064 then
        msg_type_str = "Pd"
    elseif message_type == 0x5065 then
        msg_type_str = "Pe"
    else
        msg_type_str = string.format("0x%04X", message_type)
    end
    
    -- 格式化IP地址显示
    local ip_str = string.format("%d.%d.%d.%d", 
                                bit.rshift(reply_ip, 24) % 256,
                                bit.rshift(reply_ip, 16) % 256,
                                bit.rshift(reply_ip, 8) % 256,
                                reply_ip % 256)
    
    local info_text = string.format("TRDP %s (Seq: %d, ComID: %d, ReplyIP: %s)", 
                                   msg_type_str, sequence_counter, com_id, ip_str)
    
    pinfo.cols.info = info_text
end

-- 注册协议到端口
local udp_port = DissectorTable.get("udp.port")
udp_port:add(17224, trdp_proto) -- TRDP默认端口
--备用 udp_port:add(17225, trdp_proto) -- TRDP备用端口
--备用 udp_port:add(17226, trdp_proto) -- TRDP扩展端口

-- 也可以注册到TCP端口
--备用 local tcp_port = DissectorTable.get("tcp.port")
--备用 tcp_port:add(17224, trdp_proto)
--备用 tcp_port:add(17225, trdp_proto)
--备用 tcp_port:add(17226, trdp_proto)

print("TRDP真实协议解析器已加载")
