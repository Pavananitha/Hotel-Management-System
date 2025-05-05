import tkinter as tk
from tkinter import ttk
from conn import create_connection, close_connection

class QualifiedFeedbackGuestsPage(tk.Frame):
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
        title = tk.Label(self, text="Guests with Rating 5 and 3+ Paid Services",
                         font=("Arial", 16, "bold"),  fg="white")
        title.pack(pady=20)

        # Frame for the table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Scrollbars
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")

        # Treeview
        self.tree = ttk.Treeview(table_frame,
                                 columns=("GuestID", "Name", "DOB", "Gender"),
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_y.config(command=self.tree.yview)

        scroll_x.pack(side="bottom", fill="x")
        scroll_x.config(command=self.tree.xview)

        self.tree.heading("GuestID", text="Guest ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("DOB", text="Date of Birth")
        self.tree.heading("Gender", text="Gender")

        self.tree["show"] = "headings"
        self.tree.column("GuestID", width=100, anchor="center")
        self.tree.column("Name", width=200, anchor="center")
        self.tree.column("DOB", width=120, anchor="center")
        self.tree.column("Gender", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

        self.load_data()

    def load_data(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()

            query = """
            SELECT Name, GuestID, DOB, Gender 
FROM Guest 
WHERE GuestID IN (
    SELECT GuestID 
    FROM (
        SELECT GuestID,
               (CASE WHEN EXISTS (SELECT 1 FROM Reservation WHERE GuestID = g.GuestID AND PaymentStatus = TRUE) THEN 1 ELSE 0 END) +
               (CASE WHEN EXISTS (SELECT 1 FROM Parking WHERE GuestID = g.GuestID AND PaymentStatus = TRUE) THEN 1 ELSE 0 END) +
               (CASE WHEN EXISTS (SELECT 1 FROM OrderTable WHERE GuestID = g.GuestID AND PaymentStatus = TRUE) THEN 1 ELSE 0 END) +
               (CASE WHEN EXISTS (SELECT 1 FROM EventBooking WHERE GuestID = g.GuestID AND PaymentStatus = TRUE) THEN 1 ELSE 0 END) AS ServiceCount
        FROM Guest g
    ) AS svc
    WHERE ServiceCount > 2
);
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            # Clear previous data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert rows into tree
            for row in rows:
                self.tree.insert("", "end", values=(row[1], row[0], row[2], row[3]))

        except Exception as e:
            print("Error loading data:", e)
        finally:
            close_connection(conn)
