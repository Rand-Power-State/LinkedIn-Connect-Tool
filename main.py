import requests
import subprocess
import os
import sys
import threading
import re
import zipfile
import customtkinter as ctk
from tkinter import messagebox

REQUIRED_PACKAGES = ["selenium", "requests"]

KILL_SWITCH_URL = "https://raw.githubusercontent.com/ark-lesedium/kill-switch/main/killswitch.txt"
APP_ICON = "icon.ico"  # We will remove this usage

# Agreement disclaimer
def show_agreement():
    agreement_text = (
        "DISCLAIMER:\n\n"
        "This script is intended for educational or personal use only. "
        "Using this script to interact with LinkedIn or any of its services may "
        "violate LinkedIn's Terms of Service.\n\n"
        "By clicking 'OK', you accept full responsibility."
    )
    return messagebox.askokcancel("User Agreement", agreement_text)

# Check kill switch
def check_kill_switch():
    try:
        response = requests.get(KILL_SWITCH_URL)
        if response.status_code == 200:
            if "enabled" in response.text.lower():
                messagebox.showerror("Notice", "Setup disabled by developer.")
                return False
            return True
    except:
        messagebox.showerror("Error", "Unable to check kill switch. Please check your connection.")
    return False

# Check if setup has already been completed
def check_if_setup_done():
    return os.path.exists("credentials.json") and os.path.exists("chromedriver.exe")

# Setup window class
class SetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup Requirements")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.status_label = ctk.CTkLabel(root, text="Initializing setup...", font=("Segoe UI", 16))
        self.status_label.pack(pady=30)

        self.progress = ctk.CTkProgressBar(root, width=400)
        self.progress.pack(pady=20)
        self.progress.set(0)

        self.start_button = ctk.CTkButton(root, text="Start Setup", command=self.start_setup)
        self.start_button.pack(pady=30)

    def start_setup(self):
        self.start_button.configure(state="disabled")
        threading.Thread(target=self.run_setup, daemon=True).start()

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.configure(text=message))

    def update_progress(self, value):
        self.root.after(0, lambda: self.progress.set(value))

    def install_packages(self):
        total = len(REQUIRED_PACKAGES)
        for idx, package in enumerate(REQUIRED_PACKAGES, 1):
            try:
                __import__(package)
                self.update_status(f"{package} already installed.")
            except ImportError:
                self.update_status(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            self.update_progress(idx / total * 0.2)

    def get_chrome_version(self):
        try:
            self.update_status("Detecting Chrome version...")
            process = subprocess.Popen(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True
            )
            result = process.communicate()[0].decode('utf-8')
            version = re.search(r'VERSION\s+REG_SZ\s+([\d.]+)', result, re.IGNORECASE)
            if version:
                return version.group(1)
        except:
            pass
        return None

    def fetch_driver_version(self, chrome_version):
        major_version = chrome_version.split('.')[0]
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        return None

    def download_driver(self, driver_version):
        self.update_status("Downloading ChromeDriver...")
        download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
        response = requests.get(download_url)
        with open("chromedriver.zip", "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile("chromedriver.zip", 'r') as zip_ref:
            zip_ref.extractall()

        os.remove("chromedriver.zip")
        self.update_status("ChromeDriver installed.")
        self.update_progress(0.8)

    def run_setup(self):
        try:
            self.install_packages()

            if not os.path.exists("chromedriver.exe"):
                chrome_version = self.get_chrome_version()
                if not chrome_version:
                    messagebox.showerror("Error", "Chrome not found.")
                    self.root.quit()
                    return

                driver_version = self.fetch_driver_version(chrome_version)
                if not driver_version:
                    messagebox.showerror("Error", "No compatible ChromeDriver found.")
                    self.root.quit()
                    return

                self.download_driver(driver_version)
            else:
                self.update_status("ChromeDriver already present.")

            self.update_progress(1.0)
            messagebox.showinfo("Done", "Setup complete. Launching App...")
            subprocess.Popen([sys.executable, "gui_launcher.py"])
            self.root.quit()

        except Exception as e:
            messagebox.showerror("Setup Error", str(e))
            self.root.quit()

# Entry point
if __name__ == "__main__":
    if check_kill_switch():
        if check_if_setup_done():
            messagebox.showinfo("Setup Skipped", "Setup already completed. Launching app...")
            subprocess.Popen([sys.executable, "gui_launcher.py"])
        else:
            root = ctk.CTk()
            if show_agreement():
                app = SetupApp(root)
                root.mainloop()
