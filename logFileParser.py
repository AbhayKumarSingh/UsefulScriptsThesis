#!C:/Python34/python.exe
import csv
import os
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
	eoEString = 'End of Experiment'

class Run:
	coStr = CommonValStrings()
	def __init__(self, sheetH, first, lastEx):
		self.sheet = sheetH
		self.firstRow = first
		self.lastRowEx = lastEx

	@staticmethod
	def factory( sheet, first, lastEx, typ ):
		if typ == 'FloodRun': return FloodRun(sheet, first, lastEx)
		if typ == 'ConsRun': return ConsRun(sheet, first, lastEx)
		print( 'something wrong in Run factory' )

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
			solFound = False
			for solRowIndex, solRow in self.sheet.genStringRowIndicesInRange(
					self.coStr.receivedSolutionAtString,
					self.coStr.eventCol,
					probRowIndex + 1, self.lastRowEx):
				if (solRow[nodeCol] == probRow[nodeCol]
				and solRow[solReceiTypeCol] == probRow[proStartTypeCol]) :
					actualSol = solRow
					solFound = True
					break;
			# get the diff in time
			if solFound == True:
				waitingTime = float(actualSol[self.coStr.timeCol]) - float(probRow[self.coStr.timeCol])
				yield probRow[nodeCol], waitingTime
			# append (create) a list of this diff along with nodes

	# averageWaitingTimeOfRun may not be that useful as a parameter
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
		return self.overallIntraNodeCompInRun()

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
		return self.overallInterNodeCommInRun()

class FloodRun( Run ):
	pass

class ConsRun( Run ):
	pass

class Analysis:
	coStr = CommonValStrings()
	def __init__( self, sheetReader, tpe ):
		self.sheet = sheetReader
		self.typ = tpe
		self.runList = self.runRanges()	#when in consistent state each element will have component firstRow and lastRowEx

	def printRunList( self ):
		for run in self.runList:
			print( run.firstRow, run.lastRowEx )

	def avgOfAvgOfWaitTimes( self ):
		return mean(aRun.averageWaitingTimeOfRun() for aRun in self.runList)

	def notAvgOfAvgOfWaitTimes( self ):
		pass

	def avgOfOvAllUsefulComps( self ):
		return mean(aRun.overallUsefulIntraNodeCompInRun() for aRun in self.runList)

	def avgOfOvallUsefulCommun( self ):
		return mean(aRun.overallUsefulInterNodeCommInRun() for aRun in self.runList)

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
		for i, ignore in self.sheet.genStringRowIndicesInRange(
				self.coStr.eoEString,
				self.coStr.eventCol,
				1, self.sheet.totalNumRows ):
			return i

	def runRanges( self ):
		#first find the init points
		lis = self.listInitRowIndices()
		templis = []
		#get the indexes between each init points take note of endcase
		for i in range(len(lis)):
			start = lis[i] + 1
			endEx = lis[i+1] if i < len(lis) - 1 else self.lastRunLastLimit()
			#create objects or dictionary and append in list member
			templis.append( Run.factory( self.sheet, start, endEx, self.typ ) )
		return templis

	def cleanup( self ):
		# Even though setting runList to None does not do much to avoid
		# illegal access of Run objects
		self.runList = None
		self.sheet.cleanup()

def filePathAndTypeBuilder():
	yield ('inp/data1.csv','FloodRun'), ('inp/mdata1.csv','ConsRun')
	yield ('inp/data2.csv','FloodRun'), ('inp/mdata2.csv','ConsRun')
	yield ('inp/data3.csv','FloodRun'), ('inp/mdata3.csv','ConsRun')
	yield ('inp/data4.csv','FloodRun'), ('inp/mdata4.csv','ConsRun')
	yield ('inp/data5.csv','FloodRun'), ('inp/mdata5.csv','ConsRun')
	yield ('inp/data6.csv','FloodRun'), ('inp/mdata6.csv','ConsRun')
	yield ('inp/data7.csv','FloodRun'), ('inp/mdata7.csv','ConsRun')
	yield ('inp/data8.csv','FloodRun'), ('inp/mdata8.csv','ConsRun')
	yield ('inp/data9.csv','FloodRun'), ('inp/mdata9.csv','ConsRun')
	yield ('inp/data10.csv','FloodRun'), ('inp/mdata10.csv','ConsRun')
	yield ('inp/data11.csv','FloodRun'), ('inp/mdata11.csv','ConsRun')
	yield ('inp/data12.csv','FloodRun'), ('inp/mdata12.csv','ConsRun')
	yield ('inp/data13.csv','FloodRun'), ('inp/mdata13.csv','ConsRun')
	yield ('inp/data14.csv','FloodRun'), ('inp/mdata14.csv','ConsRun')
	yield ('inp/data15.csv','FloodRun'), ('inp/mdata15.csv','ConsRun')
	yield ('inp/data16.csv','FloodRun'), ('inp/mdata16.csv','ConsRun')
	yield ('inp/data17.csv','FloodRun'), ('inp/mdata17.csv','ConsRun')
	yield ('inp/data18.csv','FloodRun'), ('inp/mdata18.csv','ConsRun')
	yield ('inp/data19.csv','FloodRun'), ('inp/mdata19.csv','ConsRun')
	yield ('inp/data20.csv','FloodRun'), ('inp/mdata20.csv','ConsRun')

def printlist( lis ):
	for i in lis:
		print( i )

def writeInCsv( filename, rows ):
	with open( filename, 'w', newline='' ) as f:
		wri = csv.writer(f)
		wri.writerows(rows)

def main():
	outputDir = 'out/out5'
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)
	waitListForGraph = []
	CompsListForGraph = []
	CommunListForGraph = []
	for compr in filePathAndTypeBuilder():
		waitTimeCompr = []
		avgCompsCompr = []
		avgCommunCompr = []
		for alog in compr:
			ana = Analysis(SheetReader( alog[0] ), alog[1] )
			waitTimeCompr.append(ana.avgOfAvgOfWaitTimes())
			avgCompsCompr.append(ana.avgOfOvAllUsefulComps())
			avgCommunCompr.append(ana.avgOfOvallUsefulCommun())
			ana.cleanup()
		waitListForGraph.append(waitTimeCompr)
		CompsListForGraph.append(avgCompsCompr)
		CommunListForGraph.append(avgCommunCompr)
	print('waitListForGraph')
	writeInCsv( outputDir + '/waitlist.csv', waitListForGraph )
	print('CompsListForGraph')
	writeInCsv( outputDir + '/comput.csv', CompsListForGraph )
	print('CommunListForGraph')
	writeInCsv( outputDir + '/communi.csv', CommunListForGraph )

def test():
	floana = Analysis(SheetReader( 'data.csv' ), 'FloodRun')
	# floana.printRunList()
	# floana.printRunList()
	# for tup in floana.runList[0].genWaitingTimesInRun() :
	# 	print( tup )
	# print( floana.runList[0].averageWaitingTimeOfRun())
	# print( floana.runList[0].overallInterNodeCommInRun())
	# print( floana.avgOfAvgOfWaitTimes())
	print( floana.avgOfOvAllUsefulComps())
	print( floana.avgOfOvallUsefulCommun())
	floana.cleanup()

if __name__ == '__main__' : main()
