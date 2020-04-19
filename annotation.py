import cv2

# アノテーションクラス
class Annotation():
    def __init__(self, width, height, fps, scale):
        self.__windowName = 'Anotation'
        self.__width = int(width)
        self.__height = int(height)
        self.__scale = scale
        self.__counter = 0
        self.__rectangles = []
        self.__fps = fps
    
    @property
    def rectangles(self):
        return self.__rectangles

    # 矩形検出のための前処理
    def __preProcessing(self, src, threshold, inversion):
        # グレースケール
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) 
        # 反転
        if(inversion == 1):
            src = cv2.bitwise_not(src)
        # しきい値指定によるフィルタリング
        ret, src = cv2.threshold(src, threshold, 255, cv2.THRESH_BINARY)
        return src
    
    # 多角形から矩形を取得する
    def __convertPolygonToRectangle(self, polygon):
        min_X = self.__width * 2
        min_Y = self.__height * 2
        max_X = 0
        max_Y = 0
        for p in polygon:
            if(max_X < p[0]):
                max_X = p[0]
            if(min_X > p[0]):
                min_X = p[0]
            if(max_Y < p[1]):
                max_Y = p[1]
            if(min_Y > p[1]):
                min_Y = p[1]
        return [min_X, min_Y, max_X, max_Y]
    
    def __getSize(self, rectangle):
        w = rectangle[2] - rectangle[0] + 1
        h = rectangle[3] - rectangle[1] + 1
        return w * h

    # 1点のみ検出する(一番サイズの大きい矩形のみ検出対象とする)
    def __onlyOne(self, rectangles):
        maxSize = 0
        maxRectangle = []
        for r in rectangles:
            size = self.__getSize(r)
            if(maxSize < size):
                maxSize = size
                maxRectangle = r
        return [maxRectangle]
    
    # 画面いっぱいの矩形は、対象外とする
    def __removeFullSize(self, rectangles):
        result = []
        maxSize = self.__width * self.__height
        for r in rectangles:
            size = self.__getSize(r)
            if(size < maxSize):
                result.append(r)
        return result

    # 矩形検出
    def __getRectangles(self, frame):
        rectangles = []
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            # ある程度の面積が有るものだけを対象とする
            a = cv2.contourArea(cnt, False)
            if(a > 1000):
                # 輪郭を直線近似する
                approx = cv2.approxPolyDP(cnt, 0.05 * cv2.arcLength(cnt, True), True)
                corner = []
                for p in approx:
                    corner.append(p[0])
                    # 輪郭をデバッグ表示
                    # frame = cv2.drawContours(frame, [approx], -1, (255,0,0),2)
                
                # 多角形から矩形を取得する
                rectangles.append(self.__convertPolygonToRectangle(corner))
        return rectangles
    
    # 含まれるものを削除する
    def __removeInner(self, rectangles):
        result = []
        for r in rectangles: 
            if(len(r)==4):
                min_x = r[0]
                min_y = r[1]
                max_x = r[2]
                max_y = r[3]
                isInclude = False
                for t in rectangles:
                    if( t[0] < min_x  and t[1] < min_y and max_x < t[2] and max_y < t[3]):
                        isInclude = True
                        break
                if(isInclude == False):
                    result.append(r)
        return result

    # マージンを適用する
    def __setMargen(self, rectangles, margin):
        for r in rectangles:
            r[0] -= margin
            if(r[0]<0):
                r[0] = 0
            r[1] -= margin
            if(r[1]<0):
                r[1] = 0
            r[2] += margin
            if(r[2] > self.__width):
                r[2] = self.__width
            r[3] += margin
            if(r[2] > self.__height):
                r[2] = self.__height
        return rectangles


    # 矩形検出（グレースケール画面）
    def detection(self, frame, controller):

        # コントロールクラスから設定値の取得
        (threshold, inversion, only_one, margin) = controller.getValue()
        
        # 矩形検出のための前処理
        frame = self.__preProcessing(frame, threshold, inversion)

        # 矩形検出は1秒に1回のみ
        self.__counter += 1
        if(self.__counter > self.__fps):
            self.__counter = 0
            # 矩形検出
            self.__rectangles = self.__getRectangles(frame)
            # 画面いっぱいの矩形は、対象外とする
            self.__rectangles = self.__removeFullSize(self.__rectangles)
            # 一つだけ検出する
            if(only_one == 1):
                self.__rectangles = self.__onlyOne(self.__rectangles)
            # 含まれるものを削除する
            self.__rectangles = self.__removeInner(self.__rectangles)

            # 余白
            self.__rectangles = self.__setMargen(self.__rectangles, margin)
            #margin
            
        # サイズを縮小する
        frame = cv2.resize(frame, dsize=(int(self.__width * self.__scale), int(self.__height * self.__scale)))
        cv2.imshow(self.__windowName, frame)