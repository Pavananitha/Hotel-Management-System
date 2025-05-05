import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class AboveAverageSalaryPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("SubqueriesPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        title = tk.Label(self, text="Employees Earning Above Average Salary", bg="black", font=("Arial", 16, "bold"))
        title.pack(pady=20)

        # Frame for table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

        # Treeview
        self.employee_table = ttk.Treeview(table_frame,
                                           columns=("EmployeeID", "Name", "DOB", "Gender", "Email", "AddrID", "PositionTitle", "Salary"),
                                           xscrollcommand=scroll_x.set,
                                           yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.employee_table.xview)
        scroll_y.config(command=self.employee_table.yview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.employee_table.pack(fill=tk.BOTH, expand=True)

        self.employee_table.heading("EmployeeID", text="Employee ID")
        self.employee_table.heading("Name", text="Name")
        self.employee_table.heading("DOB", text="Date of Birth")
        self.employee_table.heading("Gender", text="Gender")
        self.employee_table.heading("Email", text="Email")
        self.employee_table.heading("AddrID", text="Address ID")
        self.employee_table.heading("PositionTitle", text="Position")
        self.employee_table.heading("Salary", text="Salary")

        self.employee_table["show"] = "headings"

        for col in self.employee_table["columns"]:
            self.employee_table.column(col, width=130)

        self.fetch_employees()

    def fetch_employees(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            query = """
                SELECT e.EmployeeID, e.Name, e.DOB, e.Gender, e.Email, e.AddrID, e.PositionTitle, p.Salary
                FROM Employee e
                JOIN PositionDetails p ON e.PositionTitle = p.PositionTitle
                WHERE p.Salary > (SELECT AVG(Salary) FROM PositionDetails);
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            self.employee_table.delete(*self.employee_table.get_children())  # Clear table

            for row in rows:
                self.employee_table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
        finally:
            close_connection(conn)
