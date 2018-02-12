import bpy
import random

class QuickToolsPanel(bpy.types.Panel):
    """Panel for creating and setting up things quick"""
    bl_label = "Jenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        self.layout.operator("lowpolybrick.brickmaker")
        self.layout.operator("particle.setup")
        self.layout.operator("camera.setup")


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