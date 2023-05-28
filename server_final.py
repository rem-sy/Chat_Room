import socket 
from _thread import *
import sys
from collections import defaultdict as df
import time
global_registered_clients = []
global_registered_ports = {}
global_port1 = 0
global_port2 = 10

lock_file = False
class Server:
    def __init__(self):
        self.rooms = df(list)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.user = {}
        self.id = {}
        self.co = {}

    def accept_connections(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.server.bind((self.ip_address, int(self.port)))
        self.server.listen(100)

        while True:
            connection, address = self.server.accept()
            print(str(address[0]) + ":" + str(address[1]) + " Connected")
            ip = address[0]
            start_new_thread(self.clientThread, (connection, ip))

        self.server.close()

    
    
    # 1
# these are global variables


# 2
# in the main server, when a client just log in:
    # def in_some_function_a_client_just_registed():
        
    #     # some codes, and now a client just log in:

    #     global global_registered_clients
    #     global global_registered_ports
    #     global global_port1
    #     global global_port2
    #     id = 'lsz'
    #     chat_room = '1'

    #     # ok, lsz just registed. we automatically assign port for him
    #     for client in global_registered_clients: # traverse the registered clients
    #         if client == id: # in case that someone had logged in once, and he log in again
    #             continue
    #         if (client, id) not in global_registered_ports: # ok, this one is not registered yet
    #             global_port1 += 100
    #             global_port2 += 100
    #             global_registered_ports[(client, id)] = (global_port1, global_port2)
    #             global_registered_ports[(id, client)] = (global_port2, global_port1)
    #     if id not in global_registered_clients:
    #         global_registered_clients.append(id)

    # 3
    # in the main server, if a user write: "/CALL rxy"
    # def if_someone_want_to_call():
    #     global global_registered_ports
    #     me = 'lsz'
    #     called = 'rxy'
    #     rxy_ip = /CHECK rxy
    #     script = f'{rxy_ip} {global_registered_ports[(me, called)][0]} {global_registered_ports[(me, called)][1]}'

    # the script is what lsz need to run, and we run this for him.
    def clientThread(self, connection, ip):
        global global_registered_clients
        global global_registered_ports
        global global_port1
        global global_port2
        user_id = connection.recv(1024*128).decode().replace("User ", "")
        room_id = connection.recv(1024*128).decode().replace("Join ", "")
        #print(user_id)
        
        if room_id not in self.rooms:
            connection.send("New Group created\n".encode())
            global_registered_ports[room_id] = {}
            self.user[room_id] = {}
            self.id[room_id] = {}
            self.co[room_id] = {}
        else:
            connection.send("Welcome to chat room\n".encode())
        while user_id in self.id[room_id].values():
            #self.rooms[room_id].append(connection)
            connection.send('[SYSTEM] Error:\n'.encode())
            connection.send('[SYSTEM] user_id has been used in this chatroom\n'.encode())
            connection.send('[SYSTEM] you will be kicked out in 3s, please relog later\n'.encode())
            time.sleep(3)
            connection.send('[SYSTEM] Now Please relog\n'.encode())
            connection.send('[SYSTEM] Please Enter your new user_id:(using send message)\n'.encode())
            user_id = connection.recv(1024*128).decode()
            connection.send('[SYSTEM] Please Enter your new room_id:(using send message)\n'.encode())
            room_id = connection.recv(1024*128).decode()
            #self.rooms[room_id].remove(connection)
            #connection.close()
            if room_id not in self.rooms:
                connection.send("New Group created\n".encode())
                global_registered_ports[room_id] = {}
                self.user[room_id] = {}
                self.id[room_id] = {}
                self.co[room_id] = {}
            else:
                connection.send("Welcome to chat room\n".encode())
        
        self.rooms[room_id].append(connection)
        self.user[room_id][user_id] = ip
        self.id[room_id][connection] = user_id
        self.co[room_id][user_id] = connection
    
        if (room_id, user_id) not in global_registered_clients:
            global_registered_clients.append((room_id, user_id))
        # ok, lsz just registed. we automatically assign port for him
        for (chat_id, client_id) in global_registered_clients: # traverse the registered clients
            if chat_id != room_id: # in case that someone had logged in once, and he log in again
                continue
            if client_id == user_id: # in case that someone had logged in once, and he log in again
                continue
            if (client_id, user_id) not in global_registered_ports[room_id]: # ok, this one is not registered yet
                global_port1 += 100
                global_port2 += 100
                global_registered_ports[room_id][(client_id, user_id)] = [global_port1, global_port2]
                global_registered_ports[room_id][(user_id, client_id)] = [global_port2, global_port1]
        #print(user_id, room_id)
        self.broadcast(f'[SYSTEM] {user_id}进入了聊天室', connection, room_id)
        while True:
            try:
                message = connection.recv(1024*128)
                #print(str(message.decode()))
                if message:
                    if str(message.decode()) == "FILE":
                        self.broadcastFile(connection, room_id, user_id)

                    else:
                        #print(message[:6] == b'/CHECK')
                        #print(self.user.keys())
                        print(str(message.decode()))
                        if message[:6] == b'/CHECK':
                            name = str(message.decode()).split(' ', 1)[1]
                            try:
                                print(self.user[room_id][name])
                                script = f'/CALL {self.user[room_id][name]} {global_registered_ports[room_id][(user_id, name)][0]} {global_registered_ports[room_id][(user_id, name)][1]}'
                                message_to_send2 = "[SYSTEM] " + str(user_id) + " " + 'CALL YOU'
                                self.broadcastspecial(message_to_send2, self.co[room_id][name], room_id)
                                #ip_s = '/CHECK ' + name + ':' + self.user[name]
                            except:
                                script = '[SYSTEM] user not found'
                            message_to_send = script
                            print(message_to_send)
                            self.broadcastspecial(message_to_send, connection, room_id)
                            
                        else:
                            message_to_send = "<" + str(user_id) + "> " + message.decode()
                            self.broadcast(message_to_send, connection, room_id)

                else:
                    connection.send("[SYSTEM] You have been removed since some ERROR\n".encode())
                    self.remove(connection, room_id)
            except Exception as e:
                self.remove(connection, room_id)
                print(repr(e))
                print("Client disconnected earlier")
                break
        
    
    
    def broadcastFile(self, connection, room_id, user_id):
        global lock_file
        if lock_file:
            return
        lock_file = True
        #self.broadcast("FILE".encode(), connection, room_id)
        file_name = connection.recv(1024*128).decode()
        lenOfFile = connection.recv(1024*128).decode()
        for client in self.rooms[room_id]:
            if client != connection:
                try: 
                    client.send("FILE".encode())
                    time.sleep(0.1)
                    client.send(file_name.encode())
                    time.sleep(0.1)
                    client.send(lenOfFile.encode())
                    time.sleep(0.1)
                    client.send(user_id.encode())

                except:
                    print('except')
                    #self.broadcast('someone receive info failed', client, room_id)
                    #client.close()
                    client.send("[SYSTEM] You have been removed since some ERROR\n".encode())
                    self.remove(client, room_id)

        total = 0
        print(file_name, lenOfFile)
        while str(total) != lenOfFile:
            data = connection.recv(1024*128)
            total = total + len(data)
            for client in self.rooms[room_id]:
                if client != connection:
                    try: 
                        client.send(data)
                        time.sleep(0.1)
                    except:
                        #client.close()
                        print('except')
                        #self.broadcast('someone receive mater failed', client, room_id)
                        #client.close()
                        client.send("[SYSTEM] You have been removed since some ERROR\n".encode())
                        self.remove(client, room_id)
        print("Sent")
        lock_file = False



    def broadcast(self, message_to_send, connection, room_id):
        global lock_file
        if lock_file:
            return
        for client in self.rooms[room_id]:
            #if client != connection:
            try:
                client.send(message_to_send.encode())
            except:
                #client.close()
                client.send("[SYSTEM] You have been removed since some ERROR\n".encode())
                self.remove(client, room_id)
        
    def broadcastspecial(self, message_to_send, connection, room_id):
        global lock_file
        if lock_file:
            return
        for client in self.rooms[room_id]:
            if client == connection:
                try:
                    client.send(message_to_send.encode())
                except:
                    print('except')
                    #client.close()
                    client.send("[SYSTEM] You have been removed since some ERROR\n".encode())
                    self.remove(client, room_id)       

    
    def remove(self, connection, room_id):
        global global_registered_clients
        global global_registered_ports
        global global_port1
        global global_port2
        if connection in self.rooms[room_id]:
            user_id = self.id[room_id][connection]
            global_registered_clients.remove((room_id, user_id))
            for data in global_registered_ports[room_id].keys():
                if connection in data:
                    global_registered_ports[room_id].pop(data)
            self.user[room_id].pop(user_id)
            self.id[room_id].pop(connection)
            self.co[room_id].pop(user_id)
            self.rooms[room_id].remove(connection)
            
        if room_id not in self.rooms:
            global_registered_ports.pop(room_id)
        if not bool(global_registered_ports):
            global_port1 = 0
            global_port2 = 10
        #print(f'{room_id}的{user_id}退出了聊天室')
        self.broadcast(f'[SYSTEM] {user_id}退出了聊天室', connection, room_id)
        



if __name__ == "__main__":
    ip_address = "192.168.31.39"
    port = 40

    s = Server()
    s.accept_connections(ip_address, port)
