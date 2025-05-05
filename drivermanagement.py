import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class DriverManagerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Variables
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.carname_var = tk.StringVar()
        self.carnumber_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.mobnumber_var = tk.StringVar()

        # Title
        title = tk.Label(self, text="Manage Drivers", font=("Arial", 24, "bold"))
        title.pack(pady=10)

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

        # Setup GUI
        self.setup_gui()
        self.load_drivers()

    def setup_gui(self):
        # Form Frame
        form_frame = tk.LabelFrame(self, text="Driver Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        labels = ["Name", "Age", "Gender", "Car Name", "Car Number", "Location", "Mobile Number"]
        vars = [self.name_var, self.age_var, self.gender_var, self.carname_var, self.carnumber_var, self.location_var, self.mobnumber_var]

        for i, (label, var) in enumerate(zip(labels, vars)):
            tk.Label(form_frame, text=label).grid(row=i//3, column=(i%3)*2, padx=5, pady=5, sticky="e")
            tk.Entry(form_frame, textvariable=var).grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Driver", command=self.add_driver, width=15).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Update Driver", command=self.update_driver, width=15).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Delete Driver", command=self.delete_driver, width=15).grid(row=0, column=2, padx=10)
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, width=15).grid(row=0, column=3, padx=10)

        # Driver Table
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10, fill="both", expand=True)

        columns = ("DriverID", "Name", "Age", "Gender", "CarName", "CarNumber", "Location", "MobNumber")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def validate_inputs(self, name, age, gender, car_name, car_number, location, mob_number):
        if not (name and age and gender and car_name and car_number and location and mob_number):
            return "All fields are required."
        if not age.isdigit() or not (18 <= int(age) <= 99):
            return "Age must be a number between 18 and 99."
        if gender not in ['Male', 'Female', 'Other']:
            return "Gender must be Male, Female, or Other."
        import re
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$', car_number):
            return "Invalid car number format."
        if not re.match(r'^[0-9]{10}$', mob_number):
            return "Mobile number must be 10 digits."
        return None

    def add_driver(self):
        error = self.validate_inputs(self.name_var.get(), self.age_var.get(), self.gender_var.get(), self.carname_var.get(),
                                     self.carnumber_var.get(), self.location_var.get(), self.mobnumber_var.get())
        if error:
            messagebox.showerror("Validation Error", error)
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Driver (Name, Age, Gender, CarName, CarNumber, Location, MobNumber)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.name_var.get(), self.age_var.get(), self.gender_var.get(), self.carname_var.get(),
                  self.carnumber_var.get(), self.location_var.get(), self.mobnumber_var.get()))
            conn.commit()
            messagebox.showinfo("Success", "Driver added successfully.")
            self.clear_fields()
            self.load_drivers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def update_driver(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a driver to update.")
            return

        driver_id = self.tree.item(selected[0])['values'][0]
        error = self.validate_inputs(self.name_var.get(), self.age_var.get(), self.gender_var.get(), self.carname_var.get(),
                                     self.carnumber_var.get(), self.location_var.get(), self.mobnumber_var.get())
        if error:
            messagebox.showerror("Validation Error", error)
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Driver SET Name=%s, Age=%s, Gender=%s, CarName=%s,
                CarNumber=%s, Location=%s, MobNumber=%s WHERE DriverID=%s
            """, (self.name_var.get(), self.age_var.get(), self.gender_var.get(), self.carname_var.get(),
                  self.carnumber_var.get(), self.location_var.get(), self.mobnumber_var.get(), driver_id))
            conn.commit()
            messagebox.showinfo("Success", "Driver updated successfully.")
            self.clear_fields()
            self.load_drivers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def delete_driver(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a driver to delete.")
            return

        driver_id = self.tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this driver?")
        if not confirm:
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Driver WHERE DriverID=%s", (driver_id,))
            conn.commit()
            messagebox.showinfo("Success", "Driver deleted successfully.")
            self.clear_fields()
            self.load_drivers()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn)

    def load_drivers(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Driver")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        close_connection(conn)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.name_var.set(values[1])
            self.age_var.set(values[2])
            self.gender_var.set(values[3])
            self.carname_var.set(values[4])
            self.carnumber_var.set(values[5])
            self.location_var.set(values[6])
            self.mobnumber_var.set(values[7])

    def clear_fields(self):
        for var in [self.name_var, self.age_var, self.gender_var, self.carname_var, self.carnumber_var, self.location_var, self.mobnumber_var]:
            var.set("")
        self.tree.selection_remove(self.tree.selection())
