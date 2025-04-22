import customtkinter as ctk
from tkinter import messagebox
import json
import os
import subprocess
import sys

# Initialize CustomTkinter app
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("LinkedIn Auto-Connector")
app.geometry("400x550")

TASK_NAME = "LinkedInAutomationBot"

def schedule_task():
    python_path = sys.executable
    script_path = os.path.abspath("linkedin_bot.py")

    selected_hour = hour_combo.get()
    selected_minute = minute_combo.get()

    if not selected_hour or not selected_minute:
        messagebox.showwarning("Input Error", "Please select a time for scheduling.")
        return

    schedule_time = f"{selected_hour}:{selected_minute}"

    task_command = f'schtasks /create /tn {TASK_NAME} /tr "{python_path} {script_path}" /sc daily /st {schedule_time} /f'

    try:
        subprocess.run(task_command, check=True, shell=True)
        messagebox.showinfo("Success", f"Task successfully scheduled daily at {schedule_time}.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to schedule the task. Please try again.")
        return

    save_credentials_to_json()

def save_credentials_to_json():
    credentials = {
        "email": email_entry.get(),
        "password": password_entry.get(),
        "search_query": search_entry.get(),
        "max_connections": connections_entry.get()
    }

    if not all(credentials.values()):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    with open('credentials.json', 'w') as f:
        json.dump(credentials, f)

    messagebox.showinfo("Credentials Saved", "Credentials and scheduled task have been saved.")
    app.quit()

def view_task():
    # Query task info
    task_query_cmd = f'schtasks /query /tn {TASK_NAME}'
    result = subprocess.run(task_query_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        messagebox.showinfo("Scheduled Task Info", result.stdout)
    else:
        messagebox.showwarning("No Task Found", f"No scheduled task named '{TASK_NAME}' was found.")

def delete_task():
    # Confirm deletion
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the task '{TASK_NAME}'?")
    if not confirm:
        return

    delete_command = f'schtasks /delete /tn {TASK_NAME} /f'
    result = subprocess.run(delete_command, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        messagebox.showinfo("Task Deleted", f"Task '{TASK_NAME}' has been deleted successfully.")
    else:
        messagebox.showwarning("Delete Failed", f"Could not find or delete the task '{TASK_NAME}'.")

# Email input
email_label = ctk.CTkLabel(app, text="Email:")
email_label.pack(pady=5)
email_entry = ctk.CTkEntry(app, width=300)
email_entry.pack()

# Password input
password_label = ctk.CTkLabel(app, text="Password:")
password_label.pack(pady=5)
password_entry = ctk.CTkEntry(app, width=300, show="*")
password_entry.pack()

# Search query input
search_label = ctk.CTkLabel(app, text="Search Query:")
search_label.pack(pady=5)
search_entry = ctk.CTkEntry(app, width=300)
search_entry.pack()

# Max connections input
connections_label = ctk.CTkLabel(app, text="Max Connections:")
connections_label.pack(pady=5)
connections_entry = ctk.CTkEntry(app, width=300)
connections_entry.insert(0, "80")
connections_entry.pack()

# Time scheduling section
time_label = ctk.CTkLabel(app, text="Schedule Time (24h format):")
time_label.pack(pady=10)

time_frame = ctk.CTkFrame(app, fg_color="transparent")
time_frame.pack(pady=5)

hour_combo = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(0, 24)], width=80)
hour_combo.set("16")
hour_combo.pack(side="left", padx=5)

minute_combo = ctk.CTkComboBox(time_frame, values=["00", "15", "30", "45"], width=80)
minute_combo.set("00")
minute_combo.pack(side="left", padx=5)

# Save and schedule button
save_button = ctk.CTkButton(app, text="Save Credentials & Schedule Task", command=schedule_task)
save_button.pack(pady=15)

# View scheduled task button
view_button = ctk.CTkButton(app, text="View Scheduled Task", command=view_task)
view_button.pack(pady=5)

# Delete scheduled task button
delete_button = ctk.CTkButton(app, text="Delete Scheduled Task", fg_color="#9E3D3D", hover_color="#B94D4D", command=delete_task)
delete_button.pack(pady=5)

app.mainloop()
