#   Ex. 2.7 template - client side
#   Author: Barak Gonen, 2017
#   Modified for Python 3, 2020


import socket
import protocol27


IP = '127.0.0.1'
SAVED_PHOTO_LOCATION = r'C:\Users\oren\PycharmProjects\Cyber python\screenshots_python\new_image.png' # The path + filename where the copy of the screenshot at the client should be saved

def handle_server_response(my_socket, cmd):
    """
    Receive the response from the server and handle it, according to the request
    For example, DIR should result in printing the contents to the screen,
    Note - special attention should be given to SEND_PHOTO as it requires and extra receive
    """
    # (8) treat all responses except SEND_PHOTO
    if not cmd == 'SEND_PHOTO':
        length = int(my_socket.recv(4).decode())
        data = my_socket.recv(length).decode()
        print(data)
    else:
        image_size = int(my_socket.recv(4))  # Receive the 4-byte size field
        with open(SAVED_PHOTO_LOCATION, 'wb') as file:
            received_data = b""
            while len(received_data) < image_size:
                chunk = my_socket.recv(4096)  # Receive data in chunks
                received_data += chunk

            # Write the full data to the file
            file.write(received_data)

        print("Image received and saved successfully.")


def main():
    # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", protocol27.PORT))
    # (2)

    # print instructions
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')

    # loop until user requested to exit
    while True:
        cmd = input("Please enter command:\n")
        if protocol27.check_cmd(cmd):
            packet = protocol27.create_msg(cmd)
            print(f"Sending command: {cmd}")
            my_socket.send(packet.encode())
            handle_server_response(my_socket, cmd)
            if cmd == 'EXIT':
                break
        else:
            print("Not a valid command, or missing parameters\n")

    my_socket.close()

if __name__ == '__main__':
    main()