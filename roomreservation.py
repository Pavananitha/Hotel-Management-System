import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection
from datetime import datetime

class RoomReservation(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=10, pady=10)

        self.guest_data = {}
        self.room_data = {}

        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

        # Left: Guest Details
        guest_frame = ttk.LabelFrame(self, text="Guest Details", padding=10)
        guest_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        ttk.Label(guest_frame, text="Select Guest:").grid(row=0, column=0, sticky='w')
        self.guest_cb = ttk.Combobox(guest_frame, state='readonly')
        self.guest_cb.grid(row=0, column=1, sticky='w')
        self.guest_cb.bind("<<ComboboxSelected>>", self.load_guest_details)

        labels = ["Name", "DOB", "Gender", "AadharNo"]
        self.guest_labels = {}
        for i, label in enumerate(labels, start=1):
            ttk.Label(guest_frame, text=label + ":").grid(row=i, column=0, sticky='w')
            self.guest_labels[label] = ttk.Label(guest_frame, text="")
            self.guest_labels[label].grid(row=i, column=1, sticky='w')

        # Right: Reservation Details
        reservation_frame = ttk.LabelFrame(self, text="Reservation Details", padding=10)
        reservation_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.room_info = {}
        fields = ["RoomID", "Room Number", "Room Type", "Price Per Night"]
        for i, field in enumerate(fields):
            ttk.Label(reservation_frame, text=field + ":").grid(row=i, column=0, sticky='w')
            self.room_info[field] = ttk.Label(reservation_frame, text="")
            self.room_info[field].grid(row=i, column=1, sticky='w')

        # Manual date entry
        ttk.Label(reservation_frame, text="Check-in Date (YYYY-MM-DD):").grid(row=4, column=0, sticky='w')
        self.checkin = ttk.Entry(reservation_frame)
        self.checkin.grid(row=4, column=1, sticky='w')

        ttk.Label(reservation_frame, text="Check-out Date (YYYY-MM-DD):").grid(row=5, column=0, sticky='w')
        self.checkout = ttk.Entry(reservation_frame)
        self.checkout.grid(row=5, column=1, sticky='w')

        ttk.Label(reservation_frame, text="Total Nights:").grid(row=6, column=0, sticky='w')
        self.total_nights = ttk.Label(reservation_frame, text="0")
        self.total_nights.grid(row=6, column=1, sticky='w')

        ttk.Label(reservation_frame, text="Amount:").grid(row=7, column=0, sticky='w')
        self.amount = ttk.Label(reservation_frame, text="0.00")
        self.amount.grid(row=7, column=1, sticky='w')

        ttk.Label(reservation_frame, text="Payment Status:").grid(row=8, column=0, sticky='w')
        self.payment_status = ttk.Combobox(reservation_frame, state='readonly', values=["Paid", "Unpaid"])
        self.payment_status.set("Unpaid")
        self.payment_status.grid(row=8, column=1, sticky='w')

        ttk.Button(reservation_frame, text="Reserve Room", command=self.reserve_room).grid(row=9, column=0, columnspan=2, pady=10)

        # Room Table
        room_frame = ttk.LabelFrame(self, text="Available Rooms", padding=10)
        room_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        self.room_table = ttk.Treeview(room_frame, columns=("RoomID", "RoomNumber", "RoomType", "Price"), show="headings")
        for col in self.room_table["columns"]:
            self.room_table.heading(col, text=col)
        self.room_table.pack(side='left', fill='both', expand=True)
        self.room_table.bind("<<TreeviewSelect>>", self.select_room)

        scrollbar = ttk.Scrollbar(room_frame, orient="vertical", command=self.room_table.yview)
        scrollbar.pack(side='right', fill='y')
        self.room_table.configure(yscrollcommand=scrollbar.set)

        self.load_guests()
        self.load_rooms()

    def load_guests(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT GuestID, Name FROM Guest")
        guests = cursor.fetchall()
        close_connection(conn)
        cursor.close()
        self.guest_map = {f"{name} (ID: {gid})": gid for gid, name in guests}
        self.guest_cb["values"] = list(self.guest_map.keys())

    def load_guest_details(self, event):
        guest_id = self.guest_map[self.guest_cb.get()]
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Name, DOB, Gender, AadharNo FROM Guest WHERE GuestID=%s", (guest_id,))
        data = cursor.fetchone()
        close_connection(conn)
        cursor.close()
        for i, key in enumerate(["Name", "DOB", "Gender", "AadharNo"]):
            self.guest_labels[key].config(text=str(data[i]))

    def load_rooms(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.RoomID, r.RoomNumber, r.RoomType, d.PricePerNight
            FROM Room r
            JOIN RoomTypeDetails d ON r.RoomType = d.RoomType
            WHERE r.Availability = TRUE
        """)
        rooms = cursor.fetchall()
        close_connection(conn)
        cursor.close()
        for row in rooms:
            self.room_table.insert('', 'end', values=row)

    def select_room(self, event):
        selected = self.room_table.focus()
        values = self.room_table.item(selected)['values']
        if values:
            keys = ["RoomID", "Room Number", "Room Type", "Price Per Night"]
            for k, v in zip(keys, values):
                self.room_info[k].config(text=str(v))
        self.update_nights_amount()

    def update_nights_amount(self):
        try:
            in_date = datetime.strptime(self.checkin.get(), "%Y-%m-%d")
            out_date = datetime.strptime(self.checkout.get(), "%Y-%m-%d")
            nights = (out_date - in_date).days
            if nights <= 0:
                self.total_nights.config(text="0")
                self.amount.config(text="0.00")
                return
            self.total_nights.config(text=str(nights))
            price = float(self.room_info["Price Per Night"].cget("text"))
            total = price * nights
            self.amount.config(text=f"{total:.2f}")
        except Exception:
            self.total_nights.config(text="0")
            self.amount.config(text="0.00")

    def reserve_room(self):
        guest_id = self.guest_map.get(self.guest_cb.get())
        room_id = self.room_info["RoomID"].cget("text")
        if not guest_id or not room_id:
            messagebox.showerror("Error", "Please select a guest and a room.")
            return

        try:
            checkin = datetime.strptime(self.checkin.get(), "%Y-%m-%d")
            checkout = datetime.strptime(self.checkout.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return

        if checkin.date() < datetime.now().date():
            messagebox.showerror("Invalid Date", "Check-in date cannot be in the past.")
            return
        if checkout <= checkin:
            messagebox.showerror("Invalid Date", "Check-out must be after check-in.")
            return

        nights = (checkout - checkin).days
        price = float(self.room_info["Price Per Night"].cget("text"))
        total_amount = price * nights
        paid = self.payment_status.get() == "Paid"

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Reservation (GuestID, RoomID, CheckInDate, CheckOutDate, TotalPrice, PaymentStatus)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (guest_id, room_id, checkin.date(), checkout.date(), total_amount, paid))

            cursor.execute("UPDATE Room SET Availability=FALSE WHERE RoomID=%s", (room_id,))
            conn.commit()
            close_connection(conn)
            cursor.close()

            messagebox.showinfo("Success", "Room reserved successfully!")
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def reset_form(self):
        self.guest_cb.set('')
        for label in self.guest_labels.values():
            label.config(text='')
        for label in self.room_info.values():
            label.config(text='')
        self.checkin.delete(0, tk.END)
        self.checkout.delete(0, tk.END)
        self.total_nights.config(text='0')
        self.amount.config(text='0.00')
        self.payment_status.set("Unpaid")
        self.room_table.delete(*self.room_table.get_children())
        self.load_rooms()
