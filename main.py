# Import the necessary modules.
import datetime as dt 
import json
from typing import Union

FORMAT = '%H:%M:%S' # Write down the format of the received time.
WEIGHT = 75         # Person's weight in kg.
HEIGHT = 175        # Persons height in sm.
K_1 = 0.035         # The coefficient for counting calories.
K_2 = 0.029         # The coefficient for counting calories.
STEP_M = 0.65       # Step length in meters.

def load_data(today_date: str) -> tuple[str, float, dict]:
    """
    Function load data from file
    using today date. If theres no 
    such file we will create "empty" file.

    """
    file_name = "my_data_" + today_date + ".json"
    try:
        with open(file_name, "r") as f:
            data = json.load(f)
            today_date = data["today_date"]
            calories_burned = data["calories_burned"]
            storage_data = data["storage_data"]   
            return today_date, calories_burned, storage_data
    except FileNotFoundError:
        print(f"File {file_name} not found. Creating new file.")
        return today_date, 0, {}

def write_data(today_date: str, calories_burned: float, storage_data: dict) -> None:
    """
    Function write new data to file.

    """
    file_name = "my_data_" + today_date + ".json"
    with open(file_name, "w") as f:
        data = {"today_date" : today_date,
                "calories_burned": calories_burned, 
                "storage_data": storage_data
                }
        json.dump(data, f, indent=4)


def time_difference_in_hours(time1: Union[str, dt.time], time2: Union[str, dt.time]) -> float:
    """
    Calculates the difference between two times in the format "hh:mm:ss" 
    and returns the difference in hours with a fractional part.

    """
    if isinstance(time1, str):
        time1 = dt.datetime.strptime(time1, FORMAT).time()
    if isinstance(time2, str):    
        time2 = dt.datetime.strptime(time2, FORMAT).time()

    # Convert time to seconds
    time1_seconds = time1.hour * 3600 + time1.minute * 60 + time1.second
    time2_seconds = time2.hour * 3600 + time2.minute * 60 + time2.second

    # Calculate diffrence in seconds
    difference_seconds = abs(time1_seconds - time2_seconds)

    # Convert the difference to hours with a fractional part
    # and return it
    difference_hours = difference_seconds / 3600

    return difference_hours

def check_correct_data(data: tuple[str, int]) -> bool:
    """
    Check is input data correct.

    """

    return isinstance(data, tuple) and len(data) == 2 and all(data)

def check_correct_time(time: Union[str, dt.time], storage_data: dict) -> bool:
    """
    Check is input data-time correct.

    """
    # If the dictionary to store is not empty
    # and the time value received in the argument is
    # less than or equal to the largest key value in the dictionary,
    # the function returns False.
    # otherwise - True

    if isinstance(time, str):
        time = dt.datetime.strptime(time, FORMAT).time()

    if storage_data:
        max_time = max(map(lambda x: dt.datetime.strptime(x, FORMAT), storage_data.keys())).time()
        return time > max_time
    return True

def get_step_day(storage_data: dict) -> int:
    """
    Get the number of steps taken this day.

    """
    return sum(storage_data.values())

def get_distance(steps: int) -> float:
    """
    Get the distance traveled in km.

    """
    return (steps * STEP_M) / 1000

def get_spent_calories(storage_data: dict, dist: float, current_time: Union[str, dt.time]) -> float:
    """
    Get the value of calories burned.

    """
    if isinstance(current_time, str):
        current_time = dt.datetime.strptime(current_time, FORMAT).time()

    previous_time = dt.datetime.strptime(list(storage_data.keys())[-1], FORMAT).time()
    distance_time = time_difference_in_hours(current_time, previous_time)
    mean_speed = dist / distance_time 
    return WEIGHT * (K_1  + K_2  * (((mean_speed) ** 2) / HEIGHT)) * distance_time * 60

def get_actual_message(calories_burned: float, storage_data: dict) -> str:
    """
    Return a message to the terminal depending on 
    the intensity of the workout.

    """

    distance = get_distance(get_step_day(storage_data))
    if distance >= 6.5:
        message = "Great result! The goal has been achieved."
    elif distance >= 3.9:
        message = "Not bad! It was a productive day."
    elif distance >= 2:
        message = "It's not enough, but we'll catch up tomorrow!"
    else:
        message = "Lying down is also useful. The main thing is participation, not victory!"   
    
    answer = ""
    answer += f"Time: {list(storage_data.keys())[-1]}.\n"
    answer += f"Today you have walked {get_step_day(storage_data)} steps.\n"
    answer += f"The walked distance is {distance:.2f} km.\n"
    answer += f"You spent {calories_burned:.2f} kilocalories\n" + message
    return  answer

def accept_package(data: tuple[str, int]) -> None:
    """
    The main function that brings everything together into a single whole. 
    In ideal case user must call only this function.

    """

    # Get data from file with name depend on today's date,
    # if theres no such file, we will create new one
    today_date, calories_burned, storage_data = load_data(str(dt.date.today()))    

    # storage_data is a dict consist of pairs (time: steps)
    # if our dict is empty we will add "fake" element in it
    # to have start point from which we will make our callory calculation 

    if len(storage_data) == 0:
        storage_data[str(dt.datetime.now().time().replace(microsecond=0))] = 0

    # We check the correction of input data - the data type and
    # time in input data must be greater than last time in dict
    # We don't do the last check if there is only one, "fake" 
    # value in the dictionary.
    # Then, we, update value of burned calories and add incoming data to
    # dict.

    if check_correct_data(data) and (check_correct_time(data[0], storage_data) or len(storage_data) == 1):
        calories_burned += get_spent_calories(storage_data, get_distance(data[1]), data[0])
        storage_data[str(data[0])] = data[1]

    # Print message about current status
    # in terminal: time, steps, distance, callories, motivate message.
        
    print(get_actual_message(calories_burned, storage_data))

    # Write data to file
    write_data(today_date, calories_burned, storage_data)

accept_package(("10:10:10", 100))

