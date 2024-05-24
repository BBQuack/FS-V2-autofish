import pyautogui
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageChops, Image, ImageTk
import time
import threading
import numpy as np
import keyboard

class AutoFisher:
    def __init__(self, master):
        self.master = master
        self.master.title("Firestone V2 AutoFisher")
        
        # Title and description
        self.title_label = tk.Label(master, text="Firestone V2 AutoFisher", font=("Helvetica", 16, "bold"))
        self.description_label = tk.Label(master, text="Stand on the edge of a dock and look at the water in 1st person. Use lowest Roblox's Graphic Quality. I recommend using center boundary. Ensure the bobber is visible in boundary at towards bottom. Press f4 to start. \n Debugging: If it is clicking too soon, increase white percentage. \n Notes: Does not work in rain, go under a bridge .not a 100% reliable fisher. Version 0.01", font=("Helvetica", 10))
        self.status = tk.StringVar()
        self.status.set("Inactive")
        self.change_percentage_var = tk.StringVar()
        self.change_percentage_var.set("White Percentage: 0.0%")
        self.threshold = 0.06  # Default threshold
        self.BWthreshold = 128

        # Create GUI elements
        self.start_button = tk.Button(master, text="Start", command=self.start)
        self.stop_button = tk.Button(master, text="Stop", command=self.stop)
        self.boundary_button = tk.Button(master, text="Set Boundary by Click", command=self.set_boundary)
        self.center_boundary_button = tk.Button(master, text="Set Center Boundary", command=self.set_center_boundary)
        self.view_boundary_button = tk.Button(master, text="View Boundary", command=self.view_boundary)
        self.status_label = tk.Label(master, textvariable=self.status)
        self.change_label = tk.Label(master, textvariable=self.change_percentage_var)
        
        # Entry fields for manual boundary input
        self.entry_label = tk.Label(master, text="Or enter boundary coordinates:")
        self.top_left_label = tk.Label(master, text="Top-Left (x, y):")
        self.bottom_right_label = tk.Label(master, text="Bottom-Right (x, y):")

        self.top_left_x = tk.Entry(master, width=5)
        self.top_left_y = tk.Entry(master, width=5)
        self.bottom_right_x = tk.Entry(master, width=5)
        self.bottom_right_y = tk.Entry(master, width=5)

        self.set_boundary_button = tk.Button(master, text="Set Boundary Manually", command=self.set_manual_boundary)

        # Entry field for change percentage threshold
        self.threshold_label = tk.Label(master, text="White Percentage Threshold:")
        self.threshold_entry = tk.Entry(master, width=5)
        self.threshold_entry.insert(0, str(self.threshold))

        self.set_threshold_button = tk.Button(master, text="Set Threshold", command=self.set_threshold)

        # Slider for bubble threshold
        self.bubble_threshold_label = tk.Label(master, text="Bubble BW Threshold:")
        self.bubble_threshold_slider = tk.Scale(master, from_=0, to=255, orient=tk.HORIZONTAL, command=self.update_threshold)

        # Label to show black and white image
        self.bw_image_label = tk.Label(master)

        # Layout GUI elements
        self.title_label.pack(pady=10)
        self.description_label.pack(pady=5)
        self.start_button.pack()
        self.stop_button.pack()
        self.boundary_button.pack()
        self.center_boundary_button.pack()
        self.entry_label.pack()

        # Create a frame for the manual boundary input
        boundary_frame = tk.Frame(master)
        self.top_left_label.pack(in_=boundary_frame, side=tk.LEFT)
        self.top_left_x.pack(in_=boundary_frame, side=tk.LEFT)
        self.top_left_y.pack(in_=boundary_frame, side=tk.LEFT)
        self.bottom_right_label.pack(in_=boundary_frame, side=tk.LEFT)
        self.bottom_right_x.pack(in_=boundary_frame, side=tk.LEFT)
        self.bottom_right_y.pack(in_=boundary_frame, side=tk.LEFT)
        self.set_boundary_button.pack(in_=boundary_frame, side=tk.LEFT)
        boundary_frame.pack(pady=5)

        self.view_boundary_button.pack()
        self.threshold_label.pack()
        self.threshold_entry.pack()
        self.set_threshold_button.pack()
        self.bubble_threshold_label.pack()
        self.bubble_threshold_slider.pack()
        self.status_label.pack()
        self.change_label.pack()
        self.bw_image_label.pack()

        self.running = False
        self.boundary = None
        self.boundary_overlay = None

        # Set up hotkey
        keyboard.add_hotkey('f4', self.toggle)

    def update_threshold(self, value):
        self.BWthreshold = float(value)

    def set_boundary(self):
        messagebox.showinfo("Set Boundary", "Click on the top-left corner of the boundary.")
        self.master.withdraw()
        time.sleep(2)
        top_left = pyautogui.position()
        messagebox.showinfo("Set Boundary", "Now click on the bottom-right corner of the boundary.")
        time.sleep(2)
        bottom_right = pyautogui.position()
        self.master.deiconify()
        self.boundary = (top_left.x, top_left.y, bottom_right.x, bottom_right.y)
        messagebox.showinfo("Boundary Set", f"Boundary has been set: {self.boundary}")

    def set_manual_boundary(self):
        try:
            top_left_x = int(self.top_left_x.get())
            top_left_y = int(self.top_left_y.get())
            bottom_right_x = int(self.bottom_right_x.get())
            bottom_right_y = int(self.bottom_right_y.get())
            self.boundary = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
            messagebox.showinfo("Boundary Set", f"Boundary has been set: {self.boundary}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid integer coordinates.")

    def set_threshold(self):
        try:
            self.threshold = float(self.threshold_entry.get())
            messagebox.showinfo("Threshold Set", f"White percentage threshold has been set to: {self.threshold * 100}%")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid float value.")

    def start(self):
        if not self.boundary:
            messagebox.showwarning("No Boundary", "Please set the boundary first.")
            return
        self.running = True
        self.status.set("Active - Casting")
        self.thread = threading.Thread(target=self.autofish)
        self.thread.start()

    def stop(self):
        self.running = False
        self.status.set("Inactive")

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def autofish(self):
        while self.running:
            pyautogui.click()  # Click to cast
            self.status.set("Active - Waiting for Fish")
            time.sleep(1)
            initial_image = ImageGrab.grab(bbox=self.boundary)
            initial_image_np = np.array(initial_image)

            # Adjust threshold to ensure over 80% of the image is black
            self.adjust_threshold(initial_image_np)
            time.sleep(2)
            while self.running:
                current_image = ImageGrab.grab(bbox=self.boundary)
                current_image_np = np.array(current_image)
                change_percentage = self.image_changed(initial_image_np, current_image_np)
                self.change_percentage_var.set(f"White Percentage: {change_percentage * 100:.2f}%")
                if change_percentage > .9:
                    initial_image = ImageGrab.grab(bbox=self.boundary)
                    initial_image_np = np.array(initial_image)
                    self.adjust_threshold(initial_image_np)
                    time.sleep(.5)
                    change_percentage = self.image_changed(initial_image_np, current_image_np)
                    
                if change_percentage > self.threshold:
                    self.status.set("Active - Catching")
                    pyautogui.click()  # Click to catch
                    time.sleep(1)
                    break
                time.sleep(0.5)

            self.status.set("Active - Delay Between Casts")
            time.sleep(2)  # Wait before casting again

        self.status.set("Inactive")

    def adjust_threshold(self, image):
        for threshold in range(256):
            gray_image = np.mean(image, axis=2)
            bw_image = (gray_image > threshold).astype(np.uint8) * 255
            black_percentage = np.sum(bw_image == 0) / bw_image.size
            if black_percentage >= 0.9:
                self.BWthreshold = threshold
                self.bubble_threshold_slider.set(threshold)
                break

    def image_changed(self, img1, img2):
        # Save original img1 and img2 as png files
        img1_pil = Image.fromarray(img1)
        img2_pil = Image.fromarray(img2)
        img1_pil.save('original_img1.png')
        img2_pil.save('original_img2.png')

        # Convert images to grayscale
        img1_gray = np.mean(img1, axis=2)
        img2_gray = np.mean(img2, axis=2)

        # Apply a binary threshold to convert to black and white
        img1_bw = (img1_gray > self.BWthreshold).astype(np.uint8) * 255
        img2_bw = (img2_gray > self.BWthreshold).astype(np.uint8) * 255

        # Convert back to PIL images
        img1_bw_pil = Image.fromarray(img1_bw)
        img2_bw_pil = Image.fromarray(img2_bw)
        
        # Save the black and white images as png files
        img1_bw_pil.save('bw_img1.png')
        img2_bw_pil.save('bw_img2.png')

        # Update the GUI to show the black and white image
        img2_bw_tk = ImageTk.PhotoImage(img2_bw_pil)
        self.bw_image_label.configure(image=img2_bw_tk)
        self.bw_image_label.image = img2_bw_tk

        # Calculate the change percentage based on white pixels
        white_pixels = np.sum(img2_bw == 255)
        total_pixels = img2_bw.size
        change_percentage = white_pixels / total_pixels
        return change_percentage
    
    def set_center_boundary(self):
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width / 2, screen_height / 2
        radius = min(screen_width, screen_height) * 0.05
        left = int(center_x - radius)
        top = int(center_y - radius - radius)
        right = int(center_x + radius)
        bottom = int(center_y + radius - radius)
        self.boundary = (left, top, right, bottom)
        messagebox.showinfo("Boundary Set", f"Center boundary has been set: {self.boundary}")

    def view_boundary(self):
        if self.boundary:
            if self.boundary_overlay and self.boundary_overlay.winfo_exists():
                self.boundary_overlay.destroy()
            self.boundary_overlay = tk.Toplevel(self.master)
            self.boundary_overlay.geometry(f"{self.boundary[2] - self.boundary[0]}x{self.boundary[3] - self.boundary[1]}+{self.boundary[0]}+{self.boundary[1]}")
            self.boundary_overlay.overrideredirect(True)
            self.boundary_overlay.attributes("-alpha", 0.3)
            self.boundary_overlay.config(bg='red')
        else:
            messagebox.showwarning("No Boundary", "Please set the boundary first.")

root = tk.Tk()
auto_fisher = AutoFisher(root)
root.mainloop()
