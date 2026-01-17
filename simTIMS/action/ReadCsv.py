import csv

class ReadCsv:
    def __init__(self):
        self.msg_struct = {}
        self.header_struct = {}

    def read_msg_csv(self, msg_csv_path):
        # 输入csv规定列依次为：Offset，Bit No，Size，Data Type，Signal ID，Signal Name
        # try:
        with open(msg_csv_path, 'r', encoding='ansi') as f:
            reader = csv.reader(f)
            next(reader, None)  # 跳过列名

            current_key = None
            current_values = []
            sub_data = {}

            for row in reader:
                if not row:
                    continue
                first_col = row[0].strip() if row[0] else ""
                sub_key = None
                sub_values = []

                # 如果第一列为空或者第一列的值和上一行第一列相同，那么作为上一列的子项处理
                if (first_col == "") or (first_col == current_key):
                    # 第一列为空，将第二列作为key，后续列作为values
                    if len(row) > 1 and current_key is not None:
                        sub_key = row[1].strip() if row[1] else ""
                        sub_values = [row[5], row[2], row[3]] if len(row) > 2 else []
                        # 补充一列value值，默认为空
                        sub_values.append('')
                        sub_data[sub_key] = sub_values
                else:
                    if len(sub_data) > 0:
                        current_values.append(sub_data)

                    current_key = first_col
                    current_values = [row[5], row[2], row[3]] if len(row) > 1 else []
                    # 补充一列value值，默认为空
                    current_values.append('')
                    sub_data = {}
                # 新主行
                if current_key is not None:
                    self.msg_struct[current_key] = current_values

            if len(sub_data) > 0:
                current_values.append(sub_data)
                # 保存最后一行
                # if current_key is not None:
                #     self.msg_struct[current_key] = current_values

        # except FileNotFoundError:
        #     print(f"错误：找不到文件 {msg_csv_path}")
        #     return {}
        # except Exception as e:
        #     print(f"读取CSV文件时出错：{e}")
        #     return {}
        print(self.msg_struct)
        return self.msg_struct
    '''
    从csv文件里读取数据结构header部分
    '''
    def read_header_csv(self, header_csv_path):
        # 输入的csv规定列依次为：Offset，Name
        # try:
        with open(header_csv_path, 'r', encoding='ansi') as f:
            reader = csv.reader(f)
            next(reader, None)  # 跳过列名

            # 初始首列和初始后续列
            current_key = None
            current_values = []*4

            for row in reader:
                if not row:
                    continue
                # 获取csv中首列的值
                first_col = row[0].strip() if row[0] else ""
                # 本行首列值和上一行首列值是否相同，相同则合为一行处理
                if (first_col == '') or (first_col == current_key):
                    current_values[0].append(row[1].strip())
                    current_values[1] += 1
                    current_values[2] += ',0'
                else:
                    current_key = row[0].strip() if row[0] else ""
                    current_values = [[row[1].strip()], 1, '0', 0] if len(row) > 1 else []

                if current_key is not None:
                    self.header_struct[current_key] = current_values
                # 保存最后一行
                # if current_key is not None:
                #     self.header_struct[current_key] = current_values
        # except FileNotFoundError:
        #     print(f"错误：找不到文件 {header_csv_path}")
        #     return {}
        # except Exception as e:
        #     print(f"读取CSV文件时出错：{e}")
        #     return {}

        print("self.header_struct:", self.header_struct)
        return self.header_struct

# if __name__ == "__main__":
#     csv_data = ReadCsv()
#     csv_data.read_header_csv(r"../config/header.csv")
#     csv_data.read_msg_csv(r"../config/send_thms.csv")