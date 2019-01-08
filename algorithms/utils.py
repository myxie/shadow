
from csv import reader

def read_matrix(matrix):
    lmatrix = []
    f = open(matrix)
    next(f)
    csv_reader = reader(f)
    for row in csv_reader:
        lmatrix.append(list(map(int,row)))
    f.close()
    return lmatrix 
