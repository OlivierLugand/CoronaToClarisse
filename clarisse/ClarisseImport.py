import ix

import os
import json
import ntpath
import re

### A big thank you to Yanik and Anabil from the Isotropix forum for their help and support ###



class EventRewire(ix.api.EventObject):

    def path_refresh(self, sender, evtid):
        directory = ix.api.GuiWidget.open_folder(ix.application, '',
                                                 'Surface directory')  # Summon the window to choose files
        if directory:
            if os.path.isdir(str(directory)):
                path_txt.set_text(str(directory))
            else:
                ix.log_warning("Invalid directory: %s" % str(directory))

    def cancel(self, sender, evtid):
        sender.get_window().hide()

    def run(self, sender, evtid):

        ix.begin_command_batch("Import Asset")
        directory_txt = path_txt.get_text()

        ############ Get list of files to import ############

        filesCount = []
        for file in os.listdir(directory_txt):
            if file.endswith(".json"):
                filesCount.append(file)

        ############ Create Geo and materials context ############

        current_context = ix.get_current_context()
        asset_context = ix.cmds.CreateContext("Geo", current_context)
        material_asset_context = ix.cmds.CreateContext("Materials", current_context)
        allObjects = []
        all_materials = []


        for file in range(len(filesCount)):

            ############ Read json file ############

            file_txt = directory_txt + filesCount[file]

            with open(file_txt, 'r') as fp:
                dataA = json.load(fp)


            objectA = dataA[0]['object_name']



            ############################## Import Geometry ####################################

            geoFileName = ntpath.basename(file_txt)
            sep = '.'
            geoFileName = geoFileName.split(sep, 1)[0] + '.abc'
            pathGeoFile = directory_txt + geoFileName
            geo = None

            # Check if the geo is alembic
            if os.path.isfile(pathGeoFile):
                geo = ix.cmds.CreateObject(re.sub('[^a-zA-Z0-9]+', '_', str(objectA)), "GeometryBundleAlembic", "Global", asset_context)
                ix.cmds.RemoveValue([geo.get_full_name()+".filename"], [2, 1, 0])
                ix.cmds.AddValues([geo.get_full_name()+".filename"], [pathGeoFile])
                ix.cmds.CenterObjectsPivots([geo.get_full_name()], True)
                ix.cmds.SetValues([geo.get_full_name()+".translate[0]"], ["0.0"])
                ix.cmds.SetValues([geo.get_full_name()+".translate[1]"], ["0.0"])
                ix.cmds.SetValues([geo.get_full_name()+".translate[2]"], ["0.0"])
                ix.application.check_for_events()

            assignedShadingGroups = []

            for shadingGroups in dataA:
                assignedShadingGroups.append(shadingGroups['shadingGroup'])

            assignedShadingGroups = list(dict.fromkeys(assignedShadingGroups))

            for shader in dataA:
                if shader:
                    shader_name = shader['name']
                    sep = ':'
                    restShaderName = re.sub('[^a-zA-Z0-9]+', '_', str(shader_name).split(sep, 1)[0])
                    materialType = str(shader_name).split(sep, 1)[1]


                    if not str(restShaderName) in all_materials:

                        #storing all shaders in one list
                        all_materials.append(str(restShaderName))

                        if materialType == 'CoronaMtl' :
                            disp_texture = shader['disp_name']
                            opacity_texture = shader['opacity']
                            mat_context = ix.cmds.CreateContext(restShaderName, material_asset_context)
                        else:
                            mat_context = ix.cmds.CreateContext(restShaderName, material_asset_context)
                        tex_context = ix.cmds.CreateContext("textures", mat_context )
                        shading_groups = shader['shadingGroup']


                        if disp_texture:

                            slot = shader.get('disp_name')[0]

                            # create a displacement node
                            disp_node = ix.cmds.CreateObject(str(ntpath.basename(restShaderName)) + "_disp",
                                                                "Displacement", "Global",
                                                                tex_context)

                            # get texture's settings
                            textureNodeDisp = settingsStreamedMapFile(slot, tex_context, '')


                            # connect texture to displacement node
                            ix.cmds.SetTexture([disp_node.get_full_name() + ".front_value"],
                                               textureNodeDisp.get_full_name())


                        if opacity_texture:
                            #ix.application.check_for_events()
                            slot = shader.get('opacity')[0]

                            # get texture's settings
                            textureNodeOpacity = settingsStreamedMapFile(slot, tex_context, '')


                        if objectA:
                            object_name = shader.get('object_name')

                    else:
                        mat_context = material_asset_context.get_context(restShaderName)
                        shading_groups = shader['shadingGroup']



                    ################################ Create Layered Physical Material ####################################
                    if materialType == 'CoronaLayeredMtl':
                        if shader_name:
                            if mat_context.get_object(restShaderName + '_mat') :
                                layered_mat = mat_context.get_object(restShaderName + '_mat')


                            else:
                                layered_mat = ix.cmds.CreateObject(restShaderName + '_mat', "MaterialPhysicalLayered", "Global",
                                                                mat_context)

                            ############ Shader assignment ############
                            if geo :

                                geoModule = geo.get_module()

                                if geoModule.get_shading_group_count() < 2:
                                    ix.cmds.SetValues([geo.get_full_name()+".materials[0]"], [layered_mat.get_full_name()])


                                ############ Get correct index ############

                                else:
                                    dictID = {}
                                    shadingGroupID = []
                                    for i in range(geoModule.get_shading_group_count()):
                                        material = geoModule.get_material(i)
                                        sep = '>'
                                        tmp = str(geoModule.get_shading_group(i)).split(sep, 1)[1]
                                        shadingGroupID.append(int(tmp))
                                        dictID[i]=int(tmp)
                                    shadingGroupID.sort()

                                    length = shadingGroupID[-1] + 1

                                    for i in range(shading_groups,length,len(assignedShadingGroups)):
                                        for index, numIndex in dictID.items():

                                            if i == int(numIndex):

                                                ix.cmds.SetValues([geo.get_full_name()+".materials["+str(index)+"]"], [layered_mat.get_full_name()])

                        #setting layered attrs
                        if layered_mat:
                            attributes_data = shader.get('data')

                            if attributes_data:
                                for i in attributes_data:
                                    if i:

                                        if isinstance(i, dict):
                                            for clar_id, val in i.iteritems():
                                                if val !=None:

                                                    if isinstance(val, basestring):
                                                        # Remove special characters
                                                        subMat = re.sub('[^a-zA-Z0-9]+', '_', str(val))


                                                        # Set the attribute
                                                        ix.cmds.SetValues([layered_mat.get_full_name() + "." + str(clar_id)],
                                                                          [str(material_asset_context)+'/'+subMat+'/'+subMat+'_mat'])

                                                    elif isinstance(val, dict):


                                                        # Check if the texture is a file
                                                        if val.keys()[0] == 'texPath':

                                                            slot = i.get(str(clar_id))

                                                            # get texture's settings
                                                            textureNode = settingsStreamedMapFile(slot, tex_context, clar_id)
                                                            sep = 'tx_'
                                                            restClarId = str(clar_id).split(sep, 1)[1]
                                                            ix.cmds.SetTexture([layered_mat.get_full_name() + "." + str(restClarId)],
                                                                               textureNode.get_full_name())

                                                    else:
                                                        # Set the attribute
                                                        ix.cmds.SetValues([layered_mat.get_full_name() + "." + str(clar_id)],
                                                                          [str(val)])


                    ################################## Create Physical Material #######################################
                    if materialType == 'CoronaMtl' :
                        if shader_name:
                            if mat_context.get_object(restShaderName + '_mat') :
                                standard_mat = mat_context.get_object(restShaderName + '_mat')


                            else:
                                standard_mat = ix.cmds.CreateObject(restShaderName + '_mat', "MaterialPhysicalStandard", "Global",
                                                                mat_context)


                            if opacity_texture:
                                ix.cmds.SetValues([standard_mat.get_full_name() + ".sidedness"], ["1"])

                            ############ Shader assignment ############

                            if geo :


                                geoModule = geo.get_module()

                                if geoModule.get_shading_group_count() < 2:
                                    ix.cmds.SetValues([geo.get_full_name()+".materials[0]"], [standard_mat.get_full_name()])

                                    if opacity_texture:
                                        ix.cmds.SetValues([geo.get_full_name()+".clip_maps[0]"], [textureNodeOpacity.get_full_name()])
                                    if disp_texture:
                                        ix.cmds.SetValues([geo.get_full_name()+".displacements[0]"], [disp_node.get_full_name()])

                                else:
                                    ############ Get correct index if multiple shading groups ############
                                    dictID = {}
                                    shadingGroupID = []
                                    for i in range(geoModule.get_shading_group_count()):
                                        material = geoModule.get_material(i)
                                        sep = '>'
                                        tmp = str(geoModule.get_shading_group(i)).split(sep, 1)[1]
                                        shadingGroupID.append(int(tmp))
                                        dictID[i]=int(tmp)
                                    shadingGroupID.sort()


                                    length = shadingGroupID[-1] + 1



                                    for i in range(shading_groups,length,len(assignedShadingGroups)):

                                        for index, numIndex in dictID.items():

                                            if i == int(numIndex):
                                                ix.cmds.SetValues([geo.get_full_name()+".materials["+str(index)+"]"], [standard_mat.get_full_name()])

                                                if opacity_texture:
                                                    ix.cmds.SetValues([geo.get_full_name()+".clip_maps["+str(index)+"]"], [textureNodeOpacity.get_full_name()])
                                                if disp_texture:
                                                    ix.cmds.SetValues([geo.get_full_name()+".displacements["+str(index)+"]"], [disp_node.get_full_name()])








                        #setting different attrs
                        if standard_mat:
                            attributes_data = shader.get('data')

                            if attributes_data:
                                for i in attributes_data:
                                    if i:

                                        if isinstance(i, dict):
                                            for clar_id, val in i.iteritems():
                                                if val !=None:

                                                    # Everything that is a list considered as color values
                                                    if isinstance(val, list) and len(val) == 3:
                                                        ix.cmds.SetValues([standard_mat.get_full_name() + "." + str(clar_id)],
                                                                          [str(val[0]), str(val[1]), str(val[2])])

                                                    elif isinstance(val, dict):

                                                        # Check if the texture is a file
                                                        if val.keys()[0] == 'texPath':

                                                            slot = i.get(str(clar_id))

                                                            # get texture's settings
                                                            textureNode = settingsStreamedMapFile(slot, tex_context, clar_id)


                                                            # for bump mapping
                                                            if clar_id == 'normal_input':
                                                                bumpType = shader.get('normal_type')[0]
                                                                bump_node = ix.cmds.CreateObject(str(ntpath.basename(textureNode.get_name())) + "_bumpNode",
                                                                                                str(bumpType), "Global",
                                                                                                tex_context)
                                                                if bumpType == 'TextureBumpMap':
                                                                    ix.cmds.SetValues([bump_node.get_full_name() + ".input"],
                                                                                   ["0.01"])

                                                                ix.cmds.SetTexture([bump_node.get_full_name() + ".input"],
                                                                                   textureNode.get_full_name())

                                                                ix.cmds.SetTexture([standard_mat.get_full_name() + "." + str(clar_id)],
                                                                                   bump_node.get_full_name())



                                                            else:
                                                            #everything that's not a bump map
                                                                sep = 'tx_'
                                                                restClarId = str(clar_id).split(sep, 1)[1]
                                                                ix.cmds.SetTexture([standard_mat.get_full_name() + "." + str(restClarId)],
                                                                                   textureNode.get_full_name())

                                                        # Check if the texture is a sideswitch
                                                        if val.keys()[0] == 'front':

                                                            sideSwitchNode = ix.cmds.CreateObject("sideSwitch_" + str(clar_id),
                                                                                                "TextureSideSwitch", "Global", tex_context)

                                                            slot = val.get('front')

                                                            # get front texture's settings
                                                            textureNode = settingsStreamedMapFile(slot, tex_context, clar_id)

                                                            ix.cmds.SetTexture([sideSwitchNode.get_full_name() + ".front_color"],
                                                                                   textureNode.get_full_name())


                                                            slot = val.get('back')

                                                            # get back texture's settings
                                                            textureNode = settingsStreamedMapFile(slot, tex_context, clar_id)

                                                            ix.cmds.SetTexture([sideSwitchNode.get_full_name() + ".back_color"],
                                                                                   textureNode.get_full_name())

                                                            # for bump mapping
                                                            if clar_id == 'normal_input':
                                                                bumpType = shader.get('normal_type')[0]
                                                                bump_node = ix.cmds.CreateObject(str(ntpath.basename(textureNode.get_name())) + "_bumpNode",
                                                                                                str(bumpType), "Global",
                                                                                                tex_context)

                                                                ix.cmds.SetTexture([bump_node.get_full_name() + ".input"],
                                                                                   sideSwitchNode.get_full_name())

                                                                ix.cmds.SetTexture([standard_mat.get_full_name() + "." + str(clar_id)],
                                                                                   bump_node.get_full_name())



                                                            else:
                                                            #everything that's not a bump map
                                                                sep = 'tx_'
                                                                restClarId = str(clar_id).split(sep, 1)[1]
                                                                ix.cmds.SetTexture([standard_mat.get_full_name() + "." + str(restClarId)],
                                                                                   sideSwitchNode.get_full_name())


                                                    else:
                                                        # Set the attribute
                                                        if val != []:
                                                            ix.cmds.SetValues([standard_mat.get_full_name() + "." + str(clar_id)],
                                                                          [str(val)])






            ix.end_command_batch()


def settingsStreamedMapFile(texture, tex_context, clarID):


    tex = texture.values()[0]
    texU_scale = texture.values()[1][0]
    texV_scale = texture.values()[1][1]
    texUV_slot = texture.values()[1][2]
    texW_rotate = texture.values()[1][3]

    # create texture
    textureNode = ix.cmds.CreateObject(str(ntpath.basename(tex)) + "_tx",
                                                        "TextureStreamedMapFile", "Global",
                                                        tex_context)

    # setting texture values

    ix.cmds.SetValues([textureNode.get_full_name() + ".filename[0]"], [str(tex)])
    ix.cmds.SetValues([textureNode.get_full_name() + ".color_space_auto_detect"], ["0"])
    if clarID == 'tx_diffuse_front_color':
        ix.cmds.SetValues([textureNode.get_full_name() + ".file_color_space"], ["Utility|Utility - sRGB - Texture"])
    else:
        ix.cmds.SetValues([textureNode.get_full_name() + ".use_raw_data"], ["1"])
    ix.cmds.SetValues([textureNode.get_full_name() + ".uv_scale[0]"], [str(texU_scale)])
    ix.cmds.SetValues([textureNode.get_full_name() + ".uv_scale[1]"], [str(texV_scale)])
    ix.cmds.SetValues([textureNode.get_full_name() + ".uv_rotate[2]"], [str(texW_rotate)])
    if str(texUV_slot) != '1':
        ix.cmds.SetValues([textureNode.get_full_name() + ".projection"], ["7"])
        ix.cmds.SetValues([textureNode.get_full_name() + ".uv_property[0]"], ["Max Map Channel "+str(texUV_slot)])
    else:
        ix.cmds.SetValues([textureNode.get_full_name() + ".projection"], ["7"])
        ix.cmds.SetValues([textureNode.get_full_name() + ".uv_property[0]"], ["uv"])

    return textureNode




# Window creation
clarisse_win = ix.application.get_event_window()
window = ix.api.GuiWindow(clarisse_win, 900, 450, 400, 150)  # Parent, X position, Y position, Width, Height
window.set_title('Corona importer')  # Window name

# Main widget creation
panel = ix.api.GuiPanel(window, 0, 0, window.get_width(), window.get_height())
panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP,
                      ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)

# Form generation
separator_label1 = ix.api.GuiLabel(panel, 10, 10, 380, 22, " ASSET DIRECTORY: ")
separator_label1.set_text_color(ix.api.GMathVec3uc(128, 128, 128))
path_button = ix.api.GuiPushButton(panel, 320, 40, 60, 22, "Browse")
path_txt = ix.api.GuiLineEdit(panel, 10, 40, 300, 22)



close_button = ix.api.GuiPushButton(panel, 10, 100, 100, 22, "Close")
run_button = ix.api.GuiPushButton(panel, 130, 100, 250, 22, "Import")


# Connect to function
event_rewire = EventRewire()  # init the class

event_rewire.connect(path_button, 'EVT_ID_PUSH_BUTTON_CLICK',
                     event_rewire.path_refresh)
event_rewire.connect(close_button, 'EVT_ID_PUSH_BUTTON_CLICK',
                     event_rewire.cancel)
event_rewire.connect(run_button, 'EVT_ID_PUSH_BUTTON_CLICK',
                     event_rewire.run)

# Send all info to clarisse to generate window
window.show()
while window.is_shown():    ix.application.check_for_events()
window.destroy()

def get_ix(ix_local):
    """Simple function to check if ix is imported or not."""
    try:
        ix
    except NameError:
        return ix_local
    else:
        return ix


