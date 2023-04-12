import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO
import time
import Tkinter as tk
import os.path

if not os.path.exists("QLearningResult.xml"):
	print("Sorry! No instructions to follow.")
	exit()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

tree = ET.parse("QLearningResult.xml")
root = tree.getroot()

while 1:

	instruction = raw_input("Enter the instruction : ")

	for child in root:
		if child.tag == "Forward":
			for subchild in child:
				GPIO.setup(int(subchild.text),GPIO.OUT)
				GPIO.output(int(subchild.text),GPIO.LOW)

		elif child.tag == "Left":
			for subchild in child:
				GPIO.setup(int(subchild.text),GPIO.OUT)
				GPIO.output(int(subchild.text),GPIO.LOW)

		elif child.tag == "Right":
			for subchild in child:
				GPIO.setup(int(subchild.text),GPIO.OUT)
				GPIO.output(int(subchild.text),GPIO.LOW)

		elif child.tag == "Backward":
			for subchild in child:
				GPIO.setup(int(subchild.text),GPIO.OUT)
				GPIO.output(int(subchild.text),GPIO.OUT)

	for child in root:
		if instruction == "w":
			if child.tag == "Forward":
				for subchild in child:
					GPIO.output(int(subchild.text),GPIO.HIGH)
				break

		elif instruction == "a":
			if child.tag == "Left":
				for subchild in child:
					GPIO.output(int(subchild.text),GPIO.HIGH)
				break

		elif instruction == "d":
			if child.tag == "Right":
				for subchild in child:
					GPIO.output(int(subchild.text),GPIO.HIGH)
				break

		elif instruction == "s":
			if child.tag == "Backward":
				for subchild in child:
					GPIO.output(int(subchild.text),GPIO.HIGH)
				break


