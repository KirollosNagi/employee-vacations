import tkinter as tk
import sqlite3
import csv
from tkinter import messagebox

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

        # Listbox to display vacation records
        self.listbox_vacation_records = tk.Listbox(self.master)
        self.listbox_vacation_records.pack()

        # Button to export employees and vacations
        self.button_export_employees = tk.Button(self.master, text="Export Employees", command=self.export_employees)
        self.button_export_employees.pack()

        self.button_export_vacations = tk.Button(self.master, text="Export Vacations", command=self.export_vacations)
        self.button_export_vacations.pack()

        # Populate employees listbox
        self.populate_employees_listbox()
        self.populate_vacation_records_listbox()

    def add_employee(self):
        employee_name = self.entry_employee_name.get()
        if employee_name:
            self.cur.execute("INSERT INTO employees (name) VALUES (?)", (employee_name,))
            self.conn.commit()
            self.populate_employees_listbox()
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

    def check_duplicate_vacation(self, employee_id, vacation_date):
        self.cur.execute("SELECT * FROM vacations WHERE employee_id=? AND date=?", (employee_id, vacation_date))
        return self.cur.fetchone() is not None

    def populate_employees_listbox(self):
        self.listbox_employees.delete(0, tk.END)
        self.cur.execute("SELECT * FROM employees")
        employees = self.cur.fetchall()
        for employee in employees:
            self.listbox_employees.insert(tk.END, employee)

    def populate_vacation_records_listbox(self):
        self.listbox_vacation_records.delete(0, tk.END)
        self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id")
        vacation_records = self.cur.fetchall()
        for record in vacation_records:
            self.listbox_vacation_records.insert(tk.END, f"{record[0]} - {record[1]}")

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
