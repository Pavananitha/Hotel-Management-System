import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class RevenueFrame(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Title Label
        tk.Label(self, text="Hotel Revenue Report", font=("Arial", 20, "bold"), bg="white", fg="green").pack(pady=20)

        # Treeview for revenue breakdown
        columns = ("Revenue Source", "Amount")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
        self.tree.heading("Revenue Source", text="Revenue Source")
        self.tree.heading("Amount", text="Amount (₹)")
        self.tree.column("Revenue Source", anchor="center", width=200)
        self.tree.column("Amount", anchor="center", width=150)
        self.tree.pack(pady=10)

        # Button to load revenue
        load_btn = tk.Button(self, text="Load Revenue Data", command=self.load_revenue_data, font=("Arial", 12), bg="#007BFF", padx=10, pady=5)
        load_btn.pack(pady=10)

        # Total revenue label
        self.total_label = tk.Label(self, text="", font=("Arial", 16, "bold"), bg="white", fg="black")
        self.total_label.pack(pady=10)

    def load_revenue_data(self):
        conn = create_connection()
        if conn is None:
            messagebox.showerror("Connection Error", "Failed to connect to the database.")
            return

        try:
            cursor = conn.cursor()
            cursor.callproc("GetHotelRevenue")

            self.tree.delete(*self.tree.get_children())
            total = ""

            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    value = row[0]
                    if "Total Hotel Revenue" in value:
                        total = value
                    else:
                        parts = value.split(": ₹")
                        if len(parts) == 2:
                            self.tree.insert("", tk.END, values=(parts[0], parts[1]))

            self.total_label.config(text=total)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading revenue data:\n{str(e)}")
        finally:
            close_connection(conn)

