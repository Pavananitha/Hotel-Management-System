import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class UnpaidRoomsPage(tk.Frame):
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
        title = tk.Label(self, text="Rooms Reserved but Not Yet Paid", bg="black", font=("Arial", 16, "bold"))
        title.pack(pady=20)

        # Frame for table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

        # Treeview
        self.room_table = ttk.Treeview(table_frame,
                                       columns=("RoomID", "RoomNumber", "RoomType", "Availability"),
                                       xscrollcommand=scroll_x.set,
                                       yscrollcommand=scroll_y.set)

        scroll_x.config(command=self.room_table.xview)
        scroll_y.config(command=self.room_table.yview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.room_table.pack(fill=tk.BOTH, expand=True)

        # Define headings
        self.room_table.heading("RoomID", text="Room ID")
        self.room_table.heading("RoomNumber", text="Room Number")
        self.room_table.heading("RoomType", text="Room Type")
        self.room_table.heading("Availability", text="Availability")

        self.room_table["show"] = "headings"

        # Column widths
        for col in self.room_table["columns"]:
            self.room_table.column(col, width=150)

        self.fetch_unpaid_rooms()

    def fetch_unpaid_rooms(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            query = """
                SELECT * FROM Room
                WHERE RoomID IN (
                    SELECT RoomID FROM Reservation
                    WHERE PaymentStatus = FALSE
                );
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            # Clear existing table entries
            self.room_table.delete(*self.room_table.get_children())

            for row in rows:
                self.room_table.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching data:\n{e}")
        finally:
            close_connection(conn)
