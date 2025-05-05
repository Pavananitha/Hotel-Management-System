import tkinter as tk
from tkinter import ttk
from conn import create_connection, close_connection

class GuestDetailsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#ecf0f1")

        # Back Button
        back_button = tk.Button(self, text="← Back",
                                command=lambda: controller.show_frame("ViewsPage"),
                                font=("Arial", 12), bd=0, bg="#ecf0f1")
        back_button.place(x=10, y=10)

        # Search Bar
        search_label = tk.Label(self, text="Search:", font=("Arial", 12), bg="#ecf0f1")
        search_label.place(x=80, y=15)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30)
        self.search_entry.place(x=150, y=17)
        self.search_entry.bind("<KeyRelease>", self.perform_search)

        # Treeview Frame
        tree_frame = tk.Frame(self)
        tree_frame.place(x=10, y=50, relwidth=0.97, relheight=0.9)

        # Scrollbars
        x_scroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        y_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)

        self.tree = ttk.Treeview(tree_frame, xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        x_scroll.config(command=self.tree.xview)
        y_scroll.config(command=self.tree.yview)

        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.display_guest_data()

    def display_guest_data(self):
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM GuestDetailsView")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = col_names
        self.tree["show"] = "headings"

        for col in col_names:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='w')

        for row in rows:
            self.tree.insert("", "end", values=row)

        cursor.close()
        close_connection(conn)

    def perform_search(self, event):
        search_text = self.search_var.get().lower()

        conn = create_connection()
        cursor = conn.cursor()
        query = """
            SELECT * FROM GuestDetailsView
            WHERE LOWER(GuestName) LIKE %s
               OR LOWER(Gender) LIKE %s
               OR CAST(GuestID AS CHAR) LIKE %s
        """
        like_query = f"%{search_text}%"
        cursor.execute(query, (like_query, like_query, like_query))

        rows = cursor.fetchall()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

        cursor.close()
        close_connection(conn)
