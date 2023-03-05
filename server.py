import socket
import sys
import signal
import os
import threading

##############################################################################
# Creating a class of signals to process some errors
class Stopper:
    stop = False
    def __init__(self):
        signal.signal(signal.SIGQUIT, self.interrupt_handler)
        signal.signal(signal.SIGTERM, self.interrupt_handler)
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def interrupt_handler(self):
        self.stop = True


##############################################################################
# Procedure that makes the server send a "accio\r\n"
# ... receives a message, then send another "accio\r\n" command
# ... then after receiving the "confirm-accio-again\r\n\r\n" command
# ... from the client it the procedure reads in the file from the client
# ... bit by bit, returns the amount of bits
def proc(clientSock, save_path, num):
    # Getting two commands from the connection
    try:

        i = 0
        msg = b""
        error = b"ERROR"
        clientSock.send(b"accio\r\n")

        # Forming the path to the directory of which the file will be saved
        completeDir = save_path + "%d.file" % num

        # Creates the file for the given directory
        file = open(completeDir, "wb")

        # Setting the timeout of the client socket
        clientSock.settimeout(10)

        while i < 2:

            # Receives commands from the server bit by bit
            while True:
                m = clientSock.recv(1)

                msg += m

                if msg.find(b"\n") != -1:
                    break

                # Connection is closed by server
                # raise is here to construct the error for the handshake
                # ... if it does occur
                elif len(m) <= 0:
                    raise socket.error("Error : () Server did not receive any data.")

            # Checks if there was a command recorded
            if len(msg) > 0:

                if msg.find(b"confirm-accio\r\n") != -1:
                    i += 1
                    msg = b""
                    clientSock.send(b"accio\r\n")

                elif msg.find(b"confirm-accio-again\r\n\r\n") != -1:
                    i += 1
                    msg = b""

                # Continues to append to the mg string until
                # ... it matches the specified command
                elif len(msg) < len("confirm-accio\r\n") and i == 0:
                    continue

                elif len(msg) < len("confirm-accio-again\r\n\r\n") and i == 1:
                    continue

        # Reading the specified file
        if i == 2:

            # End while when TCP connection closes
            while True:
                m = clientSock.recv(BUFFER_SIZE)

                # Does not specify end of file, it specifies interruption
                # ... in getting the data from the client
                # Might be a better solution
                if len(m) <= 0:
                    file.close()
                    break

                # /n finder ???

                file.write(m)



        # Closes the connection after printing the total bits
        clientSock.close()

    except socket.error:
        file.close()
        file = open(completeDir, "wb")
        file.write(error)
        file.close()
        clientSock.close()





##############################################################################
# Setting up everything for the server to start listening
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Suppose to help with the buffer when receiving data from client
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1)

except socket.error:
    sys.stderr.write("ERROR: ()Socket not created")
    exit(1)

# Buffer size for file reading from client side
BUFFER_SIZE = 10000
port = int(sys.argv[1])
save_path = sys.argv[2]

try:
    sock.bind(("0.0.0.0", port))

except socket.error:
    sys.stderr.write("ERROR: ()Socket not created.")
    exit(1)

except ValueError:
    sys.stderr.write("ERROR: ()Port out of range.")
    exit(1)

except TypeError:
    sys.stderr.write("ERROR: ()Incorrect data type for port.")
    exit(1)

except socket.gaierror:
    sys.stderr.write("ERROR: ()Address associated to socket is incorrect.")
    exit(1)



# Buffers the connections, and "accept"
# ... takes each connection from the stored buffer
sock.listen(10)



##############################################################################
# This while loop keeps the socket and keeps connecting
# ... to different IP addresses until an error occurs
# This should handle threading the connections in parallel
i = 1
stopping = Stopper()

# manage timeout for client_sock

while not stopping.stop:

        clientSock, addr = sock.accept()
        client_thread = threading.Thread(target=proc, args=(clientSock, save_path, i))
        client_thread.start()

        # Updates the number ordering of the threading and files being
        # ... saved into the directory
        i += 1


# End connection after using socket
sock.close()
