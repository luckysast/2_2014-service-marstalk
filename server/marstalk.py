#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import socket
import threading
import sys
import math
import re
import os
import errno

host = ""
port = 4444
thrs = []

def block(code):
    opened = []
    blocks = {}
    for i in range(len(code)):
        if code[i] == '[':
            opened.append(i)
        elif code[i] == ']':
            blocks[i] = opened[-1]
            blocks[opened.pop()] = i
    return blocks
 
def parse(code):
    return ''.join(c for c in code if c in '><+-.,[]')
 
def run(code):
    code = parse(code)
    x = i = 0
    bf = {0: 0}
    blocks = block(code)
    l = len(code)
    result = ""
    while i < l:
        sym = code[i]
        if sym == '>':
            x += 1
            bf.setdefault(x, 0)
        elif sym == '<':
            x -= 1
        elif sym == '+':
            bf[x] += 1
        elif sym == '-':
            bf[x] -= 1
        elif sym == '.':
            result = result + chr(bf[x])
        elif sym == ',':
            bf[x] = int(input('Input: '))
        elif sym == '[':
            if not bf[x]: i = blocks[i]
        elif sym == ']':
            if bf[x]: i = blocks[i]
        i += 1
    return result

def compile_str(msg):
    result = ''
    val2 = 0
    for c in msg:
		ch = ord(c)	
		if ch == val2:
			result = result + ">.<"
			continue
		minus = ''
		if val2 > ch:
			ch = val2 - ch
			minus = '-'
		if val2 < ch:
			ch = ch - val2
			minus = '+'
		result = result + ''
		sq = int(math.floor(math.sqrt(ch)))
		curr1 = 0
		while curr1 < sq:
			curr1 = curr1 + 1
			result = result + "+"
		w = ch / sq
		result = result + '[>'
		i1 = 0
		while i1 < w:
			result = result + minus 
			i1 = i1 + 1
			
		if minus == '-':
			val2 = val2 - w * sq
		if minus == '+':
			val2 = val2 + w * sq		
		result = result + '<-]>'
		w2 = ch - w * sq
		while w2 > 0:
			w2 = w2 - 1
			if minus == '-':
				result = result + '-'
				val2 = val2 - 1
			if minus == '+':
				result = result + '+'
				val2 = val2 + 1
		result = result + '.<'
    return result

class Connect(threading.Thread):
	def __init__(self, sock, addr):
		self.sock = sock
		self.addr = addr
		self.bKill = False
		threading.Thread.__init__(self)
	def run (self):
		help_s = """
Commands: put, get, list, close
> """
		ptrn = re.compile(r""".*(?P<name>\w*?).*""", re.VERBOSE)                           
		self.sock.send(compile_str(help_s) + "\n\n")
		# self.sock.send(help_s)
		while True:
			if self.bKill == True:
				break
			buf = self.sock.recv(1024)
			buf = run(buf)
			if buf == "":
				break
			command = re.search( ur"\w*", buf).group()
			if command == "close":
				self.sock.send("\n" + compile_str("Bye-bye\n") + "\n\n")
				break
			elif command == "list":
				for f in os.listdir('flags/'):
					self.sock.send("\n" + compile_str("file: " + f + "\n\n"))
				break
			elif command == "put":
				self.sock.send("\n" + compile_str("id = ") + "\n\n")
				f_id = self.sock.recv(1024)
				f_id = run(f_id)
				if f_id == "":
					break
				f_id = re.search( ur"\w*", f_id).group()
				if f_id == "":
					self.sock.send("\n" + compile_str("incorrect id") + "\n\n")
					break
				self.sock.send("\n" + compile_str("flag = "))
				f_text = self.sock.recv(1024)
				f_text = run(f_text)
				if f_text == "":
					break
				f = open('flags/'+f_id, 'w')
				f.write(f_text)
				f.close()
				break
			elif command == "get":
				self.sock.send("\n" + compile_str("id = ") + "\n\n")
				f_id = self.sock.recv(1024)
				f_id = run(f_id)
				if f_id == "":
					break
				f_id = re.search( ur"\w*", f_id).group()
				if f_id == "":
					self.sock.send("\n" + compile_str("incorrect id") + "\n\n")
					break
				if os.path.exists('flags/' + f_id):
					f = open('flags/' + f_id, 'r')
					line = f.readline()
					f.close()
					self.sock.send("\n" + compile_str(line) + "\n\n")
				else:
					self.sock.send("\n" + compile_str("id not found") + "\n\n")
				break
			elif command:
				self.sock.send("\n" + compile_str("["+ command + "] unknown command\n") + "\n\n")
				break
		self.bKill = True
		self.sock.close()
		thrs.remove(self)
	def kill(self):
		if self.bKill == True:
			return
		self.bKill = True
		self.sock.close()
		# thrs.remove(self)
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(10)

if not os.path.exists("flags"):
	os.makedirs("flags")
        
try:
	while True:
		sock, addr = s.accept()
		thr = Connect(sock, addr)
		thrs.append(thr)
		thr.start()
except KeyboardInterrupt:
    print('Bye! Write me letters!')
    s.close()
    for thr in thrs:
		thr.kill()
    
