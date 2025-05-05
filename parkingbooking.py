import tkinter as tk
from tkinter import ttk, messagebox
from conn import create_connection, close_connection
import re

class ParkingBooking(tk.Frame):
    def __init__(self, parent, controller): 
        super().__init__(parent)
        self.controller = controller 
        self.configure(padx=20, pady=20)
        self.create_widgets()
        self.load_guests()

        back_btn = tk.Button(self, text="← Back", command=lambda: controller.show_frame("ReservationPage"), bg="#ecf0f1", font=("Arial", 12))
        back_btn.place(x=1100, y=10)

    def go_back(self):
        if self.controller:
            self.controller.show_frame("ReservationPage")

    def create_widgets(self):
        tk.Label(self, text="Select Guest:").grid(row=0, column=0, sticky="w")
        self.guest_combo = ttk.Combobox(self, state="readonly", width=40)
        self.guest_combo.grid(row=0, column=1, padx=5, pady=5)
        self.guest_combo.bind("<<ComboboxSelected>>", self.load_guest_details)

        self.guest_fields = {}
        labels = ["Name", "DOB", "Gender", "Aadhar No", "Mobile 1", "Mobile 2"]
        for i, label in enumerate(labels):
            tk.Label(self, text=f"{label}:").grid(row=i+1, column=0, sticky="w")
            entry = tk.Entry(self, state="readonly", width=40, bg="#f9f9f9")
            entry.grid(row=i+1, column=1, padx=5, pady=2)
            self.guest_fields[label] = entry

        tk.Label(self, text="Vehicle Number:").grid(row=7, column=0, sticky="w")
        self.vehicle_entry = tk.Entry(self, width=40)
        self.vehicle_entry.grid(row=7, column=1, padx=5, pady=5)

        tk.Label(self, text="Parking Fee (₹):").grid(row=8, column=0, sticky="w")
        self.fee_entry = tk.Entry(self, width=40)
        self.fee_entry.grid(row=8, column=1, padx=5, pady=5)

        tk.Label(self, text="Payment Status:").grid(row=9, column=0, sticky="w")
        self.payment_var = tk.StringVar(value="0")
        frame = tk.Frame(self)
        frame.grid(row=9, column=1, sticky="w", padx=5)
        tk.Radiobutton(frame, text="Unpaid", variable=self.payment_var, value="0").pack(side="left")
        tk.Radiobutton(frame, text="Paid", variable=self.payment_var, value="1").pack(side="left")

        tk.Button(self, text="Book Parking", command=self.book_parking, bg="orange", fg="black").grid(row=10, column=0, pady=10)
        tk.Button(self, text="Clear Fields", command=self.clear_fields, bg="orange", fg="black").grid(row=10, column=1)

    def load_guests(self):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT GuestID, Name FROM Guest")
            rows = cursor.fetchall()
            self.guest_map = {f"{name}-{gid}": gid for gid, name in rows}
            self.guest_combo['values'] = list(self.guest_map.keys())
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load guests: {e}")
        finally:
            cursor.close()
            close_connection(conn)

    def load_guest_details(self, event=None):
        selected = self.guest_combo.get()
        guest_id = self.guest_map.get(selected)

        if guest_id is None:
            messagebox.showerror("Selection Error", "Selected guest not found.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            # Load basic guest info
            cursor.execute(
                "SELECT Name, DOB, Gender, AadharNo FROM Guest WHERE GuestID = %s", (guest_id,))
            guest_row = cursor.fetchone()

            # Load up to 2 mobile numbers
            cursor.execute(
                "SELECT MobNo FROM GuestMobile WHERE GuestID = %s LIMIT 2", (guest_id,))
            mobile_rows = cursor.fetchall()

            if guest_row:
                values = list(guest_row)
                mobiles = [row[0] for row in mobile_rows]
                while len(mobiles) < 2:
                    mobiles.append("")
                values.extend(mobiles)
                for key, val in zip(self.guest_fields.keys(), values):
                    entry = self.guest_fields[key]
                    entry.config(state="normal")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(val))
                    entry.config(state="readonly")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading guest details: {e}")
        finally:
            cursor.close()
            close_connection(conn)

    def book_parking(self):
        guest_str = self.guest_combo.get()
        vehicle = self.vehicle_entry.get().strip().upper()
        fee = self.fee_entry.get().strip()
        payment_status = int(self.payment_var.get())

        if not guest_str or not vehicle or not fee:
            messagebox.showwarning("Missing Fields", "Please fill all required fields.")
            return

        if not self.validate_vehicle_number(vehicle):
            messagebox.showerror("Invalid Input", "Vehicle number format invalid. Example: MH12AB1234")
            return

        try:
            fee = float(fee)
            if fee < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Parking fee must be a positive number.")
            return

        guest_id = self.guest_map.get(guest_str)
        if guest_id is None:
            messagebox.showerror("Error", "Selected guest is invalid.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Parking (GuestID, VehicleNum, ParkingFee, PaymentStatus) VALUES (%s, %s, %s, %s)",
                (guest_id, vehicle, fee, payment_status)
            )
            conn.commit()
            messagebox.showinfo("Success", "Parking booked successfully!")
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to book parking: {e}")
        finally:
            cursor.close()
            close_connection(conn)

    def clear_fields(self):
        self.vehicle_entry.delete(0, tk.END)
        self.fee_entry.delete(0, tk.END)
        self.payment_var.set("0")
        self.guest_combo.set("")
        for entry in self.guest_fields.values():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.config(state="readonly")

    def validate_vehicle_number(self, vehicle):
        pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
        return re.fullmatch(pattern, vehicle) is not None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Parking Booking Management")
    root.geometry("800x600")
    ParkingBooking(root, controller=None).pack(fill="both", expand=True)
    root.mainloop()
