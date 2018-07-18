##############################################################################
'''
AUTHOR:			Yao Ji (jiyao94@126.com)
CREATED DATE:	2018/6/29
LAST UPDATE:	2018/7/18
DESCRIPTION:
'''
##############################################################################

import os, json, readline, glob, traceback
from collections import namedtuple
from openpyxl import load_workbook

def Combine(DBFileName, outputFileName, argFileName='Arguments.xlsx'):
	#FD parameter definition file
	fileName = "para_def.txt"
	jstr = {}
	with open(fileName, 'r') as f:
		line = f.readline()[:-1]
		while True:
			line.replace('\t', ' ')
			if len(line) < 1:
				pass
			elif line[0] not in ['P', 'I']:
				fb = line
				jstr[fb] = {'para':{}, 'input':{}}
			elif line[0] == 'P':
				num = int(line[1:3])
				name = line.split(' ')[-1]
				jstr[fb]['para'][name] = num
			elif line[0] == 'I':
				num = int(line[1:3])
				name = line.split(' ')[-1]
				jstr[fb]['input'][name] = num
			else:
				pass
			line = f.readline()
			if line == '':
				break
			else:
				line = line[:-1]

	#open Argument file
	wb = load_workbook(argFileName)
	#read config sheet
	ws_config = wb['Config']
	Libs = namedtuple('Libs', 'name type sPage ax dx input_lst output_lst module_lst')
	lib_lst = []
	for i in range(2, len(list(ws_config.rows)) + 1):
		lib_lst.append(Libs(ws_config[i][1].value, ws_config[i][0].value, 
								int(ws_config[i][2].value), {}, {}, [], [], []))

	#read AX and DX point configs in DB and libs
	ax_db, dx_db = {}, {}
	with open(DBFileName, 'r', encoding='utf-16') as file:
		line = file.readline()
		while line.find('BEGIN_AX') < 0:
			line = file.readline()
		while line.find('END_AX') < 0:
			if line.find('=') > -1 and len(line.split(',')) > 25:
				tag = line.split('=')[0]
				location = (int(line.split(',')[24]), int(line.split(',')[25]))
				ax_db[tag] = location
			else:
				pass
			line = file.readline()
		while line.find('BEGIN_DX') < 0:
			line = file.readline()
		while line.find('END_DX') < 0:
			if line.find('=') > -1 and len(line.split(',')) > 19:
				tag = line.split('=')[0]
				location = (int(line.split(',')[18]), int(line.split(',')[19]))
				dx_db[tag] = location
			else:
				pass
			line = file.readline()

	for i in range(len(lib_lst)):
		with open('Library/' + lib_lst[i].type, 'r', encoding='utf-16') as file:
			line = file.readline()
			while line.find('BEGIN_AX') < 0:
				line = file.readline()
			while line.find('END_AX') < 0:
				if line.find('=') > -1 and len(line.split(',')) > 25:
					tag = line.split('=')[0]
					location = (int(line.split(',')[24]), int(line.split(',')[25]))
					lib_lst[i].ax[tag] = location
				else:
					pass
				line = file.readline()
			while line.find('BEGIN_DX') < 0:
				line = file.readline()
			while line.find('END_DX') < 0:
				if line.find('=') > -1 and len(line.split(',')) > 19:
					tag = line.split('=')[0]
					location = (int(line.split(',')[18]), int(line.split(',')[19]))
					lib_lst[i].dx[tag] = location
				else:
					pass
				line = file.readline()

	#global LID counters
	LID_AX, LID_DX = 0, 0

	f = open('.DPUxx.txt.temp', 'w', encoding='utf-16')
	f_db = open(DBFileName, 'r', encoding='utf-16')

	#copy DB until the beginning of point config (exclusive)
	ax_db_reverse = {v:k for k, v in ax_db.items()}
	dx_db_reverse = {v:k for k, v in dx_db.items()}
	line_db = f_db.readline()
	while line_db.find('[POINT_DIR INFO]') < 0:
		if line_db.find('DataBlock, ') > -1:
			dataBlock = int(line_db.split('DataBlock, ')[1].split(',')[0])
		elif line_db.find('Func, ') > -1:
			blockNum = int(line_db.split(', ')[2].split(':')[0])
		elif line_db.find('Para=') > -1:
			#change LID with global counter
			loc = (dataBlock + 40000, blockNum)
			if loc in ax_db.values():
				para_lst = line_db.split(',')
				para_lst[para_lst.index(ax_db_reverse[loc]) - 1] = str(LID_AX)
				line_db = ','.join(para_lst)
				LID_AX += 1
			elif loc in dx_db.values():
				para_lst = line_db.split(',')
				para_lst[para_lst.index(dx_db_reverse[loc]) - 1] = str(LID_DX)
				line_db = ','.join(para_lst)
				LID_DX += 1
			else:
				pass
		else:
			pass
		f.write(line_db)
		line_db = f_db.readline()

	#reading input and module list from arguments
	Inputs = namedtuple('Inputs', 'index indLoc tag tagLoc')
	Outputs = namedtuple('Outputs', 'index tag tagLoc pageLoc')
	Modules = namedtuple('Modules', 'index indLoc tag desc para')

	for i in range(len(lib_lst)):
		iterRow = wb[lib_lst[i].name].rows
		while True:
			try:
				row = next(iterRow)
				if row[0].value == 'INPUTS':
					next(iterRow)
					row = next(iterRow)
					while row[0].value is not None:
						index, tag = row[0].value, row[2].value
						#inputs directly connects to database
						if tag in ax_db:
							lib_lst[i].input_lst.append(Inputs(index, [0, 0], tag, list(ax_db[tag])))
						elif tag in dx_db:
							lib_lst[i].input_lst.append(Inputs(index, [0, 0], tag, list(dx_db[tag])))
						#inputs connects to other libs outputs
						else:
							lib_lst[i].input_lst.append(Inputs(index, [0, 0], tag, [0, 0]))
						row = next(iterRow)
				elif row[0].value == 'OUTPUTS':
					next(iterRow)
					row = next(iterRow)
					while row[0].value is not None:
						index, tag = row[0].value, row[2].value
						#page outputs appended to output list
						if tag in ax_db:
							lib_lst[i].output_lst.append(Outputs(index, tag, ax_db[tag], [0, 0]))
						elif tag in dx_db:
							lib_lst[i].output_lst.append(Outputs(index, tag, dx_db[tag], [0, 0]))
						#net outputs appended to module list
						else:
							lib_lst[i].module_lst.append(Modules(index, [0, 0], tag, row[3].value, []))
						row = next(iterRow)
				elif row[0].value == 'PARAMETERS':
					next(iterRow)
					row = next(iterRow)
					while True:
						if row[0].value is not None:
							index, tag, desc, para, val = row[0].value, row[2].value, row[3].value, row[4].value, row[5].value
							lib_lst[i].module_lst.append(Modules(index, [0, 0], tag, desc, [(para, val)]))
						else:	#line only contains parameter
							para, val = row[4].value, row[5].value
							lib_lst[i].module_lst[-1].para.append((para, val))
						row = next(iterRow)
				else:
					pass
			except StopIteration:
				break

	#copy lib pages to Final for each lib
	for i in range(len(lib_lst)):
		f.write('\n')

		#first scan the lib to record page lists
		#and fill index locations for input and module lists
		pageList = []
		with open('Library/' + lib_lst[i].type, 'r', encoding='utf-16') as f_lib:
			line_lib = f_lib.readline()
			while line_lib.find('Page, ') < 0:
				line_lib = f_lib.readline()
			while line_lib.find('[POINT_DIR INFO]') < 0:
				if line_lib.find('Page, ') > -1:
					pageNum = int(line_lib.split('Page, ')[1].split(':')[0])
					pageList.append(pageNum)
				elif line_lib.find('Func, ') > -1:
					blockNum = int(line_lib.split(', ')[2].split(':')[0])
				elif line_lib.find('In=') > -1 and line_lib.find('\\') > -1:
					pass
				elif line_lib.find('Para=') > -1 and line_lib.find(',') > -1:
					for j in range(len(lib_lst[i].module_lst)):
						if lib_lst[i].module_lst[j].index == line_lib.split(',')[1]:
							lib_lst[i].module_lst[j].indLoc[:] = [pageNum, blockNum]
							break
						else:
							pass
				elif line_lib.find('Out=') > -1 and line_lib.find('\\') > -1:
					for j in range(len(lib_lst[i].input_lst)):
						if lib_lst[i].input_lst[j].index == line_lib.split('\\')[1].split(' ')[0]:
							lib_lst[i].input_lst[j].indLoc[:] = [pageNum, blockNum]
							break
						else:
							pass
					for j in range(len(lib_lst[i].module_lst)):
						if lib_lst[i].module_lst[j].index == line_lib.split('\\')[1].split(' ')[0]:
							lib_lst[i].module_lst[j].indLoc[:] = [pageNum, blockNum]
							break
						else:
							pass
				else:
					pass
				line_lib = f_lib.readline()

		#second scan to make changes to the lib
		pageCounter = 0
		module_lst_copy = lib_lst[i].module_lst[:]

		with open('Library/' + lib_lst[i].type, 'r', encoding='utf-16') as f_lib:
			line_lib = f_lib.readline()
			while line_lib.find('Page, ') < 0:
				line_lib = f_lib.readline()
			while line_lib.find('[POINT_DIR INFO]') < 0:
				if line_lib.find('Page, ') > -1:
					pageNum = int(line_lib.split('Page, ')[1].split(':')[0])
					pageOrder = int(line_lib.split(', ')[1].split(':')[1])
					#change page number and order
					newPageNum = lib_lst[i].sPage + pageCounter
					page_lst = line_lib.split(', ')
					page_lst[1] = str(newPageNum) + ':' + str(newPageNum * pageOrder // pageNum)
					line_lib = ', '.join(page_lst)
					pageCounter += 1
				elif line_lib.find('Func, ') > -1:
					funcName = line_lib.split(', ')[1]
					blockNum = int(line_lib.split(', ')[2].split(':')[0])
				elif line_lib.find('In=') > -1:
					if line_lib.find('\\') > -1:
						#add new page number to output list
						for j in range(len(lib_lst[i].output_lst)):
							if lib_lst[i].output_lst[j].index == line_lib.split('\\')[1].split(' ')[0]:
								lib_lst[i].output_lst[j].pageLoc[:] = [newPageNum, blockNum]
								break
							else:
								pass
					else:
						pass
					#change input parameters of function block
					for x in module_lst_copy:
						if x.indLoc == [pageNum, blockNum]:
							para_lst = line_lib.split(',')
							for para in x.para:
								if para[0] in jstr[funcName]['input']:
									if jstr[funcName]['input'][para[0]] == 1:
										para_lst[0] = '\t\tPara= ' + str(para[1])
									else:
										para_lst[jstr[funcName]['input'][para[0]] - 1] = str(para[1])
								else:
									pass
							line_lib = ','.join(para_lst)
							break
						else:
							pass
				elif line_lib.find('Para=') > -1:
					#change LID with global counter
					loc = (pageNum, blockNum)
					if loc in lib_lst[i].ax.values():
						para_lst = line_lib.split(',')
						para_lst[0] = '\t\tPara= ' + str(LID_AX)
						line_lib = ','.join(para_lst)
						LID_AX += 1
					elif loc in lib_lst[i].dx.values():
						para_lst = line_lib.split(',')
						para_lst[0] = '\t\tPara= ' + str(LID_DX)
						line_lib = ','.join(para_lst)
						LID_DX += 1
					else:
						pass
					#change page connection according to new page numbers
					if funcName in ['XPgAI', 'XPgDI']:
						connectPage = int(line_lib.split('Para= ')[1].split(',')[0])
						#change internal page connections
						if connectPage in pageList:
							para_lst = line_lib.split('Para= ')[1].split(',')
							para_lst[0] = str(lib_lst[i].sPage + pageList.index(connectPage))
							line_lib = '\t\tPara= ' + ','.join(para_lst)
						#change physical page connections
						else:
							for x in lib_lst[i].input_lst:
								if x.indLoc == [pageNum, blockNum]:
									if x.tagLoc == [0, 0]:		#connection is other libs not DB, store new pages
										lib_lst[i].input_lst[lib_lst[i].input_lst.index(x)].indLoc[:] = [newPageNum, blockNum]
									else:						#connection is DB, make connection
										line_lib = '\t\tPara= {0},{1},\n'.format(x.tagLoc[0], x.tagLoc[1])
										lib_lst[i].input_lst.remove(x)
									break
								else:
									pass
					#change tag name and parameters of module
					#in addition, check whether any input is connected to this module
					else:
						for x in module_lst_copy:
							if x.indLoc == [pageNum, blockNum]:
								para_lst = line_lib.split(',')
								#check whether input tag is the same as module tag
								for m in range(len(lib_lst)):
									for n in range(len(lib_lst[m].input_lst)):
										if lib_lst[m].input_lst[n].tag == x.tag:
											lib_lst[m].input_lst[n].tagLoc[:] = [newPageNum, blockNum]
										else:
											pass
								#change tag
								if x.tag is not None:
									para_lst[1] = x.tag
								else:
									pass
								#change parameters
								for para in x.para:
									if para[0] in jstr[funcName]['para']:
										if jstr[funcName]['para'][para[0]] == 1:
											para_lst[0] = '\t\tPara= ' + str(para[1])
										else:
											para_lst[jstr[funcName]['para'][para[0]] - 1] = str(para[1])
									else:
										pass
								line_lib = ','.join(para_lst)
								module_lst_copy.remove(x)
								break
							else:
								pass
				elif line_lib.find('Out=') > -1:
					pass
				else:
					pass
				f.write(line_lib)
				line_lib = f_lib.readline()

		#insert empty pages
		while i < len(lib_lst) - 1 and lib_lst[i].sPage + pageCounter < lib_lst[i + 1].sPage:
			f.write('\nPage, {0}:{0}, \nPageEnd\n'.format(lib_lst[i].sPage + pageCounter))
			pageCounter += 1

	#copy point config of DB to Final, until END_AX (exclusive)
	while line_db.find('END_AX') < 0:
		f.write(line_db)
		line_db = f_db.readline()

	#copy point configs of lib to Final, between BEGIN_AX and END_AX (exclusive)
	for i in range(len(lib_lst)):
		with open('Library/' + lib_lst[i].type, 'r', encoding='utf-16') as f_lib:
			line_lib = f_lib.readline()
			while line_lib.find('[POINT_DIR INFO]') < 0:
				line_lib = f_lib.readline()
			while line_lib.find('BEGIN_AX') < 0:
				line_lib = f_lib.readline()
			line_lib = f_lib.readline()
			while line_lib.find('END_AX') < 0:
				for x in lib_lst[i].module_lst:
					if x.index == line_lib.split('=')[0]:
						config_lst = line_lib.split('=')[1].split(',')
						config_lst[1] = x.desc
						line_lib = x.tag + '=' + ','.join(config_lst)
						lib_lst[i].module_lst.remove(x)
						break
					else:
						pass
				f.write(line_lib)
				line_lib = f_lib.readline()

	#copy point configs of DB to Final, until END_DX (exclusive)
	while line_db.find('END_DX') < 0:
		f.write(line_db)
		line_db = f_db.readline()

	#copy point configs of lib to Final, between BEGIN_DX and END_DX (exclusive)
	for i in range(len(lib_lst)):
		with open('Library/' + lib_lst[i].type, 'r', encoding='utf-16') as f_lib:
			line_lib = f_lib.readline()
			while line_lib.find('[POINT_DIR INFO]') < 0:
				line_lib = f_lib.readline()
			while line_lib.find('BEGIN_DX') < 0:
				line_lib = f_lib.readline()
			line_lib = f_lib.readline()
			while line_lib.find('END_DX') < 0:
				for x in lib_lst[i].module_lst:
					if x.index == line_lib.split('=')[0]:
						config_lst = line_lib.split('=')[1].split(',')
						config_lst[1] = x.desc
						line_lib = x.tag + '=' + ','.join(config_lst)
						lib_lst[i].module_lst.remove(x)
						break
					else:
						pass
				f.write(line_lib)
				line_lib = f_lib.readline()

	#file lib finish
	f_lib.close()

	#copy the rest of DB to Final (the last END_DX)
	f.write(line_db)
	lines_db = f_db.readlines()
	f.writelines(lines_db)

	#file db finisih
	f_db.close()

	#finish writing
	f.close()

	#in the second write, connect DB points to libs
	#also, complete the remaining inter-lib connections
	input_lst, output_lst = [], []
	for x in lib_lst:
		input_lst += x.input_lst
		output_lst += x.output_lst
	f_t = open('.DPUxx.txt.temp', 'r', encoding='utf-16')
	f = open(outputFileName, 'w', encoding='utf-16')
	line_t = f_t.readline()
	while line_t.find('ChildDeviceEnd') < 0:
		if line_t.find('DataBlock, ') > -1:
			dataBlock = int(line_t.split('DataBlock, ')[1].split(',')[0])
		elif line_t.find('Func, ') > -1:
			blockNum = int(line_t.split(', ')[2].split(':')[0])
		elif line_t.find('In=') > -1:
			for x in output_lst:
				if x.tagLoc == (dataBlock + 40000, blockNum):
					in_line = line_t.split(',')
					in_line[1] = 'B{0}-{1}'.format(x.pageLoc[1], x.pageLoc[0]) + in_line[1].split('\\')[1]
					line_t = ','.join(in_line)
					output_lst.remove(x)
					break
				else:
					pass
		else:
			pass
		f.write(line_t)
		line_t = f_t.readline()
	while line_t.find('[POINT_DIR INFO]') < 0:
		if line_t.find('Page, ') > -1:
			pageNum = int(line_t.split('Page, ')[1].split(':')[0])
		elif line_t.find('Func, ') > -1:
			funcName = line_t.split(', ')[1]
			blockNum = int(line_t.split(', ')[2].split(':')[0])
		elif line_t.find('Para=') > -1 and funcName in ['XPgAI', 'XPgDI']:
			for x in input_lst:
				if x.indLoc == [pageNum, blockNum]:
					line_t = '\t\tPara= {0},{1},\n'.format(x.tagLoc[0], x.tagLoc[1])
					input_lst.remove(x)
					break
				else:
					pass
		else:
			pass
		f.write(line_t)
		line_t = f_t.readline()

	f.write(line_t)
	lines_t = f_t.readlines()
	f.writelines(lines_t)
	f_t.close()
	os.remove('.DPUxx.txt.temp')
	f.close()

def complete(text, state):
	return glob.glob(text + '*')[state]

#start main
if __name__ == '__main__':
	try:
		readline.set_completer(complete)					#add path auto-complete
		readline.parse_and_bind("tab: complete")			#using tab for auto-complete
		readline.set_completer_delims('\t')					#just like in shell

		#Database file name
		DBFileName = input('Database DPU file: ')
		outputFileName = input('New output file: ')

		Combine(DBFileName, outputFileName)
		input('New DPU file is generated.')
	except Exception as err:
		print('Exception: ' + repr(err))
		input(traceback.format_exc())