import tkinter as tk
from tkinter import ttk
from conn import create_connection, close_connection
import mysql.connector

class ShowReservationFrame(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        title = tk.Label(self, text="Reservation Details (Using Cursor)", bg="white",
                         font=("Arial", 18, "bold"))
        title.pack(pady=20)

        # Treeview widget to display reservation data
        self.tree = ttk.Treeview(self, columns=(
            "ReservationID", "GuestID", "GuestName", "RoomID", "CheckInDate",
            "CheckOutDate", "TotalNights", "TotalPrice", "PaymentStatus"
        ), show="headings")

        # Define headings
        headings = [
            "ReservationID", "GuestID", "GuestName", "RoomID", "CheckInDate",
            "CheckOutDate", "TotalNights", "TotalPrice", "PaymentStatus"
        ]
        for col in headings:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load data
        self.load_reservation_data()

    def load_reservation_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Call the stored procedure
            cursor.callproc('ShowReservationDetails')

            # Since each FETCH in the procedure does a SELECT, each result is a separate result set.
            # Loop through all result sets from the procedure call
            for result in cursor.stored_results():
                for row in result.fetchall():
                    self.tree.insert('', 'end', values=row)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            if cursor:
                cursor.close()
            close_connection(conn)
