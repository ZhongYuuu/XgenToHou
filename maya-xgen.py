# 使用py调用maya里xgen面板

# # ------------------------------------------------------------
# # xgen
# # get xgen data
# import xgenm as xg
# import xgenm.xgGlobal as xgg
# import xgenm.XgExternalAPI as xge

# if xgg.Maya:

#     #palette is collection, use palettes to get collections first.
#     palettes = xg.palettes()
#     for palette in palettes:
#         print("Collection:" + palette)

#         #Use descriptions to get description of each collection
#         descriptions = xg.descriptions(palette)
#         for description in descriptions:
#             print("Description:" + description)
#             objects = xg.objects(palette, description, True)

#             #Get active objects,e.g. SplinePrimtives
#             for object in objects:
#                 print(" Object:" + object)
#                 attrs = xg.allAttrs(palette, description, object)
#                 for attr in attrs:
#                     print (" Attribute:" + attr + ", Value:" + xg.getAttr(attr, palette, description, object))

# # set xgen data
# # xg.setAttr("iMethod",xge.prepForAttribute("1"),"collection", "description", "SplinePrimitive")
# xg.setAttr("cacheFileName",xge.prepForAttribute("${DESC}.abc"),"nier:Nier_hair", "nier:hou1", "SplinePrimitive")

# de = xgg.DescriptionEditor
# de.refresh("Full")

# # --------------------------------------------------------
# # set all cache file name to ${DESC}.abc
# import xgenm as xg
# import xgenm.xgGlobal as xgg
# import xgenm.XgExternalAPI as xge

# if xgg.Maya:

#     palettes = xg.palettes()
#     for palette in palettes:
#         # print("Collection:" + palette)
#         if 'hair' not in palette:
#             continue
#         descriptions = xg.descriptions(palette)
#         for description in descriptions:
#             # print("Description:" + description)
#             xg.setAttr("useCache",xge.prepForAttribute("true"),palette, description, "SplinePrimitive")
#             xg.setAttr("liveMode",xge.prepForAttribute("false"),palette, description, "SplinePrimitive")
#             # xg.setAttr("iMethod",xge.prepForAttribute("1"),"collection", "description", "SplinePrimitive")
#             # xg.setAttr("cacheFileName",xge.prepForAttribute("${DESC}.abc"),"nier:Nier_hair", "nier:hou1", "SplinePrimitive")
#             xg.setAttr("cacheFileName",xge.prepForAttribute("${DESC}.abc"),palette, description, "SplinePrimitive")


# de = xgg.DescriptionEditor
# de.refresh("Full")

# # --------------------------------------------------------
# change Collection/Edit File Path
# a = xg.getAttr("xgDataPath", 'nier:Nier_hair')
# newPath = ';lakjdflksjdf'
# a = "{}{}".format(a,newPath)
# xg.setAttr("xgDataPath", a , 'nier:Nier_hair')
# # --------------------------------------------------------

# # 在lookdev工程导出毛发guides，把原本的xgen转换成curves，再选择导出即可
# import maya.cmds as cmds
# import xgenm as xg
# import xgenm.xgGlobal as xgg

# if xgg.Maya:
#     palettes = xg.palettes()
#     for palette in palettes:
#         descriptions = xg.descriptions(palette)
#         for description in descriptions:
#             print(" Description:" + description)
#             guidesName = xg.descriptionGuides(description)
#             print(guidesName)
#             cmds.select(guidesName, r = True)
#             newName = description+"_Curves"
#             mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "%s")' % (newName))
#             rootName = "-root %s " % (newName)
#             command = ('-j \
#                         -stripNamespaces\
#                         -uvWrite\
#                         -writeColorSets\
#                         -writeFaceSets\
#                         -worldSpace\
#                         -writeVisibility\
#                         -writeUVSets\
#                         -dataFormat ogawa\
#                         -frameRange 0 0\
#                         %s\
#                         -file %s' % (rootName,exportAbcPath))
#             cmds.AbcExport( j=command )
