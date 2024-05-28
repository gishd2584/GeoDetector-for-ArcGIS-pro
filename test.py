import itertools
import os
import shutil
import threading
from osgeo import ogr
from tkinter.ttk import Combobox
import arcpy
import tkinter as tk
from tkinter import Frame, Label, filedialog, messagebox
import pandas as gpd

base_path = "D:\czx\data"
arcpy.env.workspace = base_path

X_PATH_LIST = {}
X1_X2_PATH_LIST = {}
Y_PATH = {}
X_COMBOX  = {}
out_point_features = {'path' : "D:/czx/data/NTD_point.shp"}
GLOBALCONFIG = {'y_value' : "grid_code"}
GLOBALOUTPUT = {}
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
    
    def read_file():
         # 打开文件选择对话框，允许选择多个文件
        file_paths = filedialog.askopenfilenames(
        title="选择Shapefiles",
        filetypes=[("Shapefiles", "*.shp")]
        )
        if not file_paths:
            return  # 用户取消选择
        
        # 为每个Shapefile创建一个下拉框和标签
        for file_path in file_paths:
            # 读取Shapefile
            X_PATH_LIST[os.path.basename(file_path)]=file_path
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(file_path, 0)  # 0表示只读模式
            layer = dataSource.GetLayer()

            # 获取属性字段名称
            fields = [field_def.GetName() for field_def in layer.schema]

            # 获取最后一个shapefile_frame来添加新的下拉框和标签
            shapefile_frame = root.shapefile_frames[-1]

            # 创建标签
            label = Label(shapefile_frame, text=os.path.basename(file_path)+"分层字段：")
            label.pack(side=tk.TOP)
            
            # 创建并填充下拉框
            combobox = Combobox(shapefile_frame, values= fields)
            combobox.pack(side=tk.TOP)
            # combobox.bind("<<ComboboxSelected>>", print("change"))
            X_COMBOX[os.path.basename(file_path)] = combobox
            combobox.current(0)  # 设置默认选项
        
        pass

    def copy_attribute_and_add_field(shapefile_path, attribute_index):
        # 打开Shapefile
        driver = ogr.GetDriverByName('ESRI Shapefile')
        # 打开Shapefile以供写入
        dataSource = driver.Open(shapefile_path, 1)  # 1 表示读写模式
        layer = dataSource.GetLayer()
        # 获取图层定义
        layer_defn = layer.GetLayerDefn()
        # 创建新的字段名称
        base_name = os.path.splitext(os.path.basename(shapefile_path))[0]
        new_field_name = f"split_{base_name[0:3]}"
        # 检查是否存在同名字段
        field_index = layer_defn.GetFieldIndex(new_field_name)
        # 如果不存在，添加字段
        if field_index != -1:
           pass
        else:
             # 创建新的字段定义，设置为字符类型
            new_field_def = ogr.FieldDefn(new_field_name, ogr.OFTString)
            new_field_def.SetWidth(50)  # 设置字段宽度，根据需要调整

            # 添加新字段到图层
            layer.CreateField(new_field_def)

       

        # 遍历所有要素（Feature），复制属性并添加新字段
        for feature in layer:
            attribute_value = feature.GetField(attribute_index)
            feature.SetField(new_field_name, f'{attribute_value}')  
            layer.SetFeature(feature)  # 更新特征
            print(attribute_value)
        # 销毁图层和数据源
        # dataSource.ExecuteSQL('REPACK your_vector_file.shp')  # 可选，重新打包以优化文件
        layer = None
        dataSource = None
        
    def check_file_type():
        """TODO:判断是否点还是面"""
        pass
    def feature_to_point(in_features,out_raster,cell_size=1000):
        # """TODO:离散化网格"""
        cell_size = int(cell_size) #分辨率
        filename = in_features.split("/")[-1][:-4] #获取输出的时候的文件名前缀
        path =  out_raster.split(".")[0] #获取输出的文件夹目录

        out_raster = path + '/' + filename + "_raster.img"
        if  os.path.exists(out_raster):
             os.unlink(out_raster)
        print("input in :",in_features,123123,out_raster,123123,cell_size,11111111111111111111111111111)
        # 开个进程先把数据转成栅格，这样方便控制输出的网格分辨率
        t1 = threading.Thread(target=arcpy.conversion.FeatureToRaster(in_features, "NTD", out_raster, cell_size))
        # 启动线程
        t1.start()
        # 等待线程执行完毕
        t1.join()

        # 等转成栅格之后再进行下一步转成网格点
        out_point_features["path"] = os.path.join(path, filename + "_point.shp")
        # out_point_features = fileHandel.unique_filename(base_path,out_point_features) TODO：后期支持重名的时候加个后缀
        arcpy.conversion.RasterToPoint(out_raster, out_point_features["path"], "Value")
        print("success save in :",path,out_point_features["path"])
        # GeoDetector.risk_aear_detector()
        pass
    
    def X1andX2():
        """TODO:求两个X区域的交集"""
        # returen X3(和X1X2同等级的)
        pass
    # 下面就是针对Y（点要素）和X（面要素的处理了）
    # TODO：对于有偏的样本Y点要素灭有做处理
    
    def create_directory_if_not_exists(dir_name):
        dir_path = os.path.join(base_path, dir_name.split(".")[0])
    # 检查目录是否存在
        if not os.path.exists(dir_path):
            # 如果目录不存在，则创建目录
            os.makedirs(dir_path)
            print(f"目录 '{dir_path}' 已创建。")
        else:
            # 如果目录已存在，清空里面的文件
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    # 如果是文件或链接，则删除
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    # 如果是目录，则递归删除
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'无法删除 {file_path}：{e}')
            print(f"目录 '{dir_path}' 中的内容已被清空。")

    def split_point_by_polygon(PATH_LIST):
        for i in PATH_LIST:
            
            t = threading.Thread(target=fileHandel.create_directory_if_not_exists(i))
            t.start()
            t.join()
            # print(123123123123123,f"split_{i[0:3]}",out_point_features["path"],arcpy.env.workspace,X_PATH_LIST[i],os.path.join(base_path, i.split(".")[0]))
            split_field = f"split_{i[0:3]}"
            t_split = threading.Thread(target=arcpy.analysis.Split(out_point_features["path"],PATH_LIST[i], split_field, os.path.join(base_path, i.split(".")[0])))
            t_split.start()
            t_split.join()

class GeoDetector:
    def __init__(self,file):
        self.file = file
        pass
    
    def sort_y_by_x(self,Y,X):
        # TODO:这里记一下X中Y的样本数后面公式要用到
        # returen{x1:[1,2,3,4],x2:[5,6,7,8]}
        pass

    # 风险区探测、风险因子探测、生态探测以及交互探测
    # risk area detector (a), Risk factor detector (b), Ecological detector (c) and Interaction detector (d)
    def risk_aear_detector():
        # 求Y在X各个子区域中的均值、方差
        # t检验上述子区域之间的差异
        aear_risk = {}
        file_paths  = []
        for i in X_PATH_LIST:
            name_space = i.split(".")[0]
            aear_risk[name_space]={}
            data_store_dir = os.path.join(base_path, i.split(".")[0])
            for root, directories, files in os.walk(data_store_dir):
                for filename in files:
                    if filename.endswith('.shp'):
                    # 拼接完整路径
                        filepath = os.path.join(root, filename)
                        file_paths.append(filepath)
                         # 打开Shapefile
                        driver = ogr.GetDriverByName('ESRI Shapefile')
                        # 打开Shapefile以供写入
                        dataSource = driver.Open(filepath, 0)  # 1 表示读写模式s
                        layer = dataSource.GetLayer()
                        # 遍历所有要素（Feature），复制属性并添加新字段
                        sum = 0
                        sun_squared = 0
                        count = 0
                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sun_squared += y_value**2
                            count += 1 
                        arg = sum/count
                        var = sun_squared/count - arg**2
                        aear_risk[name_space][f'{filename.split(".")[0]}']= {"arg":arg,"var":var,"count":count}
                        
            # 两两组合计算
            keys = list(aear_risk[name_space].keys())
            combinations = list(itertools.combinations(keys, 2))
            # print(aear_risk[name_space],combinations)
            for combo in combinations:
                # print(combo[0],combo[1])
                t_value = (aear_risk[name_space][combo[0]]["arg"] - aear_risk[name_space][combo[1]]["arg"])/(aear_risk[name_space][combo[0]]["var"]/aear_risk[name_space][combo[0]]['count'] + aear_risk[name_space][combo[1]]["var"]/aear_risk[name_space][combo[1]]['count'])**0.5
                aear_risk[name_space][f"{combo[0]}-{combo[1]}"] = t_value
        GLOBALOUTPUT["aear_risk"] = aear_risk
        # print(GLOBALOUTPUT)
        
        # print(file_paths,'\n')
        GeoDetector.ecological_detector()
        return 'success'

    def risk_factor_detector():
        GLOBALOUTPUT['risk_factor'] = {}
        
        # 直接带入公式求q
        SSW = 0
        SST = 0
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataSource = driver.Open(out_point_features["path"], 0)  # 1 表示读写模式s
        layer = dataSource.GetLayer()
        # 遍历所有要素（Feature），复制属性并添加新字段
        sum = 0
        sun_squared = 0
        count = 0
        for feature in layer:
            y_value = feature.GetField(GLOBALCONFIG['y_value'])
            sum += y_value
            sun_squared += y_value**2
            count += 1 
        arg = sum/count
        var = sun_squared/count - arg**2
        SST = count * var
        GLOBALOUTPUT['SST'] = SST


        for i in X_PATH_LIST:
            name_space = i.split(".")[0]
           
            data_store_dir = os.path.join(base_path, i.split(".")[0])
            SSW = 0
            # 单独对不同shp文件分层处理
            for root, directories, files in os.walk(data_store_dir):
                for filename in files:
                    if filename.endswith('.shp'):
                    # 拼接完整路径
                        filepath = os.path.join(root, filename)
                         # 打开Shapefile
                        driver = ogr.GetDriverByName('ESRI Shapefile')
                        # 打开Shapefile以供写入
                        dataSource = driver.Open(filepath, 0)  # 1 表示读写模式s
                        layer = dataSource.GetLayer()
                        # 遍历所有要素（Feature），复制属性并添加新字段
                        
                        sum = 0
                        sun_squared = 0
                        count = 0
                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sun_squared += y_value**2
                            count += 1 
                        arg = sum/count
                        var = sun_squared/count - arg**2
                        SSW = SSW + count * var
            GLOBALOUTPUT['risk_factor'][name_space] = 1-SSW/SST   
        print('\n\n\n\n\n',GLOBALOUTPUT)    
        GeoDetector.interactionDetector()        
        return 'success'

    def ecological_detector():
        GLOBALOUTPUT["ecological"] = {}
        keys = list(GLOBALOUTPUT["aear_risk"].keys())
        combinations = list(itertools.combinations(keys, 2))
        # print(aear_risk[name_space],combinations)
        for combo in combinations:
            # print(combo[0],combo[1])
            SSW_x1 = 0
            SSW_x2 = 0
            N_x1 = len(GLOBALOUTPUT["aear_risk"][combo[0]])
            N_x2 = len(GLOBALOUTPUT["aear_risk"][combo[1]])

            for i in GLOBALOUTPUT["aear_risk"][combo[0]]:
                print(combo[0],11111111111111111111111111,i)
                if '-' in i:
                    continue
                # N_x1 += GLOBALOUTPUT[combo[0]][i]["count"]
                SSW_x1 = SSW_x1+(GLOBALOUTPUT["aear_risk"][combo[0]][i]["var"]*GLOBALOUTPUT["aear_risk"][combo[0]][i]["count"])

            for i in GLOBALOUTPUT["aear_risk"][combo[1]]:
                if '-' in i:
                    continue
                # N_x1 += GLOBALOUTPUT[combo[0]][i]["count"]
                SSW_x2 = SSW_x2+(GLOBALOUTPUT["aear_risk"][combo[1]][i]["var"]*GLOBALOUTPUT["aear_risk"][combo[1]][i]["count"])
            f_value = (N_x1*(N_x2-1)*SSW_x1)/(N_x2*(N_x1-1)*SSW_x2)
            GLOBALOUTPUT["ecological"][f"{combo[0]}-{combo[1]}"] = f_value
        # print(GLOBALOUTPUT)
        GeoDetector.risk_factor_detector()
        return 'success'

    def interactionDetector():
        GLOBALOUTPUT["interaction"] = {}
        keys = list(GLOBALOUTPUT["aear_risk"].keys())
        combinations = list(itertools.combinations(keys, 2))
        # print(aear_risk[name_space],combinations)
        for combo in combinations:
            t_mkdir = threading.Thread(target=fileHandel.create_directory_if_not_exists(f'{combo[0]}-{combo[1]}_shpfile'))
            t_mkdir.start()
            t_mkdir.join()
            # print(X_PATH_LIST)
            inFeatures =  [[X_PATH_LIST[f'{combo[0]}.shp'], 2], [X_PATH_LIST[f'{combo[1]}.shp'], 1]]
            outFeatures = os.path.join(base_path, f'{combo[0]}-{combo[1]}_shpfile', f'{combo[0]}-{combo[1]}.shp')
            X1_X2_PATH_LIST[f'{combo[0]}-{combo[1]}'] = outFeatures
            t_union = threading.Thread(target=arcpy.analysis.Union(inFeatures, outFeatures)) 
            t_union.start()
            t_union.join()
           
            # X_PATH_LIST[combo[0]]
           
        t_split = threading.Thread(target=fileHandel.split_point_by_polygon(X1_X2_PATH_LIST))
        t_split.start()
        t_split.join()
        for i in X1_X2_PATH_LIST:
            name_space = i.split(".")[0]
            data_store_dir = os.path.join(base_path, i.split(".")[0])
            SSW = 0
            # 单独对不同shp文件分层处理
            for root, directories, files in os.walk(data_store_dir):
                for filename in files:
                    if filename.endswith('.shp'):
                    # 拼接完整路径
                        filepath = os.path.join(root, filename)
                         # 打开Shapefile
                        driver = ogr.GetDriverByName('ESRI Shapefile')
                        # 打开Shapefile以供写入
                        dataSource = driver.Open(filepath, 0)  # 1 表示读写模式s
                        layer = dataSource.GetLayer()
                        # 遍历所有要素（Feature），复制属性并添加新字段
                        
                        sum = 0
                        sun_squared = 0
                        count = 0
                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sun_squared += y_value**2
                            count += 1 
                        arg = sum/count
                        var = sun_squared/count - arg**2
                        SSW = SSW + count * var
                        
            SST = GLOBALOUTPUT['SST']
            GLOBALOUTPUT['interaction'][name_space] = 1-SSW/SST   
        
        return 'success'
    def get_arange_of_feature_field(shp_path,field_name):
        pass

class windowHandel:
    def __init__(self):
        pass

    def choose_file():
        file_paths = filedialog.askopenfilename(
        title="选择文件",
        initialdir="/",
        filetypes=(("矢量文件", "*.shp"),("所有文件", "*.*") ),
         ) 
        
        if file_paths:  # 检查是否选择了文件
            file_label.config(text=file_paths)  # 更新标签显示所有选中的文件路径
       

    def choose_directory():
        directory_path = filedialog.askdirectory()
        if directory_path:
            dir_label.config(text=directory_path)

    def get_selected_fields():
        for i in X_PATH_LIST:
            fileHandel.copy_attribute_and_add_field(X_PATH_LIST[i], X_COMBOX[i].current())
            print(X_COMBOX[i].current())
        t = threading.Thread(target=fileHandel.feature_to_point(file_label.cget('text'),dir_label.cget('text'),resolution_entry.get()))
        t.start()
        t.join()
        fileHandel.split_point_by_polygon(X_PATH_LIST)
        print(X_COMBOX)

    def confirm():
        base_path = dir_label.cget('text')
        messagebox.showinfo("确认", f"文件路径: {file_label.cget('text')}\n输出路径: {dir_label.cget('text')}")
        # fileHandel.featureToPoint(file_label.cget('text'),dir_label.cget('text'),resolution_entry.get())
        # t = threading.Thread(target=fileHandel.feature_to_point(file_label.cget('text'),dir_label.cget('text'),resolution_entry.get()))
        # t.start()
        # t.join()
        GeoDetector.risk_aear_detector()
        # t_1 = threading.Thread(target=GeoDetector.risk_aear_detector())
        # t_1.start()
        # t_1.join()
        # t_2 = threading.Thread(target=GeoDetector.ecological_detector())
        # t_2.start()
        # t_2.join()
        # t_3 = threading.Thread(target=GeoDetector.risk_factor_detector())
        # t_3.start()
        # t_3.join()
        # t_4 = threading.Thread(target=GeoDetector.interactionDetector())
        # t_4.start() 
        # t_4.join()
        print(GLOBALOUTPUT)

    def cancel():
        root.destroy()


if __name__ == "__main__":

    root = tk.Tk()
    root.title("地理探测器")
    root.geometry("800x500")
    root.shapefile_frames = []  # 创建一个空列表来存储shapefile_frame
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
    

    # 选择X
    file_label = tk.Label(root, text="选择自变量", font=("Arial", 12))
    file_label.pack(pady=10)
    
    choose_file_btn = tk.Button(root, text="选择文件", command=fileHandel.read_file)
    choose_file_btn.pack()

     # 创建一个Frame来容纳所有的Shapefile选择器
    shapefile_frame = Frame(root)
    shapefile_frame.pack(expand=True)


    dir_label = tk.Label(root, text="选择输出路径", font=("Arial", 12))
    dir_label.pack(pady=10)

    choose_dir_btn = tk.Button(root, text="选择输出路径", command=windowHandel.choose_directory)
    choose_dir_btn.pack()

    cancel1_btn = tk.Button(root, text="hah ", command=windowHandel.get_selected_fields)
    cancel1_btn.pack(side=tk.RIGHT, padx=10)

    confirm_btn = tk.Button(root, text="开始计算", command=windowHandel.confirm)
    confirm_btn.pack(side=tk.RIGHT, padx=10)

    cancel_btn = tk.Button(root, text="取消", command=windowHandel.cancel)
    cancel_btn.pack(side=tk.RIGHT, padx=10)
    # 将shapefile_frame添加到一个列表中，以便后续可以引用它
    root.shapefile_frames.append(shapefile_frame)
    
    root.mainloop()

    print("closed window")

    