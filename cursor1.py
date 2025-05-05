import tkinter as tk
from tkinter import ttk
from conn import create_connection, close_connection

class GuestDetailsVip(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        title = tk.Label(self, text="VIP Guests with Room & Event Hall Bookings", bg="white", font=("Arial", 18, "bold"))
        title.pack(pady=20)

        # Treeview
        columns = ("Guest ID", "Name", "Room Bookings", "Event Hall Bookings")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=200)

        self.tree.pack(pady=10)

        # Fetch button
        fetch_btn = tk.Button(self, text="Fetch Guests", command=self.fetch_and_display_data, bg="#3498db",  font=("Arial", 12, "bold"))
        fetch_btn.pack(pady=10)

    def fetch_and_display_data(self):
        # Clear existing data
        for row in self.tree.get_children():
            self.tree.delete(row)

        connection = create_connection()
        cursor = connection.cursor()

        try:
            cursor.callproc('GetGuestsWithRoomAndEventBooking')

            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    guest_id = row[0]
                    name = row[1]
                    room_count = row[2]
                    eventhall_count = row[3]
                    self.tree.insert("", tk.END, values=(guest_id, name, room_count, eventhall_count))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(connection)
