import csv
import itertools

def retRow( filehandle, number ):
	var = filehandle.tell()
	filehandle.seek(0)
	#Edge cases like neg lin_num or > file_size: handle later
	row = next(itertools.islice(csv.reader(filehandle), number, number+1))
	filehandle.seek(var)
	return row

filehand = open('data.csv', 'r' )
csvhand = csv.reader( filehand )
#for i in range( 1, 25 ):
row = retRow( filehand, 14 )
print( row[2] )
print( filehand.readline() )
row = retRow( filehand, 2 )
print( row[2] )
print( filehand.readline() )
row = retRow( filehand, 21 )
print( row[2] )
print( filehand.readline() )
row = retRow( filehand, 8 )
print( row[2] )
print( filehand.readline() )
