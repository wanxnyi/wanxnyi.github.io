#--------------------------------------------------------	
#	用于导出选中的多个节点为单独的glb文件
#   其中同级关系的节点分别导出，父子关系（包括祖孙关系）的节点只导出子（孙）节点
#   不可以导出empty occurrence
#--------------------------------------------------------
#同时选中的节点之间是否为父子关系：不可以用level判断。可以getParent判断
from os.path import join

selections = scene.getSelectedOccurrences()
outputDirectory = "G:/S2021-2022/task/yuan/0505/test/select/"
outputFormat = "glb"

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
      name = core.getProperty(selection,"Name")
      fileName = name + "." + outputFormat
      filePath = join(outputDirectory,fileName)
      scene.clearSelection()
      scene.select([selection])
      #没有子节点是Part Occurrence的节点不导出
      if(scene.getPartOccurrences(selection)!=[]):
        print("导出")
        io.exportSelection(filePath)
      #?如何使选中的内容分别导出而不是一起导出：
      #a清空手动选中的节点，使用记录的选中列表来设置模拟选中并分别导出
print("--------------------------------------------------------------------------------------------")
exportOccurrence(selections,outputDirectory,outputFormat)