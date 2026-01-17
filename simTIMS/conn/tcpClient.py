import socket

def start_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"已连接到服务器 {host}:{port}")
        while True:
            message = input("输入要发送的消息（输入 quit 关闭）：")
            s.sendall(message.encode())
            if message.lower() == 'quit':
                print("通信关闭。")
                break
            data = s.recv(1024)
            reply = data.decode()
            print(f"收到回复：{reply}")
            if reply.lower() == 'quit':
                print("通信关闭。")
                break

if __name__ == "__main__":
    host = input("请输入服务器IP地址（如127.0.0.1）：")
    port = int(input("请输入端口号（如65432）："))
    start_client(host, port)