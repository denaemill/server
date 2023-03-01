import socket
import sys

BUFFER_SIZE = 10000

##############################################################################
#Getting all of the inputs from the command line
host = sys.argv[1]
port = sys.argv[2]
file = sys.argv[3]

def client_proc(sock):

    # Getting two commands from the connection
    try:
        i = 0
        msg = b""
        while i < 2:

            # Recieves commands from the server bit by bit
            while True:

                m = sock.recv(1)

                msg += m

                if msg.find(b"\n") != -1:
                    break

                # Connection is closed by server
                elif len(m) <= 0:
                    break

            # Checks if there was a command recorded
            if len(msg) > 0:

                if msg.find(b"accio\r\n") != -1:

                    if i == 0:
                        i += 1
                        msg = b""
                        sock.send(b"confirm-accio\r\n")

                    elif i == 1:
                        i += 1
                        msg = b""
                        sock.send(b"confirm-accio-again\r\n\r\n")

                # Continues to append to the mg string until
                # ... it matches the specified command
                elif len(msg) < len("accio\r\n"):
                    continue

        # Transfer the specified file
        if i == 2:

            # Opens file in binary
            with open(file, "rb") as f:

                while True:
                    fileIn = f.read(BUFFER_SIZE)

                    if not fileIn:
                        break

                    sock.send(fileIn)

        # Ending the program
        sock.close()

    except socket.error:
        sys.stderr.write("ERROR: ()Connection is no longer available.")
        exit(1)



##############################################################################
#Establishing the connection from the client
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

except socket.error:
    sys.stderr.write("ERROR: ()Socket not created")
    exit(1)

try:
    sock.settimeout(10)  # Setting timeouts for the code
    port = int(port)
    if port < 0 and port > 65535:

        sys.stderr.write("ERROR: (Traceback (most recent call last):File /autograder/submission/client.py")
        exit(1)

    else:

        sock.connect((host, port))

except socket.gaierror:
    sys.stderr.write("ERROR: ()Address-related error connecting to server")
    exit(1)

except socket.error:
    sys.stderr.write("ERROR: ()No connection established")
    exit(1)
##############################################################################


client_proc(sock)

