import time
import json
import threading

# class TimerThread(threading.Thread):
#     active_threads = []

#     def __init__(self, duration, athlete_data):
#         super().__init__()
#         self.duration = duration
#         self.athlete_data = athlete_data
#         self.timer_running = True
#         self.start_time = None

#     def run(self):
#         self.start_time = time.time()
#         while self.timer_running:
#             elapsed_time = time.time() - self.start_time
#             minutes, seconds = divmod(int(elapsed_time), 60)
#             self.update_timer_data(minutes, seconds)
#             time.sleep(1)

#             if elapsed_time >= self.duration:
#                 break

#         print("Timer completed!")

#     def update_timer_data(self, minutes, seconds):
#         flat_athlete_data = {
#             'time': f"{minutes}:{seconds:02d}",
#             **self.athlete_data
#         }
#         timer_data = []
#         timer_data.append(flat_athlete_data)
#         with open("timer_data.json", 'w') as json_file:
#             json.dump(timer_data, json_file)

#     def stop_timer(self):
#         self.timer_running = False



import time
import threading
import json

class TimerThread(threading.Thread):
    active_threads = []
    timer_data = []

    def __init__(self, duration, athlete_data):
        super().__init__()
        self.duration = duration
        self.athlete_data = athlete_data
        self.timer_running = True
        self.start_time = None

    def run(self):
        self.start_time = time.time()
        while self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            self.update_timer_data(minutes, seconds)
            time.sleep(1)

            if elapsed_time >= self.duration:
                break

        print("Timer completed!")

    def update_timer_data(self, minutes, seconds):
        flat_athlete_data = {
            'time': f"{minutes}:{seconds:02d}",
            **self.athlete_data
        }
        # TimerThread.timer_data.append(flat_athlete_data)
        with open("timer_data.json", 'w') as json_file:
            json.dump(flat_athlete_data, json_file)

    def stop_timer(self):
        self.timer_running = False

    @classmethod
    def start_timer(cls, duration, athlete_data):
        timer_thread = TimerThread(duration, athlete_data)
        cls.active_threads.append(timer_thread)
        timer_thread.start()
        return timer_thread

    @classmethod
    def stop_all_timers(cls):
        for timer_thread in cls.active_threads:
            timer_thread.stop_timer()
            timer_thread.join()
        cls.active_threads = []

    @classmethod
    def save_timer_data(cls):
        with open("timer_data.json", 'w') as json_file:
            json.dump(cls.timer_data, json_file)

def start_timer(duration, athlete_data):
    timer_thread = TimerThread(duration, athlete_data)
    timer_thread.start()
    return timer_thread

def stop_timer():
    TimerThread.stop_all_timers()

# Example usage:
# athlete_data_example = {'name': 'John Doe', 'sport': 'Running'}
# timer_thread_example = TimerThread.start_timer(300, athlete_data_example)
# print('Ok?')
# time.sleep(10)  # Let the timer run for 10 seconds (in a real scenario, you might have your application logic)
# TimerThread.stop_all_timers()
