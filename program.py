import tkinter as tk
import sqlite3
import csv
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime

class EmployeeVacationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Employee Vacation Tracker")
        self.master.geometry("400x600")

        # Initialize database
        self.conn = sqlite3.connect("employee_vacations.db")
        self.cur = self.conn.cursor()
        self.create_table()

        self.create_widgets()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS employees (
                                id INTEGER PRIMARY KEY,
                                name TEXT
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS vacations (
                                id INTEGER PRIMARY KEY,
                                employee_id INTEGER,
                                date TEXT,
                                UNIQUE(employee_id, date),
                                FOREIGN KEY(employee_id) REFERENCES employees(id)
                            )''')
        self.conn.commit()

    def create_widgets(self):
        # Label and Entry for Employee Name
        self.label_employee_name = tk.Label(self.master, text="Employee Name:")
        self.label_employee_name.pack()
        self.entry_employee_name = tk.Entry(self.master)
        self.entry_employee_name.pack()

        # Button to add employee
        self.button_add_employee = tk.Button(self.master, text="Add Employee", command=self.add_employee)
        self.button_add_employee.pack()

        # Listbox to display employees
        self.listbox_employees = tk.Listbox(self.master)
        self.listbox_employees.pack()

        # Button to remove employee
        self.button_remove_employee = tk.Button(self.master, text="Remove Employee", command=self.remove_employee)
        self.button_remove_employee.pack()

        # Label and Entry for Vacation Date
        self.label_vacation_date = tk.Label(self.master, text="Vacation Date (YYYY-MM-DD):")
        self.label_vacation_date.pack()
        self.entry_vacation_date = tk.Entry(self.master)
        self.entry_vacation_date.pack()

        # Button to record vacation
        self.button_record_vacation = tk.Button(self.master, text="Record Vacation", command=self.record_vacation)
        self.button_record_vacation.pack()

        # Button to remove vacation
        self.button_remove_vacation = tk.Button(self.master, text="Remove Vacation", command=self.remove_vacation)
        self.button_remove_vacation.pack()

        # Button to import vacations from CSV
        self.button_import_vacations = tk.Button(self.master, text="Import Vacations from CSV", command=self.import_vacations_from_csv)
        self.button_import_vacations.pack()

        # Listbox to display vacation records
        self.listbox_vacation_records = tk.Listbox(self.master)
        self.listbox_vacation_records.pack()

        # Button to export employees and vacations
        self.button_export_employees = tk.Button(self.master, text="Export Employees", command=self.export_employees)
        self.button_export_employees.pack()

        self.button_export_vacations = tk.Button(self.master, text="Export Vacations", command=self.export_vacations)
        self.button_export_vacations.pack()

        self.listbox_employees.bind("<<ListboxSelect>>", self.populate_vacation_records_listbox)
        
        # Populate employees listbox
        self.populate_employees_listbox()
        self.populate_vacation_records_listbox()

    def add_employee(self):
        employee_name = self.entry_employee_name.get()
        if employee_name:
            self.cur.execute("INSERT INTO employees (name) VALUES (?)", (employee_name,))
            self.conn.commit()
            self.populate_employees_listbox()
            self.populate_vacation_records_listbox()
            self.entry_employee_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter employee name.")

    def remove_employee(self):
        selected_employee = self.listbox_employees.curselection()
        if selected_employee:
            selected_employee_id = self.listbox_employees.get(selected_employee)[0]
            self.cur.execute("DELETE FROM employees WHERE id=?", (selected_employee_id,))
            self.cur.execute("DELETE FROM vacations WHERE employee_id=?", (selected_employee_id,))
            self.conn.commit()
            self.populate_employees_listbox()
            self.populate_vacation_records_listbox()
        else:
            messagebox.showerror("Error", "Please select an employee.")

    def record_vacation(self):
        selected_employee = self.listbox_employees.curselection()
        if selected_employee:
            selected_employee_id = self.listbox_employees.get(selected_employee)[0]
            vacation_date = self.entry_vacation_date.get()
            if vacation_date:
                if not self.check_duplicate_vacation(selected_employee_id, vacation_date):
                    self.cur.execute("INSERT INTO vacations (employee_id, date) VALUES (?, ?)", (selected_employee_id, vacation_date))
                    self.conn.commit()
                    self.populate_vacation_records_listbox()
                    self.entry_vacation_date.delete(0, tk.END)
                else:
                    messagebox.showerror("Error", "Vacation for this employee on this date already exists.")
            else:
                messagebox.showerror("Error", "Please enter vacation date.")
        else:
            messagebox.showerror("Error", "Please select an employee.")

    def remove_vacation(self):
        selected_vacation = self.listbox_vacation_records.curselection()
        if selected_vacation:
            vacation_info = self.listbox_vacation_records.get(selected_vacation)
            employee_name, vacation_date = vacation_info.split(" - ")
            self.cur.execute("SELECT id FROM employees WHERE name=?", (employee_name,))
            employee_id = self.cur.fetchone()[0]
            self.cur.execute("DELETE FROM vacations WHERE employee_id=? AND date=?", (employee_id, vacation_date))
            self.conn.commit()
            self.populate_vacation_records_listbox()
        else:
            messagebox.showerror("Error", "Please select a vacation record to remove.")

    def check_duplicate_vacation(self, employee_id, vacation_date):
        self.cur.execute("SELECT * FROM vacations WHERE employee_id=? AND date=?", (employee_id, vacation_date))
        return self.cur.fetchone() is not None

    def populate_employees_listbox(self):
        self.listbox_employees.delete(0, tk.END)
        self.cur.execute("SELECT * FROM employees")
        employees = self.cur.fetchall()
        for employee in employees:
            self.listbox_employees.insert(tk.END, employee)

    def populate_vacation_records_listbox(self, event=None):
        self.listbox_vacation_records.delete(0, tk.END)
        selected_index = self.listbox_employees.curselection()
        if selected_index:
            selected_employee_id = self.listbox_employees.get(selected_index)[0]
            self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id WHERE e.id=?", (selected_employee_id,))
        else:
            self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id")
        vacation_records = self.cur.fetchall()
        for record in vacation_records:
            self.listbox_vacation_records.insert(tk.END, f"{record[0]} - {record[1]}")


    def import_vacations_from_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            with open(filename, "r") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 2:
                        employee_name, vacation_date = row
                        try:
                            # Parsing date to ensure consistent format
                            vacation_date = self.parse_date(vacation_date)
                            employee_id = self.get_or_add_employee_id(employee_name)
                            if not self.check_duplicate_vacation(employee_id, vacation_date):
                                self.cur.execute("INSERT INTO vacations (employee_id, date) VALUES (?, ?)", (employee_id, vacation_date))
                                self.conn.commit()
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid date format: {vacation_date}")
            self.populate_employees_listbox()
            self.populate_vacation_records_listbox()
            messagebox.showinfo("Import Successful", "Vacations imported successfully.")
        else:
            messagebox.showerror("Error", "No file selected.")


    def parse_date(self, date_str):
        formats_to_try = ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%d/%m/%Y"]  # Add more formats if needed
        for date_format in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_str, date_format).date()
                return parsed_date.strftime("%Y-%m-%d")  # Standardize to YYYY-MM-DD format
            except ValueError:
                continue
        raise ValueError(f"Date string: '{date_str}' does not match any known format")

    def get_or_add_employee_id(self, employee_name):
        employee_name = employee_name.strip()
        self.cur.execute("SELECT id FROM employees WHERE name=?", (employee_name,))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            self.cur.execute("INSERT INTO employees (name) VALUES (?)", (employee_name,))
            self.conn.commit()
            return self.cur.lastrowid

    def export_employees(self):
        with open("employees.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Employee ID", "Name"])
            self.cur.execute("SELECT * FROM employees")
            employees = self.cur.fetchall()
            for employee in employees:
                writer.writerow(employee)

        messagebox.showinfo("Export Successful", "Employees exported to employees.csv")

    def export_vacations(self):
        with open("vacations.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Employee Name", "Vacation Date"])
            self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id")
            vacation_records = self.cur.fetchall()
            for record in vacation_records:
                writer.writerow(record)

        messagebox.showinfo("Export Successful", "Vacations exported to vacations.csv")

def main():
    root = tk.Tk()
    app = EmployeeVacationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
