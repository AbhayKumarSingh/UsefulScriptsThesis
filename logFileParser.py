#!C:/Python34/python.exe
import csv
import itertools
from statistics import mean

class SheetReader:
	def __init__( self, filename ):
		self.filehandle = open( filename, 'r' )
		self.csvhandle = csv.reader(self.filehandle)
		count = 0
		lis = []
		byteTotal = 0
		for row in self.filehandle:
			lis.append( byteTotal )
			count = count + 1
			byteTotal = byteTotal + len(row) + 1
		self.totalNumRows = count
		self.lineNoByteList = lis
		self.filehandle.seek(0)
		#self.totalNumRows = sum( 1 for row in csv.reader(self.filehandle) )

	def genStringRowIndicesInRange( self, string, col, start, endEx ):
		for i in range(start,endEx):
			if self.retCell(i,col) == string :
				yield i, self.retRow(i)

	def retRow( self, number ):
		var = self.filehandle.tell()
		byteNum = self.lineNoByteList[number]
		self.filehandle.seek(byteNum)
		#Edge cases like neg lin_num or > file_size: handle later
		row = next(itertools.islice( self.csvhandle, 0, 1))
		self.filehandle.seek(var)
		return row

	def retCell( self, rownum, colnum ):
		row = self.retRow( rownum )
		return row[colnum]

	def cleanup( self ):
		self.filehandle.close()

class CommonValStrings:
	eventCol = 4
	timeCol = 2
	initializedString = 'Initialized values'
	intranodeCalculationString = 'Intranode Calculation'
	packetSentFromString = 'Packet sent from'
	problemStartedAtString = 'Problem started at'
	foundSolutionAtString = 'Solution found for'
	receivedSolutionAtString = 'Solution received at'

class Run:
	coStr = CommonValStrings()
	def __init__(self, sheetH, first, lastEx):
		self.sheet = sheetH
		self.firstRow = first
		self.lastRowEx = lastEx

	# genWaitingTimesInRun fun has to be tested for different types of prob
	# is not tested till now
	def genWaitingTimesInRun( self,
			nodeCol = 5,
			proStartTypeCol = 6,
			solReceiTypeCol = 8 ):
		# For each of the prob nodes in the list (gen)
		for probRowIndex, probRow in self.sheet.genStringRowIndicesInRange(
				self.coStr.problemStartedAtString,
				self.coStr.eventCol,
				self.firstRow, self.lastRowEx ):
			# search the solution received row after the row prob started
			for solRowIndex, solRow in self.sheet.genStringRowIndicesInRange(
					self.coStr.receivedSolutionAtString,
					self.coStr.eventCol,
					probRowIndex + 1, self.lastRowEx):
				if (solRow[nodeCol] == probRow[nodeCol]
				and solRow[solReceiTypeCol] == probRow[proStartTypeCol]) :
					actualSol = solRow
					break;
			# get the diff in time
			waitingTime = float(actualSol[self.coStr.timeCol]) - float(probRow[self.coStr.timeCol])
			yield probRow[nodeCol], waitingTime
			# append (create) a list of this diff along with nodes

	# averageWaitingTimeOfRun may not be that usefull as a parameter
	def averageWaitingTimeOfRun( self ):
		# The following implementation can be improved from memory point of view
		return mean(waitTime for ignore, waitTime in self.genWaitingTimesInRun())

	def overallIntraNodeCompInRun( self ):
		return sum(
			1
			for ignored1, ignored2
			in self.sheet.genStringRowIndicesInRange(
				self.coStr.intranodeCalculationString,
				self.coStr.eventCol,
				self.firstRow, self.lastRowEx
			)
		)

	def overallUsefulIntraNodeCompInRun( self ):
		# May be to be overridden by subclasses
		# In case of flooding it is like calling overallIntraNodeCompInRun
		pass

	def overallInterNodeCommInRun( self ):
		return sum(
			1
			for ignored1, ignored2
			in self.sheet.genStringRowIndicesInRange(
				self.coStr.packetSentFromString,
				self.coStr.eventCol,
				self.firstRow, self.lastRowEx
			)
		)

	def overallUsefulInterNodeCommInRun( self ):
		# May be to be overridden by subclasses
		# In case of flooding it is like calling overallInterNodeCommInRun
		pass

class Analysis:
	coStr = CommonValStrings()
	def __init__( self, sheetReader ):
		self.sheet = sheetReader
		self.runList = self.runRanges()	#when in consistent state each element will have component firstRow and lastRowEx

	def printRunList( self ):
		for run in self.runList:
			print( run.firstRow, run.lastRowEx )

	def listInitRowIndices( self ):
		#scan throughout the file and find times and index of init
		#Note that the range is from 1 since 0th line is not of much use
		return [
			i
			for i, ignore
			in self.sheet.genStringRowIndicesInRange(
				self.coStr.initializedString,
				self.coStr.eventCol,
				1, self.sheet.totalNumRows
			)
		]

	def lastRunLastLimit( self ):
		#It may be required to change the following code for mobile agent case
		#There is a possibility of this being an attribute
		return self.sheet.totalNumRows

	def runRanges( self ):
		#first find the init points
		lis = self.listInitRowIndices()
		templis = []
		#get the indexes between each init points take note of endcase
		for i in range(len(lis)):
			start = lis[i] + 1
			endEx = lis[i+1] if i < len(lis) - 1 else self.lastRunLastLimit()
			#create objects or dictionary and append in list member
			templis.append( Run( self.sheet, start, endEx ) )
		return templis

	def cleanup( self ):
		# Even though setting runList to None does not do much to avoid
		# illegal access of Run objects
		self.runList = None
		self.sheet.cleanup()

def main():
	floana = Analysis(SheetReader( 'data.csv' ))
	# floana.printRunList()
	# floana.printRunList()
	# for tup in floana.runList[0].genWaitingTimesInRun() :
	# 	print( tup )
	# print( floana.runList[0].averageWaitingTimeOfRun())
	print( floana.runList[0].overallInterNodeCommInRun())
	floana.cleanup()

def main2():
	sheet = SheetReader('data.csv')
	print( sheet.totalNumRows )
	#print( sheet.lineNoByteList )
	#print( sheet.retRow(5300) )
	print( sheet.retCell(5300,-4) )
	sheet.cleanup()

if __name__ == '__main__' : main()
