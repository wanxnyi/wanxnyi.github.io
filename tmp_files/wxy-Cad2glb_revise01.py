#--------------------------------------------------------	
#	用于CATIA转GLB
#   脚本的执行逻辑为
#       1.从指定目录读取指定类型的文件，进行处理后分别导出
#           操作：曲面细分、修复网格、网格抽取
#       2.执行结束后在场景中再次选中一些节点，可以单独导出选中部分
#         （1）其中同级关系的节点分别导出，选中节点中如果存在父子关系（包括祖孙关系），则只导出子（孙）节点
#         （2）不可以导出empty occurrence
#   需要更新：
#   （1）选中隐藏并删除 ok 
#   （2）导出所有节点 (todo隐藏删除的问题)
#   （3）同名的问题 ok 给导出的文件命名加了ID
#	（4）改动了脚本的顺序，只有当场景中为空时才会导入模型，场景中不为空则只执行选中导出 ok
#--------------------------------------------------------
from fileinput import filename
from os import listdir
from os.path import isfile, isdir, join, normpath, splitext
import fnmatch
import time
#--------------------------------------------------------
#定义需要的参数（可修改）
#Step1
maxSag = 0.200000
maxLength = -1.000000
maxAngle = -1.000000
#Step2
Tolerance = 0.100000
#Step3
TargetStrategy = ["ratio", 50.000000]
BoundaryWeight = 1.000000
NormalWeight = 10.000000
UVWeight = 1.000000
SharpNormalWeight = 10.000000
UVSeamWeight = 1.000000
ForbidUVFoldovers = False
ProtectTopology = True
#Step4
#DecimateParameters(surfacicTolerance_1, linearTolerance_1, normalTolerance_1)
decimateParametersList = [DecimateParameters(1.000000, 0.100000, 5.000000), 
                            DecimateParameters(2.000000, 1.000000, 20.000000),
                            DecimateParameters(8.000000, 2.000000, 40.000000),
                            DecimateParameters(15.000000, 3.000000, 80.000000)]
#导入文件
_inputDirectory = r"G:\S2021-2022\task\yuan\0505\0000001-TESLA"
inputDirectory = _inputDirectory.replace('\\','/')
fileFormat = "CATProduct"
#导出文件
_outputDirectory = r"G:\S2021-2022\task\yuan\0505\test\TESLA_test\0510"
outputDirectory = _outputDirectory.replace('\\','/')
fileFormat_output = "glb"
#-----------------------------------------------------------------

def getFilesInDirectory(directory, extensions, recursive, joinPath):
	files = []
	#*listdir()返回指定的目录下的所有文件或文件夹的列表
	for f in listdir(directory):
		#* 对于列表中的每个文件或文件夹，用它的路径判断是不是一个文件
		fullPath = join(directory, f)
		#* 如果是文件，对于每一个要求的扩展名，进行匹配，
		if isfile(fullPath):
			#* 匹配上了扩展名的文件，如果是joinpath就进行路径的标准化，否则不用进行标准化。
			#* 把匹配上的文件放进files列表中
			if extensions:
				# check extensions
				extOk = False
				for ext in extensions:
					if fnmatch.fnmatch(f.upper(), "*." + ext.upper()):
						extOk = True
						break
				if not extOk:
					continue
			if joinPath:
				files.append(normpath(fullPath))
			else:
				files.append(f)
		#* 如果打开了recursive的开关，代表目录下的文件夹中的文件也应被取得，将会递归调用该函数
		elif recursive and isdir(fullPath):
			dirFiles = getFilesInDirectory(fullPath, extensions, recursive, joinPath)
			if not joinPath:
				tmp = dirFiles
				dirFiles = []
				for file in tmp:
					dirFiles.append(normpath(join(f, file)))
			files.extend(dirFiles)
	return files

def replaceFileExtension(file, newExt):
	(root,ext) = splitext(file)
	if(ext == "." + fileFormat):
		return root + "." + newExt
	else:
		return file + "." + newExt

def findGrandaparents(occurrence,parents):
    parentID = scene.getParent(occurrence)
    parents.append(parentID)
    #寻找祖父
    if(parentID != 0):
        findGrandaparents(parentID,parents)

def exportOccurrence(Occurrences,outputDirectory,outputFormat):
    #存储所有选中节点的父亲的ID
    parents = []
    for selection in Occurrences:
        #判断每个节点的父亲
        findGrandaparents(selection,parents)
    parents = set(parents)
    # print("查看祖父列表：",parents)
    for selection in Occurrences:
        print("当前节点是：",selection)
        if selection in parents:
          print("跳过")
          continue
        IDName = getIDName(selection)
        FileName = IDName + "." + fileFormat_output 
        filePath = join(outputDirectory,FileName)
        scene.clearSelection()
        scene.select([selection])
        #没有子节点是Part Occurrence的节点不导出
        if(scene.getPartOccurrences(selection)!=[]):
          print("导出")
          io.exportSelection(filePath)
 
#自己不包含在自己的所有孩子节点中
def getChildOccurrences(Occurrence,all_occurrences):
	many = scene.getChildren(Occurrence)	
	if(many):
		all_occurrences.extend(many)
		for i in many:
			getChildOccurrences(i,all_occurrences)

def process(root):
	#Step1 执行CAD细分    
	algo.tessellate(root,maxSag,maxLength,maxAngle)
	#Step2 选择隐藏并删除
	algo.hiddenSelection(root, 1024, 16, 90.000000, False)
	scene.deleteSelection()
	#Step3 执行修复网格
	algo.repairMesh(root,Tolerance)
	#Step4 执行目标减面
	algo.decimateTarget(root,TargetStrategy,BoundaryWeight,NormalWeight,UVWeight,SharpNormalWeight,UVSeamWeight,ForbidUVFoldovers,ProtectTopology)
	#Step5 执行生成LOD
	scenario.generateLODChain(root,decimateParametersList)
	#--------------------------------------------------

def getIDName(occurrence):
	name = core.getProperty(occurrence,"Name")
	Id = core.getProperty(occurrence,"Id")
	IDName = "[" + Id + "] " + name
	return IDName

#如果场景为空，导入并操作；如果场景不为空，选中并导出
root = scene.getRoot()#根节点的ID
childs = scene.getChildren(root)#场景中所有的模型的ID的列表
#如果场景为空
if (childs == []):
	print("即将导入模型并对场景中所有内容进行处理：----------------------------------------")
	inputFiles = getFilesInDirectory(inputDirectory, [fileFormat], False, False)
	#把模型全部导入
	for inputFile in inputFiles:
		io.importScene(join(inputDirectory,inputFile))
	#TODO 仅仅读取指定目录下的.CATProduct
	#TODO 如果当前目录有多个产品文件，通过唯一的PartNumber进行辨识，
		#?如何找到哪个产品文件是整体的文件。
	root = scene.getRoot()#根节点的ID
	childs = scene.getChildren(root)#场景中所有的模型的ID的列表
	for child in childs:
		scene.clearSelection()
		process([child])#只选中并删除当前这一个模型的隐藏部分
		IDName = getIDName(child)
		fileName = replaceFileExtension(IDName,fileFormat_output)
		filePath = join(outputDirectory,fileName)
		scene.select([child])	
		io.exportSelection(filePath)
		#获得当前模型的所有子节点
		all_occurrences = []
		getChildOccurrences(child,all_occurrences)
		#对每个子节点，进行有无Definition的判断
		for occurrence in all_occurrences:
			metadata = scene.getComponent(occurrence, 5) 
			if(metadata):
				try:
					definition = scene.getMetadata(metadata,"Definition")
					print("看下是哪些：",definition)
					scene.clearSelection()
					scene.select([occurrence])
					IDName = getIDName(occurrence)
					fileName = IDName + "." +fileFormat_output
					filePath = join(join(outputDirectory,"单独导出/"),fileName)
					io.exportSelection(filePath)
				except:
					print("当前节点有Metadata组件，但是没有definition")
			else:
				print("当前选中节点没有Metadata组件")		
	scene.clearSelection() 
		
#场景不为空
else:
  root = scene.getSelectedOccurrences()
  print("对选中内容导出：------------------------------------------------------------------")
  raw_time = time.strftime("%Y-%m-%d, %H：%M：%S", time.localtime())
  new_outputDirectory = join(outputDirectory,"手动选中导出",raw_time)
  exportOccurrence(root,new_outputDirectory,fileFormat_output)	
  scene.clearSelection() 
  