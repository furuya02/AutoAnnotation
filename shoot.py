import cv2

# 撮影クラス
class Shoot():
    def __init__(self, width, height):
        self.__windowName = 'Monitor'
        self.__W = int(width/30)
        self.__M = int(self.__W/4)
        self.__X = int(width/2)
        self.__Y = int(height - self.__W - self.__M * 5)
        self.__shutterColor =  (50, 50, 255)
        self.__mode = 0  # 0:idle 1:Shut    

    # シャッターボタンが押された時のイベント処理
    def __onMouseEvent(self, event, x, y, flags, param):
        if(event == cv2.EVENT_LBUTTONDOWN):
            print("event:{} x:{} y:{}".format(event, x, y))
            if((self.__X - self.__W) < x and x < (self.__X + self.__W)):
                if((self.__Y - self.__W) < y and y < (self.__Y + self.__W)):
                    self.__mode = 1

    # シャッターボタン
    def __dispShutter(self, frame):
        frame = cv2.circle(frame, (self.__X, self.__Y), self.__W, self.__shutterColor, thickness=-1)
        return cv2.circle(frame, (self.__X, self.__Y), self.__W + self.__M, self.__shutterColor, thickness=2, lineType=cv2.LINE_AA)

    # ラベル表示
    def __dispLabel(self, frame, label):
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontSize = 1.0
        size = cv2.getTextSize(label, font, fontSize, thickness=2)
        x = 10
        y = 30
        w = size[0][0]
        h = size[0][1]
        margin = 5
        cv2.rectangle(frame, (x-margin, y+margin), (x+w+margin*2, y-h-margin*2), (0,0,0), thickness=-1)
        cv2.putText(frame, label, (10, 30), font, fontSize, (255, 255, 255), thickness=2)
        return frame

    # 保存中のモニター画面（グレー画面)
    def dispGray(self, frame):         
        frame = self.__dispShutter(frame) # シャッターボタン描画
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # グレースケール
        cv2.imshow(self.__windowName, frame)
        cv2.waitKey(1)
    
    # シャッターが押されたかどうかの確認
    def Shutter(self):
        if(self.__mode == 0):
            return False
        self.__mode = 0
        return True
                    
    # モニター画面
    def disp(self, frame, rectangles, label):
        
        # シャッターボタン描画
        frame = self.__dispShutter(frame)
        
        # アノテーション表示
        for r in rectangles:
            if(len(r)==4):
                frame = cv2.rectangle(frame, (r[0], r[1]), (r[2], r[3]), (255, 255, 0), 3)
        
        # ラベル表示
        frame = self.__dispLabel(frame, label)

        cv2.imshow(self.__windowName, frame)
        cv2.setMouseCallback(self.__windowName, self.__onMouseEvent) # マウスイベント取得
