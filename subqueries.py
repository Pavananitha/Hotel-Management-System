import tkinter as tk

class SubqueriesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        back_button = tk.Button(self, text="← Back",  command=lambda: controller.show_frame("HomePage"),
                                font=("Arial", 12), bd=0, bg="#ecf0f1", fg="black")
        back_button.place(x=10, y=10)

        title = tk.Label(self, text="SubQueries & Nested Queries Page", font=("Arial", 24, "bold"))
        title.place(x=50, y=50)

        self.create_view_buttons()  # <-- This must exist!

    def create_view_buttons(self):
        buttons = [
            ("Above Average Salary Salary", lambda: self.controller.show_frame("AboveAverageSalaryPage")),
            ("Rooms are Reserved but not yet paid", lambda: self.controller.show_frame("UnpaidRoomsPage")),
            ("guests who booked expensive EventHall", lambda: self.controller.show_frame("ExpensiveHallGuestPage")),
            ("Guest given feedback 5", lambda: self.controller.show_frame("QualifiedFeedbackGuestsPage")),
            ("guests who paid more than 2 different services", lambda: self.controller.show_frame("QualifiedFeedbackGuestsPage")),
            # ("Feedback", lambda: None),
            # ("Room Reservation", lambda: None),
        ]

        y_position = 150
        button_width = 500
        button_height = 40

        for index, (button_name, command) in enumerate(buttons):
            button = tk.Button(self, text=button_name, font=("Arial", 14),
                               width=20, height=2, bg="#27ae60", command=command)
            button.place(x=50, y=y_position + (index * (button_height + 10)),
                         width=button_width, height=button_height)
            self.set_cursor_on_hover(button)

    def set_cursor_on_hover(self, button):
        def on_enter(e):
            e.widget.config(bg="#1e8449", cursor="hand2")
        def on_leave(e):
            e.widget.config(bg="#27ae60", cursor="arrow")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
