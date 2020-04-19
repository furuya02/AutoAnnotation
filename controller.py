import cv2
import numpy as np

# コントローラークラス
class Controller():
    def __init__(self, threshold, only_one, margin, inversion):
        self.__windowName = 'Cntroller'
        cv2.namedWindow(self.__windowName)

        cv2.createTrackbar('threshold', self.__windowName, 0, 255, self._nothing)
        cv2.createTrackbar('inversion', self.__windowName, 0, 1, self._nothing)
        cv2.createTrackbar('only_one', self.__windowName, 0, 1, self._nothing)
        cv2.createTrackbar('margin', self.__windowName, 0, 100, self._nothing)
        
        self.__threshold = threshold
        self.__inversion = inversion
        self.__only_one = only_one
        self.__margin = margin

        cv2.setTrackbarPos('threshold', self.__windowName, self.__threshold)
        cv2.setTrackbarPos('inversion', self.__windowName, self.__inversion)
        cv2.setTrackbarPos('only_one', self.__windowName, self.__only_one)
        cv2.setTrackbarPos('margin', self.__windowName, self.__margin)

        self.frame = np.zeros((1,300,3), np.uint8)

    # 設定変更時のイベント
    def _nothing(self, val):
        pass

    # 値の取得        
    def getValue(self):
        return (self.__threshold, self.__inversion, self.__only_one, self.__margin) 

    # コントローラ画面
    def disp(self):
        self.__threshold = cv2.getTrackbarPos('threshold', self.__windowName)
        self.__inversion = cv2.getTrackbarPos('inversion', self.__windowName)
        self.__only_one = cv2.getTrackbarPos('only_one', self.__windowName)
        self.__margin = cv2.getTrackbarPos('margin', self.__windowName)
        cv2.imshow(self.__windowName, self.frame)