import re
from zlib import crc32

from PySide6.QtCore import Signal, QObject

from action.Fcs32Calculator import Fcs32Calculator


class MsgPackAction(QObject):
    seq_ready = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.msg = {}
        self.tail_data_before = {}
        self.header_data_before = {}
        self.header_data_diff_before = {}

        self.tail_data_after = b''
        self.header_data_after = b''
        self.header_data_diff_after = b''

        self.header_hex = 0x0
        self.global_seq = 0
        # 消息实际长度
        self.msg_pack_length = 0
        self.defined_msg_length = 0

    def pack_msg(self, header_data_before, tail_data_before, header_data_diff_before=None):
        print("-----------开始打包----------")
        # print(f"header_data_before: {header_data_before}, tail_data_before: {tail_data_before}")
        # self.header_data_before = header_data_before
        # self.header_data_diff_before = header_data_diff_before
        self.tail_data_before = tail_data_before
        self.tail_data_after = b''
        self.header_data_after = b''
        self.header_data_diff_after = b''

        self.header_data_after = self.pack_head(header_data_before)
        if header_data_diff_before is not None:
            self.header_data_diff_after = self.pack_head(header_data_diff_before)
        # 消息计数
        self.global_seq += 1

        '''自定义结构部分打包'''
        # datetime_length = datetime[1] - datetime[0]
        # print(f"self.tail_data_after: {self.tail_data_after}")
        for index, (key, values) in enumerate(self.tail_data_before.items()):
            offset = [0,0]
            if re.search(r"[-]", key) is not None:
            # if index != int(key):
                offset[0] = int(re.split(r"[-]",key)[0])
                offset[1] = int(re.split(r"[-]",key)[1])
                offset_total = offset[1] - offset[0] + 1
                print(f"包含{offset_total}个字段，进行字段补充...")
                self.tail_data_after += b'\x00' * offset_total
            else:
                # print("单个字段追加...")
                if len(values) > 4:
                    bit_value = ''
                    for sub_index, (sub_key, sub_values) in enumerate(values[4].items()):
                        bit_value += sub_values[3] if sub_values[3]!='' else '0'
                    bit_value = bit_value.ljust((len(bit_value)) // 8 * 8, '0')
                    values[3] = int(bit_value, 2)
                # if len(datetime) == 6:               # 时间占6个字节：年月日时分秒各一个字节
                # print(f"追加{values[3]}")
                self.tail_data_after += int(values[3]).to_bytes(1, byteorder='big') if values[3]!='' else b'\x00'
        # print(f"self.tail_data_after: {self.tail_data_after}")
        self.data_after = self.header_data_after + self.tail_data_after

        if header_data_diff_before is not None:
            self.data_diff_after = self.header_data_after + self.tail_data_after
        else:
            self.data_diff_after = None

        print(f"self.data_after: {self.data_after}")

        self.set_pack_msg_length()
        # self.msg_ready.emit(self.data_after)
        print("-----------打包结束----------")
        return self.data_after, self.data_diff_after

    def pack_head(self, head_data_before):
        header_data_after = b''

        for index, (key, value) in enumerate(head_data_before.items()):
            '''头部结构打包'''
            opt_index = int(value[3])
            if opt_index == 0 or opt_index == 1:              # header option 选择None
                if len(value[2].split(',')) != value[1]:
                    # 按照大端序打包
                    for i in range(value[1]):
                        header_list = int(value[2].split(',')[0]) >> (8 * (value[1] - i - 1)) & 0xFF
                        header_data_after += header_list.to_bytes(1, byteorder='big')
                else:
                    header_list = value[2].split(',')
                    for i in range(value[1]):
                        header_data_after += int(header_list[i]).to_bytes(1, byteorder='big') if header_list[i] != '' else b'\x00'
            elif opt_index == 2:            # header option 选择自增
                for i in range(value[1]):
                    header_data_after += (self.global_seq >> (8 * (value[1] - i - 1)) & 0xFF).to_bytes(1, byteorder='big')
                # 把头部seq计数发出去，用于界面更新显示该字段内容
                self.seq_ready.emit(self.global_seq, index)
            elif opt_index == 3:            # header option 选择CRC头部
                cal = Fcs32Calculator()
                crc32_header = cal.fcs32(header_data_after)
                for i in range(value[1]):
                    crc = crc32_header >> (8 * i) & 0xFF
                    header_data_after += crc.to_bytes(1, byteorder='little')
            # elif opt_index == 4:            # header option 选择CRC应用数据
            #     pass
            # elif opt_index == 5:            # header option 选择CRC整包
            #     pass
            else:
                print(f"非法选项！{opt_index}")
        print(f"打包后的头部数据： {header_data_after}")
        return header_data_after

    def set_defined_msg_length(self, defined_length):
        self.defined_msg_length = defined_length

    def set_pack_msg_length(self):
        self.pack_msg_length = len(self.data_after)
        print(f"length: {self.pack_msg_length}")

    def check_msg_length(self):
        pass

    def generate_increasing_time_six_byte(self):
        pass

# if __name__ == "__main__":
#     msgpack_action = MsgPackAction()
#     data1 = {'SequenceCounter': [['0', '1', '2', '3'], 4, '0,0,0,0', 0], 'ProtocolVersion': [['4', '5'], 2, '0,0', 0], 'MsgType': [['6', '7'], 2, '65004', 0], 'ComId': [['8', '9', '10', '11'], 4, '10001', 0], 'etbTopoCnt': [['12', '13', '14', '15'], 4, '0,0,0,0', 0], 'opTrnTopoCnt': [['16', '17', '18', '19'], 4, '0,0,0,0', 0], 'DatasetLength': [['20', '21', '22', '23'], 4, '0,0,0,0', 0], 'Reserved': [['24', '25', '26', '27'], 4, '0,0,0,0', 0], 'ReplyComId': [['28', '29', '30', '31'], 4, '0,0,0,0', 0], 'ReplyAddress': [['32', '33', '34', '35'], 4, '0,0,0,0', 0], 'HeaderFCS': [['36', '37', '38', '39'], 4, '0,0,0,0', 0]}
#     data2 = {'0': ['THMS Life Signal HH', '8', 'UDINT', '1'], '1': ['THMS Life Signal HL', '8', '', '2'], '2': ['THMS Life Signal LH', '8', '', ''], '3': ['THMS Life Signal LL', '8', '', ''], '4': ['', '8', '', '', {'b7': ['Power ON THMS request received', '1', 'BOOL', ''], 'b6': ['THMS ON system state', '1', 'BOOL', ''], 'b5': ['Power OFF THMS request received', '1', 'BOOL', ''], 'b4': ['THMS OFF system state', '1', 'BOOL', ''], 'b3': ['', '1', 'BOOL', ''], 'b2': ['', '1', 'BOOL', ''], 'b1': ['', '1', 'BOOL', ''], 'b0': ['', '1', 'BOOL', '']}], '5': ['', '', '', ''], '6': ['Self-test results after Power-on', '8', 'USINT', ''], '7': ['', '8', '', '', {'b7': ['Left 3D module failure', '1', 'BOOL', ''], 'b6': ['Middle 3D module failure', '1', 'BOOL', ''], 'b5': ['Right 3D module failure', '1', 'BOOL', ''], 'b4': ['Left 2D module failure', '1', 'BOOL', ''], 'b3': ['Middle 2D module failure', '1', 'BOOL', ''], 'b2': ['Right 2D module failure', '1', 'BOOL', ''], 'b1': ['THMS software failure', '1', 'BOOL', ''], 'b0': ['Reserved', '1', 'BOOL', '']}], '8': ['Left 3D module SN', '8', 'USINT', ''], '9': ['Left 3D module SN', '8', 'USINT', ''], '10': ['Left 3D module SN', '8', 'USINT', ''], '11': ['Left 3D module SN', '8', 'USINT', ''], '12': ['Left 3D module SN', '8', 'USINT', ''], '13': ['Middle 3D module SN', '8', 'USINT', ''], '14': ['Middle 3D module SN', '8', 'USINT', ''], '15': ['Middle 3D module SN', '8', 'USINT', ''], '16': ['Middle 3D module SN', '8', 'USINT', ''], '17': ['Middle 3D module SN', '8', 'USINT', ''], '18': ['Right 3D module SN', '8', 'USINT', ''], '19': ['Right 3D module SN', '8', 'USINT', ''], '20': ['Right 3D module SN', '8', 'USINT', ''], '21': ['Right 3D module SN', '8', 'USINT', ''], '22': ['Right 3D module SN', '8', 'USINT', ''], '23': ['Left 2D module SN', '8', 'USINT', ''], '24': ['Left 2D module SN', '8', 'USINT', ''], '25': ['Left 2D module SN', '8', 'USINT', ''], '26': ['Left 2D module SN', '8', 'USINT', ''], '27': ['Left 2D module SN', '8', 'USINT', ''], '28': ['Middle 2D module SN', '8', 'USINT', ''], '29': ['Middle 2D module SN', '8', 'USINT', ''], '30': ['Middle 2D module SN', '8', 'USINT', ''], '31': ['Middle 2D module SN', '8', 'USINT', ''], '32': ['Middle 2D module SN', '8', 'USINT', ''], '33': ['Right 2D module SN', '8', 'USINT', ''], '34': ['Right 2D module SN', '8', 'USINT', ''], '35': ['Right 2D module SN', '8', 'USINT', ''], '36': ['Right 2D module SN', '8', 'USINT', ''], '37': ['Right 2D module SN', '8', 'USINT', ''], '38': ['Defect Class ID H', '8', 'UINT', ''], '39': ['Defect Class ID L', '8', '', ''], '40': ['Alarm Severity', '8', 'USINT', ''], '41': ['Defect Track Side', '8', 'USINT', ''], '42': ['Alarm Location HH', '8', 'UDINT', ''], '43': ['Alarm Location HL', '8', '', ''], '44': ['Alarm Location LH', '8', '', ''], '45': ['Alarm Location LL', '8', '', ''], '46': ['Track Circuit', '8', 'USINT', ''], '47': ['Track Circuit', '8', 'USINT', ''], '48': ['Track Circuit', '8', 'USINT', ''], '49': ['Track Circuit', '8', 'USINT', ''], '50': ['Track Circuit', '8', 'USINT', ''], '51': ['Track Circuit', '8', 'USINT', ''], '52': ['Software Version H', '8', 'USINT', ''], '53': ['Software Version L', '8', 'USINT', ''], '54-99': ['54-99 Reserved', '8', 'USINT', '']}
#
#     print(msgpack_action.pack_msg(data1, data2))