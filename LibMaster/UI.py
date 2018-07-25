###############################################################################
'''
AUTHOR:			Yao Ji (jiyao94@126.com)
CREATED DATE:	2018/7/13
LAST UPDATE:	2018/7/25
DESCRIPTION:	This is the UI of the three tools: Import, Config, Combine. It
				replace some of the functions in Config tool: User no longer
				needs to specify Config file 'Config.xlsx', configuration can
				be directly specified in the UI.
				Python UI is using PyQT5 library. This tool uses Pyforms, which
				is wrapper of PyQT. Please check its website for detaisl.
				https://github.com/UmSenhorQualquer/pyforms
				(Note that we modifies the official version of Pyforms to adapt
				to this tool.)
'''
###############################################################################
import os, json, traceback
from pyforms import BaseWidget
from pyforms.controls import ControlFile
from pyforms.controls import ControlDir
from pyforms.controls import ControlButton
from pyforms.controls import ControlTextArea
from pyforms.controls import ControlCombo
from pyforms.controls import ControlText
from pyforms.controls import ControlNumber
from pyforms.controls import ControlList
from AnyQt.QtWidgets import QFileDialog
from openpyxl import load_workbook
from Import import Import
from Config import Config
from Combine import Combine

class ControlFileOpen(ControlFile):
	def __init__(self, *args, **kwargs):
		super(ControlFileOpen, self).__init__(*args, **kwargs)
		self.use_save_dialog = kwargs.get('use_save_dialog', False)
		self.opened_file_type = kwargs.get('opened_file_type', '')

	def click(self):
		if self.opened_file_type == 'txt':
			value, _ = QFileDialog.getOpenFileName(self.parent, self._label, self.value, "Text Files (*.txt);;All Files (*)")
		elif self.opened_file_type == 'xlsx':
			value, _ = QFileDialog.getOpenFileName(self.parent, self._label, self.value, "Excel Files (*.xlsx);;All Files (*)")
		elif self.opened_file_type == 'json':
			value, _ = QFileDialog.getOpenFileName(self.parent, self._label, self.value, "Config Files (*.json);;All Files (*)")
		else:
			value, _ = QFileDialog.getOpenFileName(self.parent, self._label, self.value)
		if value and len(value) > 0:
			self.value = value

class ControlFileSave(ControlFile):
	def __init__(self, *args, **kwargs):
		super(ControlFileSave, self).__init__(*args, **kwargs)
		self.use_save_dialog = kwargs.get('use_save_dialog', True)
		self.saved_file_type = kwargs.get('saved_file_type', '')

	def click(self):
		if self.saved_file_type == 'txt':
			value, _ = QFileDialog.getSaveFileName(self.parent, self._label, self.value, "Text Files (*.txt);;All Files (*)")
		elif self.saved_file_type == 'xlsx':
			value, _ = QFileDialog.getSaveFileName(self.parent, self._label, self.value, "Excel Files (*.xlsx);;All Files (*)")
		elif self.saved_file_type == 'json':
			value, _ = QFileDialog.getSaveFileName(self.parent, self._label, self.value, "Config Files (*.json);;All Files (*)")
		else:
			value, _ = QFileDialog.getSaveFileName(self.parent, self._label, self.value)
		if value and len(value) > 0:
			self.value = value if value[-1 - len(self.saved_file_type):] == '.' + self.saved_file_type else value + '.' + self.saved_file_type

class LibMaster(BaseWidget):
	def __init__(self, title='LibMaster'):
		super(LibMaster, self).__init__(title)
		self.debug = False
		#Import controls
		self._openImportFile	= None
		self._openImportDir		= None
		self._importPathText	= ControlText()
		self._openFileButton	= ControlButton('Open a file')
		self._openDirButton		= ControlButton('Open a directory')
		self._importButton		= ControlButton('Import')
		self._importTextArea	= ControlTextArea()
		#Configure controls
		self._configCombo		= ControlCombo('Library')
		self._configNameText	= ControlText('Loop name')
		self._configPageNumber	= ControlNumber('Start page', default=1, min=1, max=20000)
		self._configDict		= {}
		self._configList		= ControlList('Application Plan',
			add_function=self.__buttonAction_Add, remove_function=self.__buttonAction_Del)
		self._configLoadButton	= ControlButton('Load')
		self._configAddButton	= ControlButton('Add')
		self._configDelButton	= ControlButton('Delete')
		self._configClearButton	= ControlButton('Clear')
		self._configSaveButton	= ControlButton('Save')
		self._configGenButton	= ControlButton('Generate')
		self._configTextArea	= ControlTextArea()
		#Combine controls
		self._openDBFile		= ControlFileOpen('Choose the database file:	', opened_file_type='txt')
		self._openArgFile		= ControlFileOpen('Choose the argument file:	', opened_file_type='xlsx')
		self._combineButton		= ControlButton('Combine')
		self._combineTextArea	= ControlTextArea()

		#setup all controls
		self.formset = [{
			'	1. Import	':[
				'',
				('','_importPathText',''),
				('','_openFileButton','', '_openDirButton',''),
				(' ','_importButton',' '),
				'',
				('','_importTextArea',''),
				''],
			'	2. Configure	':[
				'',
				('','_configCombo','','_configNameText','','_configPageNumber',''),
				('','_configList',''),
				('','_configAddButton','','_configDelButton','','_configClearButton',''),
				('','_configLoadButton','','_configSaveButton','','_configGenButton',''),
				'',
				('','_configTextArea',''),
				''],
			'	3. Combine	':[
				'',
				('','_openDBFile',''),
				('','_openArgFile',''),
				(' ','_combineButton',' '),
				'',
				('','_combineTextArea',''),
				'']}]

		#Button Actions
		self._openFileButton.value = self.__buttonAction_OpenFile
		self._openDirButton.value = self.__buttonAction_OpenDir
		self._importButton.value = self.__buttonAction_Import
		self._configLoadButton.value = self.__buttonAction_Load
		self._configAddButton.value = self.__buttonAction_Add
		self._configDelButton.value = self.__buttonAction_Del
		self._configClearButton.value = self.__buttonAction_Clear
		self._configSaveButton.value = self.__buttonAction_Save
		self._configGenButton.value = self.__buttonAction_Gen
		self._combineButton.value = self.__buttonAction_Combine

		#set all text area to read only
		self._importTextArea.readonly = True
		self._configTextArea.readonly = True
		self._combineTextArea.readonly = True

		#Combo box lists correct library files in './Library' directory
		self._configCombo += 'Select library'
		if not os.path.exists('Library'):
			os.mkdir('Library')
		else:
			file_lst = os.listdir('Library')
			for file in file_lst:
				if file[-4:] == '.txt' and (file[:-4] + '.xlsx') in file_lst:
					self._configCombo += file[:-4]
				else:
					pass

		#set configuration list property
		headers = []
		headers.append(' ' * 10 + 'Library' + ' ' * 10)
		headers.append(' ' * 10 + 'Loop Name' + ' ' * 10)
		headers.append(' Start Page ')
		headers.append(' End Page ')
		self._configList.horizontal_headers = headers
		self._configList.select_entire_row = True
		self._configList.readonly = True

	def __buttonAction_OpenFile(self):
		try:
			self._openImportFile = ControlFileOpen('Choose library file:', opened_file_type='txt')
			self._openImportFile.click()
			self._importPathText.value = self._openImportFile.value
		except Exception as err:
			self._importTextArea.__add__('Open file error: ' + repr(err))
			if self.debug:
				self._importTextArea.__add__(traceback.format_exc())

	def __buttonAction_OpenDir(self):
		try:
			self._openImportDir	= ControlDir('Choose directory:')
			self._openImportDir.click()
			self._importPathText.value = self._openImportDir.value
		except Exception as err:
			self._importTextArea.__add__('Open file error: ' + repr(err))
			if self.debug:
				self._importTextArea.__add__(traceback.format_exc())

	def __buttonAction_Import(self):
		try:
			#import a file, using main import function from 'Import.py'
			if self._openImportFile is not None and self._openImportFile.value == self._importPathText.value:
				addedFiles = Import([self._openImportFile.value], self._importTextArea.__add__)
				self._importTextArea.__add__('Import finish. Libraries are exported under \'./Library\' directory.')
				for add_file in addedFiles:
					self._configCombo += addedFiles[0][:-4]
			#import a directory, find valid files in directory before calling Import
			elif self._openImportDir is not None and self._openImportDir.value == self._importPathText.value:
				files = []
				dirs = os.listdir(self._openImportDir.value)
				for file in dirs:
					if file[-4:] == '.txt':
						files.append(self._openImportDir.value + '/' + file)
					else:
						pass
				if len(files) > 0:
					addedFiles = Import(files, self._importTextArea.__add__)
					self._importTextArea.__add__('Import finish. Libraries are exported under \'./Library\' directory.')
					for add_file in addedFiles:
						self._configCombo += add_file[:-4]
				else:
					self._importTextArea.__add__('No valid file in the directory.')
			#no file selected
			else:
				self._importTextArea.__add__('No file or directory selected.')
		except Exception as err:
			self._importTextArea.__add__('Error: ' + repr(err))
			if self.debug:
				self._importTextArea.__add__(traceback.format_exc())

	def __helper_Add2Dict(self, lst):
		combo, name, pageNum = lst[0], lst[1], int(lst[2])
		if name in self._configDict.values():
			raise Exception('Loop name conflict.')
		else:
			pass
		wb = load_workbook('./Library/' + combo + '.xlsx')
		ws = wb['Info']
		for row in list(ws.rows):
			if row[0].value == 'Page count':
				pageCount = row[1].value
			else:
				pass
		for i in range(pageCount):
			if pageNum + i in self._configDict:
				raise Exception('Page conflict.')
			else:
				pass
		lst[3] = pageNum + pageCount - 1
		for i in range(pageCount):
			self._configDict[pageNum + i] = name

	def __buttonAction_Load(self):
		try:
			self._loadConfigFile = ControlFileOpen(opened_file_type='json')
			self._loadConfigFile.click()
			if self._loadConfigFile.value != '':
				with open(self._loadConfigFile.value, 'r') as f:
					jstr = json.load(f)
					table = jstr['value']
					self._configDict.clear()
					for row in table:
						self.__helper_Add2Dict(row)
					self._configList.load_form(jstr, None)
			else:
				raise Exception('No file selected.')
			self._configTextArea.__add__('List loaded from ' + self._loadConfigFile.value)
		except Exception as err:
			self._configTextArea.__add__('\'Load\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Add(self):
		try:
			nameText = '__' + self._configCombo.text if self._configNameText.value == '' else self._configNameText.value
			lst = [self._configCombo.text, nameText, self._configPageNumber.value, 0]
			self.__helper_Add2Dict(lst)
			self._configList.__add__(lst)
			self._configList.resizecolumns = False
		except Exception as err:
			self._configTextArea.__add__('\'Add\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Del(self):
		try:
			if self._configList.selected_row_index is None:
				raise Exception('No row selected.')
			for i in range(int(self._configList.get_currentrow_value()[2]), int(self._configList.get_currentrow_value()[3]) + 1):
				del self._configDict[i]
			self._configList.__sub__(self._configList.selected_row_index)
		except Exception as err:
			self._configTextArea.__add__('\'Delete\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Clear(self):
		try:
			self._configDict.clear()
			self._configList.clear()
		except Exception as err:
			self._configTextArea.__add__('\'Clear\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Save(self):
		try:
			self._saveConfigFile = ControlFileSave(saved_file_type='json')
			self._saveConfigFile.click()
			if self._saveConfigFile.value != '':
				with open(self._saveConfigFile.value, 'w') as f:
					json.dump(self._configList.save_form({}, None), f)
			else:
				raise Exception('File not specified.')
			self._configTextArea.__add__('List saved to ' + self._saveConfigFile.value)
		except Exception as err:
			self._configTextArea.__add__('\'Save\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Gen(self):
		try:
			table = self._configList.value
			for i in range(len(table)):
				table[i][0] += '.txt'
			table.insert(0, ['Library', 'Loop Name', 'Start Page', 'End Page'])
			self._saveArgFile = ControlFileSave(saved_file_type='xlsx')
			self._saveArgFile.click()
			Config(table, self._saveArgFile.value)
			self._configTextArea.__add__('Arguments file is generated.')
			self._openArgFile.value = self._saveArgFile.value
		except Exception as err:
			self._configTextArea.__add__('\'Generate\' error: ' + repr(err))
			if self.debug:
				self._configTextArea.__add__(traceback.format_exc())

	def __buttonAction_Combine(self):
		try:
			self._saveDPUFile = ControlFileSave(saved_file_type='txt')
			self._saveDPUFile.click()
			Combine(self._openDBFile.value, self._saveDPUFile.value, self._openArgFile.value)
			self._combineTextArea.__add__('New DPU file is generated.')
		except Exception as err:
			self._combineTextArea.__add__('Error: ' + repr(err))
			if self.debug:
				self._combineTextArea.__add__(traceback.format_exc())

class LibMasterDebug(LibMaster):
	def __init__(self):
		super(LibMasterDebug, self).__init__('LibMaster - Debug')
		self.debug = True