import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class EventHallBooking(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.selected_hall = None
        self.selected_guest = None
        self.setup_widgets()
        self.load_eventhalls()
        self.load_guests()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def setup_widgets(self):
        tk.Label(self, text="Event Hall Booking", font=("Arial", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=5)

        left = tk.LabelFrame(form_frame, text="Event Hall Details")
        right = tk.LabelFrame(form_frame, text="Guest Details")

        left.grid(row=0, column=0, padx=10)
        right.grid(row=0, column=1, padx=10)

        # Event Hall inputs
        self.hall_name_var = tk.StringVar()
        self.hall_capacity_var = tk.StringVar()
        self.hall_price_var = tk.StringVar()
        self.event_type_var = tk.StringVar()

        tk.Label(left, text="Name:").grid(row=0, column=0, sticky="e")
        tk.Entry(left, textvariable=self.hall_name_var, state="readonly").grid(row=0, column=1)

        tk.Label(left, text="Capacity:").grid(row=1, column=0, sticky="e")
        tk.Entry(left, textvariable=self.hall_capacity_var, state="readonly").grid(row=1, column=1)

        tk.Label(left, text="Price/Hour:").grid(row=2, column=0, sticky="e")
        tk.Entry(left, textvariable=self.hall_price_var, state="readonly").grid(row=2, column=1)

        tk.Label(left, text="Event Type:").grid(row=3, column=0, sticky="e")
        tk.Entry(left, textvariable=self.event_type_var).grid(row=3, column=1)

        # Guest inputs
        self.guest_name_var = tk.StringVar()
        self.guest_id_var = tk.StringVar()

        tk.Label(right, text="Guest Name:").grid(row=0, column=0, sticky="e")
        tk.Entry(right, textvariable=self.guest_name_var, state="readonly").grid(row=0, column=1)

        tk.Label(right, text="Guest ID:").grid(row=1, column=0, sticky="e")
        tk.Entry(right, textvariable=self.guest_id_var, state="readonly").grid(row=1, column=1)

        # Buttons
        tk.Button(self, text="Book Event Hall", command=self.book_eventhall).pack(pady=5)
        tk.Button(self, text="Clear", command=self.clear_form).pack()

        # Event Hall Table (Only Available ones shown, Payment Status removed)
        self.hall_table = ttk.Treeview(self, columns=("id", "name", "capacity", "price"), show="headings")
        self.hall_table.heading("id", text="ID")
        self.hall_table.heading("name", text="Name")
        self.hall_table.heading("capacity", text="Capacity")
        self.hall_table.heading("price", text="Price/Hour")
        self.hall_table.bind("<ButtonRelease-1>", self.select_eventhall)
        self.hall_table.pack(pady=10, fill="x")

        # Guest Table
        self.guest_table = ttk.Treeview(self, columns=("id", "name", "dob", "gender", "aadhar"), show="headings")
        self.guest_table.heading("id", text="Guest ID")
        self.guest_table.heading("name", text="Name")
        self.guest_table.heading("dob", text="DOB")
        self.guest_table.heading("gender", text="Gender")
        self.guest_table.heading("aadhar", text="Aadhar No")
        self.guest_table.bind("<ButtonRelease-1>", self.select_guest)
        self.guest_table.pack(pady=10, fill="x")

    def load_eventhalls(self):
        self.hall_table.delete(*self.hall_table.get_children())
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT HallID, Name, Capacity, PricePerHour
            FROM EventHall
            WHERE Availability = TRUE
            ORDER BY HallID
        """)
        for row in cursor.fetchall():
            self.hall_table.insert("", "end", values=row)
        cursor.close()
        close_connection(conn)

    def load_guests(self):
        self.guest_table.delete(*self.guest_table.get_children())
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT GuestID, Name, DOB, Gender, AadharNo FROM Guest")
        for row in cursor.fetchall():
            self.guest_table.insert("", "end", values=row)
        cursor.close()
        close_connection(conn)

    def select_eventhall(self, event):
        selected = self.hall_table.focus()
        if selected:
            values = self.hall_table.item(selected)["values"]
            self.selected_hall = values[0]
            self.hall_name_var.set(values[1])
            self.hall_capacity_var.set(values[2])
            self.hall_price_var.set(values[3])

    def select_guest(self, event):
        selected = self.guest_table.focus()
        if selected:
            values = self.guest_table.item(selected)["values"]
            self.selected_guest = values[0]
            self.guest_id_var.set(values[0])
            self.guest_name_var.set(values[1])

    def clear_form(self):
        self.selected_hall = None
        self.selected_guest = None
        self.hall_name_var.set("")
        self.hall_capacity_var.set("")
        self.hall_price_var.set("")
        self.event_type_var.set("")
        self.guest_name_var.set("")
        self.guest_id_var.set("")

    def book_eventhall(self):
        if not self.selected_hall or not self.selected_guest or not self.event_type_var.get():
            messagebox.showerror("Missing Info", "Please select both an event hall, guest, and enter event type.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Fetch price
            cursor.execute("SELECT PricePerHour FROM EventHall WHERE HallID = %s", (self.selected_hall,))
            price = cursor.fetchone()[0]

            # Insert booking
            cursor.execute("""
                INSERT INTO EventBooking (GuestID, HallID, EventType, TotalCost)
                VALUES (%s, %s, %s, %s)
            """, (self.selected_guest, self.selected_hall, self.event_type_var.get(), price))

            # Update availability
            cursor.execute("UPDATE EventHall SET Availability = FALSE WHERE HallID = %s", (self.selected_hall,))
            conn.commit()

            messagebox.showinfo("Success", "Event Hall booked successfully!")
            self.clear_form()
            self.load_eventhalls()

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            close_connection(conn)
