# Steps to Successfully Run Shadow Hand Gazebo Simulation and Control Joint Angles on Your Computer  

## 1. Create a Workspace  

## 2. Download Required Resources [https://github.com/shadow-robot](https://github.com/shadow-robot)  
Download the following repositories into the `src` directory of your workspace (pay attention to the version):  
- **sr_description** ([https://github.com/shadow-robot/sr_common](https://github.com/shadow-robot/sr_common))  
- **sr_robot_msgs** ([https://github.com/shadow-robot/sr_common](https://github.com/shadow-robot/sr_common))  
- **sr_core** ([https://github.com/shadow-robot/sr_core](https://github.com/shadow-robot/sr_core))  
- **common_resources** ([https://github.com/shadow-robot/common_resources](https://github.com/shadow-robot/common_resources))  
- **ros_ethercat** ([https://github.com/shadow-robot/ros_ethercat](https://github.com/shadow-robot/ros_ethercat))  

## 3. Download the Configuration File  
Create a `config` folder inside `sr_description`, and download the `rh_controller_gazebo.yaml` file  (sr_description/hand/config/rh_controller_gazebo.yaml).  

## 4. URDF and Launch Files  
To simplify the setup, my `sr_description` package only contains the following folders:  
- `config`  
- `launch`  
- `meshes`  
- `urdf`  
- Along with the necessary `CMakeLists.txt` and `package.xml` files.  

The `meshes` folder is directly taken from the original `sr_description` package.  
The `urdf` folder contains the `sr_hand.urdf` file, which is generated from `sr_description/robots/sr_hand.urdf.xacro` . using:  
```bash
rosrun xacro xacro your_file.xacro > your_file.urdf
```

urdf has to be modified (see uploaded file). 


The `launch` folder contains `spawn_sr_hand.launch` (see uploaded file).  

## 5. Joint Angle Control  
Create a package named `sr_control` in the workspace (see uploaded file).  

## 6. Run the Simulation  
In the workspace directory, start the Gazebo simulation:  
```bash
roslaunch sr_description spawn_sr_hand.launch
```  
Run the control node:  
```bash
rosrun sr_control move_wrist_joint.py
```  

## Notes  
The steps in this document may yield different results in different environments and may not be entirely accurate.
