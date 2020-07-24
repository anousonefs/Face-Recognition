import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from parinya import LINE

Line = LINE('b1lS520rY397U7Z9cvwn9lLp0MovDjywl9JQXmh5GPL')

nameDetect = "AJ.THONGDY"
nameDetect2 = "TEE"
path = 'Images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')          # path ຂອງຮູບພາບ
    images.append(curImg)                        # ຈັດຕຽມ ຮູບພາບເຂົ້າໄປ
    classNames.append(os.path.splitext(cl)[0])    # ເອົາຊື່ file ແຕ່ບໍ່ເອົານາມສະກຸນ
print(classNames)
# print(images)

def findEncodings(images):    # ຮັບຮູບເຂົ້າມາ
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # opencv ເປັນ  BGR ແປງເປັນ RGB ກ່ອນ
        encode = face_recognition.face_encodings(img)[0]     # ທຳການເຂົ້າລະຫັດຮູບພາບໃບໜ້າ
        encodeList.append(encode)                         # ເກັບຮູບພາບທີເຂົ້າລະຫັດໄວ້
    return encodeList        # ສົ່ງຮູບໃບໜ້າທີເຂົ້າລະຫັດແລ້ວອອກໄປ

def markAttendanec(name):       # ທຳການບັນທຶກ ບຸກຄົນທີກ້ອງກວດຈັບໄດ້
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readline()
        nameList = []
        # print(myDataList)
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])   # entry[0] ເອົາແຕ່ຊື່   ບໍ່ເອົາເວລາ

        if name not in nameList:    # ຖ້າຊື່ບໍ່ຢູ່ໃນ file Attendance.csv ໃຫ້ທຳການບັນທຶກລົງໄປ
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name}, {dtString}')


encodeListKnown = findEncodings(images)    # ຈະໄດ້ລາຍການ ຮູບໃບໜ້າທີເຂົ້າລະຫັດແລ້ວ
print(len(encodeListKnown))                # ສະແດງຈຳນວນຮູບພາບທັງໝົດທີເອົາໄປ ເຂົ້າລະຫັດ

cap = cv2.VideoCapture(0)      # ອ່ານຮູບພາບຜ່ານ webcam

while True:
    success, img = cap.read()
    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)    # Resize Image 1/4
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)       # BGR TO RGB

    facesCurFrame = face_recognition.face_locations(imgs)     # ຊອກຕຳແໜ່ງໃບໜ້າ
    encodeCurFrame = face_recognition.face_encodings(imgs, facesCurFrame)   # ເອົາຮູບໃບໜ້າທີໄດ້ຈາກ webcam ມາເຂົ້າລະຫັດ

    for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):  # encodeFace in encodeCurFrame, faceLoc in faceCurFrame
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)   # compare image [True, False]
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)   # ຄ່າຄວາມຖືກຕ້ອງ
        print(faceDis, matches)
        matchIndex = np.argmin(faceDis)   # ຊອກຫາ index ຂອງຄ່າທີນ້ອຍທີສຸດ (ໃກ້ຄຽງທີສຸດ)

        if matches[matchIndex]:     # ກວດສອບວ່າຄ່ານ້ອຍສຸດນັ້ນ ເປັນຈິງ ຫລື່ ບໍ່

            name = classNames[matchIndex].upper()   # ກົງກັບຊື່ຂອງໃຜ ແປງເປັນໂຕໃຫ່ຍ
            y1, x2, y2, x1 = faceLoc   # ຕຳແໜ່ງຂອງໃບໜ້າ
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4   # ເນືອ່ງຈາກຫຍໍ້ຮູບລົງ 1/4 ຕ້ອງຄູນ 4 ເພື່ອໃຫ້ໄດ້ຮູບປົກກະຕິ
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # ຂີດເສັ້ນຂອບໃບໜ້າ
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)  # ຂີດເສັ້ນເບືອ່ງລຸ້ມ
            cv2.putText(img, name[:-1], (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)  # ສະແດງຊື່ຢູ່ຮູບ

            markAttendanec(name[:-1])    # ທຳການບັນທຶກຊື່
            print(name[:-1])    # ບ່ເອົາຕົວອັກສອນທ້າຍສຸດ

            if name[:-1] == nameDetect or name[:-1] == nameDetect2:   #  ກວດສອບວ່າ ຊື່ທີໄດ້ກົງ ກັບຊື່  ທີເຮົາຊອກຫາບໍ່
                Line.sendsticker(stickerId=2, stickerPackageId=1)   # ແຈ້ງເຕືອນຜ່ານ LINE
                Line.sendtext(f"We found {nameDetect} !!!")
                Line.sendimage(img[:, :, ::-1])

    # cv2.imshow('frame', img)   #  ສະແດງວິດີໂອອອກມາທາງໜ້າຈໍ
    # cv2.waitKey(1)

