import logging
import time
from flask import Flask, request, jsonify
import json, os, signal
from whatsapp import WhatsApp
import threading
from functools import partial
import subprocess
import re

request_queue = []
values_to_return={}

app = Flask(__name__)

whats = WhatsApp()
instance='Default'
exiting = False

def process_request():
    """
    Process incoming requests from a queue, calling the appropriate function and returning the result.

    :process: This function retrieves the first item in the request queue, which contains a dictionary with a list of form data and files,
    the function to be called, and a process identifier. It then extracts the form data and files from the list and calls the function,
    passing the extracted data as arguments. If a file is present in the request, it saves the file to a local directory and adds the path
    to the list of arguments. If the function throws an exception, it catches the exception and quits the WebDriver instance if it exists,
    then calls the home() function to redirect the user to the homepage. If there are no items in the request queue, the function sleeps
    for 1 second before checking again.

    :return: The function returns the processed data, which is stored in the global values_to_return dictionary with the process identifier
    as the key.

    Example:
        >>> process_request()
    """
    global request_queue,values_to_return
    while True:
        if len(request_queue)>0:
            request_data = request_queue[0]
            process = list(request_data.keys())

            lista = request_data[process[0]]
            form = lista[0].to_dict()
            files = lista[1].to_dict()
            func = lista[2]

            if len(form)>0:
                values = [form[key] for key in form.keys()]
                file = [files[key] for key in files.keys()][0]

                if len(str(file))>0 and not "<FileStorage: 'file' (None)>" in str(file):
                    root_path = os.path.abspath(f'{os.getcwd()}/files')
                    if not os.path.exists(root_path):
                        os.mkdir(root_path)
                    file_path = os.path.join(root_path, file.filename)
                    file.save(file_path)
                    values.append(file_path)

                try:
                    values_to_return[process[0]] = func(*values)
                except Exception as e:
                    try:
                        whats.driver.quit()
                    except Exception as e:
                        logging.exception(e)
                    home()
            else:
                try:
                    values_to_return[process[0]] = func()
                except Exception as e:
                    try:
                        whats.driver.quit()
                    except Exception as e:
                        logging.exception(e)
                    home()
            if len(request_queue) > 0:
                request_queue.pop(0)
        else:
            time.sleep(1)

def start_worker():
    """
    Starts a new thread that will continuously process requests in the request_queue.

    :return: None
    """
    worker = threading.Thread(target=process_request)
    worker.start()

@app.route('/<name_instance>')
def home(name_instance:str='Default'):
    '''
    This function sets up the Flask route and initializes the browser and
    starts the worker thread.

    :param name_instance: The name of the WhatsApp instance. Defaults to 'Default'.
    :type name_instance: str
    :return: The message indicating if the initialization was successful.
    :rtype: str
    '''
    global instance
    print(name_instance)
    if 'favicon.ico' in name_instance:
        name_instance='Default'
    print(name_instance)

    instance = name_instance
    def init(name_instance):
        try:
            name_instance = ''.join(re.findall('\w',name_instance))
            if not name_instance.startswith('profile_'):
                name_instance = 'Default'
                raise Exception

            #whats.init_browser(name_instance)
            #whats.open_whats()
            start_worker()
            return 'Sucessfully!'
        except Exception as e:
            logging.exception(e)
            whats.driver.quit()
            init(name_instance)
            return 'Sucessfully!'
    return init(name_instance)


@app.route('/get_last_content_from_contact/<contact>')
def get_last_content_from_contact(contact):
    """
        This function receives a contact name as parameter and returns the last message
        exchanged with that contact on WhatsApp. The function first checks if the browser
        is initialized, and if not, it initializes it by calling the home() function.
        Then, it creates a new request with the information received, assigns an ID to
        the request, and puts it in the request queue. It waits for the request to be
        processed and returns the content of the last message exchanged with the
        specified contact as a JSON object.

        :param contact: (str) The name of the contact to get the last message from.
        :return: (JSON) A JSON object containing the content of the last message exchanged
                 with the specified contact.

        Example:
            To get the last message exchanged with a contact named "John", you can use the
            following URL in your web browser:

            http://localhost:5000/get_last_content_from_contact/John

            This will return a JSON object with the content of the last message exchanged
            with "John".
    """
    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        id = f'get_last_content_from_contact{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, partial(whats.get_last_content_from_contact,contact)]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"

@app.route('/forward_last_msg_from_contact/<from_contact>/<to_contact>')
def forward_last_msg_from_contact(from_contact,to_contact):
    """
    This route forwards the last message from a specific contact to another contact.

    Process:

    Check if the WhatsApp instance is initialized. If not, initializes it.
    Create a dictionary to store the request data, files, and a partial function to be executed later.
    Append the dictionary to the request queue and set a unique ID for the request.
    Set the initial value of the return value for the request ID as None.
    Wait for the request to be executed by checking if the request ID is still in the list of processes. Wait for 1 second between checks.
    If the return value for the request ID is False, raise an exception and restart the application.
    Return a JSON object with the content of the forwarded message.
    :param from_contact: (str) The contact to get the last message from.
    :param to_contact: (str) The contact to forward the last message to.
    :return: (str) A JSON object with the content of the forwarded message.

    Example:
    To forward the last message from the contact "John Doe" to the contact "Jane Smith", send a GET request to:
    /forward_last_msg_from_contact/John%20Doe/Jane%20Smith
    """
    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        id = f'forward_last_msg_from_contact{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, partial(whats.forward_last_msg_from_contact,from_contact,to_contact)]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"

@app.route('/get_info_from_contact/<contact>')
def get_info_from_contact(contact):
    """
    This function retrieves information from a WhatsApp contact and returns it as JSON format.

    :param contact: (str) The name or phone number of the WhatsApp contact to retrieve information from.
    :return: (JSON) A JSON object containing the information of the specified contact.

    Example:
        To use this function, make a GET request to the URL '/get_info_from_contact/<contact>' where <contact> is the name or phone number of the desired WhatsApp contact.
    """
    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        id = f'get_info_from_contact{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, partial(whats.get_info_from_contact,contact)]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"


@app.route('/download_last_medias_from_contact/<contact>')
def download_last_medias_from_contact(contact):
    """
    This route allows the user to download the last medias (images and videos) from a specific WhatsApp contact.

    :param contact: (str) The name of the contact to download the medias from.
    :return: (str) A JSON object containing the content of the downloaded medias.

    Example:
    To download the last medias from a contact named 'John Doe', you can make a POST request to the following URL:
    http://localhost:5000/download_last_medias_from_contact/John%20Doe

    The response will be a JSON object containing the content of the downloaded medias.
    """
    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        id = f'download_last_medias_from_contact{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, partial(whats.download_last_medias_from_contact,contact)]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"


@app.route('/get_chats')
def get_chats():
    """
    This route allows the user to get a list of all WhatsApp chats.

    :return: (str) A JSON object containing a list of all the chats.

    Example:
    To get a list of all the chats, you can make a GET request to the following URL:
    http://localhost:5000/get_chats

    The response will be a JSON object containing a list of all the chats.
    """
    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)

    try:
        dict = {}
        request_data = request.form
        id = f'get_chats{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, whats.get_chats]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"

@app.route('/get_unread_chat')
def get_unread_chat():
    """
    Flask route that handles requests to get the list of unread chats from WhatsApp.

    The function checks whether the WhatsApp instance has been initialized. If it hasn't, it calls the `home()` function to start the instance. Then, it creates a unique ID for the request, initializes the corresponding entry in the `values_to_return` dictionary to `None`, and adds a dictionary entry to the `request_queue` with the request data, request files, and function `whats.get_unread_chat` to execute. The function enters a loop that waits for the ID of the current request to be removed from the `processes` list. If the `values_to_return` entry corresponding to the current ID is still `None`, an exception is raised. Otherwise, the function returns a JSON object containing the value of the `content` key in the `values_to_return` entry corresponding to the current ID.

    :return: JSON object containing the value of the `content` key in the `values_to_return` entry corresponding to the current ID
    :rtype: str

    Example:
    To get the list of unread chats from WhatsApp, make a GET request to the `/get_unread_chat` endpoint. The response will be a JSON object containing the list of unread chats. If there are no unread chats, the response will be an empty list.
    """

    global request_queue,values_to_return,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        id = f'get_unread_chat{len(request_queue)}'
        values_to_return[id]=None
        dict[id] = [request_data, request.files, whats.get_unread_chat]
        request_queue.append(dict)
        print(request_queue)
        print('values_to_return in a route')
        print(values_to_return)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':values_to_return[id]})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"



@app.route('/send_msg_to_number', methods=['POST'])
def send_msg_to_number():
    """
        This function handles the sending of a message to a phone number.

        :process request_data: (dict) A dictionary containing the phone number and message to be sent.
        :process id: (str) An identifier for the current request.
        :process values_to_return: (dict) A dictionary used to store the return values of each request.
        :process dict: (dict) A dictionary used to store each request with its corresponding id and function to be executed.
        :process request_queue: (list) A queue used to store each request.
        :returns: (str) A JSON object containing the message "Msg sent successfully" upon successful message sending.
        :raises Exception: An exception is raised if an error occurs during message sending.

        Example:
            The following is an example of how to use this function to send a message to a phone number:
            ```
            data = {'phone_number': '1234567890', 'message': 'Hello, World!'}
            response = requests.post(url='http://localhost:5000/send_msg_to_number', data=data)
            ```
    """
    global request_queue,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        print(request_data)
        id = f'send_msg_to_number{len(request_queue)}'
        values_to_return[id] = None
        dict[id]=[request_data,request.files,whats.send_msg_to_number]
        request_queue.append(dict)
        print(request_queue)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return json.dumps({'content':'Msg sent successfully'})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"


@app.route('/send_msg_to_contact', methods=['POST'])
def send_msg_to_contact():
    """
    This function sends a message to a WhatsApp contact. It receives a POST request with form data and a file (optional).

    :return: A JSON object with the content 'Msg sent successfully' if the message is sent successfully.

    :raises Exception: If there is an error, the function raises an exception and restarts the WhatsApp driver.
    """
    global request_queue,instance
    if whats.initialized_whats:
        pass
    else:
        home(instance)
    try:
        dict = {}
        request_data = request.form
        print(request_data)
        id = f'send_msg_to_contact{len(request_queue)}'
        values_to_return[id] = None
        dict[id]=[request_data,request.files,whats.send_msg_to_contact]
        request_queue.append(dict)
        print(request_queue)
        processes = [list(request_data.keys())[0] for request_data in request_queue]
        print(processes)
        while id in processes:
            processes = [list(request_data.keys())[0] for request_data in request_queue]
            time.sleep(1)
        if False == values_to_return[id]:
            raise Exception('Error! Restarting...')
        return jsonify({'content':'Msg sent successfully'})
    except Exception as e:
        logging.exception(e)
        whats.driver.quit()
        home(instance)
        return "Restarted"

@app.route("/exit")
def exit_app():
    """
    This function terminates the Flask application. It checks if a Selenium WebDriver instance has been initialized by a previous execution of the program and quits it if necessary. Then, it retrieves the port number from a file called 'parameters' (or creates it with a default value of 5000 if it doesn't exist) and uses it to identify the process listening on that port. Once the process is found, the function terminates it by sending a taskkill command to the operating system. Finally, the function deletes all Python cache files (.pyc) generated by the program.


    :return: A JSON object with the message 'Server quit!'

    Example:
        >>> To use this function, simply send a GET request to the /exit endpoint of your Flask application.
    """
    if whats.initialized_whats:
        whats.driver.quit()

    port = int(str(criar_arquivo('parameters', 'port', '5000')).strip())
    host = '127.0.0.1'
    cmd_newlines = r'\r\n'

    host_port = host + ':' + str(port)
    pid_regex = re.compile(r'[0-9]+$')

    netstat = subprocess.run(['netstat', '-n', '-a', '-o'], stdout=subprocess.PIPE)
    # Doesn't return correct PID info without precisely these flags
    netstat = str(netstat)
    lines = netstat.split(cmd_newlines)

    for line in lines:
        if host_port in line:
            pid = pid_regex.findall(line)
            if pid:
                pid = pid[0]
                os.system('taskkill /F /PID ' + str(pid))

    # And finally delete the .pyc cache
    os.system('del /S *.pyc')

    return jsonify({'content': 'Server quit!'})


def criar_arquivo(folder, name_file, valor, subs: bool = False):
    """
    This function creates a file with the given name and folder and writes a string value to it. If the file already exists and the 'subs' parameter is False, it will not overwrite the existing file. If 'subs' is True, it will replace the existing file with the new value.

    :param folder: The name of the folder where the file will be created.
    :type folder: str

    :param name_file: The name of the file to be created.
    :type name_file: str

    :param valor: The value to be written in the file.
    :type valor: str

    :param subs: Optional parameter that indicates whether to overwrite the file if it already exists. Defaults to False.
    :type subs: bool

    :return: The value that was written to the file, after reading it back from the file.
    :rtype: str

    Example:
    To create a new file called "example.txt" in the "documents" folder with the value "Hello, World!", you can call the function like this:

        >>> criar_arquivo("documents", "example.txt", "Hello, World!")

        This will create the file "example.txt" in the "documents" folder with the value "Hello, World!".

        To overwrite an existing file, set the 'subs' parameter to True, like this:

        >>> criar_arquivo("documents", "example.txt", "Goodbye, World!", subs=True)

        This will replace the existing file with the new value "Goodbye, World!".
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

def run_api(force_port:int=0):
    """
    This function runs an API on a specified port. If a port is not specified, it reads the port value from a file named
    'parameters' in the current directory. If the file does not exist or the port value is not specified in the file, the
    default port of 5000 is used. The API is run with debug mode turned off.

    :param force_port: (int) Optional. If specified, the API will be run on the specified port instead of reading the port
                       value from the file.
    :return: None

    Example:
        To run the API on the default port:
        >>> run_api()

        To run the API on a specific port:
        >>> run_api(8080)

    """
    if not force_port>0:
        port = int(str(criar_arquivo('parameters', 'port', '5000')).strip())
    else:
        port = force_port
    app.run(debug=False, port=port)





if __name__ == '__main__':
    pass