# pomodoro_timer/cli.py

import time
import threading
import datetime
import json
import os
import typer
from typing import Optional

app = typer.Typer()

class PomodoroTimer:
    def __init__(self, task_name: str, duration: int = 25 * 60):
        self.task_name = task_name
        self.total_duration = duration  # Total duration in seconds
        self.remaining_time = duration
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.timer_thread = None
        self.lock = threading.Lock()

    def start(self):
        if self.is_running:
            typer.echo("Timer is already running.")
            return
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.timer_thread = threading.Thread(target=self._run)
        self.timer_thread.start()
        typer.echo(f"Started Pomodoro for task: '{self.task_name}'")

    def _run(self):
        while self.remaining_time > 0 and self.is_running:
            with self.lock:
                if self.is_paused:
                    time.sleep(1)
                    continue
                time.sleep(1)
                self.remaining_time -= 1
                mins, secs = divmod(self.remaining_time, 60)
                timer_display = f"{mins:02d}:{secs:02d}"
                typer.echo(f"\rTime Remaining: {timer_display}", nl=False)
        if self.remaining_time <= 0:
            self.is_running = False
            typer.echo(f"\nPomodoro for task '{self.task_name}' completed!")
            self._log_completion()

    def pause(self):
        if not self.is_running or self.is_paused:
            typer.echo("Timer is not running or already paused.")
            return
        self.is_paused = True
        typer.echo("Timer paused.")
        return

    def resume(self):
        if not self.is_paused:
            typer.echo("Timer is not paused.")
            return
        self.is_paused = False
        typer.echo("Timer resumed.")
        return

    def stop(self):
        if not self.is_running:
            typer.echo("Timer is not running.")
            return
        self.is_running = False
        self.remaining_time = self.total_duration
        typer.echo("Timer stopped.")
        return

    def _log_completion(self):
        data = {
            'task_name': self.task_name,
            'completed_at': datetime.datetime.now().isoformat()
        }
        log_file = 'pomodoro_log.json'
        # Check if file exists and read existing data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        # Append new data and write back to file
        logs.append(data)
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=4)
        typer.echo("Pomodoro session logged.")
        return

# Global variable to hold the current timer instance
current_timer: Optional[PomodoroTimer] = None

# Define your Typer commands here
@app.command()
def start(task: str, duration: int = typer.Option(25, help="Duration in minutes")):
    """
    Start a Pomodoro timer for a given TASK with an optional DURATION.
    """
    global current_timer
    if current_timer and current_timer.is_running:
        typer.echo("A timer is already running. Please stop it before starting a new one.")
        raise typer.Exit()
    current_timer = PomodoroTimer(task_name=task, duration=duration * 60)
    current_timer.start()

@app.command()
def pause():
    """
    Pause the currently running Pomodoro timer.
    """
    if current_timer:
        current_timer.pause()
    else:
        typer.echo("No timer is currently running.")

@app.command()
def resume():
    """
    Resume the paused Pomodoro timer.
    """
    if current_timer:
        current_timer.resume()
    else:
        typer.echo("No timer is currently running.")

@app.command()
def stop():
    """
    Stop the currently running Pomodoro timer.
    """
    if current_timer:
        current_timer.stop()
    else:
        typer.echo("No timer is currently running.")

@app.command()
def status():
    """
    Show the status of the current Pomodoro timer.
    """
    if current_timer and current_timer.is_running:
        mins, secs = divmod(current_timer.remaining_time, 60)
        timer_display = f"{mins:02d}:{secs:02d}"
        typer.echo(f"Timer for task '{current_timer.task_name}' is running. Time remaining: {timer_display}")
    else:
        typer.echo("No timer is currently running.")

@app.command()
def log():
    """
    Display the log of completed Pomodoro sessions.
    """
    log_file = 'pomodoro_log.json'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
                if logs:
                    typer.echo("Pomodoro Log:")
                    for entry in logs:
                        completed_at = datetime.datetime.fromisoformat(entry['completed_at'])
                        typer.echo(f"- {entry['task_name']} completed at {completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    typer.echo("No Pomodoro sessions have been completed yet.")
            except json.JSONDecodeError:
                typer.echo("Log file is corrupted.")
    else:
        typer.echo("No log file found.")

def main():
    app()

if __name__ == "__main__":
    main()
