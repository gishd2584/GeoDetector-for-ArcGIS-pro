#读取数据
class fileHandel:
    def __init__(self,path,type,qulity):
        self.path = path
        pass
    def readFile():
        pass
    def checkFileType():
        """TODO:判断是否点还是面"""
        pass
    def splitDate():
        """TODO:离散化网格"""
        pass
    def X1andX2():
        """TODO:求两个X区域的交集"""
        # returen X3(和X1X2同等级的)
        pass
    # 下面就是针对Y（点要素）和X（面要素的处理了）
    # TODO：对于有偏的样本Y点要素灭有做处理

class GeoDetector:
    def __init__(self,file):
        self.file = file
        pass
    
    def sortYbyX(self,Y,X):
        # TODO:这里记一下X中Y的样本数后面公式要用到
        # returen{x1:[1,2,3,4],x2:[5,6,7,8]}
        pass

    # 风险区探测、风险因子探测、生态探测以及交互探测
    # k area detector (a), Risk factor detector (b), Ecological detector (c) and Interaction detector (d)
    def riskAearDetector(self,Y,X):
        # 求Y在X各个子区域中的均值、方差
        # t检验上述子区域之间的差异
        pass

    def riskFactorDetector(self,Y,X):
        # 直接带入公式求q
        pass

    def ecologicalDetector(self,Y,X1,X2):
        pass

    def interactionDetector(self,Y,X1,X2):
        X = fileHandel.X1andX2(X1,X2)
        self.riskFactorDetector(Y,X)

    