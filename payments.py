import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from conn import create_connection, close_connection

class PaymentPage(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_bills = []
        self.selected_rows_ids = set()
        self.bill_amounts = {}

        self.create_widgets()
        self.load_guests()

        if controller:
            back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"),
                                 bg="#ecf0f1", font=("Arial", 12))
            back_btn.place(x=1100, y=10)

    def create_widgets(self):
        left_frame = tk.Frame(self)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)

        tk.Label(left_frame, text="Select Guest:").grid(row=0, column=0, sticky='w')
        self.guest_cb = ttk.Combobox(left_frame, width=30, state='readonly')
        self.guest_cb.grid(row=0, column=1, pady=5)
        self.guest_cb.bind("<<ComboboxSelected>>", self.load_guest_details)

        labels = ["Name", "DOB", "Gender", "Aadhar", "Payment Date", "Transaction ID", "Payment Method", "Amount"]
        self.entries = {}
        for idx, label in enumerate(labels):
            tk.Label(left_frame, text=label + ":").grid(row=idx+1, column=0, sticky='w')
            if label == "Payment Method":
                cb = ttk.Combobox(left_frame, values=["Cash", "Credit Card", "Debit Card", "Online"], state="readonly")
                cb.grid(row=idx+1, column=1, pady=5)
                self.entries[label] = cb
            elif label == "Amount":
                entry = tk.Entry(left_frame, state='readonly')
                entry.grid(row=idx+1, column=1, pady=5)
                self.entries[label] = entry
            elif label == "Payment Date":
                entry = tk.Entry(left_frame, state='readonly')
                entry.grid(row=idx+1, column=1, pady=5)
                entry.insert(0, str(date.today()))
                self.entries[label] = entry
            else:
                entry = tk.Entry(left_frame, state='readonly' if label != "Transaction ID" else 'normal')
                entry.grid(row=idx+1, column=1, pady=5)
                self.entries[label] = entry

        self.pay_button = tk.Button(left_frame, text="Pay", command=self.make_payment)
        self.pay_button.grid(row=len(labels)+1, column=0, pady=10)

        self.clear_button = tk.Button(left_frame, text="Clear", command=self.clear_fields)
        self.clear_button.grid(row=len(labels)+1, column=1)

        right_frame = tk.Frame(self)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Unpaid Bills").pack()
        self.bill_tree = self.create_treeview(right_frame, columns=["ID", "Type", "Amount"])
        self.bill_tree.pack(padx=5, pady=5, fill='both', expand=True)
        self.bill_tree.bind("<Double-1>", self.select_bill)

        tk.Label(right_frame, text="Selected Payments").pack()
        self.selected_tree = self.create_treeview(right_frame, columns=["ID", "Type", "Amount"])
        self.selected_tree.pack(padx=5, pady=5, fill='both', expand=True)
        self.selected_tree.bind("<Double-1>", self.deselect_bill)

    def create_treeview(self, parent, columns):
        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree_scroll_y.config(command=tree.yview)
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x.config(command=tree.xview)
        tree_scroll_x.pack(side='bottom', fill='x')
        tree.pack(fill='both', expand=True)

        return tree

    def load_guests(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT GuestID, Name FROM Guest")
        guests = cursor.fetchall()
        self.guest_cb['values'] = [f"{name}-{gid}" for gid, name in guests]
        cursor.close()
        close_connection(conn)

    def load_guest_details(self, event):
        guest_data = self.guest_cb.get()
        if not guest_data:
            return
        gid = int(guest_data.split('-')[-1])
        self.current_guest_id = gid

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Name, DOB, Gender, AadharNo FROM Guest WHERE GuestID = %s", (gid,))
        name, dob, gender, aadhar = cursor.fetchone()

        for key, value in zip(["Name", "DOB", "Gender", "Aadhar"], [name, dob, gender, aadhar]):
            self.entries[key].config(state="normal")
            self.entries[key].delete(0, 'end')
            self.entries[key].insert(0, str(value))
            self.entries[key].config(state="readonly")

        self.entries["Payment Date"].config(state="normal")
        self.entries["Payment Date"].delete(0, 'end')
        self.entries["Payment Date"].insert(0, str(date.today()))
        self.entries["Payment Date"].config(state="readonly")

        self.load_unpaid_bills(gid)
        cursor.close()
        close_connection(conn)

    def load_unpaid_bills(self, gid):
        self.bill_tree.delete(*self.bill_tree.get_children())
        self.selected_tree.delete(*self.selected_tree.get_children())
        self.selected_bills.clear()
        self.selected_rows_ids.clear()
        self.bill_amounts.clear()

        self.entries["Amount"].config(state="normal")
        self.entries["Amount"].delete(0, 'end')
        self.entries["Amount"].insert(0, "0.00")
        self.entries["Amount"].config(state="readonly")

        queries = {
            "Reservation": ("ReservationID", "TotalPrice", "Reservation"),
            "Parking": ("ParkingID", "ParkingFee", "Parking"),
            "OrderTable": ("OrderID", "TotalAmount", "OrderTable"),
            "EventBooking": ("BookingID", "TotalCost", "EventBooking")
        }

        conn = create_connection()
        cursor = conn.cursor()
        for table, (id_col, amount_col, table_name) in queries.items():
            cursor.execute(
                f"SELECT {id_col}, {amount_col} FROM {table_name} WHERE GuestID = %s AND PaymentStatus = 0",
                (gid,))
            for row_id, amount in cursor.fetchall():
                bill_id = f"{table}-{row_id}"
                self.bill_tree.insert("", "end", iid=bill_id, values=(row_id, table, f"{amount:.2f}"))
                self.bill_amounts[bill_id] = amount
        cursor.close()
        close_connection(conn)

    def select_bill(self, event):
        selected = self.bill_tree.selection()
        for item in selected:
            if item not in self.selected_rows_ids:
                self.selected_rows_ids.add(item)
                values = self.bill_tree.item(item, "values")
                self.selected_tree.insert("", "end", iid=item, values=values)
                self.update_amount()

    def deselect_bill(self, event):
        selected = self.selected_tree.selection()
        for item in selected:
            self.selected_tree.delete(item)
            if item in self.selected_rows_ids:
                self.selected_rows_ids.remove(item)
        self.update_amount()

    def update_amount(self):
        total = sum(self.bill_amounts[item] for item in self.selected_rows_ids)
        self.entries["Amount"].config(state="normal")
        self.entries["Amount"].delete(0, 'end')
        self.entries["Amount"].insert(0, f"{total:.2f}")
        self.entries["Amount"].config(state="readonly")

    def make_payment(self):
        if not self.selected_rows_ids:
            messagebox.showwarning("No Bills", "Please select at least one unpaid bill.")
            return

        trans_id = self.entries["Transaction ID"].get()
        method = self.entries["Payment Method"].get()
        if not trans_id or not method:
            messagebox.showerror("Input Error", "Transaction ID and Payment Method are required.")
            return

        amount = float(self.entries["Amount"].get())

        conn = create_connection()
        cursor = conn.cursor()

        # Insert payment record
        cursor.execute("""
            INSERT INTO Payment (GuestID, TransactionID, PaymentMethod, PaymentDate, Amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (self.current_guest_id, trans_id, method, date.today(), amount))
        conn.commit()

        # Map table name to their primary keys
        id_columns = {
            "Reservation": "ReservationID",
            "Parking": "ParkingID",
            "OrderTable": "OrderID",
            "EventBooking": "BookingID"
        }

        for item in self.selected_rows_ids:
            table, row_id = item.split("-")
            id_column = id_columns[table]
            cursor.execute(f"UPDATE {table} SET PaymentStatus = 1 WHERE {id_column} = %s", (row_id,))
        conn.commit()

        messagebox.showinfo("Success", "Payment processed successfully!")
        cursor.close()
        close_connection(conn)
        self.load_guest_details(None)

    def clear_fields(self):
        self.guest_cb.set("")
        for key, entry in self.entries.items():
            entry.config(state="normal")
            entry.delete(0, 'end')
            if key == "Payment Date":
                entry.insert(0, str(date.today()))
                entry.config(state="readonly")
            elif key == "Amount":
                entry.insert(0, "0.00")
                entry.config(state="readonly")
            elif key == "Payment Method":
                entry.set("")
            elif key != "Transaction ID":
                entry.config(state="readonly")

        self.bill_tree.delete(*self.bill_tree.get_children())
        self.selected_tree.delete(*self.selected_tree.get_children())
        self.selected_bills.clear()
        self.selected_rows_ids.clear()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Manage Payments")
    root.geometry("1200x700")
    app = PaymentPage(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
