import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class RoomManagePage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.room_types = [
            "Double Deluxe", "Double Standard", "Presidential Suite",
            "Single Deluxe", "Single Standard", "Suite"
        ]
        self.create_widgets()
        self.load_rooms()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Labels and Inputs
        tk.Label(self, text="Room Number:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.room_number_entry = tk.Entry(self)
        self.room_number_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Room Type:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.room_type_cb = ttk.Combobox(self, values=self.room_types, state="readonly")
        self.room_type_cb.grid(row=1, column=1, padx=10, pady=5)
        self.room_type_cb.bind("<<ComboboxSelected>>", self.update_price_label)

        tk.Label(self, text="Price (₹):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.price_entry = tk.Entry(self, state="readonly", fg="white")
        self.price_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")


        # Buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Add", width=10, command=self.add_room).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update", width=10, command=self.update_room).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete", width=10, command=self.delete_room).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Clear", width=10, command=self.clear_fields).grid(row=0, column=3, padx=5)

        # Treeview for displaying rooms
        self.tree = ttk.Treeview(self, columns=("RoomID", "RoomNumber", "RoomType", "Availability"), show='headings')
        self.tree.heading("RoomID", text="Room ID")
        self.tree.heading("RoomNumber", text="Room Number")
        self.tree.heading("RoomType", text="Room Type")
        self.tree.heading("Availability", text="Available")
        self.tree.column("RoomID", width=80)
        self.tree.column("RoomNumber", width=120)
        self.tree.column("RoomType", width=150)
        self.tree.column("Availability", width=100)
        self.tree.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        self.tree.bind("<ButtonRelease-1>", self.load_selected_room)

        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def update_price_label(self, event=None):
        selected_type = self.room_type_cb.get()
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT PricePerNight FROM RoomTypeDetails WHERE RoomType = %s", (selected_type,))
            result = cursor.fetchone()
            if result:
                self.price_entry.config(state="normal")
                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, f"{result[0]:.2f}")
                self.price_entry.config(state="readonly")
            else:
                self.price_entry.config(state="normal")
                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, "N/A")
                self.price_entry.config(state="readonly")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()

    def add_room(self):
        room_number = self.room_number_entry.get().strip()
        room_type = self.room_type_cb.get()
        if not room_number or not room_type:
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Room (RoomNumber, RoomType, Availability) VALUES (%s, %s, %s)",
                           (room_number, room_type, True))
            conn.commit()
            messagebox.showinfo("Success", "Room added successfully.")
            self.load_rooms()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()

    def update_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a room to update.")
            return
        room_id = self.tree.item(selected[0])['values'][0]
        room_number = self.room_number_entry.get().strip()
        room_type = self.room_type_cb.get()
        if not room_number or not room_type:
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Room SET RoomNumber=%s, RoomType=%s WHERE RoomID=%s",
                           (room_number, room_type, room_id))
            conn.commit()
            messagebox.showinfo("Success", "Room updated successfully.")
            self.load_rooms()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()

    def delete_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a room to delete.")
            return
        room_id = self.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this room?")
        if not confirm:
            return
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Room WHERE RoomID = %s", (room_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Room deleted successfully.")
            self.load_rooms()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()

    def clear_fields(self):
        self.room_number_entry.delete(0, tk.END)
        self.room_type_cb.set("")
        self.price_entry.config(state="normal")
        self.price_entry.delete(0, tk.END)
        self.price_entry.config(state="readonly")
        self.tree.selection_remove(self.tree.selection())

    def load_selected_room(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.room_number_entry.delete(0, tk.END)
            self.room_number_entry.insert(0, values[1])
            self.room_type_cb.set(values[2])
            self.update_price_label()

    def load_rooms(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT RoomID, RoomNumber, RoomType, Availability FROM Room")
        for row in cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
        close_connection(conn)
        cursor.close()
