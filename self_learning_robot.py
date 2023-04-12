import numpy as np
import random
import time
import operator
import xml.etree.cElementTree as ET
import RPi.GPIO as GPIO
import motion
import csv
from motion import read_raw_data, ACCEL_YOUT_H, GYRO_ZOUT_H

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
fout = open("gyro_data.csv","w")

def reverse(i):
    return i[::-1]

def int2rewardValue(i,n):
    result = ""
    while i>=n:
        result += str(i%n)
        i = i//n
    else:
        result += str(i);
    return reverse(result)

def if_action_for_state(action,state):	
	for i, c in enumerate(action):
        	GPIO.output(motor_info[i][int(c)-1],GPIO.HIGH)

        time.sleep(0.05)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        Ay = acc_y/8192.0
	time.sleep(0.2)
        gyro_z = read_raw_data(GYRO_ZOUT_H)
        Gz = gyro_z/131.0
	time.sleep(0.75)

	for i, c in enumerate(action):
                GPIO.output(motor_info[i][int(c)-1],GPIO.LOW)
	
	fout.write("state : " + str(state) + " action : " + str(action) + " accel-y : " + str(Ay) + " gyro-z : " + str(Gz) + "\n")

	time.sleep(1)
	if Ay>0.35 and Gz < 10 and Gz > -10  and state == 0:
		return 25
	elif Ay<-0.35 and Gz < 15 and Gz > -15 and state == 3:
		return 25

	if Gz>4 and state == 1:
                return 25
        elif Gz<-4 and state == 2:
                return 25

	print(action)
	if state==4 and action == "0" * len(action):
		return 25
	
	GPIO.output(23, GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(23, GPIO.LOW)
	return -25
    
def assign_reward():
	for x in xrange(motor_info.shape[0]):
		for y in xrange(motor_info.shape[1]):

			GPIO.output(23,GPIO.HIGH)
			GPIO.output(motor_info[x][y],GPIO.HIGH)
			time.sleep(0.05)

			acc_y = read_raw_data(ACCEL_YOUT_H)
			Ay = acc_y/8192.0
			gyro_z = read_raw_data(GYRO_ZOUT_H)
			Gz = gyro_z/131.0

			time.sleep(0.95)
			GPIO.output(motor_info[x][y],GPIO.LOW)
			
			if (Ay>0.25):
				reward[x][0][y+1] = 25
				reward[x][3][y+1] = -25
			elif (Ay<-0.4):
				reward[x][0][y+1] = -25
				reward[x][3][y+1] = 25

			if Gz>1:
				reward[x][1][y+1] = 25
				reward[x][2][y+1] = -25
			elif Gz<-2:
				reward[x][1][y+1] = -25
				reward[x][2][y+1] = 25

			GPIO.output(23,GPIO.LOW)
			time.sleep(0.2)
			
				
						 

gamma = 0.1
alpha = 0.1

#motor_info = np.array([["FR-C","FR-A"],
#                      ["FL-C","FL-A"],
#                      ["BR-C","BR-A"],
#                      ["BL-C","BL-A"]])
motor_info = np.array([[12,16],
                      [5,6],
                      [20,21],
                      [26,19]])


for i in xrange(motor_info.shape[0]):
	for j in xrange(motor_info.shape[1]):
		GPIO.setup(motor_info[i][j],GPIO.OUT)

GPIO.setup(18,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)

FR = 0
FL = 1
BR = 2
BL = 3

I = 0
C = 1
A = 2

FRONT = 0
LEFT = 1
RIGHT = 2
BACK = 3
STOP = 4

col = np.shape(motor_info)[1]+1
row = 5
zDim = np.shape(motor_info)[0]
 
q_matrix = np.zeros((5,81))

states = np.array([0,1,2,3,4])
choice = raw_input("Do you want to continue the last session: ")
if choice == "y":
	with open("intermediate.csv","r") as csvfile:
		reader = csv.reader(csvfile)
		q_matrix = [[float(e) for e in r] for r in reader]

print(q_matrix)
print("Starting Q-Learing Process.....")
for i in range(1000):
    start_state = random.randint(0,4)
    current_state = start_state
    while True:
	print("Current State is : ")
	print(current_state)
        action = random.randint(0, 80)
        next_state = random.randint(0,4)
        action_according_to_reward = int2rewardValue(action,3)
        length_of_action_according_to_reward = len(action_according_to_reward)
        action_according_to_reward = ("0" * (4-length_of_action_according_to_reward)) + action_according_to_reward
        simultaneous_reward = if_action_for_state(action_according_to_reward,current_state)
	future_rewards = []
        for action_nxt in range(81):
            future_rewards.append(q_matrix[next_state][action_nxt])
        q_state = alpha * (simultaneous_reward + gamma * max(future_rewards) - q_matrix[current_state][action]) 
        q_matrix[current_state][action] += q_state
        stored_state = current_state
        current_state = next_state

	if simultaneous_reward == 25:
	    GPIO.output(18,GPIO.HIGH)
	    time.sleep(0.5)
	    GPIO.output(18,GPIO.LOW)
            print("goal achieved at action : " + action_according_to_reward + " for state " + str(stored_state))
	    choice = raw_input("If want to continue press y : ")
	    if choice != "y":
		with open("intermediate.csv","w") as csvfile:
			writer = csv.writer(csvfile)
			[writer.writerow(r) for r in q_matrix]
		fout.close()
		exit()	
            break

fout.close()
print("final q-matrix : ")
print(q_matrix)

root = ET.Element("motorDrivingConfiguration")

index, value = max(enumerate(q_matrix[FRONT]), key=operator.itemgetter(1))
binary_value = int2rewardValue(index,3)
length_of_binary_value = len(binary_value)
binary_value = ("0" * (4-length_of_binary_value)) + binary_value
doc = ET.SubElement(root, "Forward")
for i, c in enumerate(binary_value):
    ET.SubElement(doc, "Pin").text = str(motor_info[i][(int(c)-1)])
print("Front : " + binary_value + " and its value is " + str(value))


index, value = max(enumerate(q_matrix[LEFT]), key=operator.itemgetter(1))
binary_value = int2rewardValue(index,3)
length_of_binary_value = len(binary_value)
binary_value = ("0" * (4-length_of_binary_value)) + binary_value
doc = ET.SubElement(root, "Left")
for i, c in enumerate(binary_value):
    ET.SubElement(doc, "Pin").text = str(motor_info[i][(int(c)-1)])
print("Left : " + binary_value + " and its value is " + str(value))


index, value = max(enumerate(q_matrix[RIGHT]), key=operator.itemgetter(1))
binary_value = int2rewardValue(index,3)
length_of_binary_value = len(binary_value)
binary_value = ("0" * (4-length_of_binary_value)) + binary_value
doc = ET.SubElement(root, "Right")
for i, c in enumerate(binary_value):
    ET.SubElement(doc, "Pin").text = str(motor_info[i][(int(c)-1)])
print("Right : " + binary_value + " and its value is " + str(value))


index, value = max(enumerate(q_matrix[BACK]), key=operator.itemgetter(1))
binary_value = int2rewardValue(index,3)
length_of_binary_value = len(binary_value)
binary_value = ("0" * (4-length_of_binary_value)) + binary_value
doc = ET.SubElement(root, "Backward")
for i, c in enumerate(binary_value):
    ET.SubElement(doc, "Pin").text = str(motor_info[i][(int(c)-1)])
print("Back : " + binary_value + " and its value is " + str(value))


index, value = max(enumerate(q_matrix[STOP]), key=operator.itemgetter(1))
binary_value = int2rewardValue(index,3)
length_of_binary_value = len(binary_value)
binary_value = ("0" * (4-length_of_binary_value)) + binary_value
print("Stop : " + binary_value + " and its value is " + str(value))

tree = ET.ElementTree(root)
tree.write("QLearningResult.xml")

