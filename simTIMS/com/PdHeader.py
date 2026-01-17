import struct
from action.Fcs32Calculator import Fcs32Calculator as Fcs32

class PdHeader:
    # TRDP PD 报文头参数（示例值）
    sequence_counter = 0
    protocol_version = 0x0100  # v1.0

    '''
    message_type取值如下：
        ‘5072’H (‘Pr’)
        ‘5070’H (‘Pp’)
        ‘5064’H (‘Pd’)
        ‘5065’H (‘Pe’)
    '''
    message_type = 0

    '''
    THMS->CCU，com_id取值如下：22120和21121
    '''
    com_id = 0

    etb_topo_cnt = 0            # 固定值0
    op_trn_topo_cnt = 0         # 固定值0
    dataset_length = 0
    reserved = 0                # 固定值0
    reply_comid = 0             # 固定值0
    reply_ipaddress = 0        # 固定值0

    header_fcs = 0

    pack_fmt = ''

    def __init__(self):
        self.set_sequence_counter(1)
        self.set_protocol_version(0x0100)
        self.set_pack_fmt()
        self.set_comid()
        pass


    def set_sequence_counter(self, num):
        self.sequence_counter = num

    def add_sequence_counter(self):
        self.sequence_counter += 1

    def set_protocol_version(self, version):
        self.protocol_version = version

    def set_message_type(self, message_type):
        self.message_type = message_type

    def set_comid(self, comid='22120'):
        self.com_id = comid

    def set_length(self, length):
        self.dataset_length = length

    def get_length(self):
        return self.dataset_length

    def set_header_fcs(self):
        fcs32 = Fcs32()
        fcs_header = self.pack_fcs_header()
        self.header_fcs = fcs32.calculate_fcs32_string(fcs_header)

    def set_pack_fmt(self, fmt='!I I I I I I I I',):
        self.pack_fmt = fmt

    '''
    struct 格式: ! 代表 network byte order（大端）
    '''
    def pack_fcs_header(self):
        fcs_header = struct.pack(
            self.pack_fmt,
            self.sequence_counter,  # 4B
            (self.protocol_version + self.message_type),  # 4B
            self.com_id,  # 4B
            self.etb_topo_cnt,  # 4B
            self.op_trn_topo_cnt,  # 4B
            self.dataset_length,  # 4B
            self.reply_comid,  # 4B
            self.reserved,  # 4B
            self.reply_ipaddress    # 4B
        )
        return fcs_header

    def pack_pd_header(self):
        header = struct.pack(
             self.pack_fmt,
             self.sequence_counter,  # 4B
             (self.protocol_version + self.message_type),  # 4B
             self.com_id,  # 4B
             self.etb_topo_cnt,  # 4B
             self.op_trn_topo_cnt,  # 4B
             self.dataset_length,  # 4B
             self.reply_comid,  # 4B
             self.reserved,
             self.reply_ipaddress,
             self.header_fcs
        )

        return header
