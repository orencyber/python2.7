#   Ex. 2.7 template - server side
#   Author: Barak Gonen, 2017
#   Modified for Python 3, 2020

import socket
import protocol27
import glob
import os
import shutil
import subprocess
import pyautogui
import datetime

from server26 import server_name

IP = '0.0.0.0'
PHOTO_PATH = r'C:\Users\oren\PycharmProjects\Cyber python\screenshots_python'  # The path + filename where the screenshot at the server should be saved


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
    if not protocol27.check_cmd(cmd):
        return False, cmd, 'invalid command'
    if 'DIR' in cmd:
        broken_down = cmd.split(' ')
        parameter = broken_down[1]
        if os.path.isdir(parameter):
            return True, 'DIR', [parameter]
        else:
            return False, 'DIR', [parameter]
    if 'DELETE' in cmd:
        broken_down = cmd.split(' ')
        parameter = broken_down[1]
        if os.path.isfile(parameter):
            return True, 'DELETE', [parameter]
        return False, 'DELETE', [parameter]
    if 'COPY' in cmd:
        broken_down = cmd.split(' ')
        file_to_be_moved = broken_down[1]
        destination_file = broken_down[2]
        if os.path.isfile(file_to_be_moved) and os.path.isfile(destination_file):
            return True, 'COPY', [file_to_be_moved, destination_file]
        return False, 'DIR', [file_to_be_moved, destination_file]
    if 'EXECUTE' in cmd:
        broken_down = cmd.split()  # Split the command by spaces
        print(broken_down)
        if len(broken_down) > 1:  # Check if the command has a parameter
            parameter = broken_down[1].strip()  # Remove any leading or trailing spaces
            if os.path.isfile(parameter) and os.access(parameter, os.X_OK):  # Check if it's a valid file and executable
                return True, 'EXECUTE', [parameter]  # File is valid, return True
            else:
                return False, 'EXECUTE', ['Invalid file path or not executable']  # Invalid file or not executable
        else:
            return False, 'EXECUTE', ['Missing parameter']
    if cmd == 'TAKE_SCREENSHOT':
        if not PHOTO_PATH:
            return False, cmd
        if os.path.isdir(PHOTO_PATH):
            return True, cmd, []
        return False, cmd
    if cmd == 'SEND_PHOTO':
        if not PHOTO_PATH:
            return False, cmd
        if os.path.isdir(PHOTO_PATH):
            return True, cmd, []
    if cmd == 'EXIT':
        return True, cmd, []
    return False, cmd



def handle_client_request(command, params):
    """Create the response to the client, given the command is legal and params are OK

    For example, return the list of filenames in a directory
    Note: in case of SEND_PHOTO, only the length of the file will be sent

    Returns:
        response: the requested data

    """
    print(f"Received command: {command}")
    if command == 'DIR':
        final_dir = fr'{params[0]}\*.*'
        files_list = glob.glob(final_dir)
        return files_list
    if command == 'DELETE':
        os.remove(fr'{params[0]}')
        return 'file removed successfully'
    if command == 'COPY':
        shutil.copy(params[0], params[1])
        return 'file copied successfully'
    if command == 'EXECUTE':
        print(f"Attempting to execute: {params[0]}")
        subprocess.call(fr'{params[0]}')
        return 'command executed successfully'
    if command == 'TAKE_SCREENSHOT':
        file_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.png")
        file_path = os.path.join(PHOTO_PATH, file_name)
        # Take and save the screenshot
        print(f"Screenshot saved as {file_path}")
        pyautogui.screenshot(file_path)
        return 'screenshot saved successfully'
    if command == 'SEND_PHOTO':
        files = glob.glob(os.path.join(PHOTO_PATH, '*.png'))
        if not files:
            return None
        latest_file = max(files, key=os.path.getctime) # returns the file path
        with open(latest_file, 'rb') as file:
           file_data = file.read()
        file_size = len(file_data)
        return f"{file_size:04d}"
    if command == 'EXIT':
        return 'closing connection...'
    return 'invalid command'


def client_thread(client_socket, client_address):
    print(f"New connection from {client_address}")
    while True:
        valid_protocol, cmd = protocol27.get_msg(client_socket)
        if valid_protocol:
            valid_cmd, command, params = check_client_request(cmd)
            if valid_cmd:
                requested_data = handle_client_request(command, params)
                response = protocol27.create_msg(requested_data)
                client_socket.send(response.encode())

                if command == 'SEND_PHOTO':
                    files = glob.glob(os.path.join(PHOTO_PATH, '*.png'))
                    if files:
                        latest_file = max(files, key=os.path.getctime)
                        with open(latest_file, 'rb') as file:
                            file_data = file.read()
                        client_socket.send(file_data)

                if command == 'EXIT':
                    break
            else:
                client_socket.send(b'invalid command or parameters')
        else:
            client_socket.send(b'message not according to protocol27. try again')
            client_socket.recv(1024)  # Clean up garbage data
    client_socket.close()
    print(f"Connection closed: {client_address}")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, protocol27.PORT))
    server_socket.listen()
    print("Server is up and running")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=client_thread, args=(client_socket, client_address))
        thread.start()

if __name__ == '__main__':
    main()
