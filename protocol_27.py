"""Ex. 2.7 template - protocol"""


LENGTH_FIELD_SIZE = 4
PORT = 8820
COMMAND = 0
SIZE_FIELD = 10000


def check_cmd(data):
    """
    Check if the command is defined in the protocol, including all parameters
    For example, DELETE c:\\work\\file.txt is good, but DELETE alone is not
    """
    # convert the data from string to list
    data = data.split(' ')
    # Commands with one parameter
    cmd_with_one_param = ["DIR", "DELETE", "EXECUTE"]
    # Commands with two parameters
    cmd_with_two_params = "COPY"
    # Commands without parameters
    cmd_without_params = ["EXIT", "TAKE_SCREENSHOT", "SEND_PHOTO"]

    # If the command without parameters:
    if len(data) == 1:  # only the command
        # if data == "EXIT"/"TAKE_SCREENSHOT"/"SEND_PHOTO":
        if data[COMMAND] in cmd_without_params:
            # Then this command is valid and return True
            return True
        # Else, this command is not valid - so return False
        return False

    # If the command with one parameter:
    elif len(data) == 2:  # The command and one parameter
        if data[COMMAND] in cmd_with_one_param:
            # Then this command is valid and return True
            return True
        # Else, this command is not valid - so return False
        return False

    # If the command with two parameters:
    elif len(data) == 3:  # The command and two parameters
        if data[COMMAND] == cmd_with_two_params:
            # Then this command is valid and return True
            return True
        # Else, this command is not valid - so return False
        return False
    return False


def create_msg(data):
    """
    Create a valid protocol message, with length field
    """
    # length of data as a string
    length = str(len(data))
    # Add zeros
    zfill_length = length.zfill(LENGTH_FIELD_SIZE)
    # Return length field + data.
    # For example:
    # data = "OK", zfill_length = "0002"
    # Return: "0002OK"
    return zfill_length + data


def get_msg(my_socket):
    """
    Extract message from protocol, without the length field
    If length field does not include a number, returns False, "Error"
    """
    # Take length field from the message
    length = my_socket.recv(LENGTH_FIELD_SIZE).decode()

    # Check if length field that was taken is digit:
    if length.isdigit():
        # Receive the command
        cmd = my_socket.recv(int(length)).decode()
        # Return that everything is OK (by return True), and the command
        return True, cmd
    # If length field is not digit:
    return False, "Error"
