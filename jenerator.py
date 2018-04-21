import bpy
import random
ob = bpy.context.active_object

class QuickToolsPanel(bpy.types.Panel):
    """Panel for creating and setting up things quick"""
    bl_label = "Jenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        self.layout.operator("lowpolybrick.brickmaker")
        self.layout.operator("particle.setup")
        self.layout.operator("camera.setup")
        self.layout.operator("shader.setup")


#Creates a low-poly brick. Pretty self-explanitory
class OBJECT_OT_LowPolyBrick(bpy.types.Operator):
    bl_idname = "lowpolybrick.brickmaker"
    bl_label = "Low Poly Brick"
    bl_description = "Makes a low poly brick"
    
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        bpy.ops.object.modifier_add(type='BEVEL')

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.quads_convert_to_tris()
        randomScale = random.uniform(1,3)
        bpy.ops.transform.resize(value=(randomScale, 2.2, 2.2), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.object.editmode_toggle()
        
        #Sets up new texture for displacement if there wasn't one already
        if bpy.data.textures.get("lowpoly") is None:
            bpy.data.textures.new("lowpoly", 'CLOUDS')

        bpy.ops.object.modifier_add(type='DISPLACE')
        bpy.context.object.modifiers["Displace"].strength = random.uniform(-2,2)
        bpy.context.object.modifiers["Displace"].texture = bpy.data.textures["lowpoly"]
        displaceSeed = random.randrange(1,5)
        if displaceSeed == 1:
            bpy.context.object.modifiers["Displace"].direction = 'NORMAL'
        elif displaceSeed == 2:
            bpy.context.object.modifiers["Displace"].direction = 'RGB_TO_XYZ'
        elif displaceSeed == 3:
            bpy.context.object.modifiers["Displace"].direction = 'Y'
        elif displaceSeed == 4:
            bpy.context.object.modifiers["Displace"].direction = 'X'
        elif displaceSeed == 5:
            bpy.context.object.modifiers["Displace"].direction = 'Z'


        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        x = random.randrange(1,2)
        if x == 1:
            bpy.context.object.modifiers["Decimate"].angle_limit = 0.139626
        elif x == 2:
            bpy.context.object.modifiers["Decimate"].angle_limit = 0.0872661


        bpy.ops.object.modifier_add(type='SUBSURF')


        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bevel")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Displace")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

        return {'FINISHED'}

#Sets up a particle system that makes setting up grass and trees easier
class OBJECT_OT_ParticleSetup(bpy.types.Operator):
    bl_idname = "particle.setup"
    bl_label = "Particle Setup"
    bl_description = "Applies favorite particle settings to current object's first particle slot"
    
    def execute(self, context):
        if bpy.data.particles.get("plant") is None:
            bpy.data.particles.new("plant")
            bpy.data.particles["plant"].type = 'HAIR'
            bpy.data.particles["plant"].use_advanced_hair = True
            bpy.data.particles["plant"].use_rotations = True
            bpy.data.particles["plant"].phase_factor = 1
            bpy.data.particles["plant"].phase_factor_random = 1
            bpy.data.particles["plant"].rotation_mode = 'NOR_TAN'
            bpy.data.particles["plant"].render_type = 'PATH'
            bpy.data.particles["plant"].use_rotation_dupli = True
            bpy.data.particles["plant"].particle_size = 0.1
        obj = bpy.context.active_object
        
        if len(obj.particle_systems) == 0:
            obj.modifiers.new("plants", type='PARTICLE_SYSTEM')
            plants = obj.particle_systems[0]
        else:
            plants = obj.particle_systems[0]
            
        #https://blender.stackexchange.com/questions/21421/what-is-the-correct-context-for-applying-a-new-particle-setting-or-override-it
        par_set = bpy.data.particles["plant"] #get particle setting you want to assign
        plants.settings=par_set

        return {'FINISHED'}
    
#Creates toon shaders in Cycles and Eevee   
class OBJECT_OT_ShaderSetup(bpy.types.Operator):
    bl_idname = "shader.setup"
    bl_label = "Setup Shaders"
    bl_description = "Adds toon shaders"
    
    def execute(self, context):
        #Sets up new material if there wasn't one already, from https://blender.stackexchange.com/questions/23433/how-to-assign-a-new-material-to-an-object-in-the-scene-from-python
        tShader = bpy.data.materials.get("Toon Shader")
        if tShader is None:
            tShader = bpy.data.materials.new(name="Toon Shader")
        if ob.data.materials:
            ob.data.materials[0] = tShader
        else:
            ob.data.materials.append(tShader)
        
        # Enable 'Use nodes':
        # From https://blender.stackexchange.com/questions/5668/add-nodes-to-material-with-python
        tShader.use_nodes = True
        nodes = tShader.node_tree.nodes
        
        # Remove default
        tShader.node_tree.nodes.remove(tShader.node_tree.nodes.get('Diffuse BSDF'))
        material_output = tShader.node_tree.nodes.get('Material Output')
        material_output.location = (500,340)
        
        # Add New nodes
        mixA = tShader.node_tree.nodes.new('ShaderNodeMixShader')
        mixA.location = (260,340)
        
        emission = tShader.node_tree.nodes.new('ShaderNodeEmission')
        emission.inputs['Strength'].default_value = 1.0
        emission.location = (105,340)
        
        diffuse = tShader.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        diffuse.location = (105,225)
        
        lRay = tShader.node_tree.nodes.new('ShaderNodeLightPath')
        lRay.location = (105,650)
        
        ramp = tShader.node_tree.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'CONSTANT'
        ramp.color_ramp.elements[1].position = 0.01
        ramp.location = (-150,340)
        
        normal = tShader.node_tree.nodes.new('ShaderNodeNormal')
        normal.location = (-305,340)
        
        mapping = tShader.node_tree.nodes.new('ShaderNodeMapping')
        mapping.rotation[0] = -0.785398
        mapping.rotation[1] = -0.785398
        mapping.location = (-650,340)
        
        geo = tShader.node_tree.nodes.new('ShaderNodeNewGeometry')
        geo.location = (-830,340)

        # link Nodes
        tShader.node_tree.links.new(material_output.inputs[0], mixA.outputs[0])
        tShader.node_tree.links.new(mixA.inputs[2], emission.outputs[0])
        tShader.node_tree.links.new(mixA.inputs[1], diffuse.outputs[0])
        tShader.node_tree.links.new(mixA.inputs[0], lRay.outputs[0])
        tShader.node_tree.links.new(emission.inputs[0], ramp.outputs[0])
        tShader.node_tree.links.new(diffuse.inputs[0], ramp.outputs[0])
        tShader.node_tree.links.new(ramp.inputs[0], normal.outputs[1])
        tShader.node_tree.links.new(normal.inputs[0], mapping.outputs[0])
        tShader.node_tree.links.new(mapping.inputs[0], geo.outputs[1])
        return {'FINISHED'}
    
    
#Creates a camera that rotates around the center to show off modeling projects    
class OBJECT_OT_TurnaboutCamera(bpy.types.Operator):
    bl_idname = "camera.setup"
    bl_label = "Turnabout Camera"
    bl_description = "Adds turnabout camera and empty control"
    
    def execute(self, context):
        bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=(0, 0, 0), rotation=(1.5708, -0, -0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        
        objects = bpy.data.objects
        a = objects['Empty']
        b = objects['Camera']
        a.parent = b
        bpy.ops.transform.translate(value=(0, -30, 10), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        bpy.context.scene.frame_current = 0
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')
        bpy.context.scene.frame_current = 240
        bpy.ops.transform.translate(value=(0, 360, 0), constraint_axis=(False, True, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        #bpy.ops.graph.interpolation_type(type='LINEAR')
        bpy.ops.anim.keyframe_insert_menu(type='Rotation')

        bpy.context.scene.frame_current = 0

        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)  
def unregister():
    bpy.utils.unregister_module(__name__)  

if __name__ == "__main__":
    register()