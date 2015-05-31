#!C:/Python34/python.exe
import eventFileCreator
import os
import logFileParser as lf
import csv
import re

def fun( path ):
	filename = os.path.basename( path )
	filename = os.path.splitext( filename )[0]
	matchObj = re.match('([fc])([a-z])t(\d+)n(\d+)s(\d+)p', filename )
	if matchObj.group(1) == 'f' :
		typ = 'FloodRun'
	elif matchObj.group(1) == 'c' :
		typ = 'ConsRun'
	else :
		print('Something wrong in filename type')
	return [ matchObj.group(1), matchObj.group(2), 't', matchObj.group(3), 'n',
		matchObj.group(4), 's', matchObj.group(5), 'p' ], typ

def processCsv():
	# read from recentlog
	with open( 'E:/ResourcesAndOutpForThesis/UsefulScriptsThesis/recentlog.txt', 'r' ) as f :
		toBeProcessed = f.readline()
	# find out what kind of log it is
	astring, typ = fun( toBeProcessed )
	# process it
	ana = lf.Analysis(lf.SheetReader( toBeProcessed ), typ )
	astring.append(str(ana.avgOfAvgOfWaitTimes()))
	astring.append(str(ana.avgOfOvAllUsefulComps()))
	astring.append(str(ana.avgOfOvallUsefulCommun()))
	ana.cleanup()
	# write in ....
	with open( 'E:/ResourcesAndOutpForThesis/UsefulScriptsThesis/filename.csv', 'a', newline='' ) as f:
		wri = csv.writer(f)
		wri.writerow(astring)

def executePossiblities():
	eventFileCreator.flooding = 'E:/Typhon Test-bed/events.pl'
	eventFileCreator.conscientious = 'E:/MobileAgentPart/events.pl'
	eventFileCreator.totalNumNodes = 16
	eventFileCreator.topology = 'g'
	eventFileCreator.availableSol = (('type2','a',5000),)
	eventFileCreator.pattern = (('i',),(8,'s'),(1,'p'))
	eventFileCreator.timeGaps = (0,4000,3000)
	eventFileCreator.originTime = 0
	eventFileCreator.reps = 5
	eventFileCreator.timeBwTwoFresh = 10000
	for numOfSol, numOfProb in genPairSolProb( 8, 4, 16 ):
		print( numOfSol, numOfProb)
		eventFileCreator.pattern = (('i',),(numOfSol,'s'),(numOfProb,'p'))
		# create the event file
		eventFileCreator.main()
		originalPath = os.getcwd()
		# execute flood
		os.chdir('E:/Typhon Test-bed')
		os.system('autom.bat')
		processCsv()
		# execute cons
		os.chdir('E:/MobileAgentPart')
		os.system('autom.bat')
		processCsv()
		os.chdir( originalPath )

# genPairSolProb is a generator which generate the different pairs from
# starting number of solution and problem nodes to end such that sum of sol nodes
# and prob nodes does not exceed totalNum. The generator assumes solNodeStart and/or
# probNodeStart are greater than zero. You can also set maximum number of problem node
# and solution node possible.
def genPairSolProb( solNodeStart, probNodeStart, totalNum,
			maxProb=float('inf'), maxSol=float('inf')):
	if solNodeStart > maxSol :
		return
	for numOfProb in range( probNodeStart, totalNum - solNodeStart + 1 ):
		if numOfProb > maxProb :
			break
		yield( solNodeStart, numOfProb )

	for numOfSol in range( solNodeStart + 1, totalNum ):
		if numOfSol > maxSol :
			break
		for numOfProb in range( 1, totalNum - numOfSol + 1 ):
			if numOfProb > maxProb :
				break
			yield( numOfSol, numOfProb )

if __name__ == '__main__': executePossiblities()
