import socket
import csv

def initSocket():
    host = '127.0.0.1'
    port = 5000

    global mySocket
    mySocket = socket.socket()
    mySocket.connect((host,port))

def Main():

    initSocket()
    d = []
    with open("data.csv") as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if row:
                d.append(row)
    print (d[0][0])


    for i in range(5):
        for j in range(len(d[i])-8):
            for k in range(j, j+8):

                mySocket.send(str(d[i][k]).encode())
                print("Sending:" + str(d[i][k]))

                answer = mySocket.recv(1024).decode()
                print("answer:" + str(answer))

    mySocket.send("END".encode())

    mySocket.close()

if __name__ == '__main__':
    Main()
