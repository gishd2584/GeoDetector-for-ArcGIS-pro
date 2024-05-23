import os
import threading
import arcpy
import tkinter as tk
from tkinter import filedialog, messagebox
base_path = "D:\czx\data"
arcpy.env.workspace = base_path

#读取数据
class fileHandel:
    def __init__(self,path,type,qulity):
        self.path = path
        pass
    def unique_filename(path, filename, add_suffix=True):
    # 检查文件是否存在
        if os.path.exists(os.path.join(path, filename)):
            # 如果存在，添加后缀
            if add_suffix:
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(path, f"{name}_{counter}{ext}")):
                    counter += 1
                filename = f"{name}_{counter}{ext}"
        return filename
    def readFile():
        pass
    def checkFileType():
        """TODO:判断是否点还是面"""
        pass
    def featureToPoint(in_features,out_raster,cell_size=1000):
        """TODO:离散化网格"""
        cell_size = int(cell_size)
        filename = in_features.split("/")[-1][:-4]
        path =  out_raster.split(".")[0]
        out_raster = path + '/' + filename + "_raster.img"
        # out_raster =  filename + "_raster"
        print(out_raster)
        t1 = threading.Thread(target=arcpy.conversion.FeatureToRaster(in_features, "NTD", out_raster, cell_size))

        # 启动线程
        t1.start()
        # 等待线程执行完毕
        t1.join()
        # out_point_features = out_raster.split(".")[0] + filename + "_point"
        out_point_features =   filename + "_point.shp"
        out_point_features = fileHandel.unique_filename(base_path,out_point_features)
        in_raster = out_raster
        arcpy.conversion.RasterToPoint(in_raster, out_point_features, "Value")
        print(out_point_features,"success")
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
        pass

class windowHandel:
    def __init__(self):
        pass

    def choose_file():
        file_paths = filedialog.askopenfilename(
        title="选择文件",
        initialdir="/",
        filetypes=(("所有文件", "*.*"), ("文本文件", "*.txt"), ("图片文件", "*.png;*.jpg;*.gif"),),
        multiple=True ) # 允许选择多个文件
        
        if file_paths:  # 检查是否选择了文件
            file_label.config(text="\n".join(file_paths))  # 更新标签显示所有选中的文件路径


    def choose_directory():
        directory_path = filedialog.askdirectory()
        if directory_path:
            dir_label.config(text=directory_path)

    def confirm():
        messagebox.showinfo("确认", f"文件路径: {file_label.cget('text')}\n输出路径: {dir_label.cget('text')}")
        fileHandel.featureToPoint(file_label.cget('text'),dir_label.cget('text'),resolution_entry.get())

    def cancel():
        root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("地理探测器")
    root.geometry("800x500")

    # 添加分辨率输入框
    resolution_label = tk.Label(root, text="输入分辨率（单位：米）:", font=("Arial", 12))
    resolution_label.pack()

    resolution_entry = tk.Entry(root, font=("Arial", 12))
    resolution_entry.pack()

    # 选择Y
    file_label = tk.Label(root, text="选择应变量", font=("Arial", 12))
    file_label.pack(pady=10)
    

    choose_file_btn = tk.Button(root, text="选择文件", command=windowHandel.choose_file)
    choose_file_btn.pack()
    

    # 选择X1和X2
    file_label = tk.Label(root, text="选择自变量", font=("Arial", 12))
    file_label.pack(pady=10)
    
    

    choose_file_btn = tk.Button(root, text="选择文件", command=windowHandel.choose_file)
    choose_file_btn.pack()

    dir_label = tk.Label(root, text="选择输出路径", font=("Arial", 12))
    dir_label.pack(pady=10)

    choose_dir_btn = tk.Button(root, text="选择输出路径", command=windowHandel.choose_directory)
    choose_dir_btn.pack()

    confirm_btn = tk.Button(root, text="确定", command=windowHandel.confirm)
    confirm_btn.pack(side=tk.RIGHT, padx=10)

    cancel_btn = tk.Button(root, text="取消", command=windowHandel.cancel)
    cancel_btn.pack(side=tk.RIGHT, padx=10)

    root.mainloop()

    print("hello world")

    