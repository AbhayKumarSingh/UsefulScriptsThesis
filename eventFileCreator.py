#!C:/Python34/python.exe
import os
import random

# flooding = '../test/event1.pl'
# conscientious = '../test/event2.pl'
# totalNumNodes = 25
# topology = 'g'
# # The following generally variables represent from the point of flooding. Conscientious must be done accordingly.
# availableSol = (('type2','a',30),('type3','b',30))
# # In case of 's' and 'p' below the preceding numbers denotes number of 's' or 'p' for each type in order
# pattern = (('i',),(3,2,'s'),(3,2,'p'))
# timeGaps = (0,4000,1000)
# originTime = 0
# reps = 3
# timeBwTwoFresh = 10000

flooding = 'E:/Typhon Test-bed/events.pl'
conscientious = 'E:/MobileAgentPart/events.pl'
totalNumNodes = 36
topology = 'g'
availableSol = (('type2','a',5000),)
pattern = (('i',),(1,'s'),(15,'p'))
timeGaps = (0,4000,3000)
originTime = 0
reps = 5
timeBwTwoFresh = 20000

class WriteInFile:
	randomList = None
	def __init__(self, pathvalue ):
		if not os.path.exists(os.path.dirname(pathvalue)):
			os.makedirs(os.path.dirname(pathvalue))
		self.fileHandle = open( pathvalue, 'w' )

	@classmethod
	def createRandomList(cls):
		# the following logic is very specific to the situation at the timeof writing
		# This may need modification to generalize situation
		lis = []
		timeAccum = originTime
		shuffledlist = list(range( 0, totalNumNodes ))
		for i in range(reps) :
			random.shuffle( shuffledlist )
			numOfSolNode = sum(pattern[1][:-1])
			numOfProbNode = sum(pattern[2][:-1])
			for index in range( len(timeGaps) ) :
				innerlis = []
				if index == 0:
					pass
				elif index == 1:
					innerlis = innerlis + shuffledlist[:numOfSolNode]
				elif index == 2:
					innerlis = innerlis + shuffledlist[ numOfSolNode : numOfSolNode + numOfProbNode ]
				else:
					print( 'some problem' )
				timeAccum = timeAccum + timeGaps[index]
				if timeAccum != 0 :
					innerlis.append( timeAccum )
				else:
					innerlis.append( 1 )
				lis.append( innerlis )
			timeAccum = timeAccum + timeBwTwoFresh
		cls.randomList = lis

	def writeEventFiles( self ):
		stringToWritten = ''
		stringToWritten += ':-dynamic prevInst/1.\n' +\
		':-dynamic thingstobedone/1.\n' +\
		':-dynamic pos/1.\n' +\
		'outputFileName(' + self.csvFileName() + ').\n' +\
		self.mySolPart() +\
		'events(\n\t[\n' +\
		self.eventsAtInstances() +\
		'\t]\n).\n'
		self.fileHandle.write( stringToWritten )

	# Currently (20May15) csvFileName handles homogeneous case
	def csvFileName( self ):
		astring = ''
		astring += self.idchar() + topology +\
		't' + str( totalNumNodes ) + 'n' +\
		str( pattern[1][0] ) + 's' +\
		str( pattern[2][0] ) + 'p'
		return astring


	# this fun removes last comma. This is different from trailing comma
	def removeLastComma( self, aString ):
		lastCommaIndex = aString.rfind(',')
		if lastCommaIndex != -1 :
			return (aString[:lastCommaIndex] + aString[lastCommaIndex + 1:])
		return aString

	def toBeDoneInInst(self, event, numOfTimes, nodeList, instant ):
		strcomp = ''
		strcomp += '\t\t(\n' +\
		'\t\t\t' + str(instant) + ',\n' +\
		'\t\t\t[\n' + \
		self.template( event, numOfTimes, nodeList ) +\
		'\t\t\t]\n' + \
		'\t\t),\n'
		return strcomp

	def template( self, event, numOfTimes, nodeList ) :
		innerString = ''
		accum = 0
		if event == 'init' :
			return '\t\t\t\t( init, a, b, fun )\n'
		if event == 'end' :
			return '\t\t\t\t( end, a, b, fun )\n'
		for issueType, times in enumerate(numOfTimes) :
			for i in range(times) :
				innerString += '\t\t\t\t(' + \
				event +', n' + str(nodeList[accum + i]) +\
				', ' + availableSol[issueType][0] +\
				', ' + self.getDataToAttach( event, issueType ) + '),\n'
			accum = accum + times
		# in future remove extra commas after the last tuple in python code
		return (self.removeLastComma( innerString ))

	def eventsAtInstances(self):
		strcomp = ''
		for index, time in enumerate(self.randomList) :
			nodeList = time[:-1]
			instant = time[-1]
			modedIndex = index % len(pattern)
			signature = pattern[modedIndex][-1]
			numOfTimes = pattern[modedIndex][:-1]
			# In the function calls to handlers below think of
			# better parameter than index
			if signature == 'i' :
				strcomp += self.handleInit( index, instant )
			elif signature == 's' :
				strcomp += self.handleSol( index, numOfTimes, nodeList, instant )
			elif signature == 'p' :
				strcomp += self.handleProb( index, numOfTimes, nodeList, instant )
			else :
				print( 'not valid signature' )
		strcomp += self.toBeDoneInInst( 'end', 'notImp', 'notImp', instant + timeBwTwoFresh )
		return (self.removeLastComma( strcomp ))

	def mySolPart( self ):
		return ''

	def prepPacket( self, sol ):
		stringToWritten = ''
		for rep in range(sol[2]):
			stringToWritten += sol[1]
		return stringToWritten

	def handleProb(self, index, numOfTimes, nodeList, instant ):
		return self.toBeDoneInInst( 'prob', numOfTimes, nodeList, instant )

	def handleInit(self, index, instant ):
		# In the following function call only the init is important
		# Other arguments are useless
		return self.toBeDoneInInst( 'init', 0, 0, instant )

	def cleanup( self ):
		self.fileHandle.close()

class FloodFile( WriteInFile ):
	def idchar( self ):
		return 'f'

	def mySolPart( self ):
		stringToWritten = ''
		for sol in availableSol:
			stringToWritten += 'mysol( ' + sol[0] + ', ' +\
			self.prepPacket( sol ) + ').\n'
		return stringToWritten

	def getDataToAttach( self, event, issueType ):
		if event == 'sol':
			return 'dontcare'
		elif event == 'prob':
			return '-1'
		else:
			print( 'something wrong in getDataToAttach' )

	def handleSol(self, index, numOfTimes, nodeList, instant ):
		return self.toBeDoneInInst( 'sol', numOfTimes, nodeList, instant )

class ConsFile( WriteInFile ):
	def idchar( self ):
		return 'c'

	def getDataToAttach( self, event, issueType ):
		if event == 'startagent':
			return self.prepPacket( availableSol[issueType] )
		elif event == 'prob':
			return '-1'
		else:
			print( 'something wrong in getDataToAttach' )

	def handleSol(self, index, numOfTimes, nodeList, instant ):
		if index == 1 :
			return self.toBeDoneInInst( 'startagent', numOfTimes, nodeList, instant )
		else :
			return ''

def main():
	# create folders if it does not exists
	WriteInFile.createRandomList()
	floodOutFile = FloodFile( flooding )
	consOutFile = ConsFile( conscientious )
	floodOutFile.writeEventFiles()
	consOutFile.writeEventFiles()
	floodOutFile.cleanup()
	consOutFile.cleanup()

def test():
	a = ('type2', 'a', 15 )
	var = WriteInFile('../test/event1.pl')
	print( var.prepPacket(a))

if __name__ == '__main__': main()
