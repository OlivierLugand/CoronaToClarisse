import os, MaxPlus, json, io, pymxs
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QMessageBox,QFileDialog,QErrorMessage

fname = os.path.join(os.path.join(os.path.dirname(__file__)),"ConvertorTree.ui")
ui_type, base_type = MaxPlus.LoadUiType(fname)


######  GLOBAL VARIABLES
rt = pymxs.runtime

######  Dictionnary pairs Clarisse/Corona

clarisse_coronaLayeredMtl_pairs = {
                            'base': 'baseMtl', 
                            'layer_1': 'Layers[0]',
                            'weight_1': 'amounts[0]',
                            'tx_weight_1': 'mixmaps[0]',
 
                            'layer_2': 'Layers[1]',
                            'weight_2': 'amounts[1]',
                            'tx_weight_2': 'mixmaps[1]',
 
                            'layer_3': 'Layers[2]',
                            'weight_3': 'amounts[2]',
                            'tx_weight_3': 'mixmaps[2]',
 
                            'layer_4': 'Layers[3]',
                            'weight_4': 'amounts[3]',
                            'tx_weight_4': 'mixmaps[3]',
 
                            'layer_5': 'Layers[4]',
                            'weight_5': 'amounts[4]',
                            'tx_weight_5': 'mixmaps[4]',
                            }
clarisse_coronaLightMtl_pairs = {
                            'diffuse_front_color': 'color', 
                            'specular_1_color': 'specularColor',
                            'normal_input' : 'normalCamera',
                            'opacity' : 'transparency'
                             }
clarisse_coronaMtl_pairs = {
                            'diffuse_front_color': 'colorDiffuse',
                            'tx_diffuse_front_color': 'texmapDiffuse',
                            'diffuse_front_strength': 'levelDiffuse',
                            'diffuse_roughness': None,
                            'diffuse_back_color': 'colorTranslucency',
                            'tx_diffuse_back_color': 'texmapTranslucency',
                            'diffuse_back_strength': 'levelTranslucency',
                            'tx_diffuse_back_strength': 'texmapTranslucencyFraction',
 
                            'diffuse_sss_mix': 'levelSss',
                            'diffuse_sss_mode': None,
                            'diffuse_sss_density_scale': None,
                            'diffuse_sss_color_1': 'sssScatterColor',
                            'tx_diffuse_sss_color_1': 'texmapScatterColor',
                            'diffuse_sss_distance_1': 'sssRadius',
                            'tx_diffuse_sss_distance_1': 'texmapSssRadius',
                            'diffuse_sss_weight_1': 'sssWeight1',
                            'tx_diffuse_sss_weight_1': 'texmapSssAmount',
                            'diffuse_sss_color_2': None,
                            'diffuse_sss_distance_2': None,
                            'diffuse_sss_weight_2': None,
                            'diffuse_sss_color_3': None,
                            'diffuse_sss_distance_3': None,
                            'diffuse_sss_weight_3': None,
                            'diffuse_sss_group[0]': None,
 
                            'diffuse_normal_mode': None,
                            'diffuse_normal_input': None,
 
                            'specular_1_color': 'colorReflect',
                            'tx_specular_1_color': 'texmapReflect',
                            'specular_1_strength': 'levelReflect',
                            'specular_1_roughness': 'reflectGlossiness',
                            'tx_specular_1_roughness': 'texmapReflectGlossiness',
                            'specular_1_anisotropy': 'anisotropy',
                            'tx_specular_1_anisotropy': 'texmapReflectAnisotropy',
                            'specular_1_anisotropy_rotation': 'anisotropyRotation',
                            'tx_specular_1_anisotropy_rotation': 'texmapReflectAnisotropyRotation',
                            'specular_1_fresnel_mode': None,
                            'specular_1_index_of_refraction': 'fresnelIor',
                            'specular_1_fresnel_preset': None,
                            'specular_1_fresnel_reflectivity': None,
                            'specular_1_fresnel_edge_tint': None,
                            'specular_1_brdf': None,
                            'specular_1_exit_color': None,
                            'specular_1_normal_mode': None,
                            'specular_1_normal_input': None,
 
                            'specular_2_color': None,
                            'specular_2_strength': None,
                            'specular_2_roughness': None,
                            'specular_2_anisotropy': None,
                            'specular_2_anisotropy_rotation': None,
                            'specular_2_fresnel_mode': None,
                            'specular_2_index_of_refraction': None,
                            'specular_2_fresnel_preset': None,
                            'specular_2_fresnel_reflectivity': None,
                            'specular_2_fresnel_edge_tint': None,
                            'specular_2_brdf': None,
                            'specular_2_exit_color': None,
                            'specular_2_normal_mode': None,
                            'specular_2_normal_input': None,
 
                            'transmission_color': 'colorRefract',
                            'tx_transmission_color': 'texmapRefract',
                            'transmission_strength': 'levelRefract',
                            'transmission_link_to_specular': None,
                            'transmission_linked_to': None,
                            'transmission_index_of_refraction': 'ior',
                            'transmission_roughness': 'refractGlossiness',
                            'transmittance_color': None,
                            'transmittance_density': None,
                            'transmission_exit_color': None,
                            'transmission_normal_mode': None,
                            'transmission_normal_input': None,
 
                            'emission_color': 'colorSelfIllum',
                            'tx_emission_color': 'texmapSelfIllum',
                            'emission_strength': 'levelSelfIllum',
 
                            'normal_input' : 'texmapBump',
 
                            'opacity': None
                            }
                                                                                       
clarisse_corona_pairs = { 'CoronaLayeredMtl' : clarisse_coronaLayeredMtl_pairs, 'CoronaMtl' : clarisse_coronaMtl_pairs, 'CoronaLightMtl' : clarisse_coronaLightMtl_pairs}



class MyWidget(base_type, ui_type):
    def __init__(self, parent = None):
        base_type.__init__(self)
        ui_type.__init__(self)
        self.setupUi(self)
        MaxPlus.AttachQWidgetToMax(self)
        
        
        pb_browse = self.pushButtonBrowse
        pb_browse.clicked.connect(self.buttonBrowse)
        
        pb_addObjects = self.pushButtonAddObjects
        pb_addObjects.clicked.connect(self.buttonAddObjects)
        
        pb_removeObjects = self.pushButtonRemoveObjects
        pb_removeObjects.clicked.connect(self.buttonRemoveObjects)
        
        pb_export = self.pushButtonExport
        pb_export.clicked.connect(self.buttonExport)
        
            
        cb_exportMesh = self.checkBox
            
        
        self.listMeshes = []
        self.listMaterials = []
        self.listSubMaterials = []
        
                
    
    def buttonAddObjects(self):
        
        ############ List of Selected Meshes Names ###########
        
        self.NumberMeshesAdded = getSelectedMeshesMaterials()
        
        if len(self.listMeshes) == 0 :
            for i in range(len(self.NumberMeshesAdded)):
                self.listMeshes.append(self.NumberMeshesAdded[i])
                
        else :
            for i in range(len(self.NumberMeshesAdded)):
            
            
                objectName = str(self.NumberMeshesAdded[i][0])
                if objectName in str(self.listMeshes):
                    errorOutputFile = str('Mesh : '+ objectName + ' already exists in the list')
                    msgBox = QMessageBox()
                    msgBox.setText(errorOutputFile)
                    msgBox.exec_()
                else:
                    self.listMeshes.append(self.NumberMeshesAdded[i])
                    
                
        
        
        ############ Fill list ############
                
        
        tree = self.treeWidget
        
        if tree.topLevelItemCount() == 0:
        
            for i in range(len(self.listMeshes)):
                self.topItem = QtWidgets.QTreeWidgetItem()
                self.topItem.setText( 0 , self.listMeshes[i][0])
                self.topItem.setText( 1 , self.listMeshes[i][1])
                if not len(self.listMeshes[i]) == 2 :
                    self.topItem.setBackground(0,QtGui.QBrush(QtGui.QColor(50,128,50)))
                    self.topItem.setBackground(1,QtGui.QBrush(QtGui.QColor(50,128,50)))
                tree.addTopLevelItem(self.topItem)
                if not len(self.listMeshes[i]) == 2 :
                    j = 2
                    while j < len(self.listMeshes[i]):
                        self.item1 = QtWidgets.QTreeWidgetItem(self.topItem)
                        self.item1.setText( 0, '' )
                        self.item1.setText( 1, self.listMeshes[i][j])
                        self.item1.setBackground(1,QtGui.QBrush(QtGui.QColor(50,128,50)))
                        j += 1
        
        else:
            listTopLevelItemName = []
            for i in range(tree.topLevelItemCount()):
                topLevelItemName = tree.topLevelItem(i)
                listTopLevelItemName.append(topLevelItemName.text(0))
            
            
            for i in range(len(self.listMeshes)):
                if not self.listMeshes[i][0] in listTopLevelItemName :
                    
                    self.topItem = QtWidgets.QTreeWidgetItem()
                    self.topItem.setText( 0 , self.listMeshes[i][0])
                    self.topItem.setText( 1 , self.listMeshes[i][1])
                    if not len(self.listMeshes[i]) == 2 :
                        self.topItem.setBackground(0,QtGui.QBrush(QtGui.QColor(50,128,50)))
                        self.topItem.setBackground(1,QtGui.QBrush(QtGui.QColor(50,128,50)))
                    tree.addTopLevelItem(self.topItem)
                    
                    if not len(self.listMeshes[i]) == 2 :
                        j = 2
                        while j < len(self.listMeshes[i]):
                            
                            self.item1 = QtWidgets.QTreeWidgetItem(self.topItem)
                            self.item1.setText( 0, '' )
                            self.item1.setText( 1, self.listMeshes[i][j])
                            self.item1.setBackground(1,QtGui.QBrush(QtGui.QColor(50,128,50)))
                            j += 1
        
        
        


        
    def buttonRemoveObjects(self):
        tree = self.treeWidget
        selectedItems = tree.selectedItems()
        for i in range(len(selectedItems)):
            self.item = selectedItems[i]
            self.row = tree.indexFromItem(self.item).row()
            tree.takeTopLevelItem(self.row)
            del self.listMeshes[self.row]
    
    def buttonBrowse(self):
        browseLine = self.lineEdit
        path = QFileDialog.getExistingDirectory()
        browseLine.setText(path)
            
    def buttonExport(self):
        #obj = self.objButton
        browseLine = self.lineEdit
        finalPath = browseLine.text()
        
        ############ Check if an output path is defined ############
        if finalPath == '':
            errorOutputFile = str('Please define the output file')
            msgBox = QMessageBox()
            msgBox.setText(errorOutputFile)
            msgBox.exec_()
                
        else:
            shader = []
            
            ############ Get list of objects ############
            
            for i in range(len(self.listMeshes)):
                dataAll = []
                dataMesh = rt.execute("$'"+self.listMeshes[i][0]+"'")
                materialClass =  str(rt.classOf(dataMesh.material))
                
                
                if materialClass == 'Multimaterial' :
                    subMaterialCount = dataMesh.material.materialIDList
                    shader = fillJson(dataMesh, subMaterialCount)
                    
                else:
                    materialCount = [1]
                    shader = fillJson(dataMesh, materialCount)
            
            
                try:
                    to_unicode = unicode
                except NameError:
                    to_unicode = str
                    
                
                if shader:
                    
                    ############ Write JSON file ############
                    
                    fileName = shader[0].get('object_name')
                    fileNameSave = finalPath + '/' + fileName + '.json'
                    with io.open(fileNameSave, 'w', encoding='utf8') as outfile:
                        str_ = json.dumps(shader, indent=4, separators=(',', ': '), ensure_ascii=False)
                        outfile.write(to_unicode(str_))
                
                ############ Check if export mesh is selected ############
                
                exportCheckBox = self.checkBox
                if exportCheckBox.isChecked() == True:
                    fileExportMesh = finalPath + '/' + fileName + '.abc'
                    rt.select(dataMesh)
                    if not materialClass == 'Multimaterial':
                        modifierID = rt.materialmodifier()
                        rt.addModifier(dataMesh,modifierID)
                            
                    rt.exportFile(fileExportMesh, rt.Name("noPrompt"), selectedOnly=True)
            
    
    


def getSelectedMeshesMaterials():
    selObjects = rt.selection
    listSelection = []
    for i in range(len(selObjects)):
        meshNameMaterial = []
        dataMesh = selObjects[i]
        meshNameMaterial.append(str(dataMesh.name))
        materialClass = str(rt.classOf(dataMesh.material))
        
        if materialClass == 'Multimaterial' :
            meshNameMaterial.append(str(dataMesh.material.name))
            subMaterialCount = dataMesh.material.materialIDList
            for i in range(len(subMaterialCount)):
                meshNameMaterial.append(str(dataMesh.material.materialList[i]))
            
        elif materialClass == 'CoronaLayeredMtl' :
            meshNameMaterial.append(str(dataMesh.material))
            meshNameMaterial.append(str(dataMesh.material.baseMtl))
            flex = dataMesh.material.Layers[0]
            if len(dataMesh.material.Layers) > 0 :
                for i in range(len(dataMesh.material.Layers)):
                    if not dataMesh.material.Layers[i] == None:
                        meshNameMaterial.append(str(dataMesh.material.Layers[i]))
                        
        else:
            meshNameMaterial.append(str(dataMesh.material))
                        
        listSelection.append(meshNameMaterial)
    return listSelection
    
def getSettingsBitmap(texMap):
    fileName = texMap.filename
    texPath = fileName.replace("\\" , "/")
    bitmapSettings = []
    bitmapSettings.append(texMap.coords.U_Tiling)
    bitmapSettings.append(texMap.coords.V_Tiling)
    bitmapSettings.append(texMap.coords.mapChannel)
    bitmapSettings.append(texMap.coords.W_angle)
    bitmap = {'texPath':str(texPath),'bitmapSettings': bitmapSettings}
    return bitmap
    
def getSettingsCoronaBitmap(texMap):
    fileName = texMap.filename
    texPath = fileName.replace("\\" , "/")
    bitmapSettings = []
    bitmapSettings.append(texMap.tilingU)
    bitmapSettings.append(texMap.tilingV)
    bitmapSettings.append(texMap.uvwChannel)
    bitmapSettings.append(texMap.wAngle)
    bitmap = {'texPath':str(texPath),'bitmapSettings': bitmapSettings}
    return bitmap

def fillJson(object, numMaterials):
    shaderA = []
    numLayers = []
    
    ############ Check if it is not a multimaterial ############
    
    if not len(numMaterials) > 1:
        dataMeshName = str(object.name)
        
        ############ Check if it is a Corona Layered Material ############
        
        if str(rt.classOf(object.material)) == 'CoronaLayeredMtl' :
            
            ############ Get settings of Corona Layered Material's children ############
            
            attributes = getSettingsCoronaMtl(object.material.baseMtl,dataMeshName,0)
            if attributes:
                if not attributes in shaderA:
                    shaderA.append(attributes)
            for i in range(len(object.material.Layers)):
                if not object.material.Layers[i] == None :
                    attributes = getSettingsCoronaMtl(object.material.Layers[i],dataMeshName,0)
                    if attributes:
                        if not attributes in shaderA:
                            shaderA.append(attributes)
                            
            ############ Get settings of Corona Layered Material ############
                            
            attributes = getSettingsCoronaLayeredMtl(object.material,dataMeshName,0)
            if attributes:
                if not attributes in shaderA:
                    shaderA.append(attributes)
                            
        else:
            
            ############ Get settings of Corona Material ############
            
            attributes = getSettingsCoronaMtl(object.material,dataMeshName,0)
            if attributes:
                if not attributes in shaderA:
                    shaderA.append(attributes)
                    
        
        
    ####################### IF MULTI MATERIAL #####################
    else:
        for i in range(len(numMaterials)):
            dataMeshName = str(object.name)
            if str(rt.classOf(object.material.materialList[i])) == 'CoronaLayeredMtl' :
                
                ############ Get settings of Corona Layered Material's children ############
                
                attributes = getSettingsCoronaMtl(object.material.materialList[i].baseMtl,dataMeshName,i)
                if attributes:
                    if not attributes in shaderA:
                        shaderA.append(attributes)
                for j in range(len(object.material.materialList[i].Layers)):
                    if not object.material.materialList[i].Layers[j] == None :
                        attributes = getSettingsCoronaMtl(object.material.materialList[i].Layers[j],dataMeshName,i)
                        if attributes:
                            if not attributes in shaderA:
                                shaderA.append(attributes)
                                
                ############ Get settings of Corona Layered Material ############
                                
                attributes = getSettingsCoronaLayeredMtl(object.material.materialList[i],dataMeshName,i)
                if attributes:
                    if not attributes in shaderA:
                        shaderA.append(attributes)
                                
            else :
                
                ############ Get settings of Corona Material ############
                
                attributes = getSettingsCoronaMtl(object.material.materialList[i],dataMeshName,i)
                if attributes:
                    if not attributes in shaderA:
                        shaderA.append(attributes)
            
    
    return shaderA

def getSettingsCoronaMtl(CrnMtl,meshName,ID):
    dataMaterialName = str(CrnMtl)
    materialProperties = rt.getPropNames(CrnMtl)
    attributes = {'object_name' : meshName, 'disp_name' : [], 'name': dataMaterialName, 'data': [], 'normal_type': [], 'opacity':[], 'shadingGroup': ID}
    pairs = clarisse_corona_pairs.get('CoronaMtl')
    for i in materialProperties:
        value = rt.getProperty(CrnMtl, i)
        attrA = []
        if str(rt.classOf(value)) == 'Color' :
            attrA.append(value.r/255)
            attrA.append(value.g/255)
            attrA.append(value.b/255)
        if str(rt.classOf(value)) == 'Double' :
            if str(i) == 'reflectGlossiness' or str(i) == 'refractGlossiness':
                attrA = 1 - value
            else :
                attrA = value
        if str(rt.classOf(value)) == 'UndefinedClass' :
            attrA = None
        if str(rt.classOf(value)) == 'CoronaFrontBack' :
            textureProperties = rt.getPropNames(value)
            attrA = {'front':'','back':''}
            for t in textureProperties:
                texValues = rt.getProperty(value,t)
                if str(t) == 'frontTexmap' :
                    if str(rt.classOf(texValues)) == 'CoronaBitmap':
                        texPath = getSettingsCoronaBitmap(texValues)
                        attrA.update({'front':texPath})
                        
                    else:
                        texPath = getSettingsBitmap(texValues)
                        attrA.update({'front':texPath})
                if str(t) == 'backTexmap' :
                    if str(rt.classOf(texValues)) == 'CoronaBitmap':
                        texPath = getSettingsCoronaBitmap(texValues)
                        attrA.update({'back':texPath})
                    else:
                        texPath = getSettingsBitmap(texValues)
                        attrA.update({'back':texPath})
            
                            
                
        if str(rt.classOf(value)) == 'Bitmaptexture' :
            texPath = getSettingsBitmap(value)
            attrA = texPath
        if str(rt.classOf(value)) == 'CoronaBitmap' :
            texPath = getSettingsCoronaBitmap(value)
            attrA = texPath
            
        ############ Check if bump is a normal input ############
        if str(i) == 'texmapBump' :
            if str(rt.classOf(value)) == 'CoronaNormal' :
                textureProperties = rt.getPropNames(value)
                for k in textureProperties :
                    valueSubTex = rt.getProperty(value, k)
                    if str(k) == 'normalMap':
                        if str(rt.classOf(valueSubTex)) == 'CoronaBitmap':
                            texPath = getSettingsCoronaBitmap(valueSubTex)
                            attrA = texPath
                            attributes['normal_type'].append('TextureNormalMap')
                        else:
                            texPath = getSettingsBitmap(valueSubTex)
                            attrA = texPath
                            attributes['normal_type'].append('TextureNormalMap')
            if str(rt.classOf(value)) == 'Bitmaptexture':
                texPath = getSettingsBitmap(value)
                attrA = texPath
                attributes['normal_type'].append('TextureBumpMap')
            if str(rt.classOf(value)) == 'CoronaBitmap' :
                texPath = getSettingsCoronaBitmap(value)
                attrA = texPath
                attributes['normal_type'].append('TextureBumpMap')
                
        if str(i) == 'texmapDisplace':
            if str(rt.classOf(value)) == 'Bitmaptexture' :
                texPath = getSettingsBitmap(value)
                attributes['disp_name'].append(texPath)
            if str(rt.classOf(value)) == 'CoronaBitmap' :
                texPath = getSettingsCoronaBitmap(value)
                attributes['disp_name'].append(texPath)
                
        if str(i) == 'texmapOpacity':
            if str(rt.classOf(value)) == 'Bitmaptexture' :
                texPath = getSettingsBitmap(value)
                attributes['opacity'].append(texPath)
            if str(rt.classOf(value)) == 'CoronaBitmap' :
                texPath = getSettingsCoronaBitmap(value)
                attributes['opacity'].append(texPath)
        
        if pairs:
            for clar_id, corona_id in pairs.iteritems():
                if str(i) == corona_id:
                    attr = {clar_id: attrA}
                    attributes['data'].append(attr)
                    
    return attributes

def getSettingsCoronaLayeredMtl(CrnLydMtl,meshName,ID):
    dataMaterialName = str(CrnLydMtl)
    attributes = {'object_name' : meshName, 'disp_name' : [], 'name': dataMaterialName, 'data': [], 'normal_type': [], 'shadingGroup': ID}
    pairs = clarisse_corona_pairs.get('CoronaLayeredMtl')
    for i in range(len(CrnLydMtl.Layers)):
        if not CrnLydMtl.Layers[i] == None :
            attr = {'base': CrnLydMtl.baseMtl.name}
            if not attr in attributes['data']:
                attributes['data'].append(attr)
            for clar_id, corona_id in pairs.iteritems():
                if 'Layers['+str(i)+']' == corona_id:
                    attr = {clar_id: CrnLydMtl.Layers[i].name}
                    attributes['data'].append(attr)
                if 'amounts['+str(i)+']' == corona_id:
                    attr = {clar_id: CrnLydMtl.amounts[i]}
                    attributes['data'].append(attr)
                if 'mixmaps['+str(i)+']' == corona_id:
                    if not CrnLydMtl.mixmaps[i] == None:
                        if str(rt.classOf(CrnLydMtl.mixmaps[i])) == 'Bitmaptexture' :
                            fileName = CrnLydMtl.mixmaps[i].filename
                            texPath = fileName.replace("\\" , "/")
                            bitmapSettings = []
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].coords.U_Tiling)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].coords.V_Tiling)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].coords.mapChannel)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].coords.W_angle)
                            bitmap = {'texPath':str(texPath),'bitmapSettings': bitmapSettings}
                        if str(rt.classOf(CrnLydMtl.mixmaps[i])) == 'CoronaBitmap' :
                            fileName = CrnLydMtl.mixmaps[i].filename
                            texPath = fileName.replace("\\" , "/")
                            bitmapSettings = []
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].tilingU)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].tilingV)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].uvwChannel)
                            bitmapSettings.append(CrnLydMtl.mixmaps[i].wAngle)
                            bitmap = {'texPath':str(texPath),'bitmapSettings': bitmapSettings}
                        attr = {clar_id: bitmap}
                        attributes['data'].append(attr)
                    else:
                        attr = {clar_id: None}
                        attributes['data'].append(attr)
    return attributes

coronaToClarisse = MyWidget()
coronaToClarisse.show()

