
import glob
import itertools
import json
import os
import shutil
import threading
import numpy as np
from osgeo import ogr
from tkinter.ttk import Combobox
import arcpy
import tkinter as tk
from tkinter import Frame, Label, filedialog, messagebox
import pandas as gpd
from scipy.stats import t
from scipy.stats import f,ncf
import pandas as pd

base_path = {"path":"D:\czx\data"}
arcpy.env.workspace = base_path["path"]

X_PATH_LIST = {}
X1_X2_PATH_LIST = {}
Y_PATH = {}
Y_COMBOX = {}
X_COMBOX  = {}
out_point_features = {'path' : "D:/czx/data/NTD_point.shp"}
GLOBALCONFIG = {'y_value' : "grid_code",'alpha':0.05}
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
    
    
    def out_excel():
        i = 0
        # 创建一个空的DataFrame，用于存储所有工作表的名称
        for main_key, main_value in GLOBALOUTPUT["aear_risk"].items():
            aear_risk_excel_data = {}
            for key, value in main_value.items():
                print(key,value)
                if '-' in key:
                    aear_risk_excel_data[f'{key}'] = value['reject']
                else:
                    aear_risk_excel_data[f'{key}'] = value['arg']
            df = pd.DataFrame(aear_risk_excel_data, index=[0])
            if i == 0:
                df.to_excel(f"{base_path['path']}/result.xlsx", sheet_name=f"aear_{main_key}")
                i += 1
            else:
                with pd.ExcelWriter(f"{base_path['path']}/result.xlsx", mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:  # 'a' 表示追加模式
                    # 将DataFrame写入Excel的新工作表
                    df.to_excel(writer, sheet_name=f"{main_key}")



        
        risk_factor_excel_data = {}
        for main_key, main_value in GLOBALOUTPUT["risk_factor"].items():
            print(main_key,main_value,22222222222222)
            rounded_q = np.round(main_value['q'], 2)
            q_str = str(rounded_q)
            rounded_p = np.round(main_value['p_value'], 2)
            p_str = str(rounded_p)
            risk_factor_excel_data[f'{main_key}'] = [q_str,p_str]

        for main_key, main_value in GLOBALOUTPUT["interaction"].items():
            
            rounded_q = np.round(main_value, 2)
            q_str = str(rounded_q)
            risk_factor_excel_data[f'{main_key}'] = [q_str,'X']
            
        df = pd.DataFrame(risk_factor_excel_data, index=['q','p'])
        # df.to_excel(f"{base_path['path']}/risk_factor_and_interaction.xlsx")
        with pd.ExcelWriter(f"{base_path['path']}/result.xlsx", mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:  # 'a' 表示追加模式
                    # 将DataFrame写入Excel的新工作表
                    df.to_excel(writer, sheet_name=f"{'risk_inter'}")


       
        ecological_excel_data = {}
        for main_key, main_value in GLOBALOUTPUT["ecological"].items():
            ecological_excel_data[f'{main_key}'] = main_value['reject']
            df = pd.DataFrame(ecological_excel_data, index=[0])
            # df.to_excel(f"{base_path['path']}/ecological.xlsx")
            with pd.ExcelWriter(f"{base_path['path']}/result.xlsx", mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:  # 'a' 表示追加模式
                    # 将DataFrame写入Excel的新工作表
                    df.to_excel(writer, sheet_name=f"{'ecological'}")


        # 将字典转换为JSON格式的字符串，ensure_ascii=False允许非ASCII字符
        json_str = json.dumps(GLOBALOUTPUT, ensure_ascii=False)

        # 将JSON字符串写入文件
        with open(f"{base_path['path']}/raw_data.json", 'w', encoding='utf-8') as json_file:
            json_file.write(json_str)    
            
        
          

    

    def format_dict(d, indent=0):
        space = '    '  # 定义每个缩进级别的空格数
        result = ""
        # 添加开始的大括号
        result += "{\n"
 
        # 遍历字典中的所有项
        for key, value in d.items():
            # 添加键和值之间的分隔符（除了第一个键之外）
            if result.endswith("{\n"):
                sep = ""
            else:
                sep = ",\n"
            
            # 添加缩进
            result += (indent + 1) * space + sep + f"{key!r}: "
            
            # 如果值是字典，则递归调用self.format_dict
            if isinstance(value, dict):
                result += fileHandel.format_dict(value, indent + 1)
            # 如果值是列表，则格式化列表
            elif isinstance(value, list):
                result += fileHandel.format_list(value, indent + 1)
            # 其他类型直接转换为字符串
            else:
                result += str(value)
            
        # 添加结束的大括号
        result += "\n" + indent * space + "}"
        return result

    def format_list(self,list, indent=0):
        space = '    '  # 定义每个缩进级别的空格数
        result = "[\n"
        
        for item in list:
            # 添加项之间的分隔符（除了第一个项之外）
            if result.endswith("[\n"):
                sep = ""
            else:
                sep = ",\n"
            
            # 添加缩进
            result += (indent + 1) * space + sep
            
            # 如果项是字典或列表，则递归调用相应的格式化函数
            if isinstance(item, dict):
                result += self.format_dict(item, indent + 1)
            elif isinstance(item, list):
                result += self.format_list(item, indent + 1)
            # 其他类型直接转换为字符串
            else:
                result += str(item)
        
        result += "\n" + indent * space + "]"
        return result
    
    # 因为arcgiss在分割的时候需要一个字符类型的字段，所以这里对于用于分割的字段进行处理
    def copy_attribute_and_add_field(shapefile_path, attribute_index,union=False):
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
        if union:
            new_field_name = f"union_id"
        
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
        FID = 0
        for feature in layer:
            if union:
                FID = FID + 1
                attribute_value = FID
            else:
                attribute_value = feature.GetField(attribute_index)
            feature.SetField(new_field_name, f'{attribute_value}')  
            layer.SetFeature(feature)  # 更新特征
            print(attribute_value)
        # 销毁图层和数据源
        # dataSource.ExecuteSQL('REPACK your_vector_file.shp')  # 可选，重新打包以优化文件
        layer = None
        dataSource = None
        
 
    def feature_to_point(in_features,out_raster,cell_size=1000):
        # """TODO:离散化网格"""
        cell_size = int(cell_size) #分辨率
        filename = in_features.split("/")[-1][:-4] #获取输出的时候的文件名前缀
        path =  out_raster.split(".")[0] #获取输出的文件夹目录

        out_raster = path + '/' + filename + "_raster.img"

        # 使用glob模块查找所有以该前缀开头的文件
        files_to_delete = glob.glob(f'{path}/{filename}_*')
        # 遍历找到的文件并删除它们
        for file_path in files_to_delete:
            if os.path.isfile(file_path):  # 确保是一个文件
                print(f'Deleting file: {file_path}')
                os.remove(file_path)  # 删除文件
            else:
                print(f'Skipping non-file: {file_path}')
                if  os.path.exists(out_raster):
                    os.unlink(out_raster)
        # print("input in :",in_features,123123,out_raster,123123,cell_size,11111111111111111111111111111)
        # 开个进程先把数据转成栅格，这样方便控制输出的网格分辨率
        t1 = threading.Thread(target=arcpy.conversion.FeatureToRaster(in_features, GLOBALCONFIG['y_field'][Y_COMBOX[os.path.basename(in_features)].current()], out_raster, cell_size))
        # 启动线程
        t1.start()
        # 等待线程执行完毕
        t1.join()

        # 等转成栅格之后再进行下一步转成网格点
        out_point_features["path"] = os.path.join(path, filename + "_point.shp")
        # out_point_features = fileHandel.unique_filename(base_path,out_point_features) TODO：后期支持重名的时候加个后缀
        arcpy.conversion.RasterToPoint(out_raster, out_point_features["path"], "Value")
        print("success save in :",path,out_point_features["path"])
        fileHandel.split_point_by_polygon(X_PATH_LIST)
        # GeoDetector.risk_aear_detector()
        pass
    
    def X1andX2():
        """TODO:求两个X区域的交集"""
        # returen X3(和X1X2同等级的)
        pass
    # 下面就是针对Y（点要素）和X（面要素的处理了）
    # TODO：对于有偏的样本Y点要素灭有做处理
    
    def create_directory_if_not_exists(dir_name):
        dir_path = os.path.join(base_path["path"], dir_name.split(".")[0])
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

    def split_point_by_polygon(PATH_LIST,union=False):
        for i in PATH_LIST:
            t = threading.Thread(target=fileHandel.create_directory_if_not_exists(i))
            t.start()
            t.join()
            # print(123123123123123,f"split_{i[0:3]}",out_point_features["path"],arcpy.env.workspace,X_PATH_LIST[i],os.path.join(base_path, i.split(".")[0]))
            print(f"split_{i[0:3]}",177)
            split_field = f"split_{i[0:3]}"
            if union:
                split_field = 'union_id'
            t_split = threading.Thread(target=arcpy.analysis.Split(out_point_features["path"],PATH_LIST[i], split_field, os.path.join(base_path["path"], i.split(".")[0])))
            t_split.start()
            t_split.join()

class GeoDetector:
    def __init__(self): 
        pass

    # 风险区探测、风险因子探测、生态探测以及交互探测
    # risk area detector (a), Risk factor detector (b), Ecological detector (c) and Interaction detector (d)

    def start(self):
        self.risk_aear_detector()

    def risk_aear_detector(self):
        # 求Y在X各个子区域中的均值、方差
        # t检验上述子区域之间的差异
        aear_risk = {}
        file_paths  = []
        for i in X_PATH_LIST:
            name_space = i.split(".")[0]
            aear_risk[name_space]={}
            data_store_dir = os.path.join(base_path["path"], i.split(".")[0])
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
                        sum_squared = 0
                        count = 0
                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sum_squared += y_value**2
                            count += 1 
                        arg = sum/count
                        var = sum_squared/count - arg**2
                        aear_risk[name_space][f'{filename.split(".")[0]}']= {"arg":arg,"var":var,"count":count}
                        
            # 两两组合计算
            keys = list(aear_risk[name_space].keys())
            combinations = list(itertools.combinations(keys, 2))
            print(aear_risk,name_space,230)
            # print(aear_risk[name_space],combinations)
            for combo in combinations:
                print(aear_risk[name_space][combo[0]],aear_risk[name_space][combo[1]],combo[0],combo[1],232)
                t_value = (aear_risk[name_space][combo[0]]["arg"] - aear_risk[name_space][combo[1]]["arg"])/(aear_risk[name_space][combo[0]]["var"]/aear_risk[name_space][combo[0]]['count'] + aear_risk[name_space][combo[1]]["var"]/aear_risk[name_space][combo[1]]['count'])**0.5
                df = (aear_risk[name_space][combo[0]]["var"]/aear_risk[name_space][combo[0]]['count'] + aear_risk[name_space][combo[1]]["var"]/aear_risk[name_space][combo[1]]['count'])/((1/(aear_risk[name_space][combo[0]]['count']-1))*((aear_risk[name_space][combo[0]]["var"])/(aear_risk[name_space][combo[0]]['count']))**2+((1/(aear_risk[name_space][combo[1]]['count']-1))*((aear_risk[name_space][combo[1]]["var"])/(aear_risk[name_space][combo[1]]['count']))**2))
                critical_value = t.ppf(1 - GLOBALCONFIG['alpha'] / 2, df)
                if abs(t_value) > critical_value:
                    # print("拒绝零假设，认为两组之间存在显著差异。")
                    aear_risk[name_space][f"{combo[0]}-{combo[1]}"] = {'t':t_value,'df':df,'critical_value':critical_value,'reject':"Y"}
                else:
                    # print("不能拒绝零假设，认为两组之间没有显著差异。")
                    aear_risk[name_space][f"{combo[0]}-{combo[1]}"] = {'t':t_value,'df':df,'critical_value':critical_value,'reject':"N"}
        GLOBALOUTPUT["aear_risk"] = aear_risk
        self.ecological_detector()
        return 'success'

    def risk_factor_detector(self):
        GLOBALOUTPUT['risk_factor'] = {}
        
        # 直接带入公式求q
        SSW = 0
        SST = 0
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataSource = driver.Open(out_point_features["path"], 0)  # 1 表示读写模式s
        layer = dataSource.GetLayer()
        # 遍历所有要素（Feature），复制属性并添加新字段
        sum = 0
        sum_squared = 0
        count = 0
        for feature in layer:
            y_value = feature.GetField(GLOBALCONFIG['y_value'])
            sum += y_value
            sum_squared += y_value**2
            count += 1 
        arg = sum/count
        var = sum_squared/count - arg**2
        SST = count * var
        GLOBALOUTPUT['SST'] = SST
        GLOBALOUTPUT['total_var'] = var
        GLOBALOUTPUT['total_count'] = count

        for i in X_PATH_LIST:
            name_space = i.split(".")[0]
            data_store_dir = os.path.join(base_path["path"], i.split(".")[0])
            SSW = 0
            # 单独对不同shp文件分层处理
            for root, directories, files in os.walk(data_store_dir):
                sum_arg_squared = 0
                sum_N_exp_half_time_arg = 0
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
                        sum_squared = 0
                        count = 0
                        
                        

                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sum_squared += y_value**2
                            count += 1 
                            
                        arg = sum/count
                        var = sum_squared/count - arg**2
                        SSW = SSW + count * var
                        sum_arg_squared = sum_arg_squared + arg**2
                        sum_N_exp_half_time_arg = sum_N_exp_half_time_arg + ((count)**0.5)*arg
                        q = 1-SSW/SST
                        #lamda value N_popu=totalcount N_stra= count
                        lamda = (sum_arg_squared - (sum_N_exp_half_time_arg)**2 / GLOBALOUTPUT['total_count']) / GLOBALOUTPUT['total_var']
                        # F value
                        F_value = (GLOBALOUTPUT['total_count'] - count)* q / ((count - 1)* (1 - q))
                        #p value
                        p_value = ncf.sf(F_value, count - 1, GLOBALOUTPUT['total_count'] - count, nc=lamda)
            GLOBALOUTPUT['risk_factor'][name_space] = {'q':q,'lamda':lamda,'F_value':F_value,'p_value':p_value}  
        print('\n\n\n\n\n',GLOBALOUTPUT)    
        self.interactionDetector()        
        return 'success'

    def ecological_detector(self):
        GLOBALOUTPUT["ecological"] = {}
        keys = list(GLOBALOUTPUT["aear_risk"].keys())
        combinations = list(itertools.combinations(keys, 2))
        # print(aear_risk[name_space],combinations)
        for combo in combinations:
            # print(combo[0],combo[1])
            SSW_x1 = 0
            SSW_x2 = 0
            # N_x1 = len(GLOBALOUTPUT["aear_risk"][combo[0]])
            # N_x2 = len(GLOBALOUTPUT["aear_risk"][combo[1]])
            N_x1 = 0
            N_x2 = 0

            for i in GLOBALOUTPUT["aear_risk"][combo[0]]:
                print(combo[0],11111111111111111111111111,i)
                if '-' in i:
                    continue
                N_x1 = N_x1 + GLOBALOUTPUT["aear_risk"][combo[0]][i]["count"]
                SSW_x1 = SSW_x1+(GLOBALOUTPUT["aear_risk"][combo[0]][i]["var"]*GLOBALOUTPUT["aear_risk"][combo[0]][i]["count"])

            for i in GLOBALOUTPUT["aear_risk"][combo[1]]:
                if '-' in i:
                    continue
                N_x2 = N_x2 + GLOBALOUTPUT["aear_risk"][combo[1]][i]["count"]
                SSW_x2 = SSW_x2+(GLOBALOUTPUT["aear_risk"][combo[1]][i]["var"]*GLOBALOUTPUT["aear_risk"][combo[1]][i]["count"])

            f_value = (N_x1*(N_x2-1)*SSW_x1)/(N_x2*(N_x1-1)*SSW_x2)
            alpha = GLOBALCONFIG["alpha"]
            dfn = N_x1  # 组间自由度
            dfd = N_x2 # 组内自由度
            critical_value = f.ppf(1 - alpha, dfn,dfd)
            if f_value > critical_value:
                # print("拒绝零假设")
                GLOBALOUTPUT["ecological"][f"{combo[0]}-{combo[1]}"] = {'f_value':f_value,'N_x1':N_x1,'N_x2':N_x2,'SSW_x1':SSW_x1,'SSW_x2':SSW_x2,'reject':"Y",'critical_value':critical_value}
            else:
                # print("不能拒绝零假设")
                GLOBALOUTPUT["ecological"][f"{combo[0]}-{combo[1]}"] = {'f_value':f_value,'N_x1':N_x1,'N_x2':N_x2,'SSW_x1':SSW_x1,'SSW_x2':SSW_x2,'reject':"N",'critical_value':critical_value}
           
        # print(GLOBALOUTPUT)
        self.risk_factor_detector()
        return 'success'

    def interactionDetector(self):
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
            outFeatures = os.path.join(base_path["path"], f'{combo[0]}-{combo[1]}_shpfile', f'{combo[0]}-{combo[1]}.shp')
            X1_X2_PATH_LIST[f'{combo[0]}-{combo[1]}'] = outFeatures
            t_union = threading.Thread(target=arcpy.analysis.Union(inFeatures, outFeatures)) 
            t_union.start()
            t_union.join()
            fileHandel.copy_attribute_and_add_field(outFeatures, 0,True)
            # X_PATH_LIST[combo[0]]
       
        t_split = threading.Thread(target=fileHandel.split_point_by_polygon(X1_X2_PATH_LIST,True))
        t_split.start()
        t_split.join()
        for i in X1_X2_PATH_LIST:
            name_space = i.split(".")[0]
            data_store_dir = os.path.join(base_path["path"], i.split(".")[0])
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
                        sum_squared = 0
                        count = 0
                        for feature in layer:
                            y_value = feature.GetField(GLOBALCONFIG['y_value'])
                            sum += y_value
                            sum_squared += y_value**2
                            count += 1 
                        arg = sum/count
                        var = sum_squared/count - arg**2
                        SSW = SSW + count * var
                        
            SST = GLOBALOUTPUT['SST']
            GLOBALOUTPUT['interaction'][name_space] = 1-SSW/SST   
        
        return 'success'
    def get_arange_of_feature_field(shp_path,field_name):
        pass

class windowHandel:
    def __init__(self, root):
        self.root = root
        self.root.title("地理探测器")
        self.root.geometry("800x500")
        self.root.shapefile_frames = []  # 创建一个空列表来存储shapefile_frame
    

        # 创建顶部Frame
        top_frame = tk.Frame(root, relief="solid")
        top_frame.pack(fill='x',side=tk.TOP)  # 横向填充，不扩展高度

        # 在顶部Frame中添加组件

         # 选择Y
        choose_file_btn = tk.Button(top_frame, text="选择自变量文件", command=self.choose_file)
        choose_file_btn.pack(side=tk.LEFT, padx=10)
        # 选择X
        choose_file_btn = tk.Button(top_frame, text="选择因变量文件（可以多选）", command=self.read_file)
        choose_file_btn.pack(side=tk.LEFT, padx=10)
        # 选择输出路径
        choose_dir_btn = tk.Button(top_frame, text="选择输出路径", command=self.choose_directory)
        choose_dir_btn.pack(side=tk.LEFT, padx=10)


        # 创建中间Frame
        mid_frame_1 = tk.Frame(root,   relief="solid" )
        mid_frame_1.pack(fill='x',side=tk.TOP, pady=5)  
         # 创建中间Frame
        mid_frame_2 = tk.Frame(root,  relief="solid"  )
        mid_frame_2.pack(fill='x',side=tk.TOP, pady=5)  
         # 创建中间Frame
        mid_frame_3 = tk.Frame(root,   relief="solid" )
        mid_frame_3.pack(fill='x',side=tk.TOP, pady=5)  
        # 创建中间Frame
        mid_frame_4 = tk.Frame(root,   relief="solid" )
        mid_frame_4.pack(fill='x',side=tk.TOP, pady=5)  


        # 在中间Frame中添加组件
    
        # 添加检验时alpha值输入框
        alpha_label = tk.Label(mid_frame_1, text="输入检验计算时的alpha值：", font=("Arial", 12))
        alpha_label.pack(side=tk.LEFT)

        self.alpha_entry = tk.Entry(mid_frame_1, font=("Arial", 12))
        self.alpha_entry.pack(side=tk.LEFT)

        # 添加分辨率输入框
        resolution_label = tk.Label(mid_frame_2, text="输入格网分辨率（单位：米）:", font=("Arial", 12))
        resolution_label.pack(side=tk.LEFT)

        self.resolution_entry = tk.Entry(mid_frame_2, font=("Arial", 12))
        self.resolution_entry.pack(side=tk.LEFT)

        self.file_label = tk.Label(mid_frame_3, text="自变量文件路径：", font=("Arial", 12))
        self.file_label.pack(side=tk.LEFT)

        self.dir_label = tk.Label(mid_frame_4, text="输出路径：", font=("Arial", 12))
        self.dir_label.pack(side=tk.LEFT)

        # # 创建底部Frame
        # bottom_frame = tk.Frame(root,  relief="solid")
        # bottom_frame.pack(fill='both', expand=True) 

        # # 在底部Frame中添加组件
        # label_bottom = tk.Label(bottom_frame, text="底部区域")
        # label_bottom.pack()

        # 创建一个Frame来容纳所有的Shapefile选择器
        shapefile_frame_Y = Frame(root)
        shapefile_frame_Y.pack(side=tk.LEFT, fill=tk.BOTH,padx=20)

        shapefile_frame_X = Frame(root)
        shapefile_frame_X.pack(side=tk.LEFT, fill=tk.BOTH)

        confirm_btn = tk.Button(root, text="开始计算", command=self.confirm)
        confirm_btn.pack(side=tk.BOTTOM, padx=10)

        # cancel_btn = tk.Button(root, text="取消", command=self.cancel)
        # cancel_btn.pack(side=tk.BOTTOM, padx=10)
        # 将shapefile_frame添加到一个列表中，以便后续可以引用它
        self.root.shapefile_frames.append(shapefile_frame_Y)

        self.root.shapefile_frames.append(shapefile_frame_X)

    def choose_file(self):
        Y_COMBOX.clear()

        shapefile_frame = root.shapefile_frames[-2]
        self.destroy_widgets(shapefile_frame)
        file_path = filedialog.askopenfilename(
        title="选择文件",
        initialdir="/",
        filetypes=(("矢量文件", "*.shp"),("所有文件", "*.*") ),
         ) 
        
        if file_path:  # 检查是否选择了文件
            self.file_label.config(text=f'自变量文件路径->{file_path}')  # 更新标签显示所有选中的文件路径
            GLOBALCONFIG['Y_PATH'] = file_path

            # 读取Shapefile
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(file_path, 0)  # 0表示只读模式
            layer = dataSource.GetLayer()

            # 获取属性字段名称
            fields = [field_def.GetName() for field_def in layer.schema]

            # 获取倒数2个shapefile_frame来添加新的下拉框和标签
            shapefile_frame = root.shapefile_frames[-2]


            # 在外层Frame内创建内层Frame
            inner_frame = tk.Frame(shapefile_frame,  relief="solid")
            inner_frame.pack(side=tk.TOP, fill='x')
           
            # 创建标签
            label = Label(inner_frame, text="自变量:\t"+os.path.basename(file_path)+"取值字段：")
            label.pack(side=tk.LEFT)
            
            # 创建并填充下拉框
            combobox = Combobox(inner_frame, values= fields)
            combobox.pack(side=tk.LEFT)
            # combobox.bind("<<ComboboxSelected>>", print("change"))
            Y_COMBOX[os.path.basename(file_path)] = combobox
            GLOBALCONFIG['y_field'] = fields
            combobox.current(0)  # 设置默认选项
    def read_file(self):
        shapefile_frame = root.shapefile_frames[-1]
        X_COMBOX .clear()
        X_PATH_LIST.clear()
        self.destroy_widgets(shapefile_frame)
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
            X_PATH_LIST[os.path.basename(file_path)] = file_path
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(file_path, 0)  # 0表示只读模式
            layer = dataSource.GetLayer()

            # 获取属性字段名称
            fields = [field_def.GetName() for field_def in layer.schema]

            # 获取最后一个shapefile_frame来添加新的下拉框和标签
            shapefile_frame = root.shapefile_frames[-1]
            # 在外层Frame内创建内层Frame
            inner_frame = tk.Frame(shapefile_frame,  relief="solid")
            inner_frame.pack(side=tk.TOP, fill='x')
            # 创建标签
            label = Label(inner_frame, text="因变量:\t"+os.path.basename(file_path)+"分层字段：")
            label.pack(side=tk.LEFT)
            
            # 创建并填充下拉框
            combobox = Combobox(inner_frame, values= fields)
            combobox.pack(side=tk.LEFT)
            # combobox.bind("<<ComboboxSelected>>", print("change"))
            X_COMBOX[os.path.basename(file_path)] = combobox
            combobox.current(0)  # 设置默认选项
        
        pass
    def choose_directory(self):
        directory_path = filedialog.askdirectory()
        GLOBALCONFIG['output_path'] = directory_path
        if directory_path:
            self.dir_label.config(text=f'输出路径->{directory_path}')

    

    def confirm(self):
        if self.file_label.cget('text')=="自变量文件路径：" or self.dir_label.cget('text')=="输出路径：" or self.alpha_entry.get()=='' or self.resolution_entry.get()=='' or X_PATH_LIST == {}:
            messagebox.showinfo("错误", "参数不完整")
            print(self.file_label.cget('text')=="自变量文件路径：" , self.dir_label.cget('text')=="输出路径：",self.alpha_entry.get()=='',self.resolution_entry.get()=='',X_PATH_LIST )
        else:
            base_path["path"] = GLOBALCONFIG['output_path']
            messagebox.showinfo("确认", f" {self.file_label.cget('text')}\n {self.dir_label.cget('text')}")
            for i in X_PATH_LIST:
                fileHandel.copy_attribute_and_add_field(X_PATH_LIST[i], X_COMBOX[i].current())
                print(X_COMBOX[i].current())
            # fileHandel.featureToPoint(self.file_label.cget('text'),self.dir_label.cget('text'),self.resolution_entry.get())
            GLOBALCONFIG["alpha"] = float(self.alpha_entry.get())
            print(GLOBALCONFIG)
            t = threading.Thread(target=fileHandel.feature_to_point(GLOBALCONFIG['Y_PATH'],GLOBALCONFIG['output_path'] ,self.resolution_entry.get()))
            t.start()
            t.join()
            geodetector = GeoDetector()
            geodetector.start()
        
            print(GLOBALOUTPUT)    
            fileHandel.out_excel()
            messagebox.showinfo("完成", "文件已保存到" + base_path["path"] + "下" + "output.txt")
        # self.root.destroy()

    def destroy_widgets(self, frame):
    # 遍历frame中的所有子组件
        for widget in frame.winfo_children():
            # 调用每个组件的destroy方法
            widget.destroy()
    def cancel(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    windowHandel = windowHandel(root)
    root.mainloop()
    print("closed window")

    