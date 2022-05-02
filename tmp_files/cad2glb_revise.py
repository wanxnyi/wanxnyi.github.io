#用于CATIA转GLB
from os import listdir
from os.path import isfile, isdir, join, normpath, splitext
import fnmatch

def getFilesInDirectory(directory, extensions, recursive, joinPath):
	files = []
	for f in listdir(directory):
		fullPath = join(directory, f)
		if isfile(fullPath):
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
	return root + "." + newExt

#获取某一节点的所有子节点(没用上)
all_occurrences = []
def getChildOccurrences(Occurrence):
	many = scene.getChildren(Occurrence)	
	if(many):
		all_occurrences.extend(many)
		for i in many:
			getChildOccurrences(i)

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
inputDirectory = "G:/S2021-2022/task/yuan/0425/转向系统/"
fileFormat = "CATProduct"
#导出文件
outputDirectory = "G:/S2021-2022/task/yuan/0425/test/"
fileFormat_output = "glb"
#-----------------------------------------------------------------
def process(root,fileName):
	#Step1 执行CAD细分    
	algo.tessellate(root,maxSag,maxLength,maxAngle)
	#Step2 执行修复网格
	algo.repairMesh(root,Tolerance)
	#Step3 执行目标减面
	algo.decimateTarget(root,TargetStrategy,BoundaryWeight,NormalWeight,UVWeight,SharpNormalWeight,UVSeamWeight,ForbidUVFoldovers,ProtectTopology)
	#Step4 执行生成LOD
	scenario.generateLODChain(root,decimateParametersList)
	#--------------------------------------------------
	#导出保存
	io.exportScene(join(outputDirectory,fileName))

#获取所有选中的节点，如果没有选中的内容，就获取整个场景
root = scene.getSelectedOccurrences()
if(root):
	print("对选中内容进行process处理：------------------------------------------------------------------")
	name_root = core.getProperty(root[0],"Name")
	fileName_root = replaceFileExtension(name_root,fileFormat_output)
	process(root,fileName_root)
else:
	print("没有选中的内容，即将导入模型并对场景中所有内容进行处理：----------------------------------------")
	inputFiles = getFilesInDirectory(inputDirectory, [fileFormat], True, False)
	for inputFile in inputFiles:
		io.importScene(join(inputDirectory,inputFile))
		root = [scene.getRoot()]
		#在没有选中的情况下 对于场景中的每个模型，都执行process处理
		childs = scene.getChildren(root[0])
		for child in childs:
			name = core.getProperty(child,"Name")
			fileName = replaceFileExtension(name,fileFormat_output)
			process([child],fileName)
			scene.deleteOccurrences([child])	