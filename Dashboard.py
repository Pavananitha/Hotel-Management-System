import tkinter as tk
# Dashboard.py
from cursor import CursorPage  # This imports the CursorPage class from cursor.py
from view import ViewsPage  # Import ViewsPage
from itcfeatures import ITCFeaturesPage  # Import the class
from reservation import ReservationPage
from driversinfo import DriverInfoPage
from homepage import HomePage
from subqueries import SubqueriesPage
from employeesinfo import EmployeeDetailsPage
from guestinfo import GuestDetailsPage
from eventbookingdetails import EventBookingDetailsPage
from tkinter import messagebox
from roomdetails import RoomDetailsPage
from eventhalldetails import EventHallDetailsPage
from foodmenu import FoodMenuDetailsPage
from drivermanagement import DriverManagerPage
from employeemanagement import EmployeePage
from eventhallmanagement import EventHallPage
from GuestManagement import GuestPage
from menumanagement import MenuPage
from restaurantmanager import RestaurantManagePage
from roommanagement import RoomManagePage
from eventhallbooking import EventHallBooking
from orderfood import FoodOrderPage
from parkingbooking import ParkingBooking
from payments import PaymentPage
from checkout import CheckOut
from roomreservation import RoomReservation
from feedback import Feedback
from cursor4 import LongStayGuests
from cursor2 import RevenueFrame
from cursor1 import GuestDetailsVip
from cursor3 import AvailableSpacesPage
from cursor5 import UnpaidBillsPage
from cursor6 import ShowReservationFrame
from subquery1 import AboveAverageSalaryPage
from subquery2 import UnpaidRoomsPage
from subquery3 import ExpensiveHallGuestPage
from subquery4 import GuestFeedRating5
from subquery5 import QualifiedFeedbackGuestsPage

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ITC HOTEL")

        # Get full screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        self.configure(bg="white")

        # Allow resize (maximize/minimize)
        self.resizable(True, True)
        # Sidebar
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        # Main container for pages
        self.container = tk.Frame(self, bg="#ecf0f1")
        self.container.pack(side="right", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)


        # Frame manager
        self.frames = {}
        self.history = []
        self.current_page = None

        # Load your custom pages here
        # Example: from homepage import HomePage
        # self.add_page("HomePage", HomePage)
        self.add_page("CursorPage", CursorPage)
        self.add_page("ViewsPage", ViewsPage)
        self.add_page("DriverInfoPage", DriverInfoPage)
        self.add_page("ITCFeaturesPage", ITCFeaturesPage)
        self.add_page("ReservationPage", ReservationPage)
        self.add_page("HomePage", HomePage)
        self.add_page("SubqueriesPage", SubqueriesPage)
        self.add_page("EmployeeDetailsPage", EmployeeDetailsPage)
        self.add_page("GuestDetailsPage", GuestDetailsPage)
        self.add_page("EventBookingDetailsPage", EventBookingDetailsPage)
        self.add_page("RoomDetailsPage", RoomDetailsPage)
        self.add_page("EventHallDetailsPage", EventHallDetailsPage)
        self.add_page("FoodMenuDetailsPage", FoodMenuDetailsPage)
        self.add_page("DriverManagerPage", DriverManagerPage)
        self.add_page("EmployeePage", EmployeePage)
        self.add_page("EventHallPage", EventHallPage)
        self.add_page("GuestPage", GuestPage)
        self.add_page("MenuPage", MenuPage)
        self.add_page("RestaurantManagePage", RestaurantManagePage)
        self.add_page("RoomManagePage", RoomManagePage)
        self.add_page("EventHallBooking", EventHallBooking)
        self.add_page("FoodOrderPage", FoodOrderPage)
        self.add_page("ParkingBooking", ParkingBooking)
        self.add_page("PaymentPage", PaymentPage)
        self.add_page("CheckOut", CheckOut)
        self.add_page("RoomReservation", RoomReservation)
        self.add_page("Feedback", Feedback)
        self.add_page("LongStayGuests", LongStayGuests)
        self.add_page("RevenueFrame", RevenueFrame)
        self.add_page("GuestDetailsVip", GuestDetailsVip)
        self.add_page("AvailableSpacesPage", AvailableSpacesPage)
        self.add_page("UnpaidBillsPage", UnpaidBillsPage)
        self.add_page("ShowReservationFrame", ShowReservationFrame)
        self.add_page("AboveAverageSalaryPage", AboveAverageSalaryPage)
        self.add_page("UnpaidRoomsPage", UnpaidRoomsPage)
        self.add_page("ExpensiveHallGuestPage", ExpensiveHallGuestPage)
        self.add_page("GuestFeedRating5", GuestFeedRating5)
        self.add_page("QualifiedFeedbackGuestsPage", QualifiedFeedbackGuestsPage)
        

        self.create_sidebar()

    def create_sidebar(self):
        """Sidebar buttons go here — customize as needed."""
        tk.Label(self.sidebar, text="Dashboard", bg="#2c3e50", fg="white", font=("Arial", 18, "bold")).pack(pady=20)

        # Add your sidebar buttons like this:
        self.add_sidebar_button("Exit", "Exit")
        self.add_sidebar_button("HomePage", "HomePage")
        self.add_sidebar_button("Joins, Where", "ITCFeaturesPage")
        self.add_sidebar_button("Triggers,simple queries", "ReservationPage")
        self.add_sidebar_button("View", "ViewsPage")
        self.add_sidebar_button("Cursor", "CursorPage")
        self.add_sidebar_button("Nested Queries", "SubqueriesPage")

        

    def add_sidebar_button(self, text, page_name):
        if text == "Exit":
            command = self.quit  # Closes the application
        else:
            command = lambda: self.show_frame(page_name)
        
        btn = tk.Button(self.sidebar, text=text, font=("Arial", 14), width=20, pady=10,
                        bg="#34495e", activebackground="#34495e", bd=0, command=command)

        if text == "Exit":
            btn.pack(side="bottom", pady=20)
        else:
            btn.pack(pady=5)


    def add_page(self, name, page_class):
        """Register and load a page."""
        frame = page_class(parent=self.container, controller=self)
        self.frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        if not self.current_page:
            self.show_frame(name)

    def show_frame(self, name):
        """Display the specified page."""
        if self.current_page and self.current_page != name:
            self.history.append(self.current_page)
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            self.current_page = name

    def go_back(self):
        """Go to the previous page."""
        if self.history:
            prev_page = self.history.pop()
            self.show_frame(prev_page)

  # Cursor page
    def set_cursor_on_hover(self, button):
        """Set cursor to hand2 on hover and back to arrow on leave."""
        def on_enter(e):
            e.widget.config(bg="#34495e", cursor="hand2")  # Hover effect (hand cursor)

        def on_leave(e):
            e.widget.config(bg="#2c3e50", cursor="arrow")  # Reset to normal cursor

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        # cursor page end.

if __name__ == "__main__":
    app = Dashboard()
    # Register the CursorPage and add it
    app.add_page("CursorPage", CursorPage)
    app.mainloop()
