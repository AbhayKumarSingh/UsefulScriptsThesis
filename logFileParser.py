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

class FloodAnalysis:
	eventCol = 4
	timeCol = 2
	initializedString = 'Initialized values'
	intranodeCalculationString = 'Intranode Calculation'
	packetSentFromString = 'Packet sent from'
	problemStartedAtString = 'Problem started at'
	foundSolutionAtString = 'Solution found for'
	receivedSolutionAtString = 'Solution received at'

	def __init__( self, sheetReader ):
		self.sheet = sheetReader
		self.runList = self.runRanges()	#when in consistent state each element will have component firstRow and lastRowEx

	# genWaitingTimesInRun fun has to be tested for different types of prob
	# is not tested till now
	def genWaitingTimesInRun( self, run,
			nodeCol = 5,
			proStartTypeCol = 6,
			solReceiTypeCol = 8 ):
		# For each of the prob nodes in the list (gen)
		for probRowIndex, probRow in self.sheet.genStringRowIndicesInRange(
				self.problemStartedAtString,
				self.eventCol,
				run['firstRow'], run['lastRowEx'] ):
			# search the solution received row after the row prob started
			for solRowIndex, solRow in self.sheet.genStringRowIndicesInRange(
					self.receivedSolutionAtString,
					self.eventCol,
					probRowIndex + 1, run['lastRowEx']):
				if (solRow[nodeCol] == probRow[nodeCol]
				and solRow[solReceiTypeCol] == probRow[proStartTypeCol]) :
					actualSol = solRow
					break;
			# get the diff in time
			waitingTime = float(actualSol[self.timeCol]) - float(probRow[self.timeCol])
			yield probRow[nodeCol], waitingTime
			# append (create) a list of this diff along with nodes

	# averageWaitingTimeOfRun may not be that usefull as a parameter
	def averageWaitingTimeOfRun( self, run ):
		# The following implementation can be improved from memory point of view
		return mean(waitTime for ignore, waitTime in self.genWaitingTimesInRun( run ))

	def printRunList( self ):
		for run in self.runList:
			print( run['firstRow'], run['lastRowEx'] )

	def listInitRowIndices( self ):
		#scan throughout the file and find times and index of init
		#Note that the range is from 1 since 0th line is not of much use
		# return [i for i in range(1,self.sheet.totalNumRows) if self.sheet.retCell(i,self.eventCol) == self.initializedString]
		return [
			i
			for i, ignore
			in self.sheet.genStringRowIndicesInRange(
				self.initializedString,
				self.eventCol,
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
			templis.append( dict( firstRow = start, lastRowEx = endEx ) )
		return templis

	def cleanup( self ):
		self.sheet.cleanup()

def main():
	floana = FloodAnalysis(SheetReader( 'data.csv' ))
	# floana.printRunList()
	for tup in floana.genWaitingTimesInRun(floana.runList[0]) :
		print( tup )
	print( floana.averageWaitingTimeOfRun(floana.runList[0]))
	floana.cleanup()

def main2():
	sheet = SheetReader('data.csv')
	print( sheet.totalNumRows )
	#print( sheet.lineNoByteList )
	#print( sheet.retRow(5300) )
	print( sheet.retCell(5300,-4) )
	sheet.cleanup()

if __name__ == '__main__' : main()
