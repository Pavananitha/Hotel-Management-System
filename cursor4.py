import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection

class LongStayGuests(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

        title_label = tk.Label(self, text="Guests Who Stayed More Than 5 Nights", font=("Arial", 18, "bold"), bg="white", fg="#003366")
        title_label.pack(pady=10)

        # Treeview Frame
        tree_frame = tk.Frame(self, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbar
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=("GuestID", "Name", "Nights"), show="headings", yscrollcommand=scroll_y.set)
        self.tree.heading("GuestID", text="Guest ID")
        self.tree.heading("Name", text="Guest Name")
        self.tree.heading("Nights", text="Total Nights")
        self.tree.column("GuestID", width=100, anchor="center")
        self.tree.column("Name", width=250)
        self.tree.column("Nights", width=120, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)

        # Load Button
        load_btn = tk.Button(self, text="Load Long-Stay Guests", font=("Arial", 12, "bold"), bg="#007ACC", command=self.load_guests)
        load_btn.pack(pady=10)

    def load_guests(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.callproc('GetLongStayGuests') ## cursor is called in this line

            self.tree.delete(*self.tree.get_children())  # Clear previous data

            for result in cursor.stored_results():
                for row in result.fetchall():
                    info = row[0]
                    try:
                        parts = info.replace('GuestID:', '').replace('Name:', '').replace('Nights:', '').split(',')
                        guest_id = int(parts[0].strip())
                        name = parts[1].strip()
                        nights = int(parts[2].strip())
                        self.tree.insert("", tk.END, values=(guest_id, name, nights))
                    except Exception as e:
                        print("Parsing error:", e)

            close_connection(conn)
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")
