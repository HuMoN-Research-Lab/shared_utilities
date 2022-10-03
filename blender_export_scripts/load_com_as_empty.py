import bpy

path_to_com_xyz_npy = r"D:\Dropbox\FreeMoCapProject\FreeMocap_Data\sesh_2022-09-19_16_16_50_in_class_jsm\DataArrays\totalBodyCOM_frame_XYZ.npy"

com_xyz = np.load(path_to_com_xyz_npy)

com_xyz = com_xyz*0.001

bpy.ops.object.empty_add(type='SPHERE')
this_empty = bpy.context.active_object
this_empty.name = 'neck_center'
this_empty.scale = [.2, .2, .2]

for frame_num in range(com_xyz.shape[0]):
    this_empty.location = [com_xyz[frame_num,0],
                        com_xyz[frame_num,1],
                        com_xyz[frame_num,2]]
    this_empty.keyframe_insert(data_path='location',frame=frame_num)
