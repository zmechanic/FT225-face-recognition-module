import time

'''
字段长度说明
SyncWord 2bytes 固定的消息开头同步字 0xEF 0xAA
MsgID 1byte 消息 ID (例如 RESET)
Size  2bytes Data size, 单位 byte
Data Nbytes data,command 消息对应的参数。 65535>=N>=0，N=0 表示此消息无参数。
Check 1byte 消息对应的 协议的奇偶校验码，计算方式为整条协议除去 SyncWord 部分后，其余字节按位做 XOR 运算。

'''

'''

0成功
MR_REJECTED1模组拒绝该命令
MR_ABORTED2录入/验证算法已终止
MR_FAILED4_CAMERA4相机打开失败
MR_FAILED4_UNKNOWNREASON5未知错误
MR_FAILED4_INVALIDPARAM6无效的参数
MR_FAILED4_NOMEMORY7内存不足
MR_FAILED4_UNKNOWNUSER8没有已录入的用户
MR_FAILED4_MAXUSER9录入超过最大用户数量
MR_FAILED4_FACEENROLLED10人脸已录入
MR_FAILED4_LIVENESSCHECK12活体检测失败
MR_FAILED4_TIMEOUT13录入或解锁超时
MR_FAILED4_AUTHORIZATION14加密芯片授权失败
MR_FAILED4_READ_FILE19读文件失败
MR_FAILED4_WRITE_FILE20写文件失败
MR_FAILED4_NO_ENCRYPT21通信协议未加密
MR_FAILED4_NO_RGBIMAGE23RGB 图像没有 ready
MR_FAILED4_JPGPHOTO_LARGE24JPG照片过大（照片注册）
MR_FAILED4_JPGPHOTO_SMALL25JPG照片过小（照片注册）




'''
MR_RESULTS = {
    0: 'MR_SUCCESS(0): Operation successful',
    1: 'MR_REJECTED(1): The module rejected the command',
    2: 'MR_ABORTED(2): Entry/verification algorithm terminated',
    4: 'MR_FAILED4_CAMERA(4): Camera failed to open',
    5: 'MR_FAILED4_UNKNOWNREASON(5): Unknown error',
    6: 'MR_FAILED4_INVALIDPARAM(6): Invalid parameter',
    7: 'MR_FAILED4_NOMEMORY(7): Insufficient memory',
    8: 'MR_FAILED4_UNKNOWNUSER(8): No enrolled user',
    9: 'MR_FAILED4_MAXUSER(9): Exceeded maximum number of users',
    10: 'MR_FAILED4_FACEENROLLED(10): Face already enrolled',
    12: 'MR_FAILED4_LIVENESSCHECK(12): Liveness check failed',
    13: 'MR_FAILED4_TIMEOUT(13): Enrollment or unlock timeout',
    14: 'MR_FAILED4_AUTHORIZATION(14): Encryption chip authorization failed',
    19: 'MR_FAILED4_READ_FILE(19): Failed to read file',
    20: 'MR_FAILED4_WRITE_FILE(20): Failed to write file',
    21: 'MR_FAILED4_NO_ENCRYPT(21): Communication protocol not encrypted',
    23: 'MR_FAILED4_NO_RGBIMAGE(23): RGB image not ready',
    24: 'MR_FAILED4_JPGPHOTO_LARGE(24): JPG photo too large (photo registration)',
    25: 'MR_FAILED4_JPGPHOTO_SMALL(25): JPG photo too small (photo registration)',
}


import serial
import struct

ser = serial.Serial('COM8', 115200, timeout=1)

DEBUG = False

def make_deluser_data(uid):
    sync_word = 0xefaa
    msgid = 0x20
    size = 2
    uid = int(uid)
    packet = struct.pack('>H B H H', sync_word, msgid, size, uid)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet

def make_demo_data(enable):
    sync_word = 0xefaa
    msgid = 0xfe
    size = 1
    enable_byte = 1 if enable else 0
    packet = struct.pack('>H B H B', sync_word, msgid, size, enable_byte)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet

def make_verify_data():
    sync_word = 0xefaa
    msgid = 0x12
    size = 2
    need_poweroff_byte = 0
    timeout_byte = 10
    packet = struct.pack('>H B H B B', sync_word, msgid, size, need_poweroff_byte, timeout_byte)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet

def get_parity_code(packet):
    parity_code = 0
    for b in packet[2:]:
        parity_code ^= b
    return parity_code

def make_enroll_data(username):
    sync_word = 0xefaa
    msgid = 0x1d
    size = 35
    admin = 0
    # user_name 为 32 bytes
    user_name:bytes[32] = bytearray(32)  # 创建一个32字节的字节数组
    user_name[:len(username)] = username.encode()  # 将字符串'admin'放入字节数组
    face_dir = 0
    timeout = 0
    packet = struct.pack('>H B H B 32s B B', sync_word, msgid, size, admin, user_name, face_dir, timeout)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    if DEBUG:
        print(f'packet: {" ".join(f"{b:02x}" for b in packet)}')


    return packet

enroll_direction = {
    'middle':0x01,
    'right':0x02,
    'left':0x04,
    'down':0x08,
    'up':0x10,
}

def make_enroll_5_data(username,direction):
    sync_word = 0xefaa
    msgid = 0x13
    size = 35
    admin = 0
    user_name = username.encode()
    face_dir = direction
    timeout = 20
    packet = struct.pack('>H B H B 32s B B', sync_word, msgid, size, admin, user_name, face_dir, timeout)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet
    

def make_enroll_with_photo_data(username,photo_path):
    sync_word = 0xefaa
    msgid = 0x1e
    size = 35
    admin = 5
    user_name = username.encode()
    face_dir = 0
    timeout = 0
    # todo 读取照片


no_data_cmd = {
    'reset':0x10,
    'getstatus':0x11,
    'delalluser':0x21,
    'getalluser':0x24,
    'face_reset':0x23,
    'enroll_with_photo':0x1e
}


def make_cmd_with_no_data(cmd):
    sync_word = 0xefaa
    msgid = cmd
    size = 0x0000
    packet = struct.pack('>H B h', sync_word, msgid, size)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet



def make_get_user_data():
    sync_word:bytes = 0xefaa
    msgid:bytes = 0x24
    size:bytes = 0x0000
    packet = struct.pack('>H B h', sync_word, msgid, size)
    parity_code = get_parity_code(packet)
    packet += parity_code.to_bytes()
    return packet

def check_buffer(buffer):
    if buffer[0] == 0x01:
        print(f'note:  nid: {buffer[3]} state: {buffer[5]}')


def get_note_data(data):
    nid = data[0]
    if nid == 0x01:
        state, left, top, right, bottom, yaw, pitch, roll = struct.unpack('<hhhhhhhh', data[1:])
        print(f'Face status: {data[1:]}')
        print(f'state: {state} left: {left} top: {top} right: {right} bottom: {bottom} yaw: {yaw} pitch: {pitch} roll: {roll}')
        
        if state == 0x00:
            print('Face status: OK')
        if state == 0x01:
            print('Face status: No face detected')
        if state == 0x02:
            print('Face status: Too far up')
        if state == 0x03:
            print('Face status: Too far down')
        if state == 0x04:
            print('Face status: Too far left')
        if state == 0x05:
            print('Face status: Too far right')
        if state == 0x06:
            print('Face status: Too far away')
        if state == 0x07:
            print('Face status: Too close')
        if state == 0x08:
            print('Face status: Eyebrows obstructed')
        if state == 0x09:
            print('Face status: Eyes obstructed')
        if state == 0x0a:
            print('Face status: Face obstructed')
        if state == 0x0b:
            print('Face status: Incorrect enrollment direction')
        if state == 0x0c:
            print('Face status: Eyes detected in closed-eye state')
        if state == 0x0d:
            print('Face status: Eyes closed')
        if state == 0x0e:
            print('Face status: Unable to determine status in closed-eye mode')
    elif nid == 0x00:
        print('Device ready')
    elif nid == 0x02:
        print('Device error')
    else:
        print('Unknown message', nid)
    
    
def get_reply_data(data):
    mid, result = struct.unpack('BB', data[:2])
    reply_data = data[2:]
    if result == 0x00:
        print('Operation Successful')

        if mid == 0x12:
            print('Verify successful')
            uid, username, isadmin, unlockstatus = struct.unpack('>H 32s B B', reply_data)
            print(f'uid: {uid}, username: {username.decode()}, isadmin: {isadmin}, unlockstatus: {unlockstatus}')
            if DEBUG:
                print(f'uid: {uid} username: {username.decode()} isadmin: {isadmin} unlockstatus: {unlockstatus}')
        elif mid == 0x13:
            print('Enrollment successful')
            uid, face_dir = struct.unpack('>H B', reply_data)
            print(f'uid: {uid} face_dir: {face_dir}')
            print(reply_data.hex())
            if face_dir == enroll_direction['middle']:
                print('Front face enrollment successful')
                print('Enrolling left face')
                data = make_enroll_5_data(username, enroll_direction['left'])
                ser.write(data)
            if face_dir == 0x05:
                print('Left face enrollment successful')
                print('Enrolling right face')
                data = make_enroll_5_data(username, enroll_direction['right'])
                ser.write(data)
            if face_dir == 0x07:
                print('Right face enrollment successful')
                print('Enrolling upper face')
                data = make_enroll_5_data(username, enroll_direction['up'])
                ser.write(data)
            if face_dir == 0x17:
                print('Upper face enrollment successful')
                print('Enrolling lower face')
                data = make_enroll_5_data(username, enroll_direction['down'])
                ser.write(data)
            if face_dir == enroll_direction['down']:
                print('Lower face enrollment successful')
        elif mid == 0x1d:
            print('Enrollment successful')
            uid, face_dir = struct.unpack('>H B', reply_data)
            print(f'uid: {uid} face_dir: {face_dir}')
        elif mid == 0x20:
            print('User deleted successfully')
        elif mid == 0x24:
            print('User data retrieval successful')
        elif mid == 0xfe:
            print('Demo mode enabled successfully')
       
    else:
        print('Operation Failed')
    print(f'mid: {mid} result: {result}  {MR_RESULTS[result]} reply_data: {reply_data.hex()}')


def read_serial_data():
    header = bytearray(2)
    msg_types=['REPLY','NOTE','IMAGE']
    while True:
        if ser.in_waiting > 0:
            if len(header) == 2:
                header[0:1] = header[1:2]  # 拷贝header[1]到header[0]
                header[1:2] = ser.read(1)  # 从串口读取一个字节并拷贝到header[1]
                
            else:
                header.append(ser.read(1))
            if header.hex() == 'efaa':
                msg_type,size=struct.unpack('>Bh',ser.read(3))
                data = ser.read(size)
                check = ser.read(1)
                print(f'recv: {msg_types[msg_type]} size: {size} ')
                if msg_type == 0x01:
                    get_note_data(data)
                elif msg_type == 0x00:
                    get_reply_data(data)
                else:
                    print(f'data: {" ".join(f"{b:02x}" for b in data)} check: {check.hex()}')

            


if __name__ == '__main__':
    import threading
    threading.Thread(target=read_serial_data, daemon=True).start()

    while True:
        cmd = input('Please enter command: ')
        if cmd=='enroll':
            #只录入正脸
            username = input('Please enter username: ')
            data = make_enroll_data(username)
        elif cmd=='enroll5':
            #录入正脸和上下左右四个方向
            username = input('Please enter username: ')
            
            #清除录入人脸
            data = make_cmd_with_no_data(no_data_cmd['face_reset'])
            ser.write(data)
            time.sleep(1)
            #录入正脸
            print('录入正脸')
            data = make_enroll_5_data(username,enroll_direction['middle'])
        elif cmd=='verify':
            data = make_verify_data()
        elif cmd=='getuser':
            data = make_get_user_data()
        elif cmd=='deluser':
            uid = input('Please enter user ID: ')
            data = make_deluser_data(uid)
        elif cmd=='demo':
            data = make_demo_data(True)
        elif cmd=='status':
            data = make_cmd_with_no_data(no_data_cmd['getstatus'])
        else:
            print('Unknown Command')
            continue
        print(f'Sending out command data: {" ".join(f"{b:02x}" for b in data)}')
        ser.write(data)
        time.sleep(1)
