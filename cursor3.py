import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class AvailableSpacesPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        title = tk.Label(self, text="Available Rooms and Event Halls", font=("Arial", 18, "bold"), bg="white")
        title.pack(pady=20)

        # Treeview table
        columns = ("Type", "ID", "Name", "Category")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.CENTER)
        self.tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, anchor='ne')

        # Fetch button
        fetch_btn = tk.Button(self, text="Fetch Available Spaces", command=self.fetch_data, bg="#27ae60",  font=("Arial", 12))
        fetch_btn.pack(pady=10)

    def fetch_data(self):
        self.tree.delete(*self.tree.get_children())
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc("GetAvailableRoomsAndEventHalls")

            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data:\n{e}")
        finally:
            close_connection(conn)
