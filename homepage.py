import tkinter as tk
from tkinter import PhotoImage

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#bdc3c7")  # Set frame background color to gray
        self.controller = controller


        # Title
        title = tk.Label(self, text="Welcome to ITC Grand Hotel", font=("Arial", 28, "bold"), fg="#2980b9", bg="#bdc3c7")
        title.pack(pady=30)

        # Description text
        description_text = (
            "Experience the epitome of luxury and hospitality at ITC Grand Hotel.\n"
            "We offer world-class amenities, elegant rooms, fine dining, and \n"
            "impeccable service to ensure an unforgettable stay.\n\n"
            "Key Features:\n"
            "• Luxurious Rooms and Suites with Modern Amenities\n"
            "• Multi-cuisine Restaurants and Private Dining Options\n"
            "• State-of-the-art Conference and Banquet Halls\n"
            "• Wellness Spa, Fitness Center, and Pool\n"
            "• 24x7 Concierge, Room Service, and Transportation\n"
            "• Eco-friendly and Sustainable Hospitality Practices\n"
            "• Personalized Guest Services & Digital Room Management"
        )

        description = tk.Label(self, text=description_text, font=("Arial", 18), fg="#2980b9", bg="#bdc3c7", justify="left", anchor="w")
        description.pack(padx=50, pady=10, anchor="w")

        # Optional: Add a hotel quote or tagline
        quote = tk.Label(self, text="“Luxury redefined — where comfort meets elegance.”", font=("Arial", 20, "italic"),
                         fg="#2980b9", bg="#bdc3c7")
        quote.pack(pady=10)

        # # Optional: Add a back button to navigate to the home page (or previous page)
        # back_button = tk.Button(self, text="← Back", command=self.controller.go_back,
        #                         font=("Arial", 12), bd=0, bg="#ecf0f1", fg="black")
        # back_button.pack(pady=20)

