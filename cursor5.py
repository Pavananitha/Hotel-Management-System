import tkinter as tk
from tkinter import ttk
from conn import create_connection, close_connection

class UnpaidBillsPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        super().__init__(parent, bg="white")
        self.parent = parent
        self.create_widgets()

        # Back button
        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("CursorPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def create_widgets(self):
        # Create treeview for displaying unpaid bills
        self.tree = ttk.Treeview(self, columns=("GuestID", "GuestName", "BillType", "BillID"), show="headings")
        self.tree.heading("GuestID", text="Guest ID")
        self.tree.heading("GuestName", text="Guest Name")
        self.tree.heading("BillType", text="Bill Type")
        self.tree.heading("BillID", text="Bill ID")
        self.tree.place(x=20, y=50, width=1150, height=600)

        self.load_unpaid_bills()

    def load_unpaid_bills(self):
        conn = create_connection()  # Establish database connection
        cursor = conn.cursor()

        try:
            cursor.callproc('ShowUnpaidBillsByGuest')  # Call the stored procedure

            # Fetch all results from the procedure
            for result in cursor.stored_results():
                rows = result.fetchall()

                # Insert each row into the treeview
                for row in rows:
                    self.tree.insert("", tk.END, values=row)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            close_connection(conn)  # Close the connection after the operation is done

# Assuming you have a controller and parent frame set up properly
# Example usage:
# root = tk.Tk()
# controller = Controller(root)
# UnpaidBillsPage(root, controller).pack()
# root.mainloop()
