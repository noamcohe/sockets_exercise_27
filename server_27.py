"""
Ex - 2.7 template - server side
Author: Noam Cohen, 2020
Modified for Python 3, 2020
"""

import socket
import protocol_27
from glob import glob
import os
import shutil
import subprocess
import pyautogui
from ntpath import basename


IP = "0.0.0.0"
# The path + filename where the screenshot at the server should be saved
PHOTO_PATH = "C:\\Networks\\work\\source_screenshot.jpg"
PARAM1 = 1
PARAM2 = 2
LENGTH_WITHOUT_PARAMS = 1
LENGTH_WITH_ONE_PARAM = 2
LENGTH_WITH_TWO_PARAMS = 3


def get_file_name(list_of_files):
    """
    Get list of files in a specific folder,
    when all the files we got with their path.
    """
    # Running all over the list
    for i in range(len(list_of_files)):
        # And takes from all paths, the file name:
        list_of_files[i] = basename(list_of_files[i])
    return list_of_files


def dir_cmd(path):
    """
    Return the contents of a specific folder on the remote computer.
    """
    # All files in the path, as a list.
    result = glob(path)
    empty_list = []
    # If the folder is empty:
    if empty_list == result:
        return "This folder is empty"
    # Call to get_file_name:
    result = get_file_name(result)
    # Convert it to string type (if the path is valid, of course)
    result = '\n'.join(result)
    # Return the string
    return result


def delete_cmd(file):
    """
    Delete the passed file as a function parameter.
    """
    # Delete the file.
    os.remove(file)
    # If the deletion was successful:
    return "File deleted"


def copy_cmd(file1, file2):
    """
    Copy the data on the first file to second file.
    """
    # Copy all the data from file1 to file2.
    shutil.copy(file1, file2)
    # Return that the command succeeded:
    return "Copied"


def execute_cmd(software):
    """
    Running software on the server.
    """
    try:
        # Running software
        subprocess.call(software)
        # If the command succeeded:
        return "This command was successful"
    # Else:
    except Exception as e:
        return "Failed to run software, " + str(e)


def take_screenshot_cmd():
    """
    Screenshot of the remote computer, and save in 'path'.
    """
    # Create screenshot
    image = pyautogui.screenshot()
    try:
        # Save screenshot in PHOTO_PATH
        image.save(PHOTO_PATH)
        # If the save was successful
        return "This command was successful"
    # Else:
    except Exception as e:
        return "This command failed, " + str(e)


def photo_size():
    """
    Return the size of the image
    """
    try:
        size = os.stat(PHOTO_PATH)
        data = size.st_size
        # Return the size of the image
        return data
    except Exception as e:
        return "There is no photo to send, " + str(e)


def send_photo_cmd(destination_socket):
    """
    Send the screenshot to the client.
    First, send to the client the image size.
    Second, send a field of length size.
    And after that, send data.
    """
    try:
        # Get the size of photo from 'photo_size'
        size_of_image = photo_size()
        # Add length field
        data = protocol_27.create_msg(str(size_of_image))
        # Send it to the client
        destination_socket.send(data.encode())
        # Open the source photo
        with open(PHOTO_PATH, 'rb') as read_file:
            while size_of_image > 0:
                # If size of photo > size field:
                if size_of_image > protocol_27.SIZE_FIELD:
                    image = read_file.read()
                    destination_socket.send(image)
                    size_of_image -= protocol_27.SIZE_FIELD
                else:
                    image = read_file.read()
                    destination_socket.send(image)
                    size_of_image -= size_of_image
        return "Sent photo successfully"
    except Exception as e:
        return "This command failed, " + str(e)


def one_param(cmd):
    """
    Check if the commands with one param are valid.
    This function check only the param of the command
    """
    if os.path.exists(cmd[PARAM1]):
        return True, LENGTH_WITH_ONE_PARAM
    return False, None


def two_params(cmd):
    """
    Check if the commands with two param are valid.
    This function check only the params of the command
    """
    if os.path.exists(cmd[PARAM1]) and os.path.exists(cmd[PARAM2]):
        return True, LENGTH_WITH_TWO_PARAMS
    return False, None


def check_params(cmd):
    """
    Check if the params are valid.
    """
    cmd = cmd.split(' ')
    # Commands without parameters
    cmd_without_params = ["EXIT", "TAKE_SCREENSHOT", "SEND_PHOTO"]
    # Commands with one parameter
    cmd_with_one_param = ["DIR", "DELETE", "EXECUTE"]
    # Commands with two parameters
    cmd_with_two_params = "COPY"

    # If the command without params:
    if cmd[protocol_27.COMMAND] in cmd_without_params:
        return True, LENGTH_WITHOUT_PARAMS
    # Else if the command with one param:
    elif cmd[protocol_27.COMMAND] in cmd_with_one_param:
        return one_param(cmd)
    # Else if the command with two params:
    elif cmd[protocol_27.COMMAND] in cmd_with_two_params:
        return two_params(cmd)


def check_client_request(cmd):
    """
    Break cmd to command and parameters
    Check if the command and params are good.

    For example, the filename to be copied actually exists

    Returns:
        valid: True/False
        command: The requested cmd (ex. "DIR")
        params: List of the cmd params (ex. ["c:\\cyber"])
    """
    # Use protocol.check_cmd first
    is_valid_cmd = protocol_27.check_cmd(cmd)
    # If the command is valid:
    if is_valid_cmd:
        # Then make sure the params are valid
        (are_params_valid, length) = check_params(cmd)
        if are_params_valid:
            cmd = cmd.split(' ')
            if length == LENGTH_WITHOUT_PARAMS:
                return True, cmd[protocol_27.COMMAND], None
            elif length == LENGTH_WITH_ONE_PARAM:
                return True, cmd[protocol_27.COMMAND], cmd[PARAM1]
            elif length == LENGTH_WITH_TWO_PARAMS:
                return True, cmd[protocol_27.COMMAND], cmd[PARAM1:]
        # If The params are not valid:
        return False, None, None
    # If the command is not valid:
    return False, None, None


def handle_client_request(destination_socket, command, params):
    """
    Create the response to the client, given the command is legal and params are OK

    For example, return the list of filenames in a directory
    Note: in case of SEND_PHOTO, only the length of the file will be sent

    Returns:
        response: the requested data

    """
    # If the user enter "DIR":
    rsp = None
    if command == "DIR":
        # Then call to dir_cmd and return the result into rsp
        rsp = dir_cmd(params + '\\*.*')
    # If the user enter "DELETE":
    if command == "DELETE":
        # Then call to delete_cmd and return the result into rsp
        # The deletion can be failed and return exception
        rsp = delete_cmd(str(params))
    # If the user enter "COPY":
    if command == "COPY":
        # Then call to copy_cmd and return the result into rsp
        rsp = copy_cmd(params[0], params[1])
    # If the user enter "EXECUTE":
    if command == "EXECUTE":
        # Then call to execute_cmd and return the result into rsp
        # The command can be failed and return exception
        rsp = execute_cmd(str(params))
    # If the user enter "TAKE_SCREENSHOT":
    if command == "TAKE_SCREENSHOT":
        # Then call to take_screenshot_cmd and return the result into rsp
        # The command can be failed and return exception
        rsp = take_screenshot_cmd()
    # If the user enter "SEND_PHOTO":
    if command == "SEND_PHOTO":
        # Then call to photo_size and return the result into rsp
        # The command can be failed and return exception
        rsp = send_photo_cmd(destination_socket)
    # If the user enter "EXIT":
    if command == "EXIT":
        # Then return "Bye"
        rsp = "Bye"
    return rsp


def main():
    # open socket with client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, protocol_27.PORT))
    server_socket.listen()
    print("Server is up and running")

    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    # handle requests until user asks to exit
    while True:
        # Check if protocol is OK, e.g. length field OK
        (valid_protocol, cmd) = protocol_27.get_msg(client_socket)
        if valid_protocol:
            # Check if params are good, e.g. correct number of params, file name exists
            (valid_cmd, command, params) = check_client_request(cmd)
            if valid_cmd:
                # prepare a response using "handle_client_request"
                rsp = handle_client_request(client_socket, command, params)
                # add length field using "create_msg"
                msg = protocol_27.create_msg(rsp)
                # send to client
                client_socket.send(msg.encode())
                # If the command is "EXIT":
                if command == 'EXIT':
                    break
            else:
                # prepare proper error to client
                response = protocol_27.create_msg('Bad command or parameters')
                # send to client
                client_socket.send(response.encode())

        else:
            # prepare proper error to client
            response = protocol_27.create_msg('Packet not according to protocol')
            # send to client
            client_socket.send(response.encode())
            # Attempt to clean garbage from socket
            client_socket.recv(1024)

    # close sockets
    print("Closing connection")


if __name__ == '__main__':
    main()
