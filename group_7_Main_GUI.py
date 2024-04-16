import tkinter as tk
import subprocess

def open_manual_publishing():
    # TO run the single editable publishing script
    subprocess.Popen(["python", "./mqtt-single/group_7_publisher_GUI.py"])
    subprocess.Popen(["python", "./mqtt-single/group_7_subscriber_GUI.py"])

def open_automatic_publishing():
    # TO run the multiple publishing script
    subprocess.Popen(["python", "./mqtt_multiple/group_7_publisher_GUI.py"])
    subprocess.Popen(["python", "./mqtt_multiple/group_7_subscriber_GUI.py"])

def setup_gui():
    root = tk.Tk()
    # Configure the main window
    root.resizable(True, False)
    root.title("COMP216 Final Project - Group 7")

    # Set the window size
    window_width = 380
    window_height = 250
    root.geometry(f"{window_width}x{window_height}")

    # Get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Find the center position
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    # Set the position of the window to the center of the screen
    root.geometry(f'+{center_x}+{center_y}')

    label1 = tk.Label(root, text="Health Monitoring System")
    label1.grid(row=0, column=0, columnspan=3, padx=10, pady=(30, 0))
    label2 = tk.Label(root, text="by Aileen Salcedo and Tessa Mathew")
    label2.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 20))
    label3 = tk.Label(root, text="Select the type of publishing:")
    label3.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 20))

    # Single publishing button
    single_button = tk.Button(root, text="Single Publishing", command=open_manual_publishing)
    single_button.grid(row=3, column=0, padx=20, pady=10, ipadx=20, ipady=20)

    # Multiple publishing button
    multiple_button = tk.Button(root, text="Multiple Publishing", command=open_automatic_publishing)
    multiple_button.grid(row=3, column=1, padx=20, pady=10, ipadx=20, ipady=20)

    root.mainloop()

if __name__ == "__main__":
    setup_gui()
