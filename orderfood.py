import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from conn import create_connection, close_connection

class FoodOrderPage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.selected_items = {}  # {item_name: [price, quantity]}
        self.total_amount = 0.0
        self.create_widgets()
        self.load_menu_data()
        self.load_guest_data()

        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        tk.Label(self, text="Select Guest:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.guest_combobox = ttk.Combobox(self, state='readonly')
        self.guest_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.guest_combobox.bind("<<ComboboxSelected>>", self.update_guest_id)

        tk.Label(self, text="Guest ID:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.guest_id_entry = tk.Entry(self, state='readonly')
        self.guest_id_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self, text="Order Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.order_date_var = tk.StringVar(value=str(date.today()))
        self.order_date_entry = tk.Entry(self, textvariable=self.order_date_var, state='readonly')
        self.order_date_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Total Amount:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.total_amount_var = tk.StringVar(value="0.00")
        self.total_amount_entry = tk.Entry(self, textvariable=self.total_amount_var, state='readonly')
        self.total_amount_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(self, text="Order Food", command=self.place_order).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self, text="Clear Fields", command=self.clear_fields).grid(row=2, column=2, columnspan=2, pady=10)

        tk.Label(self, text="Selected Items:").grid(row=3, column=0, columnspan=4)
        selected_frame = tk.Frame(self)
        selected_frame.grid(row=4, column=0, columnspan=4, sticky='nsew')
        self.selected_table = ttk.Treeview(selected_frame, columns=('Item', 'Price', 'Quantity', 'Total'), show='headings', height=5)
        self.selected_table.heading('Item', text='Item')
        self.selected_table.heading('Price', text='Unit Price')
        self.selected_table.heading('Quantity', text='Qty')
        self.selected_table.heading('Total', text='Total')
        y_scroll_sel = ttk.Scrollbar(selected_frame, orient="vertical", command=self.selected_table.yview)
        self.selected_table.configure(yscrollcommand=y_scroll_sel.set)
        y_scroll_sel.pack(side=tk.RIGHT, fill=tk.Y)
        self.selected_table.pack(fill='both', expand=True)
        self.selected_table.bind("<Double-1>", self.remove_selected_item)

        tk.Label(self, text="Full Menu:").grid(row=5, column=0, columnspan=4)
        menu_frame = tk.Frame(self)
        menu_frame.grid(row=6, column=0, columnspan=4, sticky='nsew')
        self.menu_table = ttk.Treeview(menu_frame, columns=('MenuID', 'Restaurant', 'Item', 'Price'), show='headings', height=10)
        self.menu_table.heading('MenuID', text='Menu ID')
        self.menu_table.heading('Restaurant', text='Restaurant')
        self.menu_table.heading('Item', text='Item Name')
        self.menu_table.heading('Price', text='Price')
        y_scroll_menu = ttk.Scrollbar(menu_frame, orient="vertical", command=self.menu_table.yview)
        self.menu_table.configure(yscrollcommand=y_scroll_menu.set)
        y_scroll_menu.pack(side=tk.RIGHT, fill=tk.Y)
        self.menu_table.pack(fill='both', expand=True)
        self.menu_table.bind("<ButtonRelease-1>", self.select_item_from_menu)

    def load_menu_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        query = """
            SELECT m.MenuID, r.Name, m.ItemName, m.Price 
            FROM Menu m
            JOIN Restaurant r ON m.RestaurantID = r.RestaurantID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.menu_table.delete(*self.menu_table.get_children())
        for row in rows:
            self.menu_table.insert('', tk.END, values=row)
        cursor.close()
        close_connection(conn)

    def load_guest_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT GuestID, Name FROM Guest")
        rows = cursor.fetchall()
        self.guest_combobox['values'] = [f"{row[1]} - {row[0]}" for row in rows]
        cursor.close()
        close_connection(conn)

    def update_guest_id(self, event):
        selected = self.guest_combobox.get()
        if selected:
            guest_id = selected.split(" - ")[1]
            self.guest_id_entry.config(state='normal')
            self.guest_id_entry.delete(0, tk.END)
            self.guest_id_entry.insert(0, guest_id)
            self.guest_id_entry.config(state='readonly')

    def select_item_from_menu(self, event):
        selected = self.menu_table.focus()
        values = self.menu_table.item(selected, 'values')
        if values:
            item_name = values[2]
            price = float(values[3])
            if item_name in self.selected_items:
                self.selected_items[item_name][1] += 1
            else:
                self.selected_items[item_name] = [price, 1]
            self.update_selected_table()

    def update_selected_table(self):
        self.selected_table.delete(*self.selected_table.get_children())
        self.total_amount = 0.0
        for item_name, (price, qty) in self.selected_items.items():
            total = price * qty
            self.selected_table.insert('', tk.END, values=(item_name, f"{price:.2f}", qty, f"{total:.2f}"))
            self.total_amount += total
        self.total_amount_var.set(f"{self.total_amount:.2f}")

    def remove_selected_item(self, event):
        selected = self.selected_table.focus()
        values = self.selected_table.item(selected, 'values')
        if values:
            item_name = values[0]
            if item_name in self.selected_items:
                if self.selected_items[item_name][1] > 1:
                    self.selected_items[item_name][1] -= 1
                else:
                    del self.selected_items[item_name]
                self.update_selected_table()

    def place_order(self):
        guest_id = self.guest_id_entry.get().strip()
        order_date = self.order_date_var.get()
        total = float(self.total_amount_var.get())

        if not guest_id or not self.selected_items:
            messagebox.showerror("Error", "Please select a guest and at least one item.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO OrderTable (GuestID, OrderDate, TotalAmount, PaymentStatus)
                VALUES (%s, %s, %s, FALSE)
            """, (guest_id, order_date, total))
            order_id = cursor.lastrowid

            # # If you use OrderDetails:
            # for item_name, (price, qty) in self.selected_items.items():
            #     cursor.execute("""
            #         INSERT INTO OrderTable (OrderID, ItemName, UnitPrice, Quantity)
            #         VALUES (%s, %s, %s, %s)
            #     """, (order_id, item_name, price, qty))

            conn.commit()
            messagebox.showinfo("Success", "Order placed successfully!")
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {e}")
        finally:
            cursor.close()
            close_connection(conn)

    def clear_fields(self):
        self.guest_combobox.set('')
        self.guest_id_entry.config(state='normal')
        self.guest_id_entry.delete(0, tk.END)
        self.guest_id_entry.config(state='readonly')
        self.selected_items.clear()
        self.total_amount = 0.0
        self.total_amount_var.set("0.00")
        self.selected_table.delete(*self.selected_table.get_children())
