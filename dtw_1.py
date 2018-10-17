"""DTW example"""

import math
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import socket


def initSocket():
    """Initialize the tcp/ip socket"""
    host = "127.0.0.1"
    port = 5000

    mySocket = socket.socket()
    mySocket.bind((host,port))

    mySocket.listen(1)
    global conn
    conn, addr = mySocket.accept()
    print ("Connection from established: " + str(addr))

def localDistance(templateFrame, testFrame):
    """Compute the Euclidian distance between two feature 'vectors'"""

    assert type(templateFrame) == type(testFrame) == float

    return math.sqrt(pow(templateFrame - testFrame, 2))

def prettyPrintingArray(a):
    """Print an array with nice line wrapping"""

    for i in range(len(a)):
        for j in range(len(a[i])):
            print(a[i][j], end='')
        print("|")


def dtw(template, test):

    # A data structure to hold the shortest "global distance so far"
    # this is an array (implemented as a list of lists)
    globalDistance = []
    initialValue = -1
    for i in range(len(template)):
        thisRow = []
        for j in range(len(test)):
            thisRow.append(initialValue)
        globalDistance.append(thisRow)

#    print ("Initialized global distance")
#    prettyPrintingArray(globalDistance)

    # second matrix (list of lists) to track the shortest path. Its going to hold the coordinates of the previous point
    backpointer = []
    initialBackpointer = (None, None)
    for i in range(len(template)):
        thisRow = []
        for j in range(len(test)):
            thisRow.append(initialBackpointer)
        backpointer.append(thisRow)
#    print("initialized backpointer:")
#    prettyPrintingArray(backpointer)

    # visit every position in the global distance matrix in order
    for i in range(len(template)):
        for j in range(len(test)):

            # deal with the edge cases first
            # Starting point: total distance is the local distance because there are no other incoming paths
            if (i==0) and (j==0):
                globalDistance[i][j] = localDistance(template[i], test[j])
                backpointer[i][j] = (None, None)

            # incoming path comes from one direction when i=0
            elif (i==0):
                # check if previous position has been visited
                assert globalDistance[i][j-1] >= 0

                globalDistance[i][j] = globalDistance[i][j-1] + localDistance(template[i], test[j])
                backpointer[i][j] = (i, j-1)

            # incoming path comes from one direction when j=0
            elif (j==0):
                # check if previous position has been visited
                assert globalDistance[i-1][j] >= 0

                globalDistance[i][j] = globalDistance[i-1][j] + localDistance(template[i], test[j])
                backpointer[i][j] = (i-1, j)

            # the general case where paths come from three directions
            else:
                # check if previous positions has been visited
                assert globalDistance[i][j-1]   >= 0
                assert globalDistance[i-1][j]   >= 0
                assert globalDistance[i-1][j-1] >= 0

                lowestGlobalDistance = globalDistance[i-1][j]
                backpointer[i][j] = (i-1, j)

                if globalDistance[i][j-1] < lowestGlobalDistance:
                    lowestGlobalDistance = globalDistance[i][j-1]
                    backpointer[i][j] = (i, j-1)

                if globalDistance[i-1][j-1] < lowestGlobalDistance:
                    lowestGlobalDistance = globalDistance[i-1][j-1]
                    backpointer[i][j] = (i-1, j-1)

                globalDistance[i][j] = lowestGlobalDistance + localDistance(template[i], test[j])

    # the best global distance is just the value in the "last" corner of the matrix
    D = globalDistance[len(template)-1][len(test)-1]

    # now do the backtrace
    alignment=[]

    # start at the end - the last frame of the template aligns with the last frame of the test signal
    i,j = len(template)-1 , len(test)-1
    alignment.append( (i,j) )

    while ( (i!=0) or (j!=0) ):
        alignment.append(backpointer[i][j])
        i,j = backpointer[i][j]               # Knackpunkt(!): i,j momentaner punkt; backpointer[i][j] späterer punkt

    alignment.reverse()

    return D, alignment

def main():
    initSocket()

    template = [0.00079342884228238400, -0.64797733408535600000, 7.51569652570030000000, 8.13736043805227000000, -0.65270681519082600000, 6.78654697206245000000, 8.05186411919532000000, -1.50192128219591000000]

    print("Getting data.....")
    receiving = True

    fig = plt.gcf()
    fig.show()
    fig.canvas.draw()


    while receiving:
        data=[]
        for i in range(8):
            dataRec = conn.recv(1024).decode()

            if str(dataRec) == "END":
                receiving = False
                print("All data received!", str(dataRec))
                break

            elif not dataRec:
                print("Couldn't receive data!")
                conn.send("0".encode())

            else:
                data.append(float(dataRec))
                conn.send("1".encode())

        if receiving == True:
            D, alignment = dtw(template, data)

            if D < 12:
                plt.plot(data, 'r-', linewidth = 5)
            else:
                plt.plot(data, 'm-')

            plt.plot(template)
            plt.title("Distance from template to test: " + str(D))


            fig.canvas.draw()
            fig.clear()


    conn.close()



if __name__ == "__main__":
    main()
