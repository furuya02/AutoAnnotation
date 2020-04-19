import cv2
import time


import shoot as sh
import annotation as an
import controller as cn
import manifest as ma

# 設定
outputPath = "/tmp/tmp0"
s3Path = "s3://my-bucket/MyProject"
projectName = "MyProject"

def main():
    
    # カメラ初期化
    deviceId = 3 # Webカメラ
    height = 600
    width = 800
    cap = cv2.VideoCapture(deviceId)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print("FPS:{}　WIDTH:{}　HEIGHT:{}".format(fps, width, height))

    # アノテーションクラス初期化    
    scale = 0.5
    annotation = an.Annotation(width, height, fps, scale)

    # コントロールクラス初期化    
    threshold = 120 # ２値化の敷居値
    only_one = 1 # １件だけ検出する
    margin = 0 # 余白
    inversion = 0 # 白黒反転
    controller = cn.Controller(threshold, only_one, margin, inversion)

    # マニフェストクラス初期化    
    manifest = ma.Manifest(outputPath, width, height, s3Path, projectName)
    
    # 撮影クラス初期化    
    shoot = sh.Shoot(width, height)

    while True:
        
        # カメラ画像取得
        ret, frame = cap.read()
        if(frame is None):
            continue

        # ラベル読み込み
        with open('./label.txt') as f:
            label = f.read()

        if(shoot.Shutter()):
            # 画面をグレーにする
            shoot.dispGray(frame.copy())
            # 名前作成
            fileName = "{}-{}".format(label, int(time.time() * 1000000))
            # 画像保存
            cv2.imwrite("{}/{}.jpg".format(outputPath, fileName), frame)
            # アノテーション保存
            manifest.save("{}.jpg".format(fileName), annotation.rectangles, label)
            time.sleep(0.5)
            print("saved")

        # コントローラ表示
        controller.disp()
        # アノテーション取得
        annotation.detection(frame.copy(), controller)
        # モニター表示
        shoot.disp(frame.copy(), annotation.rectangles, label) 

        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

main()
