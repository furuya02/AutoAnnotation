
import os
import json
import datetime

class Data():
    def __init__(self, src):
        # プロジェクト名の取得
        for key in src.keys():
            index = key.rfind("-metadata")
            if(index!=-1):
                projectName = key[0:index]

        # メタデータの取得
        metadata = src[projectName + '-metadata']
        class_map = metadata["class-map"]

        # 画像名の取得
        self.__imgFileName = os.path.basename(src["source-ref"])
        self.__baseName = self.__imgFileName.split('.')[0]
        # 画像サイズの取得
        project = src[projectName]
        image_size = project["image_size"]
        self.__img_width = image_size[0]["width"]
        self.__img_height = image_size[0]["height"]
        
        self.__annotations = []
        # アノテーションの取得
        for annotation in project["annotations"]:
            class_id = annotation["class_id"]
            top = annotation["top"]
            left = annotation["left"]
            width = annotation["width"]
            height = annotation["height"]

            self.__annotations.append({
                "label": class_map[str(class_id)],
                "width": width,
                "top": top,
                "height": height,
                "left": left
            })
    def getLabels(self):
        labels = []
        for annotation in self.__annotations:
            labels.append(annotation["label"])
        return labels



# マニュフェストクラス
class Manifest():
    def __init__(self, outputPath, width, height, s3Path, projectName):
        self.__width = width
        self.__height =  height
        self.__outputFile = "{}/output.manifest".format(outputPath)
        self.__s3Path = s3Path
        self.__projectName = projectName
        self.__labels = []

        self.__jsonList = []
        if os.path.exists(self.__outputFile):
            with open(self.__outputFile, 'r') as f:
                self.__jsonList = f.read().split('\n')
        
        for src in self.__jsonList:
            data = Data(json.loads(src))
            labels = data.getLabels()
            for label in labels:
                if((label in self.__labels) == False):
                    self.__labels.append(label)
    
    def __createJson(self, imageName, rectangles, label):

        if(label in self.__labels):
            cls_id = self.__labels.index(label)
        else:
            self.__labels.append(label)
            cls_id = len(self.__labels)-1

        src = {}
        src["source-ref"] = "{}/{}".format(self.__s3Path, imageName)
        src[self.__projectName] = {}
        src[self.__projectName]["annotations"] = []
        for rectangle in rectangles:
            src[self.__projectName]["annotations"].append({
                    "class_id": cls_id,
                    "width": int(rectangle[2])-int(rectangle[0]),
                    "top": int(rectangle[1]),
                    "height": int(rectangle[3])-int(rectangle[1]),
                    "left": int(rectangle[0])
            })
        src[self.__projectName]["image_size"] = []
        src[self.__projectName]["image_size"].append({
            "width": self.__width,
            "height": self.__height,
            "depth": 3
        })
        src["{}-metadata".format(self.__projectName)] = {}
        src["{}-metadata".format(self.__projectName)]["job-name"] = "labeling-job"
        src["{}-metadata".format(self.__projectName)]["class-map"] = {
            str(cls_id): label 
        }
        src["{}-metadata".format(self.__projectName)]["human-annotated"] = "yes"
        src["{}-metadata".format(self.__projectName)]["objects"] = [{
             "confidence": 1
        }]
        dt = datetime.datetime.now()
        src["{}-metadata".format(self.__projectName)]["creation-date"] = dt.isoformat(timespec='microseconds')
        src["{}-metadata".format(self.__projectName)]["type"] = "groundtruth/object-detection"
        return src

    def save(self, imageName, rectangles, label):
        src = self.__createJson(imageName, rectangles, label)
        print(src)
        str = json.dumps(src)
        self.__jsonList.append(str)
        text = "\n".join(self.__jsonList)
        with open(self.__outputFile, "w") as f: 
            f.write(text)   