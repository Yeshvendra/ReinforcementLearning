import numpy as np
import random
import operator
import xml.etree.cElementTree as ET

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
    

gamma = 0.1
alpha = 0.8

motor_info = np.array([["FR-C","FR-A"],
                      ["FL-C","FL-A"],
                      ["BR-C","BR-A"],
                      ["BL-C","BL-A"]])


reward = np.array([[[0,25,-25],
                    [0,25,-25],
                    [0,-25,25],
                    [0,-25,25],
                    [25,-25,-25]],
                   [[0,-25,25],
                    [0,25,-25],
                    [0,-25,25],
                    [0,25,-25],
                    [25,-25,-25]],
                   [[0,25,-25],
                    [0,25,-25],
                    [0,-25,25],
                    [0,-25,25],
                    [25,-25,-25]],
                   [[0,-25,25],
                    [0,25,-25],
                    [0,-25,25],
                    [0,25,-25],
                    [25,-25,-25]]])

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

#col = np.shape(motor_info)[1]
#reward = np.zeros(())

q_matrix = np.zeros((5,81))

states = np.array([0,1,2,3,4])

for i in range(100):
    start_state = random.randint(0,4)
    current_state = start_state
    while True:
        action = random.randint(0, 80)
        next_state = random.randint(0,4)
        action_according_to_reward = int2rewardValue(action,3)
        length_of_action_according_to_reward = len(action_according_to_reward)
        action_according_to_reward = ("0" * (4-length_of_action_according_to_reward)) + action_according_to_reward
        simultaneous_reward = 0
        for i, c in enumerate(action_according_to_reward):
            simultaneous_reward += reward[i][current_state][int(c)]
        future_rewards = []
        for action_nxt in range(81):
            future_rewards.append(q_matrix[next_state][action_nxt])
        q_state = alpha * (simultaneous_reward + gamma * max(future_rewards) - q_matrix[current_state][action]) 
        q_matrix[current_state][action] += q_state
        stored_state = current_state
        current_state = next_state
        if simultaneous_reward == 100:
            print("goal achieved at action : " + action_according_to_reward + " for state " + str(stored_state))
            break

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
doc = ET.SubElement(root, "Stop")
for i, c in enumerate(binary_value):
    ET.SubElement(doc, "Pin").text = str(motor_info[i][(int(c)-1)])
print("Stop : " + binary_value + " and its value is " + str(value))

tree = ET.ElementTree(root)
tree.write("QLearningResult.xml")
