import socket

def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"服务器已启动，监听 {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"已连接：{addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode()
                print(f"收到消息：{message}")
                if message.lower() == 'quit':
                    print("通信关闭。")
                    break
                reply = input("回复消息（输入 quit 关闭）：")
                conn.sendall(reply.encode())
                if reply.lower() == 'quit':
                    print("通信关闭。")
                    break

if __name__ == "__main__":
    host = input("请输入服务器IP地址（如127.0.0.1）：")
    port = int(input("请输入端口号（如65432）："))
    start_server(host, port)