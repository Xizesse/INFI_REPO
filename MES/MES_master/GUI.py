import tkinter as tk
from tkinter import messagebox
import sys


class OPCUAClientGUI:
    def __init__(self, master, on_connect, on_disconnect):
        self.master = master
        self.really_count = 0
        self.day_count = 0
        self.order_queue = None
        master.title("MES Client Interface")
        master.configure(bg='lightgray')
        master.geometry("900x600")
        #COmentário

        # Add GUI elements
        self.connect_button = tk.Button(master, text="Connect", command=on_connect)
        self.connect_button.place(x=50, y=200)

        self.disconnect_button = tk.Button(master, text="Disconnect", command=on_disconnect)
        self.disconnect_button.place(x=50, y=230)

        self.status_label = tk.Label(master, text="Disconnected", fg="red")
        self.status_label.place(x=50, y=260)

        self.light_indicator = tk.Label(master, bg="grey", width=2, height=1)
        self.light_indicator.place(x=50, y=290)
        self.blinking = False

        # Day Count
        self.day_count_label = tk.Label(master, text=f"Day Count: {self.day_count}")
        self.day_count_label.pack()

        # Button to increment day count
        self.increment_button = tk.Button(master, text="Increment Day", command=self.increment_day_count)
        self.increment_button.pack()

        self.reset_button = tk.Button(master, text="Reset Day", command=self.reset_day_count)
        self.reset_button.pack()

        # Bind the window closing event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        #queue
        self.queue_display_label = tk.Label(master, text="Queue: Empty")
        self.queue_display_label.pack()

    def on_closing(self):
        self.really_quit(self.really_count)

    def really_quit(self, count):
        quit_string = "Do you "
        for i in range(count):
            quit_string += "really "
        quit_string += "want to quit?"
        
        if messagebox.askokcancel("Quit", quit_string):
            if self.really_count < 1:
                self.really_count += 1
                self.really_quit(self.really_count)
            else:
                self.master.destroy()
                sys.exit()

    def start_blinking(self):
        self.blinking = True
        self.blink()
    
    def stop_blinking(self):
       self.blinking = False
       self.light_indicator.config(bg="grey")  # Reset to default color when not blinking

    def blink(self):
        if self.blinking:
            current_color = self.light_indicator.cget("bg")
            new_color = "green" if current_color == "grey" else "grey"
            self.light_indicator.config(bg=new_color)
            self.master.after(300, self.blink)  # Schedule next blink

    def increment_day_count(self):
        self.day_count += 1
        self.day_count_label.config(text=f"Day Count: {self.day_count}")
        #print(f"Day Count incremented to {self.day_count}")

    def reset_day_count(self):
        self.day_count = 0
        self.day_count_label.config(text=f"Day Count: {self.day_count}")
        print("Day Count reset to 0")

    def update_queue(self):
        # Update the queue display based on the current items in the queue
        if self.order_queue.empty():
            self.queue_display_label.config(text="Queue: Empty")
        else:
            queue_contents = list(self.order_queue.queue)
            self.queue_display_label.config(text=f"Queue: {queue_contents}")

    def set_queue(self, queue):
        self.order_queue = queue
        self.update_queue()