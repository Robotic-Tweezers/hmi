from distutils.log import debug
from tkinter import Y
from typing import Type
from xmlrpc.client import ProtocolError

from serialparser import Serialparser
from time import sleep

import orientation_msg_pb2

import socket
import vive

import math

from liveplot import Liveplot

class HMIServer:
	def __init__(self, host, port, vive, serialparser, debug=False):
		self.port = port
		self.host = host

		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.s.settimeout(1) # seconds
			self.s.connect((self.host, self.port))
		except socket.error:
			print("!!!! Socket error! Not connected to client !!!!")

		self.vive = vive
		self.serialparser = serialparser

		self.pot_position = 0
		self.en_switch = 0

		self.gain = 0

		self.roll = 0
		self.pitch = 0
		self.yaw = 0

		self.debug = debug

	def update_data(self):
		# Get data from arduino over serial (potentiometer and limit switch)
		if self.serialparser != None and self.serialparser.msg_available():
			(self.pot_position, self.en_switch) = self.serialparser.getmsg()
			# print(self.pot_position)

		# Vive data will always be updating in its thread
		self.roll = self.vive.roll() * math.pi/180
		self.pitch = self.vive.pitch() * math.pi/180
		self.yaw = self.vive.yaw() * math.pi/180


	def send_data(self):
		d = orientation_msg_pb2.OrientationMsg()
		d.roll = self.roll
		d.pitch = self.pitch
		d.yaw = self.yaw

		if self.debug:
			print("Sending Data: ", d)

		dbytes = d.SerializeToString()

		try:
			self.s.sendall(dbytes)
		except socket.timeout:
			pass

		# try:
		# 	print(self.s.recv(1024))
		# except socket.timeout:
		# 	pass

	def start(self):
		while True:
			self.update_data()
			self.send_data()
			sleep(0.01)

if __name__ == "__main__":
	sp = Serialparser("COM8", 9600)
	hmis = HMIServer("192.168.1.212", 0, 0, sp)
	hmis.start()
