import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection
import mysql.connector


class Feedback(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.configure(padx=10, pady=10)
        self.create_widgets()
        self.populate_guest_combobox()
        self.populate_feedback_table()

        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"),
                             bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Guest Details Frame
        guest_frame = ttk.LabelFrame(self, text="Guest Details")
        guest_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        ttk.Label(guest_frame, text="Select Guest:").grid(row=0, column=0, sticky="w")
        self.guest_cb = ttk.Combobox(guest_frame, state="readonly")
        self.guest_cb.grid(row=0, column=1, pady=5)
        self.guest_cb.bind("<<ComboboxSelected>>", self.fill_guest_details)

        labels = ["Name", "DOB", "Gender", "AadharNo"]
        self.guest_labels = {}
        for i, label in enumerate(labels, start=1):
            ttk.Label(guest_frame, text=label + ":").grid(row=i, column=0, sticky="w")
            lbl = ttk.Label(guest_frame, text="")
            lbl.grid(row=i, column=1, sticky="w", pady=2)
            self.guest_labels[label] = lbl

        # Feedback Entry Frame
        feedback_frame = ttk.LabelFrame(self, text="Feedback")
        feedback_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        ttk.Label(feedback_frame, text="Service Type:").grid(row=0, column=0, sticky="w")
        self.service_cb = ttk.Combobox(feedback_frame, state="readonly", values=[
            "Room Service", "Accommodation", "Housekeeping", "Dinning", "Events",
            "Transportation", "Security", "Guest Relation", "WiFi & Smart Controls"
        ])
        self.service_cb.grid(row=0, column=1, pady=5)

        ttk.Label(feedback_frame, text="Rating:").grid(row=1, column=0, sticky="w")
        self.rating_cb = ttk.Combobox(feedback_frame, state="readonly", values=[
            "1 - Bad", "2 - Poor", "3 - Average", "4 - Good", "5 - Excellent"
        ])
        self.rating_cb.grid(row=1, column=1, pady=5)

        button_frame = tk.Frame(feedback_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Submit", command=self.submit_feedback).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).grid(row=0, column=1, padx=5)

        # Feedback Table
        table_frame = ttk.LabelFrame(self, text="All Feedback")
        table_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="nsew")

        columns = ("GuestID", "Name", "ServiceType", "Rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

    def populate_guest_combobox(self):
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT GuestID, Name FROM Guest")
            self.guests = cursor.fetchall()
            self.guest_cb['values'] = [f"{name} - {gid}" for gid, name in self.guests]
            close_connection(conn)
            cursor.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load guests: {e}")

    def fill_guest_details(self, event=None):
        selection = self.guest_cb.get()
        if not selection:
            return
        guest_id = int(selection.split("-")[-1].strip())

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Name, DOB, Gender, AadharNo FROM Guest WHERE GuestID = %s", (guest_id,))
            result = cursor.fetchone()
            close_connection(conn)
            cursor.close()

            if result:
                self.guest_labels["Name"].config(text=result[0])
                self.guest_labels["DOB"].config(text=result[1])
                self.guest_labels["Gender"].config(text=result[2])
                self.guest_labels["AadharNo"].config(text=result[3])
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load guest details: {e}")

    def submit_feedback(self):
        if not self.guest_cb.get() or not self.service_cb.get() or not self.rating_cb.get():
            messagebox.showwarning("Missing Data", "Please fill all fields.")
            return

        guest_id = int(self.guest_cb.get().split("-")[-1].strip())
        service_type = self.service_cb.get()
        rating = int(self.rating_cb.get().split(" - ")[0])

        try:
            conn = create_connection()
            cursor = conn.cursor()
            query = "INSERT INTO Feedback (GuestID, Rating, ServiceType) VALUES (%s, %s, %s)"
            cursor.execute(query, (guest_id, rating, service_type))
            conn.commit()
            close_connection(conn)
            cursor.close()

            messagebox.showinfo("Success", "Feedback submitted successfully.")
            self.populate_feedback_table()
            self.clear_fields()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to submit feedback: {e}")

    def clear_fields(self):
        self.guest_cb.set('')
        for lbl in self.guest_labels.values():
            lbl.config(text="")
        self.service_cb.set('')
        self.rating_cb.set('')

    def populate_feedback_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = create_connection()
            cursor = conn.cursor()
            query = """
                SELECT f.GuestID, g.Name, f.ServiceType, f.Rating
                FROM Feedback f
                JOIN Guest g ON f.GuestID = g.GuestID
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
            close_connection(conn)
            cursor.close()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to load feedbacks: {e}")

# Run standalone
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Feedback Management")
    root.geometry("750x500")
    Feedback(root).pack(fill="both", expand=True)
    root.mainloop()
