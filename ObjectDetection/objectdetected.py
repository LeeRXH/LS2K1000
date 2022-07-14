import cv2
#from .. import bizhang
thres = 0.5# 置信度阈值

cap = cv2.VideoCapture(1)#打开摄像头
cap.set(3,1280)
cap.set(4,720)
cap.set(10,70)

classNames= []
classFile = 'C:/Users/lrx/Desktop/ls2k/LS2K1000/ObjectDetection/coco.names'#可检测物体名目
with open(classFile,'r') as f:
    classNames = f.read().splitlines()

configPath = 'C:/Users/lrx/Desktop/ls2k/LS2K1000/ObjectDetection/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'#配置文件
weightsPath = 'C:/Users/lrx/Desktop/ls2k/LS2K1000/ObjectDetection/frozen_inference_graph.pb'#权重文件

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


#逐帧判断
while True:
    success, img = cap.read()
    classIds, confs, bbox = net.detect(img, confThreshold=thres)
    print(classIds, bbox)

    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            cv2.rectangle(img,box,color=(0,255,0),thickness=2)
            cv2.putText(img,classNames[classId-1],(box[0]+10,box[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                        cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            if (classNames=='person'):       #检测到人
                #bizhang.stop()          #              
                print('小车停下')
            if ((classNames=='cup')|(classNames=='bottle')):
                #bizhang.stop()          #检测到杯子也停下
                height=box[0]*1.5       #通过置信框的大小测量杯子的高度
                               
    cv2.imshow("Output",img)
   #q键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print('code Completed')

cap.release()
cv2.destroyAllWindows()
