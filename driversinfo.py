import tkinter as tk
from conn import create_connection, close_connection

class DriverInfoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Back button
        back_button = tk.Button(self, text="← Back",
                                command=lambda: controller.show_frame("ViewsPage"),
                                font=("Arial", 12), bd=0, bg="#ecf0f1")
        back_button.place(x=10, y=10)

        # Title
        title = tk.Label(self, text="Driver Information", font=("Arial", 24, "bold"))
        title.place(x=50, y=50)

        # Search field
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self, textvariable=self.search_var, font=("Arial", 12), width=30)
        search_entry.place(x=50, y=100)

        search_btn = tk.Button(self, text="Search", font=("Arial", 12), command=self.search_driver)
        search_btn.place(x=320, y=95)

        # Table headers
        self.headers = ["DriverID", "Name", "Age", "Gender", "CarName", "CarNumber", "Location", "MobNumber"]
        for col_index, header in enumerate(self.headers):
            label = tk.Label(self, text=header, font=("Arial", 12, "bold"), relief="ridge")
            label.place(x=20 + col_index * 120, y=140, width=120, height=30)

        self.data_labels = []
        self.display_driver_info()

    def display_driver_info(self):
        connection = create_connection()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM DriverInfo")
            data = cursor.fetchall()

            # Clear previous data
            for label in self.data_labels:
                label.destroy()
            self.data_labels.clear()

            for row_index, row in enumerate(data):
                for col_index, value in enumerate(row):
                    label = tk.Label(self, text=value, font=("Arial", 12), relief="groove")
                    label.place(x=20 + col_index * 120, y=170 + row_index * 30, width=120, height=30)
                    self.data_labels.append(label)
        except Exception as e:
            print("Error displaying driver info:", e)
        finally:
            close_connection(connection)

    def search_driver(self):
        connection = create_connection()
        if not connection:
            return

        try:
            search_text = f"%{self.search_var.get()}%"
            query = """
                SELECT * FROM DriverInfo
                WHERE Name LIKE %s OR
                      DriverID = %s OR
                      CarNumber LIKE %s OR
                      MobNumber LIKE %s OR
                      Location LIKE %s
            """
            params = (search_text,) * 5
            cursor = connection.cursor()
            cursor.execute(query, params)
            data = cursor.fetchall()

            for label in self.data_labels:
                label.destroy()
            self.data_labels.clear()

            for row_index, row in enumerate(data):
                for col_index, value in enumerate(row):
                    label = tk.Label(self, text=value, font=("Arial", 12), relief="groove")
                    label.place(x=20 + col_index * 120, y=170 + row_index * 30, width=120, height=30)
                    self.data_labels.append(label)
        except Exception as e:
            print("Error in search:", e)
        finally:
            close_connection(connection)
