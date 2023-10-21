import logging
import os
import time
import requests
from datetime import datetime


def criar_arquivo(folder, name_file, valor, subs: bool = False):
    """
    This function creates a file with a given name and folder path, and writes a given value to it. It can also substitute the content of an existing file.

    :param folder: (str) the name of the folder where the file will be created
    :param name_file: (str) the name of the file to be created
    :param valor: (str) the value to be written to the file
    :param subs: (bool) a flag that indicates whether to substitute the content of an existing file with the new value. Default is False.
    :return: (str) the value that was written to the file.

    Example:
        To create a file named "example.txt" in the folder "my_folder" with the value "Hello, World!", use the following code:

        >>> criar_arquivo('my_folder', 'example.txt', 'Hello, World!')

    This will create a file named "example.txt" with the value "Hello, World!" inside the folder "my_folder". If the file already exists, it will not be substituted by default.
    """
    path_folder = os.path.abspath(os.getcwd() + f'/{folder}')
    path_file = os.path.abspath(os.getcwd() + f'/{folder}/{name_file}')

    if not os.path.exists(path_folder):
        os.mkdir(path_folder)

    bytes = valor.encode()
    if not os.path.exists(path_file) or subs:
        with open(path_file, 'wb') as file:
            file.write(bytes)
    with open(path_file, 'rb') as file:
        bytes = file.read()
        valor = bytes.decode()
    return valor


port = criar_arquivo('parameters', 'port', '5000')
base_url = f"http://127.0.0.1:{port}"


def send_msg_to_number(msg, number, file_path):
    """
    This function sends a message to a phone number using a third-party API. It can also send a file along with the message.

    :param msg: (str) the message to be sent
    :param number: (str) the phone number to send the message to
    :param file_path: (str) the path to a file to be sent along with the message. Default is an empty string.
    :return: (str) the response text from the API

    Example:
        To send a message "Hello, World!" to the phone number "555-1234", use the following code:

        >>> send_msg_to_number('Hello, World!', '555-1234')

    This will send a message to the phone number "555-1234" using the API specified in the `base_url` variable in the code. If a file is not specified, no file will be sent. The function returns the response text from the API.
    """
    url = base_url + "/send_msg_to_number"
    msg = msg
    number = number
    file_path = file_path
    if len(str(file_path)) > 0:
        with open(file_path, "rb") as file:
            print('reading file')
            files = {"file": file}
            data = {"msg": msg, "number": number}
            response = requests.post(url, files=files, data=data)
    else:
        files = {"file": ''}
        data = {"msg": msg, "number": number}
        response = requests.post(url, files=files, data=data)

    print(response.text)


def send_msg_to_contact(msg, contact, file_path):
    """
    This function sends a message to a contact using a third-party API. It can also send a file along with the message.

    :param msg: (str) the message to be sent
    :param contact: (str) the name of the contact to send the message to
    :param file_path: (str) the path to a file to be sent along with the message. Default is an empty string.
    :return: (str) the response text from the API

    Example:
        To send a message "Hello, World!" to the contact "John Smith", use the following code:

        >>> send_msg_to_contact('Hello, World!', 'John Smith')

    This will send a message to the contact "John Smith" using the API specified in the `base_url` variable in the code. If a file is not specified, no file will be sent. The function returns the response text from the API.
    """
    url = base_url + "/send_msg_to_contact"
    msg = msg
    contact = contact
    file_path = file_path
    if len(str(file_path)) > 0:
        with open(file_path, "rb") as file:
            print('reading file')
            files = {"file": file}
            data = {"msg": msg, "contact": contact}
            response = requests.post(url, files=files, data=data)
    else:
        files = {"file": ''}
        data = {"msg": msg, "contact": contact}
        response = requests.post(url, files=files, data=data)

    print(response.text)


def get_last_content_from_contact(contato):
    """
    This function retrieves the last content sent by a contact using a third-party API.

    :param contato: (str) the name of the contact to retrieve the last content from
    :return: (str) the response text from the API

    Example:
        To retrieve the last content sent by the contact "John Smith", use the following code:

        >>> get_last_content_from_contact('John Smith')

    This will retrieve the last content sent by the contact "John Smith" using the API specified in the `base_url` variable in the code. The function returns the response text from the API, which can be parsed to extract the relevant information.
    """
    url = base_url + f"/get_last_content_from_contact/{contato}"
    response = requests.get(url)
    # print(response.text)
    return response


def forward_last_msg_from_contact(from_contact, to_contact):
    """
    This function forwards the last message sent by a contact to another contact using a third-party API.

    :param from_contact: (str) the name of the contact who sent the last message to be forwarded
    :param to_contact: (str) the name of the contact to whom the last message will be forwarded
    :return: (str) the response text from the API

    Example:
        To forward the last message sent by the contact "John Smith" to the contact "Jane Doe", use the following code:

        >>> forward_last_msg_from_contact('John Smith', 'Jane Doe')

    This will forward the last message sent by the contact "John Smith" to the contact "Jane Doe" using the API specified in the `base_url` variable in the code. The function returns the response text from the API, which can be parsed to check if the message was forwarded successfully.
    """
    url = base_url + f"/forward_last_msg_from_contact/{from_contact}/{to_contact}"
    response = requests.get(url)
    # print(response.text)
    return response


def get_info_from_contact(contato):
    """
    Retrieve information about a WhatsApp contact.

    :param contato: str - The phone number or contact name of the WhatsApp user.
    :return: dict - A dictionary containing information about the contact.
            Example: {'name': 'John Doe', 'number': '+1234567890', 'status': 'online', 'profile_picture': 'https://...'}
    :raises: requests.exceptions.RequestException if the request to the server fails.

    This function sends a GET request to the WhatsApp server to retrieve information about a contact.
    The function takes in the phone number or contact name of the contact as a string. It then sends a GET request to the WhatsApp server to retrieve the information.
    The response from the server is a dictionary that contains information such as the name, number, status, and profile picture of the contact.
    If the request to the server fails, an exception will be raised.
    """
    url = base_url + f"/get_info_from_contact/{contato}"
    response = requests.get(url)
    # print(response.text)
    return response


def get_unread_chat():
    """
    Get a list of unread chat messages from the server.

    :return: A response object that contains a list of unread chat messages.
    :rtype: requests.models.Response

    Example:
        >>> response = get_unread_chat()
        >>> print(response.text)
    """
    url = base_url + f"/get_unread_chat"
    response = requests.get(url)
    # print(response.text)
    return response


def create_new_instance(name_instance):
    """
    Creates a new instance on the messaging platform with the given name.

    :param name_instance: (str) The name of the new instance to be created.
    :return: (str) The response from the server indicating whether the instance was created successfully.

    Example:
        To create a new instance named "my_instance", use:
        >>> create_new_instance("my_instance")
    """
    url = base_url + f"/{name_instance}"
    response = requests.get(url)
    # print(response.text)
    return response


def shutdown():
    url = base_url + f"/exit"
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError as e:
        logging.exception(e)


if __name__ == '__main__':
    pass
