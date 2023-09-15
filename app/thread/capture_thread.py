import sys
import socket
import struct
import numpy
import cv2
from PySide6.QtCore import QThread, Signal, QMutex
from PySide6.QtGui import QImage, QPixmap
from ..common.model_info import ModelInfo
import random
import struct

def imageCv2Qt(image):
    height, width, bytesPerComponent = image.shape
    bytesPerLine = 3 * width
    cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
    QImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(QImg)
    return pixmap


class CaptureThread(QThread):
    signal_image = Signal(QPixmap)
    errorSignal = Signal(str)
    def __init__(self):
        super(CaptureThread, self).__init__()
        self.qmutex = QMutex()  # 进行锁
        self.Threadopen = True
        self.img_sock = None
        self.is_connect = False
        self.is_label = True #是否标识
        
        
    def InitPort(self, ip, imgport):
        self.ip = ip
        self.imgport = imgport
    
    def InitSocket(self):
        img_address = (self.ip, self.imgport)
        if self.img_sock == None:
            try:
                self.img_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # self.img_sock.settimeout(3)
                # 开启连接
                print("img socket start")
                self.img_sock.connect(img_address)
                self.is_connect = True
                print("img socket connected")
                
            except (socket.error, socket.timeout) as msg:
                print(msg)
                self.errorSignal.emit("capture_thread 连接失败!")


    def recv_all(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def run(self):
        self.InitSocket()
        if self.is_connect != True:
            return 
        
        print("capture waiting...")
        while self.Threadopen:
            
            self.qmutex.lock()
            image_data_len = None
            while self.Threadopen:
                buf = self.img_sock.recv(struct.calcsize('I'))
                image_data_len = struct.unpack('I', buf)[0]
                if (image_data_len == 0):
                    continue
                else:
                    break
                
            image_data = self.recv_all(self.img_sock, image_data_len) # ??????
            # print(image_data)
            data = numpy.frombuffer(image_data, dtype='uint8')
            tmp = cv2.imdecode(data, cv2.IMREAD_COLOR)  # 解码处理，返回mat图片
            
            img = cv2.resize(tmp, (1280, 720))
            self.qmutex.unlock()
            # cv2.imshow("test", img)
            # cv2.imwrite("E://test.jpeg", img)
            
            try:
                buf = self.img_sock.recv(struct.calcsize('I'))
                num_boxes = struct.unpack('I', buf)[0]
                boxes = [] # tlwhs
                # 左上角点和宽高
                box_data_length = struct.calcsize('ffff')
                for _ in range(num_boxes):
                    box_data = self.img_sock.recv(box_data_length)
                    box = struct.unpack('ffff', box_data)
                    boxes.append(box)
                    
                # 类序号
                ids = []
                for _ in range(num_boxes):
                    id_data = self.img_sock.recv(struct.calcsize('I'))
                    id = struct.unpack('I', id_data)[0]
                    ids.append(id)
                    
                # 置信度
                scores = []
                for _ in range(num_boxes):
                    score_data = self.img_sock.recv(struct.calcsize('f'))
                    score = struct.unpack('f', score_data)[0]
                    scores.append(score)
                    
                labels = []
                for _ in range(num_boxes):
                    label_data = self.img_sock.recv(struct.calcsize('f'))
                    label = struct.unpack('f', label_data)[0]
                    labels.append(label)
            except Exception as e:
                print(e)
                
                
            if self.is_label:
                try:
                    for i in range(0, int(num_boxes)):
                        (x, y, w, h) = boxes[i]
                        (x, y, w, h) = map(int, (x, y, w, h))
                        print(ModelInfo.instance().color_list[int(labels[i])])
                        cv2.rectangle(img, (x, y), (x + w, y + h), ModelInfo.instance().color_list[int(labels[i])], 3) # 识别框
                        cv2.putText(img, ModelInfo.instance().class_list[int(labels[i])] + str("%.2f" % scores[i]), (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, ModelInfo.instance().color_list[int(labels[i])], 1)  # 画面，文本内容，位置，字体，字体大小，RGB颜色，厚度
                except Exception as e:
                    print(e)
            
            pixmap = imageCv2Qt(img)
            # image = ImageObject(img, boxes, ids, scores, labels)
            self.signal_image.emit(pixmap)
            
            
    def isConnect(self):
        return self.is_connect
            
    def setLabel(self, flag: bool):
        self.is_label = flag
            
            