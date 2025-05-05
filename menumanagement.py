import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class MenuPage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.selected_menu_id = None

       

        # ---------- Form Section ----------
        form_frame = tk.LabelFrame(self, text="Manage Menu", padx=10, pady=10)
        form_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(form_frame, text="Restaurant:").grid(row=0, column=0, sticky="w")
        self.restaurant_cb = ttk.Combobox(form_frame, state="readonly")
        self.restaurant_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form_frame, text="Item Name:").grid(row=1, column=0, sticky="w")
        self.item_name_entry = tk.Entry(form_frame)
        self.item_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form_frame, text="Price:").grid(row=2, column=0, sticky="w")
        self.price_entry = tk.Entry(form_frame)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Buttons
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Add", command=self.add_menu).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", command=self.update_menu).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_menu).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_fields).grid(row=0, column=3, padx=5)

        # ---------- Display Section ----------
        display_frame = tk.LabelFrame(self, text="Full Menu")
        display_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("MenuID", "Restaurant", "ItemName", "Price")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_menu)

        self.load_restaurants()
        self.load_menu_data()

         # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def load_restaurants(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT RestaurantID, Name FROM Restaurant")
        restaurants = cursor.fetchall()
        close_connection(conn)
        cursor.close()

        self.restaurant_map = {name: rid for rid, name in restaurants}
        self.restaurant_cb['values'] = list(self.restaurant_map.keys())
        if restaurants:
            self.restaurant_cb.current(0)

    def load_menu_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = create_connection()
        cursor = conn.cursor()
        query = """
        SELECT m.MenuID, r.Name, m.ItemName, m.Price 
        FROM Menu m 
        JOIN Restaurant r ON m.RestaurantID = r.RestaurantID
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        close_connection(conn)
        cursor.close()
 

    def add_menu(self):
        restaurant_name = self.restaurant_cb.get()
        item_name = self.item_name_entry.get().strip()
        price = self.price_entry.get().strip()

        if not item_name or not price:
            messagebox.showwarning("Validation Error", "All fields must be filled.")
            return

        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a positive number.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Menu (RestaurantID, ItemName, Price) VALUES (%s, %s, %s)",
                (self.restaurant_map[restaurant_name], item_name, price_val)
            )
            conn.commit()
            messagebox.showinfo("Success", "Menu item added.")
            self.load_menu_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()


    def update_menu(self):
        if self.selected_menu_id is None:
            messagebox.showwarning("No Selection", "Select a menu item to update.")
            return
        restaurant_name = self.restaurant_cb.get()
        item_name = self.item_name_entry.get().strip()
        price = self.price_entry.get().strip()

        try:
            price_val = float(price)
            if price_val <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a positive number.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Menu SET RestaurantID=%s, ItemName=%s, Price=%s WHERE MenuID=%s",
                (self.restaurant_map[restaurant_name], item_name, price_val, self.selected_menu_id)
            )
            conn.commit()
            messagebox.showinfo("Success", "Menu item updated.")
            self.load_menu_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()


    def delete_menu(self):
        if self.selected_menu_id is None:
            messagebox.showwarning("No Selection", "Select a menu item to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
        if not confirm:
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Menu WHERE MenuID=%s", (self.selected_menu_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Menu item deleted.")
            self.load_menu_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            close_connection(conn)
            cursor.close()


    def load_selected_menu(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], "values")
            self.selected_menu_id = values[0]
            restaurant_name = values[1]
            self.restaurant_cb.set(restaurant_name)
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.insert(0, values[2])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])

    def clear_fields(self):
        self.selected_menu_id = None
        self.restaurant_cb.current(0)
        self.item_name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

