import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class CheckOut(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_guest_id = None
        self.selected_checkouts = []

        self.configure(padx=10, pady=10)
        self.setup_ui()

        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def setup_ui(self):
        # Guest Selection
        tk.Label(self, text="Select Guest").grid(row=0, column=0, sticky="w")
        self.guest_combo = ttk.Combobox(self, state="readonly", width=30)
        self.guest_combo.grid(row=0, column=1, sticky="w")
        self.guest_combo.bind("<<ComboboxSelected>>", self.load_guest_data)

        # Guest Details (not in a table)
        self.details_frame = tk.Frame(self)
        self.details_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        self.name_label = tk.Label(self.details_frame, text="Name: ")
        self.name_label.grid(row=0, column=0, sticky="w")
        self.dob_label = tk.Label(self.details_frame, text="DOB: ")
        self.dob_label.grid(row=0, column=1, padx=10, sticky="w")
        self.gender_label = tk.Label(self.details_frame, text="Gender: ")
        self.gender_label.grid(row=1, column=0, sticky="w")
        self.aadhar_label = tk.Label(self.details_frame, text="Aadhar: ")
        self.aadhar_label.grid(row=1, column=1, padx=10, sticky="w")

        # Booked Rooms and Halls Table
        tk.Label(self, text="Currently Booked (Not Available)").grid(row=2, column=0, columnspan=2, sticky="w")
        self.booking_tree_frame = tk.Frame(self)
        self.booking_tree_frame.grid(row=3, column=0, columnspan=2, pady=5)

        self.booking_tree = ttk.Treeview(self.booking_tree_frame, columns=("Type", "ID", "Name", "Details", "RID/HID"), show="headings", height=8)
        for col in ("Type", "ID", "Name", "Details", "RID/HID"):
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=130 if col != "Details" else 200)
        self.booking_tree.pack(side="left", fill="y")

        scrollbar1 = ttk.Scrollbar(self.booking_tree_frame, orient="vertical", command=self.booking_tree.yview)
        self.booking_tree.configure(yscrollcommand=scrollbar1.set)
        scrollbar1.pack(side="right", fill="y")

        self.booking_tree.bind("<<TreeviewSelect>>", self.select_for_checkout)

        # Ready to Checkout Table
        tk.Label(self, text="Ready to Checkout").grid(row=4, column=0, columnspan=2, sticky="w")
        self.ready_tree_frame = tk.Frame(self)
        self.ready_tree_frame.grid(row=5, column=0, columnspan=2, pady=5)

        self.ready_tree = ttk.Treeview(self.ready_tree_frame, columns=("Type", "ID", "Name", "Details", "RID/HID"), show="headings", height=6)
        for col in ("Type", "ID", "Name", "Details", "RID/HID"):
            self.ready_tree.heading(col, text=col)
            self.ready_tree.column(col, width=130 if col != "Details" else 200)
        self.ready_tree.pack(side="left", fill="y")

        scrollbar2 = ttk.Scrollbar(self.ready_tree_frame, orient="vertical", command=self.ready_tree.yview)
        self.ready_tree.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.pack(side="right", fill="y")

        self.ready_tree.bind("<Double-1>", self.remove_from_checkout)

        # Buttons
        ttk.Button(self, text="Check Out", command=self.perform_checkout).grid(row=6, column=0, sticky="e", padx=5, pady=5)
        ttk.Button(self, text="Clear", command=self.clear_all).grid(row=6, column=1, sticky="w", padx=5, pady=5)

        self.load_guest_list()

    def load_guest_list(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT GuestID, Name FROM Guest")
        guests = cursor.fetchall()
        self.guest_map = {f"{name} - {gid}": gid for gid, name in guests}
        self.guest_combo['values'] = list(self.guest_map.keys())
        close_connection(conn)
        cursor.close()

    def load_guest_data(self, event=None):
        self.clear_all(exclude_combo=True)

        guest_key = self.guest_combo.get()
        self.selected_guest_id = self.guest_map.get(guest_key)

        if not self.selected_guest_id:
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Guest details
        cursor.execute("SELECT Name, DOB, Gender, AadharNo FROM Guest WHERE GuestID = %s", (self.selected_guest_id,))
        guest = cursor.fetchone()
        if guest:
            self.name_label.config(text=f"Name: {guest[0]}")
            self.dob_label.config(text=f"DOB: {guest[1]}")
            self.gender_label.config(text=f"Gender: {guest[2]}")
            self.aadhar_label.config(text=f"Aadhar: {guest[3]}")

        # Rooms
        cursor.execute("""
            SELECT r.ReservationID, rm.RoomID, rm.RoomNumber, rm.RoomType
            FROM Reservation r
            JOIN Room rm ON r.RoomID = rm.RoomID
            WHERE r.GuestID = %s AND rm.Availability = FALSE
        """, (self.selected_guest_id,))
        rooms = cursor.fetchall()
        for res_id, room_id, number, rtype in rooms:
            self.booking_tree.insert("", "end", values=("Room", res_id, number, f"Type: {rtype}", room_id))

        # Event Halls
        cursor.execute("""
            SELECT eb.BookingID, eh.HallID, eh.Name, eh.Capacity
            FROM EventBooking eb
            JOIN EventHall eh ON eb.HallID = eh.HallID
            WHERE eb.GuestID = %s AND eh.Availability = FALSE
        """, (self.selected_guest_id,))
        halls = cursor.fetchall()
        for book_id, hall_id, name, capacity in halls:
            self.booking_tree.insert("", "end", values=("EventHall", book_id, name, f"Capacity: {capacity}", hall_id))

        close_connection(conn)
        cursor.close()

    def select_for_checkout(self, event=None):
        selected = self.booking_tree.selection()
        for item in selected:
            vals = self.booking_tree.item(item, "values")
            if not self.is_already_in_ready(vals):
                self.ready_tree.insert("", "end", values=vals)

    def is_already_in_ready(self, values):
        for row in self.ready_tree.get_children():
            if self.ready_tree.item(row, "values") == values:
                return True
        return False

    def remove_from_checkout(self, event):
        selected = self.ready_tree.identify_row(event.y)
        if selected:
            self.ready_tree.delete(selected)

    def perform_checkout(self):
        if not self.ready_tree.get_children():
            messagebox.showwarning("No Selection", "Please select at least one booking to checkout.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            for row in self.ready_tree.get_children():
                item = self.ready_tree.item(row, "values")
                typ, booking_id, _, _, rid_or_hid = item
                if typ == "Room":
                    cursor.execute("UPDATE Room SET Availability = TRUE WHERE RoomID = %s", (rid_or_hid,))
                elif typ == "EventHall":
                    cursor.execute("UPDATE EventHall SET Availability = TRUE WHERE HallID = %s", (rid_or_hid,))
            conn.commit()
            messagebox.showinfo("Success", "Checkout completed successfully.")
            self.load_guest_data()
            self.ready_tree.delete(*self.ready_tree.get_children())
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Checkout failed: {e}")
        finally:
            close_connection(conn)
            cursor.close()

    def clear_all(self, exclude_combo=False):
        if not exclude_combo:
            self.guest_combo.set("")
        for lbl in [self.name_label, self.dob_label, self.gender_label, self.aadhar_label]:
            lbl.config(text=lbl.cget("text").split(":")[0] + ":")
        self.booking_tree.delete(*self.booking_tree.get_children())
        self.ready_tree.delete(*self.ready_tree.get_children())
