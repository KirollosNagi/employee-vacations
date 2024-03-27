import tkinter as tk
import sqlite3
from tkinter import messagebox

class EmployeeVacationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Employee Vacation Tracker")
        self.master.geometry("400x500")

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

    def record_vacation(self):
        selected_employee = self.listbox_employees.curselection()
        if selected_employee:
            selected_employee_id = self.listbox_employees.get(selected_employee)[0]
            vacation_date = self.entry_vacation_date.get()
            if vacation_date:
                self.cur.execute("INSERT INTO vacations (employee_id, date) VALUES (?, ?)", (selected_employee_id, vacation_date))
                self.conn.commit()
                self.populate_vacation_records_listbox()
                self.entry_vacation_date.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Please enter vacation date.")
        else:
            messagebox.showerror("Error", "Please select an employee.")

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

def main():
    root = tk.Tk()
    app = EmployeeVacationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
