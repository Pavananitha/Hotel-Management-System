# File: RestaurantManagePage.py

import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class RestaurantManagePage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.selected_restaurant_id = None

        self.create_widgets()
        self.load_data()

          # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Form labels and entries
        tk.Label(self, text="Restaurant Name").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Seating Capacity").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.capacity_entry = tk.Entry(self)
        self.capacity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Mobile Number").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.mobile_entry = tk.Entry(self)
        self.mobile_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Add", command=self.add_restaurant).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update_restaurant).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_restaurant).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_fields).grid(row=0, column=3, padx=5)

        # Table
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Capacity", "Mobile"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Capacity", text="Seating Capacity")
        self.tree.heading("Mobile", text="Mobile Number")
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Capacity", width=120)
        self.tree.column("Mobile", width=100)
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def add_restaurant(self):
        name = self.name_entry.get()
        capacity = self.capacity_entry.get()
        mobile = self.mobile_entry.get()

        if not name or not capacity.isdigit() or not mobile.isdigit() or len(mobile) != 10:
            messagebox.showerror("Validation Error", "Please provide valid inputs.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Restaurant (Name, SeatingCapacity) VALUES (%s, %s)", (name, int(capacity)))
            restaurant_id = cursor.lastrowid
            cursor.execute("INSERT INTO RestaurantMobile (RestaurantID, MobileNumber) VALUES (%s, %s)", (restaurant_id, mobile))
            conn.commit()
            messagebox.showinfo("Success", "Restaurant added successfully.")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add restaurant.\n{e}")
        finally:
            close_connection(conn)

    def update_restaurant(self):
        if not self.selected_restaurant_id:
            messagebox.showwarning("No Selection", "Please select a restaurant to update.")
            return

        name = self.name_entry.get()
        capacity = self.capacity_entry.get()
        mobile = self.mobile_entry.get()

        if not name or not capacity.isdigit() or not mobile.isdigit() or len(mobile) != 10:
            messagebox.showerror("Validation Error", "Please provide valid inputs.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Restaurant SET Name=%s, SeatingCapacity=%s WHERE RestaurantID=%s",
                           (name, int(capacity), self.selected_restaurant_id))
            cursor.execute("UPDATE RestaurantMobile SET MobileNumber=%s WHERE RestaurantID=%s",
                           (mobile, self.selected_restaurant_id))
            conn.commit()
            messagebox.showinfo("Success", "Restaurant updated successfully.")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update restaurant.\n{e}")
        finally:
            close_connection(conn)

    def delete_restaurant(self):
        if not self.selected_restaurant_id:
            messagebox.showwarning("No Selection", "Please select a restaurant to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this restaurant?")
        if not confirm:
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Restaurant WHERE RestaurantID=%s", (self.selected_restaurant_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Restaurant deleted successfully.")
            self.clear_fields()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete restaurant.\n{e}")
        finally:
            close_connection(conn)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = create_connection()
            cursor = conn.cursor()
            query = """
            SELECT r.RestaurantID, r.Name, r.SeatingCapacity, m.MobileNumber 
            FROM Restaurant r 
            JOIN RestaurantMobile m ON r.RestaurantID = m.RestaurantID
            ORDER BY r.RestaurantID
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data.\n{e}")
        finally:
            close_connection(conn)

    def on_row_click(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
        values = self.tree.item(selected_item, 'values')
        self.selected_restaurant_id = values[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, values[2])
        self.mobile_entry.delete(0, tk.END)
        self.mobile_entry.insert(0, values[3])

    def clear_fields(self):
        self.selected_restaurant_id = None
        self.name_entry.delete(0, tk.END)
        self.capacity_entry.delete(0, tk.END)
        self.mobile_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

