"""
Ex - 2.7 template - client side
Author: Noam Cohen, 2020
Modified for Python 3, 2020
"""


import socket
import protocol_27


IP = "127.0.0.1"
# The path + filename where the copy of the screenshot at the client should be saved
SAVED_PHOTO_LOCATION = "C:\\Networks\\work\\destination_screenshot.jpg"


def handle_server_response(my_socket, cmd):
    """
    Receive the response from the server and handle it, according to the request
    For example, DIR should result in printing the contents to the screen,
    Note- special attention should be given to SEND_PHOTO as it requires and extra receive
    """
    # (8) treat all responses except SEND_PHOTO
    # Get response from the server, by "protocol.get_msg"
    (valid_rsp, rsp) = protocol_27.get_msg(my_socket)
    # If the response valid:
    if valid_rsp:
        # Then print it
        print(rsp)
        # (10) treat SEND_PHOTO
        # If the response is a digit:
        if rsp.isdigit():
            if cmd == "SEND_PHOTO":
                size = int(rsp)
                try:
                    with open(SAVED_PHOTO_LOCATION, 'wb') as write_file:
                        while True:
                            if size > protocol_27.SIZE_FIELD:
                                write_file.write(my_socket.recv(protocol_27.SIZE_FIELD))
                                size -= protocol_27.SIZE_FIELD
                            else:
                                write_file.write(my_socket.recv(size))
                                break
                    (valid_response, response) = protocol_27.get_msg(my_socket)
                    print(response)
                except Exception as e:
                    print("Error, " + str(e))


def main():
    # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, protocol_27.PORT))

    # print instructions
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')

    # loop until user requested to exit
    while True:
        cmd = input("Please enter command:\n")
        if protocol_27.check_cmd(cmd):
            # Add length field
            packet = protocol_27.create_msg(cmd)
            # Send the command + length field to the server
            my_socket.send(packet.encode())
            # Take only the command
            command = cmd.split(' ')
            # Receive the response from the server
            # Send to 'handle_server_response' my_socket and the command (without the params)
            handle_server_response(my_socket, command[protocol_27.COMMAND])
            # If the command is 'EXIT'
            if cmd == 'EXIT':
                # Then break the loop
                break
        else:
            print("Not a valid command, or missing parameters")

    my_socket.close()


if __name__ == '__main__':
    main()
