###############################################################################
'''
AUTHOR:			Yao Ji (jiyao94@126.com)
CREATED DATE:	2018/7/23
LAST UPDATE:	2018/7/25
DESCRIPTION:	Main program to start UI.
'''
###############################################################################
import pyforms, argparse
from UI import LibMaster, LibMasterDebug

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='Turn on debug mode.', action='store_true')
args = parser.parse_args()

if args.debug:
	pyforms.start_app(LibMasterDebug)
else:
	pyforms.start_app(LibMaster)