#!/usr/bin/python

# -----------------------------------------------------------
# Test Generator for the IEC61131-3 Test library
#
# (C) 2017-2020 Hofer Florian, Bolzano, ITALY
# Released under GNU Public License (GPL)
# email info@florianhofer.it
# -----------------------------------------------------------

import xlrd
import os.path
import exp
import wbk

def generateConst ():
	"""Generate constant values for the test
	Generate values that represent test parameters and test size parameters
	to add to the test POU"""

	# Collector for the parametrized test values
	testvars = []
	seqlen = 0
	for s in steps:
		testvar = []
		for v in steps[s]:
			const = "( " + typeVar[0]['Name'] + " := " + str(int(steps[s][v][0]))
			for t in typeVar[1]:
				const += ", " + typeVar[1][t]['Name'] + " := " + str((steps[s][v][1][t]['Value']))
	
			for t in typeVar[2]:
				const += ", " + typeVar[2][t]['Name'] + " := " + str(steps[s][v][2][t]['Value'])
			const += " )"
				
			testvar.append(const)

		seqlen = max(seqlen, len(testvar))
		testvars.append(testvar)
	
	# Finally, return the constants for test function 
	constants = {0:{ 'Name': "NoOfTests",	'Type': "INT", 'Value' : len(testvars)}}
	constants[1] = { 'Name': "NoOfInputs",	'Type': "INT", 'Value' : seqlen}
	constants[2] = { 'Name': "TestVars",	'Type': "ARRAY [1..NoOfTests,1..NoOfInputs] OF Vars"+testName, 'Value' : testvars}
	#print constants

	return constants
	# fix len steps to len array

def generateVars():
	"""Generate -required- variable list to add to the test POU"""
	
	variables = {0:{ 'Name': instanceName,	'Type': fbName}}
	variables[1] = { 'Name': 'ptrVars', 	'Type': 'POINTER TO ' + testName + '_vars'}
	variables[2] = { 'Name': 'i', 			'Type': 'INT', 'Value' : "1"}
	
	return variables

"""
Main program

Read test workbook and generate test cases/import for the IEC61131-3
""" 

wb = xlrd.open_workbook(os.path.join('','test_unit.xlsx'))
wb.sheet_names()
sh = wb.sheet_by_index(0)

#Header information
testName = sh.cell(0,1).value
fbName = sh.cell(0,4).value
instanceName = sh.cell(0,6).value

scanPos = 0

testFile = exp.expWriter(testName=testName, fileName=testName)

# test file is open, create header and lets scan for data!e
testFile.createHeader()
	
while True:
	state = sh.cell(scanPos,0).value
	
	if state != "State":
		scanPos += 1
	else:
		break
	
# found header, scan for labels.
typeVar = wbk.getFunctionVars(sh.row_values(scanPos, 2))

scanPos += 1 # next line, start to scan

# build step dictionary
cnt = 0
steps = {}
print (scanPos)
#while sh.nrows > scanPos:
steps[cnt] = wbk.readSequence(sh, scanPos, typeVar)
print (scanPos)

testFile.writeConstatns(generateConst())
testFile.writeVariables(generateVars())
testFile.createStateMachine(instanceName, typeVar)
testFile.createFooter()
testFile.createTestDUT(typeVar)

testFile.close()
