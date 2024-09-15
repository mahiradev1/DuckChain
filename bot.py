import requests
import time
import json
from colorama import Fore, Style
from fake_useragent import UserAgent

# Load authorization data from the tokens.txt file
with open('tokens.txt', 'r') as file:
    authorizations = [line.strip() for line in file]

headers = {
    'accept-language': 'en-US,en;q=0.9',
    'if-none-match': 'W/"129-83t1ejiXqZksI6D5DMDXM+paHE4"',
    'origin': 'https://tgdapp.duckchain.io',
    'priority': 'u=1, i',
    'referer': 'https://tgdapp.duckchain.io/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
}

# Function to fetch and process task list
def get_task_list(authorization_data):
    api_url = 'https://preapi.duckchain.io/task/task_list'
    headers['authorization'] = f'tma {authorization_data}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # Print the raw response for debugging
        # print(Fore.YELLOW + "Full Response:" + Style.RESET_ALL, response.text)

        # Parse the response and extract task data
        data = response.json().get('data')

        if data and isinstance(data, dict):  # Ensure data is a dictionary
            return data
        else:
            print(Fore.RED + "Task data not found or invalid format in response." + Style.RESET_ALL)
            return None

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching task list: {e}" + Style.RESET_ALL)
        return None

# Function to execute a task by type and ID
def execute_task_by_type(task_category, task, authorization_data):
    task_id = task.get('taskId')
    task_type = task.get('taskType')
    api_url = ''

    if task_category == 'daily':
        if task_type == 'daily_check_in':
            api_url = 'https://preapi.duckchain.io/task/sign_in?'
        else:
            api_url = f'https://preapi.duckchain.io/task/{task_type}?taskId={task_id}'
    else:
        api_url = f'https://preapi.duckchain.io/task/partner?taskId={task_id}'
  

    headers['authorization'] = f'tma {authorization_data}'
    print(f'api = {api_url}')
    print(f'task_type = {task_type}')
    time.sleep(2)  # Adjust the sleep time as needed
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # Check if the task was executed successfully
        result = response.json()
        if result.get('code') == 200 and result.get('data') is True:
            print(Fore.GREEN + f"Task '{task_type}' with ID {task_id} executed successfully!" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Task '{task_type}' with ID {task_id} failed." + Style.RESET_ALL)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error executing task '{task_type}' with ID {task_id}: {e}" + Style.RESET_ALL)

def userinfo(authorization_data):
    api_url = 'https://preapi.duckchain.io/user/info'
    headers['authorization'] = f'tma {authorization_data}' 

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        duck_name = data.get('data', {}).get('duckName')
        if duck_name:
            print(Fore.GREEN + "Duck Name:" + Style.RESET_ALL, duck_name)
        else:
            print(Fore.RED + "Duck name not found in response." + Style.RESET_ALL)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching user info: {e}" + Style.RESET_ALL)

def quack_execute(authorization_data):
    api_url = 'https://preapi.duckchain.io/quack/execute?'
    headers['authorization'] = f'tma {authorization_data}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        decibel = data.get('data', {}).get('decibel')
        quack_times = data.get('data', {}).get('quackTimes')

        if decibel and quack_times:
            print(Fore.GREEN + "Balance:" + Style.RESET_ALL, decibel)
            print(Fore.GREEN + "Total Click:" + Style.RESET_ALL, quack_times)
        else:
            print(Fore.RED + "Decibel or Quack Times not found in response." + Style.RESET_ALL)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error executing quack: {e}" + Style.RESET_ALL)

if __name__ == '__main__':
    ua = UserAgent()
    while True:
        for i, authorization_data in enumerate(authorizations):
            headers['user-agent'] = ua.random
            print(Fore.YELLOW + f"\n=== Account {i+1} ===" + Style.RESET_ALL)
            userinfo(authorization_data)
            quack_execute(authorization_data)
            task_list = get_task_list(authorization_data)  # Fetch task list

            if task_list:
                # Process and execute each task
                for task_category, tasks in task_list.items():
                    for task in tasks:
                        task_id = task.get('taskId')
                        task_type = task.get('taskType')
                        content = task.get('content')
                       
                        print(Fore.BLUE + f"Executing task: {content} (Type: {task_type}, ID: {task_id})" + Style.RESET_ALL)
                        
                        # Call the function to execute the task based on category and task details
                        execute_task_by_type(task_category, task, authorization_data)
                        time.sleep(2)
            time.sleep(1)
