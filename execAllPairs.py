#!C:/Python34/python.exe
import eventFileCreator
import os

def executePossiblities():
	eventFileCreator.flooding = 'E:/Typhon Test-bed/events.pl'
	eventFileCreator.conscientious = 'E:/MobileAgentPart/events.pl'
	eventFileCreator.totalNumNodes = 9
	eventFileCreator.availableSol = (('type2','a',5000),)
	eventFileCreator.pattern = (('i',),(8,'s'),(1,'p'))
	eventFileCreator.timeGaps = (0,4000,3000)
	eventFileCreator.originTime = 0
	eventFileCreator.reps = 5
	eventFileCreator.timeBwTwoFresh = 5000
	for numOfSol, numOfProb in genPairSolProb( 1, 1, 9 ):
		print( numOfSol, numOfProb)
		eventFileCreator.pattern = (('i',),(numOfSol,'s'),(numOfProb,'p'))
		# create the event file
		eventFileCreator.main()
		originalPath = os.getcwd()
		# execute flood
		os.chdir('E:/Typhon Test-bed')
		os.system('autom.bat')
		# execute cons
		os.chdir('E:/MobileAgentPart')
		os.system('autom.bat')
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
