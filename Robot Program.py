# This macro shows an example of running a program on the robot using the Python API (online programming)
# More information about the RoboDK API appears here:
# https://robodk.com/doc/en/RoboDK-API.html
from robolink import *    # API to communicate with RoboDK
from robodk import *      # robodk robotics toolbox
# used for processing coordinate data from computer vision program
import json
# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()
# Select a robot (a popup is displayed if more than one robot is available)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected or available')
RUN_ON_ROBOT = False
# Important: by default, the run mode is RUNMODE_SIMULATE
# If the program is generated offline manually the runmode will be RUNMODE_MAKE_ROBOTPROG,
# Therefore, we should not run the program on the robot
if RDK.RunMode() != RUNMODE_SIMULATE:
    RUN_ON_ROBOT = False
if RUN_ON_ROBOT:

    # Connect to the robot using default IP
    success = robot.Connect() # Try to connect once
    status, status_msg = robot.ConnectedState()
    if status != ROBOTCOM_READY:
        # Stop if the connection did not succeed
        print(status_msg)
        raise Exception("Failed to connect: " + status_msg)
    # This will set to run the API programs on the robot and the simulator (online programming)
    RDK.setRunMode(RUNMODE_RUN_ROBOT)

# Get the current joint position of the robot
# (updates the position on the robot simulator)
joints_ref = robot.Joints()
# get the current position of the TCP with respect to the reference frame:
# (4x4 matrix representing position and orientation)
target_ref = robot.Pose()
pos_ref = target_ref.Pos()
# It is important to provide the reference frame and the tool frames when generating programs offline
# It is important to update the TCP on the robot mostly when using the driver
robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(robot.PoseTool())

# robot.setZoneData(10) # Set the rounding parameter
robot.setSpeed(200) # Set linear speed in mm/s
# set gripper force & speed
robot.RunCodeCustom('rq_set_force(50)', INSTRUCTION_CALL_PROGRAM)
robot.RunCodeCustom('rq_set_speed(100)', INSTRUCTION_CALL_PROGRAM)

# !!!ACTUAL PROGRAM STARTS HERE!!! Everything above this line is setting up the robot

# start is the starting position of the robot
# free drive to these 2 positions and enter targets into RoboDK
originPose = RDK.Item('Origin').Pose()
binPose = RDK.Item('Bin').Pose()

# load object coordinate data from JSON file
inputFile = open(r"C:\Users\KuphJr\Desktop\CSCI5551FinalProject-master\CSCI5551FinalProject-master\data.json")
coordinateJSON = json.loads(inputFile.read())
coordinatePoses = []
for coordinate in coordinateJSON:
	# translates based upon the originPosition which is the bottom left corner of the bottom left square
	coordinatePoses.append((originPose * transl(-coordinate['x'], coordinate['y'], -coordinate['z'])) * rotz((pi/2)-coordinate['rz']))

#start at the origin with the gripper open
robot.MoveJ(originPose * transl(0,0,-50))
robot.RunCodeCustom('rq_open_and_wait', INSTRUCTION_CALL_PROGRAM)
robodk.pause(1)
i = 0
	
while i < len(coordinatePoses)-2:
	# move to position 50 mm above object
	robot.MoveJ(coordinatePoses[i] * transl(0,0,-50))
	# move down linearly to the object
	robot.MoveL(coordinatePoses[i])
	# close the robot gripper
	robot.RunCodeCustom('rq_close_and_wait', INSTRUCTION_CALL_PROGRAM)
	robodk.pause(1)
	# move linearly to position 50 mm above object
	robot.MoveL(coordinatePoses[i] * transl(0,0,-50))
	# increment index
	i+=1
	# move to position 50 mm above location to set object
	robot.MoveJ(coordinatePoses[i] * transl(0,0,-50))
	# move down linearly to the location to set object
	robot.MoveL(coordinatePoses[i])
	# open the robot gripper
	robot.RunCodeCustom('rq_open_and_wait', INSTRUCTION_CALL_PROGRAM)
	robodk.pause(1)
	# move linearly to position 50 mm above object
	robot.MoveL(coordinatePoses[i] * transl(0,0,-50))
	# increment index
	i+=1
	
# move to position 50 mm above origin	
robot.MoveJ(originPose * transl(0,0,-50))
	
