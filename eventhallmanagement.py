import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class EventHallPage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.configure(padx=10, pady=10)
        self.create_widgets()
        self.load_data()

         # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Labels and Entry fields
        tk.Label(self, text="Hall Name").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Capacity").grid(row=1, column=0, sticky="w")
        self.capacity_entry = tk.Entry(self)
        self.capacity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Price Per Hour").grid(row=2, column=0, sticky="w")
        self.price_entry = tk.Entry(self)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="Availability").grid(row=3, column=0, sticky="w")
        self.availability_var = tk.BooleanVar()
        self.availability_check = tk.Checkbutton(self, text="Available", variable=self.availability_var)
        self.availability_check.grid(row=3, column=1, sticky="w")

        # Buttons
        tk.Button(self, text="Add", command=self.add_event_hall).grid(row=4, column=0, pady=10)
        tk.Button(self, text="Update", command=self.update_event_hall).grid(row=4, column=1, pady=10)
        tk.Button(self, text="Delete", command=self.delete_event_hall).grid(row=5, column=0, pady=10)
        tk.Button(self, text="Clear", command=self.clear_fields).grid(row=5, column=1, pady=10)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("HallID", "Name", "Capacity", "PricePerHour", "Availability"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=6, column=0, columnspan=2, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM EventHall")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        close_connection(conn)

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.capacity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.availability_var.set(True)
        self.tree.selection_remove(self.tree.selection())

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.capacity_entry.delete(0, tk.END)
            self.capacity_entry.insert(0, values[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])
            self.availability_var.set(values[4])

    def add_event_hall(self):
        name = self.name_entry.get().strip()
        try:
            capacity = int(self.capacity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Capacity and Price must be numeric.")
            return
        availability = self.availability_var.get()

        if not name:
            messagebox.showerror("Missing Data", "Hall Name is required.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO EventHall (Name, Capacity, PricePerHour, Availability)
                VALUES (%s, %s, %s, %s)
            """, (name, capacity, price, availability))
            conn.commit()
            close_connection(conn)
            messagebox.showinfo("Success", "Event hall added successfully.")
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_event_hall(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Select a row to update.")
            return
        hall_id = self.tree.item(selected[0])["values"][0]
        name = self.name_entry.get().strip()
        try:
            capacity = int(self.capacity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Capacity and Price must be numeric.")
            return
        availability = self.availability_var.get()

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE EventHall
                SET Name=%s, Capacity=%s, PricePerHour=%s, Availability=%s
                WHERE HallID=%s
            """, (name, capacity, price, availability, hall_id))
            conn.commit()
            close_connection(conn)
            messagebox.showinfo("Success", "Event hall updated successfully.")
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_event_hall(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Select a row to delete.")
            return
        hall_id = self.tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this event hall?")
        if not confirm:
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM EventHall WHERE HallID=%s", (hall_id,))
            conn.commit()
            close_connection(conn)
            messagebox.showinfo("Deleted", "Event hall deleted successfully.")
            self.load_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", str(e))
