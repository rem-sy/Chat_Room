# 基于SOCKET的在线聊天室

based on：\
https://github.com/arijitiiest/Socket-Chat-App ，\
 https://blog.csdn.net/submarineas/article/details/106308719

Multi group Chat(and Video) Application using python sockets and Tkinter GUI

Our Leader:

![img](111.ico)

members: 李熠星，吕嗣哲，王崇华，卢施宇

# 功能

* 使用 Room Id and User Id 创建和加入一个聊天室；

* 在聊天室内互发信息，互传文件，享受高速互联；

* 使用 /CHECK USERID 向任何同聊天室成员发起和接受视频聊天（server自动分配端口）；

* 或在 Message 输入"ip_of_someone port1 port2" + 视频键向任何同聊天室成员发起和接受视频聊天（自己指定ip和端口）；

* 精致UI，给双眼美的享受；

* 用户友好型系统，进入退出聊天室，收到他人视频邀请都有 SYSTEM 信息提醒；

* 任何界面随时退出，登录界面，聊天室界面，视频界面（选中自己窗口 BACKSPACE 一键关闭所有视频，选中他人窗口 ESC 关闭选中视频通道）；

* 各 Room 互相独立，Room 内 id 互相独立，不用担心被其他聊天室骚扰，不用担心他人冒充；

* 选中 server ip，局域网内畅快联机；

* 联机安全，退出登录后server端自动清空用户信息


# 帮助文档

1. 如果在聊天框发送help或Help或HELP或hElp或heLP...，会得到的一些英文版本的help说明：

	HELP file:\
                    -1.Text Chat: \
                    ---Just type in and click "send" on the upper line;\
                    -2.Video Chat: \
                    ---2.1. Input "/CHECK someone" to call someone up;\
                    ---2.2. If someone is calling you up, you would receive a message of "<someone\> CALL YOU"\
                    ---2.3. IF the call is NOT answered in 1 min, the call would fail. (HE/SHE might be bisy)\
                    ---2.4. You can also call some one by: Input "ip_of_A port1 port2" to call A; \
                    -3.Send File: \
                    ---3.1 Choose the file to send, and click "send" bottim below; \
                    ---3.2 Notice that sending file would occupy the text channel, \
                    ---    messages cannot be sent during the sending of the file,\
                    ---    and the file will be broadcast to everyone in the chat room; \
                    -4.SYSTEM Message: \
                    ---4.1 When you enter a chatroom, anyone in this chatroom will receive 'someone enter the chatroom'; \
                    ---4.2 When you leave a chatroom, anyone else in this chatroom will receive 'someone leave the chatroom'; \
                    ---4.3 firmly believe [SYSTEM] not <SYSTEM\> not <system\> not ...\
                    \
                    ---    messages cannot be sent during the sending of the file,\
                    ---    and the file will be broadcast to everyone in the chat room; \


2. 视频语音通话-操作说明文档：

    2.1. 打视频：直接发送文本 "/CHECK someone" 或 "ip_of_someone port1 port2"+视频键

    2.2 如果有人打视频给你，*只有你*会收到一份<someone\> CALL YOU 的消息

    2.3 打视频之后1min内，对方打回视频给你，那么视频和语音通话将接通；若1min内未接通则挂断，显示对方忙

    2.4 支持多人视频和语音通话；音视频通话不会影响文字聊天和文件传输；

    2.5 退出视频通话：\
        若点击对方视频框，键入ESC，会仅退出*与该好友*的音视频聊天；\
        若点击自己视频框，键入Backspace，会强制退出*所有*的音视频聊天。

3. 文字聊天

    支持中英文

4. 文件传输

    传就完了。详见英文help

5. 可能的优化方向

    为用户添加以及个性化聊天框和头像，实现加入进行中视频的功能，美化视频聊天窗口，添加一对一传文件功能。。。



# For More Help：
* 联系:\
    rem_lsy@163.com（卢施宇）