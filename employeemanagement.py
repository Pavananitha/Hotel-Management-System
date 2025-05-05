import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class EmployeePage(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.position_salary = {}
        self.selected_employee_id = None
        self.create_widgets()
        self.load_positions()
        self.load_employees()

         # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ITCFeaturesPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Employee Details Frame
        form_frame = tk.LabelFrame(self, text="Employee Details")
        form_frame.pack(fill="x", padx=10, pady=10)

        labels = ["Name", "DOB (YYYY-MM-DD)", "Gender", "Email", "Street", "Village", "District", "State", "PinCode", "Mobile Number", "Position", "Salary"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            if label == "Gender":
                self.entries[label] = ttk.Combobox(form_frame, values=["Male", "Female", "Other"], state="readonly")
            elif label == "Position":
                self.entries[label] = ttk.Combobox(form_frame, state="readonly")
                self.entries[label].bind("<<ComboboxSelected>>", self.update_salary)
            elif label == "Salary":
                self.entries[label] = tk.Entry(form_frame, state="readonly")
            else:
                self.entries[label] = tk.Entry(form_frame)
            self.entries[label].grid(row=i, column=1, sticky="w", padx=5, pady=5)

        # Button Frame
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add Employee", command=self.add_employee).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Employee", command=self.update_employee).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Delete Employee", command=self.delete_employee).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_fields).grid(row=0, column=3, padx=5)

        # Employee List Frame
        list_frame = tk.LabelFrame(self, text="Existing Employees")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Email", "Position"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_employee)

    def load_positions(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PositionTitle, Salary FROM PositionDetails")
        data = cursor.fetchall()
        self.position_salary = {pos: sal for pos, sal in data}
        self.entries["Position"]["values"] = list(self.position_salary.keys())
        cursor.close()
        close_connection(conn)


    def update_salary(self, event):
        position = self.entries["Position"].get()
        salary = self.position_salary.get(position, "")
        self.entries["Salary"].config(state="normal")
        self.entries["Salary"].delete(0, tk.END)
        self.entries["Salary"].insert(0, str(salary))
        self.entries["Salary"].config(state="readonly")

    def add_employee(self):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            # Insert into Address
            cursor.execute("""
                INSERT INTO Address (Street, Village, District, State, PinCode)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.entries["Street"].get(),
                self.entries["Village"].get(),
                self.entries["District"].get(),
                self.entries["State"].get(),
                self.entries["PinCode"].get()
            ))
            addr_id = cursor.lastrowid

            # Insert into Employee
            cursor.execute("""
                INSERT INTO Employee (Name, DOB, Gender, Email, AddrID, PositionTitle)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                self.entries["Name"].get(),
                self.entries["DOB (YYYY-MM-DD)"].get(),
                self.entries["Gender"].get(),
                self.entries["Email"].get(),
                addr_id,
                self.entries["Position"].get()
            ))
            emp_id = cursor.lastrowid

            # Insert into EmployeeMobile
            cursor.execute("""
                INSERT INTO EmployeeMobile (EmployeeID, MobileNumber)
                VALUES (%s, %s)
            """, (emp_id, self.entries["Mobile Number"].get()))

            conn.commit()
            messagebox.showinfo("Success", "Employee added successfully!")
            self.clear_fields()
            self.load_employees()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn, cursor)

    def load_employees(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EmployeeID, e.Name, e.Email, e.PositionTitle
            FROM Employee e
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        cursor.close()
        close_connection(conn)
 

    def load_selected_employee(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        data = self.tree.item(selected)["values"]
        self.selected_employee_id = data[0]

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.Name, e.DOB, e.Gender, e.Email, a.Street, a.Village, a.District, a.State, a.PinCode,
                   em.MobileNumber, e.PositionTitle
            FROM Employee e
            JOIN Address a ON e.AddrID = a.AddrID
            JOIN EmployeeMobile em ON e.EmployeeID = em.EmployeeID
            WHERE e.EmployeeID = %s
        """, (self.selected_employee_id,))
        result = cursor.fetchone()
        if result:
            keys = list(self.entries.keys())
            for i in range(len(keys)):
                entry = self.entries[keys[i]]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, result[i])
                if keys[i] in ["Gender", "Position"]:
                    entry.set(result[i])
            self.update_salary(None)
        close_connection(conn, cursor)

    def update_employee(self):
        if not self.selected_employee_id:
            messagebox.showerror("Error", "No employee selected.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            # Get existing AddrID
            cursor.execute("SELECT AddrID FROM Employee WHERE EmployeeID = %s", (self.selected_employee_id,))
            addr_id = cursor.fetchone()[0]

            # Update Address
            cursor.execute("""
                UPDATE Address
                SET Street=%s, Village=%s, District=%s, State=%s, PinCode=%s
                WHERE AddrID=%s
            """, (
                self.entries["Street"].get(),
                self.entries["Village"].get(),
                self.entries["District"].get(),
                self.entries["State"].get(),
                self.entries["PinCode"].get(),
                addr_id
            ))

            # Update Employee
            cursor.execute("""
                UPDATE Employee
                SET Name=%s, DOB=%s, Gender=%s, Email=%s, PositionTitle=%s
                WHERE EmployeeID=%s
            """, (
                self.entries["Name"].get(),
                self.entries["DOB (YYYY-MM-DD)"].get(),
                self.entries["Gender"].get(),
                self.entries["Email"].get(),
                self.entries["Position"].get(),
                self.selected_employee_id
            ))

            # Update Mobile
            cursor.execute("""
                UPDATE EmployeeMobile
                SET MobileNumber=%s
                WHERE EmployeeID=%s
            """, (
                self.entries["Mobile Number"].get(),
                self.selected_employee_id
            ))

            conn.commit()
            messagebox.showinfo("Success", "Employee updated.")
            self.clear_fields()
            self.load_employees()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn, cursor)

    def delete_employee(self):
        if not self.selected_employee_id:
            messagebox.showerror("Error", "No employee selected.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Employee WHERE EmployeeID = %s", (self.selected_employee_id,))
            conn.commit()
            messagebox.showinfo("Success", "Employee deleted.")
            self.clear_fields()
            self.load_employees()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            close_connection(conn, cursor)

    def clear_fields(self):
        for entry in self.entries.values():
            entry.config(state="normal")
            entry.delete(0, tk.END)
        self.selected_employee_id = None
