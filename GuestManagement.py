import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class GuestPage(tk.Frame):
    def __init__(self, parent, controller=None): 
        super().__init__(parent)
        self.controller = controller
        self.selected_guest_id = None
        self.create_widgets()
        self.load_guests()

         # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Labels and Entries
        fields = ['Name', 'DOB (YYYY-MM-DD)', 'Gender', 'Aadhar No', 'Street', 'Village', 'District', 'State', 'PinCode', 'Mobile']
        self.entries = {}

        form_frame = tk.Frame(self)
        form_frame.pack(padx=10, pady=10, fill='x')

        for i, field in enumerate(fields):
            tk.Label(form_frame, text=field).grid(row=i // 2, column=(i % 2) * 2, sticky='e', padx=5, pady=3)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky='w', padx=5, pady=3)
            self.entries[field] = entry

        # Gender ComboBox
        self.entries['Gender'] = ttk.Combobox(form_frame, values=['Male', 'Female', 'Other'], state='readonly', width=28)
        self.entries['Gender'].grid(row=1, column=1, sticky='w', padx=5, pady=3)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add Guest", command=self.add_guest).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Update Guest", command=self.update_guest).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Delete Guest", command=self.delete_guest).grid(row=0, column=2, padx=10)
        ttk.Button(btn_frame, text="Clear", command=self.clear_fields).grid(row=0, column=3, padx=10)

        # Guest Table
        table_frame = tk.Frame(self)
        table_frame.pack(padx=10, pady=10, fill='both', expand=True)

        columns = ('GuestID', 'Name', 'DOB', 'Gender', 'Aadhar', 'Street', 'Village', 'District', 'State', 'PinCode', 'Mobile')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')

        self.tree.pack(fill='both', expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_row_select)

    def load_guests(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT G.GuestID, G.Name, G.DOB, G.Gender, G.AadharNo,
                   A.Street, A.Village, A.District, A.State, A.PinCode, GM.MobNo
            FROM Guest G
            JOIN Address A ON G.AddrID = A.AddrID
            JOIN GuestMobile GM ON G.GuestID = GM.GuestID
        """)
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        close_connection(conn)

    def add_guest(self):
        try:
            data = {k: self.entries[k].get() for k in self.entries}
            conn = create_connection()
            cursor = conn.cursor()

            # Insert Address
            cursor.execute("""
                INSERT INTO Address (Street, Village, District, State, PinCode)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['Street'], data['Village'], data['District'], data['State'], data['PinCode']))
            addr_id = cursor.lastrowid

            # Insert Guest
            cursor.execute("""
                INSERT INTO Guest (Name, DOB, Gender, AadharNo, AddrID)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['Name'], data['DOB (YYYY-MM-DD)'], data['Gender'], data['Aadhar No'], addr_id))
            guest_id = cursor.lastrowid

            # Insert Mobile
            cursor.execute("INSERT INTO GuestMobile (GuestID, MobNo) VALUES (%s, %s)", (guest_id, data['Mobile']))

            conn.commit()
            messagebox.showinfo("Success", "Guest added successfully.")
            self.clear_fields()
            self.load_guests()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def update_guest(self):
        if not self.selected_guest_id:
            messagebox.showwarning("Warning", "Please select a guest to update.")
            return

        try:
            data = {k: self.entries[k].get() for k in self.entries}
            conn = create_connection()
            cursor = conn.cursor()

            # Get AddrID
            cursor.execute("SELECT AddrID FROM Guest WHERE GuestID = %s", (self.selected_guest_id,))
            addr_id = cursor.fetchone()[0]

            # Update Address
            cursor.execute("""
                UPDATE Address SET Street=%s, Village=%s, District=%s, State=%s, PinCode=%s
                WHERE AddrID = %s
            """, (data['Street'], data['Village'], data['District'], data['State'], data['PinCode'], addr_id))

            # Update Guest
            cursor.execute("""
                UPDATE Guest SET Name=%s, DOB=%s, Gender=%s, AadharNo=%s
                WHERE GuestID = %s
            """, (data['Name'], data['DOB (YYYY-MM-DD)'], data['Gender'], data['Aadhar No'], self.selected_guest_id))

            # Update Mobile
            cursor.execute("""
                UPDATE GuestMobile SET MobNo=%s WHERE GuestID = %s
            """, (data['Mobile'], self.selected_guest_id))

            conn.commit()
            messagebox.showinfo("Success", "Guest updated successfully.")
            self.clear_fields()
            self.load_guests()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def delete_guest(self):
        if not self.selected_guest_id:
            messagebox.showwarning("Warning", "Please select a guest to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this guest?")
        if not confirm:
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            # Delete Guest record (ON DELETE CASCADE should handle address and mobile if set in schema)
            cursor.execute("DELETE FROM Guest WHERE GuestID = %s", (self.selected_guest_id,))
            conn.commit()
            messagebox.showinfo("Success", "Guest deleted successfully.")
            self.clear_fields()
            self.load_guests()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        if 'Gender' in self.entries:
            self.entries['Gender'].set('')
        self.selected_guest_id = None

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, 'values')
        self.selected_guest_id = values[0]
        field_names = ['Name', 'DOB (YYYY-MM-DD)', 'Gender', 'Aadhar No', 'Street', 'Village', 'District', 'State', 'PinCode', 'Mobile']
        for field, value in zip(field_names, values[1:]):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, value)

# To test independently
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Guest Management")
    root.geometry("1200x600")
    GuestPage(root).pack(fill='both', expand=True)
    root.mainloop()
