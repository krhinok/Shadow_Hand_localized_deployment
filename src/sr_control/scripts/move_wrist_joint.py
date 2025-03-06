import rospy
from std_msgs.msg import Float64

def set_joint_positions(joint_positions):
    """
    发布多个关节的目标位置到 Gazebo 控制器。
    :param joint_positions: 字典，键为关节名称，值为目标角度（弧度）
    """
    publishers = {}
    for joint_name in joint_positions.keys():
        topic_name = f'/{joint_name}/command'
        publishers[joint_name] = rospy.Publisher(topic_name, Float64, queue_size=10)
    
    rospy.sleep(1)  # 等待 ROS 话题连接
    
    for joint_name, position in joint_positions.items():
        rospy.loginfo(f"Setting {joint_name} to {position} radians")
        publishers[joint_name].publish(Float64(position))
    
if __name__ == "__main__":
    rospy.init_node('joint_position_controller')
    
    # 定义需要控制的关节及其目标角度（单位：弧度）
    joint_targets = {
        'sh_rh_thj1_position_controller': 0.6,
        'sh_rh_thj2_position_controller': 0.0,
        'sh_rh_thj3_position_controller': 0.8,
        'sh_rh_lfj0_position_controller': 0.5,
        'sh_rh_ffj3_position_controller': 0.5,
        'sh_rh_lfj4_position_controller': 0.2,
        'sh_rh_ffj4_position_controller': 0.2
    }
    
    set_joint_positions(joint_targets)
    
    rospy.spin()

