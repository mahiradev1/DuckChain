import requests
import time
import json
from colorama import Fore, Style
from fake_useragent import UserAgent
from datetime import datetime,timedelta

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

task_execution_tracker = {}

# Function to print the countdown
def display_countdown(remaining_seconds):
    while remaining_seconds > 0:
        hours, remainder = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        print(Fore.YELLOW + f"Waiting for next execution: {countdown_str} remaining..." + Style.RESET_ALL, end='\r')
        time.sleep(1)
        remaining_seconds -= 1
    print()  # Move to the next line after countdown is done

# Function to fetch task list
def get_task_list(authorization_data):
    api_url = 'https://preapi.duckchain.io/task/task_list'
    headers['authorization'] = f'tma {authorization_data}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json().get('data')
        if data and isinstance(data, dict):  # Ensure data is a dictionary
            return data
        else:
            print(Fore.RED + "Task data not found or invalid format in response." + Style.RESET_ALL)
            return None

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching task list: {e}" + Style.RESET_ALL)
        return None

# Function to fetch task info
def task_info(authorization_data):
    api_url = 'https://preapi.duckchain.io/task/task_info'
    headers['authorization'] = f'tma {authorization_data}'
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        data = response.json().get('data')
        if data:
            return data  # Return task info data
        else:
            print(Fore.RED + "Task info data not found in response." + Style.RESET_ALL)
            return None

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching task info: {e}" + Style.RESET_ALL)
        return None

# Function to execute a task by type and ID
def execute_task_by_type(task_category, task, authorization_data, completed_tasks):
    task_id = task.get('taskId')
    task_type = task.get('taskType')
    api_url = ''
    
    # Skip task if ID is in completed tasks
    if task_id in completed_tasks.get(task_category, []):
        # print(Fore.YELLOW + f"Task '{task_type}' with ID {task_id} already completed, skipping." + Style.RESET_ALL)
        return
    
    # Skip "oneTime" tasks if ID is in partner category
    if task_category == 'oneTime' and task_id in completed_tasks.get('partner', []):
        # print(Fore.YELLOW + f"Task '{task_type}' with ID {task_id} is a one-time task but is already present in partner tasks. Skipping." + Style.RESET_ALL)
        return
    
    # Set API URL based on task category and type
    if task_category == 'daily':
        if task_type == 'daily_check_in':
            api_url = 'https://preapi.duckchain.io/task/sign_in?'
        else:
            api_url = f'https://preapi.duckchain.io/task/{task_type}?taskId={task_id}'
    else:
        api_url = f'https://preapi.duckchain.io/task/partner?taskId={task_id}'

    headers['authorization'] = f'tma {authorization_data}'

    # Track task execution time
    now = datetime.now()
    task_key = (task_category, task_id)
    if task_key in task_execution_tracker:
        last_exec_time = task_execution_tracker[task_key]
        if (now - last_exec_time) < timedelta(hours=6):
            remaining_time = timedelta(hours=6) - (now - last_exec_time)
            remaining_seconds = int(remaining_time.total_seconds())
            print(Fore.YELLOW + f"Task '{task_type}' with ID {task_id} is on cooldown." + Style.RESET_ALL)
            display_countdown(remaining_seconds)
            return
    else:
        task_execution_tracker[task_key] = now  # Set first execution time
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get('code') == 200 and result.get('data') is True:
            print(Fore.GREEN + f"Task '{task_type}' with ID {task_id} executed successfully!" + Style.RESET_ALL)
            # Update the execution time
            task_execution_tracker[task_key] = now
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
        box_amount = data.get('data', {}).get('boxAmount', 0)
        if duck_name:
            print(Fore.GREEN + "Duck Name:" + Style.RESET_ALL, duck_name)
        else:
            print(Fore.RED + "Duck name not found in response." + Style.RESET_ALL)
        
        return box_amount  # Return the boxAmount to use later

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error fetching user info: {e}" + Style.RESET_ALL)
        return 0

def open_box(authorization_data):
    api_url = 'https://preapi.duckchain.io/box/open?openType=-1'
    headers['authorization'] = f'tma {authorization_data}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get('code') == 200:
            print(Fore.GREEN + "Box opened successfully!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to open the box." + Style.RESET_ALL)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error opening box: {e}" + Style.RESET_ALL)

# Ensure quack_execute always runs
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
    try:
        while True:
            for i, authorization_data in enumerate(authorizations):
                headers['user-agent'] = ua.random
                print(Fore.YELLOW + f"\n=== Account {i+1} ===" + Style.RESET_ALL)
                # Ensure quack_execute always runs
                quack_execute(authorization_data)
                # Fetch and process task info and task list
                task_info_data = task_info(authorization_data)
                if task_info_data:
                    # Ensure task_info_data is a dictionary and contains the expected keys
                    if isinstance(task_info_data, dict):
                        completed_tasks = {
                            'social_media': task_info_data.get('socialMedia', []),
                            'partner': task_info_data.get('partner', []),
                            'daily': task_info_data.get('daily', [])
                        }

                        task_list = get_task_list(authorization_data)
                        if task_list:
                            for task_category, tasks in task_list.items():
                                for task in tasks:
                                    execute_task_by_type(task_category, task, authorization_data, completed_tasks)
                
              

                # Wait before processing the next account
                time.sleep(3)  # Adjust sleep time as needed

    except KeyboardInterrupt:
        print(Fore.RED + "\nScript interrupted by user." + Style.RESET_ALL)
