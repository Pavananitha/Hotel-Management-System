import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class ExpensiveHallGuestPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("SubqueriesPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        title = tk.Label(self, text="Guests Who Booked the Most Expensive Event Hall",
                         bg="black", font=("Arial", 16, "bold"))
        title.pack(pady=20)

        # Table frame
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

        # Treeview
        self.guest_table = ttk.Treeview(table_frame,
                                        columns=("GuestID", "Name", "DOB", "Gender", "AadharNo", "PricePerHour"),
                                        xscrollcommand=scroll_x.set,
                                        yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.guest_table.xview)
        scroll_y.config(command=self.guest_table.yview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.guest_table.pack(fill=tk.BOTH, expand=True)

        # Define headings
        self.guest_table.heading("GuestID", text="Guest ID")
        self.guest_table.heading("Name", text="Name")
        self.guest_table.heading("DOB", text="DOB")
        self.guest_table.heading("Gender", text="Gender")
        self.guest_table.heading("AadharNo", text="Aadhar No")
        self.guest_table.heading("PricePerHour", text="Hall Price/Hour")

        self.guest_table["show"] = "headings"

        # Column widths
        for col in self.guest_table["columns"]:
            self.guest_table.column(col, width=150)

        self.fetch_data()

    def fetch_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            query = """
                SELECT g.GuestID, g.Name, g.DOB, g.Gender, g.AadharNo, e.PricePerHour
                FROM Guest g
                JOIN EventBooking eb ON g.GuestID = eb.GuestID
                JOIN EventHall e ON eb.HallID = e.HallID
                WHERE e.PricePerHour = (
                    SELECT MAX(PricePerHour) FROM EventHall
                );
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            self.guest_table.delete(*self.guest_table.get_children())

            for row in rows:
                self.guest_table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data:\n{e}")
        finally:
            close_connection(conn)
