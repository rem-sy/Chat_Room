import tkinter as tk
from tkinter import filedialog
import time
import threading
import os
import cv2
import sys
from socket import *
from PIL import Image, ImageTk
import struct
import zlib
import pickle
import pyaudio
import base64
from memory_pic import bg_png
# 取base64图片
logo = base64.b64decode(bg_png)
# pyqt页面  base64转化QPixmap
if os.path.exists('bg.png'):
    logo = Image.open('bg.png')
else:
    with open('./bg.png', 'wb') as w:  # 创建临时的文件
    # 把这个one图片解码出来，写入文件中去
        w.write(logo)
    logo = Image.open('bg.png')
    
""" with open('./bg.png', 'wb') as w:  # 创建临时的文件
    # 把这个one图片解码出来，写入文件中去
    w.write(logo) """


global_frame = None

global_videoing = False
# global_video_number = 0
GLOBAL_restart = False
global_connected = {}

global_idx = 0

    # def set_global_idx(self, local_idx):
    #     self.global_idx = local_idx

        # global global_connected

# global_video_number -= 1
# if global_video_number == 0:
#     global_videoing = False
# print(f'Finished chat with {global_video_number + 1}; Current state: on video = {global_videoing}, current video cnt = {global_video_number}')
                

CHUNK = 1024
FORMAT = pyaudio.paInt16    # 格式
CHANNELS = 2    # 输入/输出通道数
RATE = 44100    # 音频数据的采样频率
RECORD_SECONDS = 0.5    # 记录秒

def check_GLOBAL_restart(local_idx = None):
    global global_videoing 
    # global global_video_number 
    global GLOBAL_restart 
    global global_connected
    if GLOBAL_restart:
        global_videoing = False
        # global_video_number = 0
        global_connected[local_idx] = False
        return True
    return False

def check_GLOBAL_connected(local_idx = None):
    global global_videoing 
    # global global_video_number 
    global GLOBAL_restart 
    global global_connected
    if not global_connected[local_idx]:
        # global_video_number -= 1
        # if global_video_number == 0:
        #     global_videoing = False
        global_videoing = False
        for connected in global_connected.values():
            if connected:
                global_videoing = True
                break
        print(f'<check global connected> Finished chat with #{local_idx}; Current state: on video = {global_videoing}, {global_connected}')
        return True
    return False  

class Audio_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('', port)
        if version == 4:
            self.sock = socket(AF_INET ,SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6 ,SOCK_STREAM)
        # self.sock.settimeout(60) # set time out ! 

        self.p = pyaudio.PyAudio()  # 实例化PyAudio,并于下面设置portaudio参数
        self.stream = None
    def __del__(self):
        self.sock.close()   # 关闭套接字
        if self.stream is not None:
            self.stream.stop_stream()   # 暂停播放 / 录制
            self.stream.close()     # 终止流
        self.p.terminate()      # 终止会话

    def set_global_idx(self, local_idx):
        self.global_idx = local_idx

    def run(self):
        global global_videoing 
        # global global_video_number 
        global GLOBAL_restart 
        global global_connected

        print("Audio channel starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("Audio channel success connected...")
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")     # 返回对应于格式字符串fmt的结构，L为4
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer = CHUNK
                                  )
        while global_videoing:
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            while global_videoing and len(data) < payload_size:
                if check_GLOBAL_connected(self.global_idx):
                    break  
                if check_GLOBAL_restart(self.global_idx):
                    break
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while global_videoing and len(data) < msg_size:
                if check_GLOBAL_connected(self.global_idx):
                    break  
                if check_GLOBAL_restart(self.global_idx):
                    break
                data += conn.recv(81920)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frames = pickle.loads(frame_data)
            for frame in frames:
                self.stream.write(frame, CHUNK)

class Audio_Client(threading.Thread):
    def __init__(self ,ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        # self.sock.settimeout(60) # set time out ! 
        self.p = pyaudio.PyAudio()
        self.stream = None
        # print("AUDIO client starts...")
    def __del__(self) :
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
    def set_global_idx(self, local_idx):
        self.global_idx = local_idx
    def run(self):
        while global_videoing:
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                if not global_videoing:
                    break
                time.sleep(3)
                continue
        if global_videoing:
            # print("AUDIO client connected...")
            self.stream = self.p.open(format=FORMAT, 
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)
        while global_videoing and self.stream.is_active():
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            senddata = pickle.dumps(frames)
            try:
                self.sock.sendall(struct.pack("L", len(senddata)) + senddata)
            except:
                break


class Video_Server(threading.Thread):
    def __init__(self, port, version) :
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = ('', port)
        if version == 4:
            self.sock = socket(AF_INET ,SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6 ,SOCK_STREAM)

        # self.sock.settimeout(60) # set time out ! 

    def __del__(self):
        self.sock.close()
        try:
            cv2.destroyAllWindows()
        except:
            pass
    def set_global_idx(self, local_idx):
        self.global_idx = local_idx
    def run(self):
        global global_videoing
        # global global_video_number
        global global_connected
        # local_video_number = global_video_number
        print("VIDEO channel starts...")
        self.sock.bind(self.ADDR)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("VIDEO channel success connected...")
        data = "".encode("utf-8")
        payload_size = struct.calcsize("L")		# 结果为4
        cv2.namedWindow(f'Server Camera #{self.global_idx}', cv2.WINDOW_NORMAL)
        while global_videoing:
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            while global_videoing and len(data) < payload_size:
                if check_GLOBAL_connected(self.global_idx):
                    break  
                if check_GLOBAL_restart(self.global_idx):
                    break
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while global_videoing and len(data) < msg_size:
                if check_GLOBAL_connected(self.global_idx):
                    break  
                if check_GLOBAL_restart(self.global_idx):
                    break
                data += conn.recv(81920)
            zframe_data = data[:msg_size]
            data = data[msg_size:]
            frame_data = zlib.decompress(zframe_data)
            frame = pickle.loads(frame_data)
            cv2.imshow(f'Server Camera #{self.global_idx}', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                global_connected[self.global_idx] = False
                # global_video_number -= 1
                # if global_video_number == 0:
                #     global_videoing = False
                global_videoing = False
                for connected in global_connected.values():
                    if connected:
                        global_videoing = True
                        break
                print(f'Finished chat with #{self.global_idx}; Current state: on video = {global_videoing}, {global_connected}')
                break

class Video_Client(threading.Thread):
    def __init__(self ,ip, port, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:	# 限制最大帧间隔为3帧
            self.fx = 0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)

        self.connected = False
        # self.sock.settimeout(60) # set time out ! 

        # self.global_frame = global_frame
        # self.cap = cv2.VideoCapture(0) # A:\视频素材oooooooooo'\obs录屏
        # self.cap = cv2.VideoCapture('A:/视频oooooooooooo/游戏小记录/lol/4.21打腕豪.mp4') # 
    def __del__(self) :
        self.sock.close()
        # self.cap.release()
    def set_global_idx(self, local_idx):
        self.global_idx = local_idx

    def is_connected(self, ):
        return self.connected

    def run(self):
        global global_frame
        global global_videoing
        # global global_video_number
        global global_connected
        # print("VIDEO client starts...")
        while global_videoing:
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            try:
                self.sock.connect(self.ADDR)
                self.connected = True
                break
            except:
                time.sleep(3)
                continue
        # if global_videoing:
            # print("VIDEO client connected...")
        while global_videoing:
            if check_GLOBAL_connected(self.global_idx):
                break  
            if check_GLOBAL_restart(self.global_idx):
                break
            # ret, frame = self.cap.read()
            if global_frame is None:
                continue

            # tmp = threading.Thread(show_self(frame))
            # tmp.start()
            # cv2.imshow("My Camera", global_frame) # showing my camera 
            # if cv2.waitKey(1) & 0xFF == 27:
            #     break
            sframe = cv2.resize(global_frame, (0,0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe)
            zdata = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                self.sock.sendall(struct.pack("L", len(zdata)) + zdata)
            except:
                global_connected[self.global_idx] = False
                # global_video_number -= 1
                # if global_video_number == 0:
                    # global_videoing = False
                global_videoing = False
                for connected in global_connected.values():
                    if connected:
                        global_videoing = True
                        break
                print(f'<video client> Finished chat with #{self.global_idx}; Current state: on video = {global_videoing}, {global_connected}')
                break
            # for i in range(self.interval):
            #     self.cap.read()


def VIDEO_chat(ip, port1, port2, local_idx):
    global global_videoing
    # global global_video_number
    global global_connected 
    # global global_idx 

    vclient = Video_Client(ip, port1, 1, 4) # ATTENTION: this IP1 is *my ip* !!!
    aclient = Audio_Client(ip, port1+1, 4) 
    vserver = Video_Server(port2, 4)
    aserver = Audio_Server(port2+1, 4)
    # local_idx = global_idx
    global_connected[local_idx] = True
    vclient.set_global_idx(local_idx)
    aclient.set_global_idx(local_idx)
    vserver.set_global_idx(local_idx)
    aserver.set_global_idx(local_idx)

    vclient.start()
    aclient.start()
    time.sleep(1)    # make delay to start server
    vserver.start()
    aserver.start()
    start_time = time.time()
    while global_videoing:
        if check_GLOBAL_connected(local_idx):
            break  
        if check_GLOBAL_restart(local_idx):
            break
        time.sleep(1)
        vconnected = vclient.is_connected()
        if ( not vconnected ) and ( time.time() - start_time > 60) :
            print(f'Video & Audio connection: did not answer within one minute, they might be busy now. Please call later.')
            # global_video_number -= 1
            # if global_video_number == 0:
            #     global_videoing = False
            # global_connected[local_idx] = False
            print(f'<chat runner> Finished chat with #{local_idx}; Current state: on video = {global_videoing} {global_connected}')
            sys.exit(0)
            break
        if  not vserver.is_alive() or not vclient.is_alive(): # one of them is down ...
            print("Video chat finished, connection lost or cut.")
            global_connected[local_idx] = False
            sys.exit(0)
        if  not aserver.is_alive() or not aclient.is_alive(): # 
            print("Audio chat finished, connection lost or cut.")
            global_connected[local_idx] = False
            sys.exit(0)


class GUI:
    
    def __init__(self, ip_address, port):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.connect((ip_address, int(port)))

        self.Window = tk.Tk()
        self.Window.withdraw()

        self.login = tk.Toplevel()
        def Re(event = None):
            tmp = threading.Thread(self.goAhead(self.userEntryName.get(), self.roomEntryName.get()))
            tmp.start()
        self.login.bind("<Return>", Re)
        self.login.protocol('WM_DELETE_WINDOW', self.close)
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=350)

        #photo = ImageTk.PhotoImage(Image.open('bg.png').resize((470, 550), Image.ANTIALIAS))  
        photo = ImageTk.PhotoImage(logo.resize((470, 550), Image.ANTIALIAS))  
        
        self.bg= tk.Label(self.login, image= photo, compound = tk.CENTER)
        self.bg.place(relwidth=1, relheight=1)
        self.pls = tk.Label(self.login, 
                            text="Please Login to a chatroom", 
                            justify=tk.CENTER,
                            font=("Comic Sans MS", 16, "bold"),
                            bg='papayawhip',
                            fg='sienna')

        self.pls.place(relheight=0.15, relx=0.5, rely=0.15, anchor='center')

        self.userLabelName = tk.Label(self.login, text="Username: ", font=("Comic Sans MS", 11, "bold"),bg="papayawhip", fg='sienna')
        # self.userLabelName.config(bg='SystemTransparent')
        self.userLabelName.place(relwidth=0.3,relheight=0.1, relx=0.15, rely=0.3)

        self.userEntryName = tk.Entry(self.login, font="Helvetica 12",bg='papayawhip', fg='sienna')
        self.userEntryName.place(relwidth=0.4 ,relheight=0.1, relx=0.45, rely=0.3)
        self.userEntryName.focus()

        self.roomLabelName = tk.Label(self.login, text="Room Id: ", font=("Comic Sans MS", 11, "bold"), bg='papayawhip', fg='sienna')
        self.roomLabelName.place(relwidth=0.3,relheight=0.1, relx=0.15, rely=0.45)

        self.roomEntryName = tk.Entry(self.login, font="Helvetica 11", show="*", bg='papayawhip', fg='sienna')
        self.roomEntryName.place(relwidth=0.4 ,relheight=0.1, relx=0.45, rely=0.45)
        
        self.go = tk.Button(self.login, 
                            text="CONTINUE", 
                            font=("Comic Sans MS", 12, "bold"), 
                            bg='tan',
                            fg='sienna',
                            command = lambda: self.goAhead(self.userEntryName.get(), self.roomEntryName.get()))
    
        self.go.place(relx=0.35, rely=0.62)

        self.Window.protocol('WM_DELETE_WINDOW', self.logout)
        def Re2(event = None):
            tmp = threading.Thread(self.sendButton(self.entryMsg.get()))
            tmp.start()
        self.Window.bind("<Return>", Re2)
        self.to_show_my_camera= True
        self.Window.mainloop()
        
        ###################

    def goAhead(self, username, room_id=0):
        self.name = username
        self.server.send(str.encode(username))
        time.sleep(0.1)
        self.server.send(str.encode(room_id))
        
        self.login.destroy()
        self.layout()

        rcv = threading.Thread(target=self.receive) 
        rcv.start()

    def layout(self):
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="tan")

        self.chatBoxHead = tk.Label(self.Window, 
                                    bg = "lightyellow", 
                                    fg = "sienna", 
                                    text = self.name , 
                                    font = ("Calibri", 13, "bold"), 
                                    pady = 5)

        self.chatBoxHead.place(relwidth = 1)

        self.line = tk.Label(self.Window, width = 450, bg = "tan")
		
        self.line.place(relwidth = 1, rely = 0.07, relheight = 0.012) 
		
        self.textCons = tk.Text(self.Window, 
                                width=20, 
                                height=2, 
                                bg="lightyellow", 
                                fg="sienna", 
                                font=("Calibri", 11), 
                                padx=5, 
                                pady=5,
                                ) 
		
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08) 

        	
        self.labelBottom = tk.Label(self.Window, bg="tan", height=80 ) 
		
        self.labelBottom.place(relwidth = 1, 
							    rely = 0.8) 
		
        self.entryMsg = tk.Entry(self.labelBottom, 
                                bg = "lightyellow", 
                                fg = "tan", 
                                font = ("Calibri", 11))
        self.entryMsg.place(relwidth = 0.65, 
							relheight = 0.025, 
							rely = 0.008, 
							relx = 0.011) 
        self.entryMsg.focus()

        self.buttonMsg = tk.Button(self.labelBottom, 
								text = "Send", 
								font = ("Calibri", 11, "bold"), 
								width = 16, 
								bg = "chocolate", 
								command = lambda : self.sendButton(self.entryMsg.get())) 
        self.buttonMsg.place(relx = 0.67, 
							rely = 0.008, 
							relheight = 0.025, 
							relwidth = 0.21) 

        ##############
        
        self.buttonClose = tk.Button(self.labelBottom, 
								text = "○", 
								font = "Helvetica 10 bold", 
								width = 8, 
								bg = "chocolate", 
								command = lambda : self.video(self.entryMsg.get())) 
        self.buttonClose.place(relx = 0.90, 
							rely = 0.008, 
							relheight = 0.025, 
							relwidth = 0.09)
        ##############

        self.labelFile = tk.Label(self.Window, bg="tan", height=80) 
		
        self.labelFile.place(relwidth = 1, 
							    rely = 0.9) 
		
        self.fileLocation = tk.Label(self.labelFile, 
                                text = "Choose file to send",
                                bg = "lightyellow", 
                                fg = "tan", 
                                font = ("Calibri", 11))
        self.fileLocation.place(relwidth = 0.65, 
                                relheight = 0.025, 
                                rely = 0.004, 
                                relx = 0.011) 

        self.browse = tk.Button(self.labelFile, 
								text = "Browse", 
								font = ("Calibri", 11, "bold"), 
								width = 13, 
								bg = "chocolate", 
								command = self.browseFile)
        self.browse.place(relx = 0.67, 
							rely = 0.004, 
							relheight = 0.025, 
							relwidth = 0.15) 

        self.sengFileBtn = tk.Button(self.labelFile, 
								text = "Send", 
								font = ("Calibri", 11, "bold"), 
								width = 13, 
								bg = "chocolate", 
								command = self.sendFile)
        self.sengFileBtn.place(relx = 0.84, 
							rely = 0.004, 
							relheight = 0.025, 
							relwidth = 0.15)
    

        self.textCons.config(cursor = "arrow")
        scrollbar = tk.Scrollbar(self.textCons) 
        scrollbar.place(relheight = 1, 
						relx = 0.974)

        scrollbar.config(command = self.textCons.yview)
        self.textCons.config(state = tk.DISABLED)
        
        ##done

        
    def browseFile(self):
        self.filename = filedialog.askopenfilename(initialdir="/", 
                                    title="Select a file",
                                    filetypes = (("Text files", 
                                                "*.txt*"), 
                                                ("all files", 
                                                "*.*")))
        self.fileLocation.configure(text="File Opened: "+ self.filename)


    def sendFile(self):
        self.server.send("FILE".encode())
        time.sleep(0.1)
        self.server.send(str("client_" + os.path.basename(self.filename)).encode())
        time.sleep(0.1)
        self.server.send(str(os.path.getsize(self.filename)).encode())
        time.sleep(0.1)

        file = open(self.filename, "rb")
        data = file.read(1024*128)
        while data:
            self.server.send(data)
            data = file.read(1024*128)
        self.textCons.config(state=tk.DISABLED)
        self.textCons.config(state = tk.NORMAL)
        self.textCons.insert(tk.END, "<You> "
                                     + str(os.path.basename(self.filename)) 
                                     + " Sent\n\n")
        self.textCons.config(state = tk.DISABLED) 
        self.textCons.see(tk.END)


    def sendButton(self, msg):
        if msg.lower() == 'help':
            print(f'HELP file:\n\
                    -1.Text Chat: \n\
                    ---Just type in and click "send" on the upper line;\n\
                    -2.Video Chat: \n\
                    ---2.1. Input "/CHECK someone" to call someone up;\n\
                    ---2.2. If someone is calling you up, you would receive a message of "<someone> CALL YOU"\n\
                    ---2.3. IF the call is NOT answered in 1 min, the call would fail. (HE/SHE might be bisy)\n\
                    ---2.4. You can also call some one by: Input "ip_of_A port1 port2" to call A; \n\
                    -3.Send File: \n\
                    ---3.1 Choose the file to send, and click "send" bottim below; \n\
                    ---3.2 Notice that sending file would occupy the text channel, \n\
                    ---    messages cannot be sent during the sending of the file,\n\
                    ---    and the file will be broadcast to everyone in the chat room; \n\
                        ')
        self.textCons.config(state = tk.DISABLED) 
        self.msg=msg 
        self.entryMsg.delete(0, tk.END) 
        snd= threading.Thread(target = self.sendMessage) 
        snd.start() 


    def receive(self):
        while True:
            try:
                message = self.server.recv(1024*128).decode()
                str_msg = str(message)

                if str_msg == "FILE":
                    file_name = self.server.recv(1024*128).decode()
                    lenOfFile = self.server.recv(1024*128).decode()
                    send_user = self.server.recv(1024*128).decode()

                    
                    
                    if os.path.exists(file_name):
                        os.remove(file_name)
                    
                    total = 0
                    with open(file_name, 'wb') as file:
                        while str(total) != lenOfFile:
                            data = self.server.recv(1024*128)
                            total = total + len(data)     
                            file.write(data)
                    
                    self.textCons.config(state=tk.DISABLED)
                    self.textCons.config(state = tk.NORMAL)
                    self.textCons.insert(tk.END, "<" + str(send_user) + "> " + file_name + " Received\n\n")
                    self.textCons.config(state = tk.DISABLED) 
                    self.textCons.see(tk.END)
                
                elif str_msg[:5] == '/CALL':
                    # this is a calling message for me
                    call_msg = str_msg[6:]
                    # print(f'<test call in receive> {self.name} get: {str_msg},{call_msg}')
                    self.video(call_msg)

                else:
                    self.textCons.config(state=tk.DISABLED)
                    self.textCons.config(state = tk.NORMAL)
                    self.textCons.insert(tk.END, 
                                    message+"\n\n") 

                    self.textCons.config(state = tk.DISABLED) 
                    self.textCons.see(tk.END)

            except: 
                # self.server.close()
                print(f'receive failed ...')
                break 
                #print('except')
                pass

    def sendMessage(self):
        self.textCons.config(state=tk.DISABLED) 
        while True:  
            self.server.send(self.msg.encode())
            # self.textCons.config(state = tk.NORMAL)
            # self.textCons.insert(tk.END, 
            #                 "<You> " + self.msg + "\n\n") 

            # self.textCons.config(state = tk.DISABLED) 
            # self.textCons.see(tk.END)
            break
    
    
    def close(self):
        #time.sleep(0.5)
        self.Window.destroy()
        print("quit before login")
        self.server.close()
        
    def logout(self):
        #time.sleep(0.5)
        self.Window.destroy()
        print("logout successfully")
        self.server.close()
 
    #def receive(self):
        
    def video(self, msg):
        self.entryMsg.delete(0, tk.END)
        global global_frame
        global global_videoing
        # global global_video_number
        global GLOBAL_restart
        global global_idx
        global global_connected

        try:
            ip = msg.split(' ', 2)[0]
            port1 = msg.split(' ', 2)[1]
            port2 = msg.split(' ', 2)[2]
            # def run_video_chat(ip, port1, port2):
            #     VIDEO_chat(ip, port1, port2)
                # os.system(f"python main2_A_for_bi-camera.py --host1 {ip} --port1 {port1} --port2 {port2} --flag {self.to_show_my_camera}")
            port1 = int(port1)
            port2 = int(port2)
            if not ( port1 >= 0 and port2 >= 0 ):
                print(f'input video info is not correct: "{msg}"')
                return
        except:
            print(f'input video info is not correct: "{msg}"')
            return
        
        global_idx += 1
        local_idx = global_idx
        global_connected[local_idx] = True
        if not global_videoing: # global_video_number == 0: # first time call up the video
            global_videoing = True
            GLOBAL_restart = False # powerful !!!
            t1 = threading.Thread(target=get_my_camera)
            t1.start()
            t2 = threading.Thread(target=show_my_camera)
            t2.start()
        global_videoing = True
        # global_video_number += 1

        # assert global_frame is not None
        paras = (ip, port1, port2, local_idx)
        thread = threading.Thread(target = VIDEO_chat, args =paras)
        thread.start()

        # self.to_show_my_camera = False
        
def get_my_camera(flag = True):
    if flag:
        global global_frame
        global global_videoing
        # global global_video_number
        cap = cv2.VideoCapture(0)
        while global_videoing and cap.isOpened():

            global_videoing = False
            for connected in global_connected.values():
                if connected:
                    global_videoing = True
                    break

            if check_GLOBAL_restart():
                break
            ret, frame = cap.read()

            # cv2.imshow("My Camera", frame) # showing my camera 
            global_frame = frame
            # print(global_frame)
            # if cv2.waitKey(1) & 0xFF == 27:
            #     break
            # print()
            # print(global_frame)
            for i in range(1):
                cap.read()

def show_my_camera(flag = True):
    if flag:      
        global global_videoing
        # global global_video_number  
        while global_videoing:

            if check_GLOBAL_restart():
                break
            if global_frame is None:
                continue
            cv2.namedWindow('My Camera', cv2.WINDOW_NORMAL)
            frame = global_frame
            cv2.imshow("My Camera", frame) # showing my camera 
            if cv2.waitKey(1) & 0xFF == 8: # Backspace
                GLOBAL_restart = True
                global_videoing = False
                # global_video_number = 0
                break
            # if cv2.waitKey(1) & 0xFF == 27: # ESC
            #     continue
                


class connect():
    def __init__(self):
        self.Window = tk.Tk()
        self.Window.withdraw()
        self.login = tk.Toplevel()
        def Re(event = None):
            tmp = threading.Thread(self.goAhead(self.userEntryName.get(), self.roomEntryName.get()))
            tmp.start()
        self.login.bind("<Return>", Re)
        self.login.protocol('WM_DELETE_WINDOW', self.close)
        self.login.title("Connect")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=350)

        #photo = ImageTk.PhotoImage(Image.open('bg.png').resize((470, 550), Image.ANTIALIAS))  
        photo = ImageTk.PhotoImage(logo.resize((470, 550), Image.ANTIALIAS))  
        
        self.bg= tk.Label(self.login, image= photo, compound = tk.CENTER)
        self.bg.place(relwidth=1, relheight=1)
        self.pls = tk.Label(self.login, 
                            text="Please Connect to the server", 
                            justify=tk.CENTER,
                            font=("Comic Sans MS", 16, "bold"),
                            bg='papayawhip',
                            fg='sienna')

        self.pls.place(relheight=0.15, relx=0.5, rely=0.15, anchor='center')

        self.userLabelName = tk.Label(self.login, text="IP: ", font=("Comic Sans MS", 11, "bold"),bg="papayawhip", fg='sienna')
        # self.userLabelName.config(bg='SystemTransparent')
        self.userLabelName.place(relwidth=0.3,relheight=0.1, relx=0.15, rely=0.3)

        self.userEntryName = tk.Entry(self.login, font="Helvetica 12",bg='papayawhip', fg='sienna')
        self.userEntryName.place(relwidth=0.4 ,relheight=0.1, relx=0.45, rely=0.3)
        self.userEntryName.focus()

        self.roomLabelName = tk.Label(self.login, text="Port: ", font=("Comic Sans MS", 11, "bold"), bg='papayawhip', fg='sienna')
        self.roomLabelName.place(relwidth=0.3,relheight=0.1, relx=0.15, rely=0.45)

        self.roomEntryName = tk.Entry(self.login, font="Helvetica 11", show="*", bg='papayawhip', fg='sienna')
        self.roomEntryName.place(relwidth=0.4 ,relheight=0.1, relx=0.45, rely=0.45)
        
        self.go = tk.Button(self.login, 
                            text="CONTINUE", 
                            font=("Comic Sans MS", 12, "bold"), 
                            bg='tan',
                            fg='sienna',
                            command = lambda: self.goAhead(self.userEntryName.get(), self.roomEntryName.get()))

        self.go.place(relx=0.35, rely=0.62)
        self.Window.mainloop()
        
    
    def goAhead(self, username, room_id=0):
        self.login.destroy()
        self.Window.destroy()
        try:
            GUI(username, room_id)
            import sys
            sys.exit(0)
        except:
            print('Connect Failed')
    
    def close(self):
        self.login.destroy()
        self.Window.destroy()
        print("Quit before connect!")
        


if __name__ == "__main__":
    """ host = socket.gethostbyname('DESKTOP-UQ6FTAP')
    print(host) """

    # import sys
    # sys.exit(0)
    # ip_address = "192.168.31.39" # Redmi 5G
    # ip_address = "10.181.199.111"
    connect()
    """ ip_address = "127.0.0.1"
    port = 40
    g = GUI(ip_address, port) """

    import sys
    sys.exit(0)


###

