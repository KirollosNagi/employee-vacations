import tkinter as tk
import sqlite3
import csv
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime, timedelta
import os

class EmployeeVacationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Employee Vacation Tracker")
        self.master.geometry("500x700")

        # Initialize database
        self.conn = sqlite3.connect("employee_vacations.db")
        self.cur = self.conn.cursor()
        self.create_table()

        self.create_widgets()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS employees (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                start_date DATE
                            )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS vacations (
                                id INTEGER PRIMARY KEY,
                                employee_id INTEGER,
                                date DATE,
                                UNIQUE(employee_id, date),
                                FOREIGN KEY(employee_id) REFERENCES employees(id)
                            )''')
        self.conn.commit()

    def create_widgets(self):
        # Label and Entry for Employee Name
        self.label_employee_name = tk.Label(self.master, text="Employee Name:")
        self.label_employee_name.grid(row=0, column=0, padx=10, pady=5)
        self.entry_employee_name = tk.Entry(self.master)
        self.entry_employee_name.grid(row=0, column=1, padx=10, pady=5)

        # Label and Entry for Start Date
        self.label_start_date = tk.Label(self.master, text="Start Date (YYYY-MM-DD):")
        self.label_start_date.grid(row=1, column=0, padx=10, pady=5)
        self.entry_start_date = tk.Entry(self.master)
        self.entry_start_date.grid(row=1, column=1, padx=10, pady=5)

        # Button to add employee
        self.button_add_employee = tk.Button(self.master, text="Add Employee", command=self.add_employee)
        self.button_add_employee.grid(row=2, column=0, columnspan=1, padx=10, pady=5)

        # Button to import employees from CSV
        self.button_import_employees = tk.Button(self.master, text="Import Employees from CSV", command=self.import_employees_from_csv)
        self.button_import_employees.grid(row=2, column=1, columnspan=1, padx=10, pady=5)
        
        # Listbox to display employees
        self.listbox_employees = tk.Listbox(self.master)
        self.listbox_employees.grid(row=3, column=0, columnspan=1,rowspan=2, padx=10, pady=5)
        
        # Label to display actual start date
        self.label_actual_start_date = tk.Label(self.master, text="")
        self.label_actual_start_date.grid(row=3, column=1, columnspan=1,rowspan=1, padx=10, pady=5)
        
        # Label to display PTO Balance
        self.label_balance = tk.Label(self.master, text="")
        self.label_balance.grid(row=4, column=1, columnspan=1,rowspan=1, padx=10, pady=5)
        
        # Button to remove employee
        self.button_remove_employee = tk.Button(self.master, text="Remove Employee", command=self.remove_employee)
        self.button_remove_employee.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        # Label and Entry for Vacation Date
        self.label_vacation_date = tk.Label(self.master, text="Vacation Date (YYYY-MM-DD):")
        self.label_vacation_date.grid(row=6, column=0, columnspan=1, padx=10, pady=5)
        self.entry_vacation_date = tk.Entry(self.master)
        self.entry_vacation_date.grid(row=6, column=1, columnspan=1, padx=10, pady=5)

        # Button to record vacation
        self.button_record_vacation = tk.Button(self.master, text="Record Vacation", command=self.record_vacation)
        self.button_record_vacation.grid(row=7, column=0, columnspan=1, padx=10, pady=5)

        # Button to import vacations from CSV
        self.button_import_vacations = tk.Button(self.master, text="Import Vacations from CSV", command=self.import_vacations_from_csv)
        self.button_import_vacations.grid(row=7, column=1, columnspan=1, padx=10, pady=5)

        # Listbox to display vacation records
        self.listbox_vacation_records = tk.Listbox(self.master)
        self.listbox_vacation_records.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        # Button to remove vacation
        self.button_remove_vacation = tk.Button(self.master, text="Remove Vacation", command=self.remove_vacation)
        self.button_remove_vacation.grid(row=9, column=0, columnspan=2, padx=10, pady=5)


        # Button to export employees and vacations
        self.button_export_employees = tk.Button(self.master, text="Export Employees", command=self.export_employees)
        self.button_export_employees.grid(row=10, column=0, columnspan=1, padx=10, pady=5)

        self.button_export_vacations = tk.Button(self.master, text="Export Vacations", command=self.export_vacations)
        self.button_export_vacations.grid(row=10, column=1, columnspan=1, padx=10, pady=5)

        self.button_export_vacations = tk.Button(self.master, text="Export All Employees sheets", command=self.export_employees_all)
        self.button_export_vacations.grid(row=11, column=0, columnspan=2, padx=10, pady=5)

        self.listbox_employees.bind("<<ListboxSelect>>", self.populate_vacation_records_listbox)

        # Populate employees listbox
        self.populate_employees_listbox()
        self.populate_vacation_records_listbox()

    def get_vacations_taken(self, emp_id, start_date, end_date):
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        self.cur.execute("SELECT COUNT(*) FROM vacations WHERE employee_id=? AND date >= ? AND date <= ?", (emp_id, start_date_str, end_date_str))
        vacations_taken = self.cur.fetchone()[0]
        return vacations_taken

    def calculate_pto_balance(self, emp_id, start_date, reference_date):
        six_months_after_start = start_date + timedelta(days=180)
        start_date_plus_one_year = datetime(six_months_after_start.year + 1, 1, 1).date()
        
        if reference_date <= six_months_after_start:
            return 6 - self.get_vacations_taken(emp_id, start_date, reference_date)
        elif reference_date <= start_date_plus_one_year:
            remaining_days = (start_date_plus_one_year - six_months_after_start).days  # Approximate remaining months
            yearly_pto = round(remaining_days / 365 * 21)  # 21 days PTO per year
            return yearly_pto - self.get_vacations_taken(emp_id, six_months_after_start, reference_date)
        else:
            old_balance = self.calculate_pto_balance(emp_id, start_date, start_date_plus_one_year)
            return self.calculate_pto_balance_helper(emp_id, start_date_plus_one_year, reference_date, old_balance)
    
    def calculate_pto_balance_helper(self, emp_id, first_full_year, reference_date, old_balance=0):
        balance = 0
        i = first_full_year.year
        while i < reference_date.year:
            start_date = datetime(i, 1, 1).date()
            end_date = datetime(i, 3, 1).date()
            balance += old_balance + 21 - self.get_vacations_taken(emp_id, start_date, end_date)
            balance = min(balance, 21) # PTO cap
            start_date = datetime(i, 3, 2).date()
            end_date = datetime(i, 12, 31).date()
            balance -= self.get_vacations_taken(emp_id, start_date, end_date)
            old_balance = balance
            balance = 0
            i += 1

        if reference_date < datetime(i, 3, 1).date():
            start_date = datetime(i, 1, 1).date()
            end_date = reference_date
            balance += old_balance + 21 - self.get_vacations_taken(emp_id, start_date, end_date)
            return balance
        else:
            start_date = datetime(i, 1, 1).date()
            end_date = datetime(i, 3, 1).date()
            balance += old_balance + 21 - self.get_vacations_taken(emp_id, start_date, end_date)
            balance = min(balance, 21) # PTO cap
            start_date = datetime(i, 3, 2).date()
            end_date = reference_date
            balance -= self.get_vacations_taken(emp_id, start_date, end_date)
            return balance

    def add_employee(self):
        employee_name = self.entry_employee_name.get()
        start_date = self.entry_start_date.get()
        if employee_name:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                self.cur.execute("INSERT INTO employees (name, start_date) VALUES (?, ?)", (employee_name, start_date_obj))
                self.conn.commit()
                self.populate_employees_listbox()
                self.entry_employee_name.delete(0, tk.END)
                self.entry_start_date.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
        else:
            messagebox.showerror("Error", "Please enter employee name and start date.")

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
        self.cur.execute("SELECT id, name FROM employees")
        employees = self.cur.fetchall()
        for employee in employees:
            self.listbox_employees.insert(tk.END, employee)

    def populate_vacation_records_listbox(self, event=None):
        self.listbox_vacation_records.delete(0, tk.END)
        selected_index = self.listbox_employees.curselection()
        if selected_index:
            selected_employee_id = self.listbox_employees.get(selected_index)[0]
            self.cur.execute("SELECT name, start_date FROM employees WHERE id=?", (selected_employee_id,))
            employee_info = self.cur.fetchone()
            if employee_info:
                employee_name, start_date_str = employee_info
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                balance = self.calculate_pto_balance(selected_employee_id, start_date, datetime.now().date())
                self.label_balance.config(text=f"PTO Balance for {employee_name}: {balance} days")
                self.label_actual_start_date.config(text=f"Start Date for {employee_name}: {start_date_str}")
                self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id WHERE e.id=?", (selected_employee_id,))
            else:
                self.label_balance.config(text="")
                self.label_actual_start_date.config(text="")
        else:
            self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id")
            self.label_balance.config(text="")
            self.label_actual_start_date.config(text="")

        vacation_records = self.cur.fetchall()
        for record in vacation_records:
            self.listbox_vacation_records.insert(tk.END, f"{record[0]} - {record[1]}")

    def import_employees_from_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            with open(filename, "r") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) == 2:
                        employee_name, start_date_str = row
                        try:
                            # Parsing date to ensure consistent format
                            start_date = self.parse_date(start_date_str)
                            employee_id = self.get_employee_id(employee_name)
                            if not employee_id:
                                self.cur.execute("INSERT INTO employees (name, start_date) VALUES (?, ?)", (employee_name, start_date))
                                self.conn.commit()
                            else:
                                self.cur.execute("UPDATE employees SET start_date=? WHERE id=?", (start_date, employee_id))
                                self.conn.commit()
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid start date format: {start_date_str}")
            self.populate_employees_listbox()
            messagebox.showinfo("Import Successful", "Employees imported successfully.")
        else:
            messagebox.showerror("Error", "No file selected.")

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
                            employee_id = self.get_employee_id(employee_name)
                            if not employee_id:
                                messagebox.showerror("Error", f"Employee '{employee_name}' not found.")
                                print(f"Employee '{employee_name}' not found.")
                                continue
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
                if parsed_date > datetime.now().date():
                    print(f"Date '{date_str}' is in the future. Skipping.")
                    raise ValueError
                return parsed_date.strftime("%Y-%m-%d")  # Standardize to YYYY-MM-DD format
            except ValueError:
                continue
        raise ValueError(f"Date string: '{date_str}' does not match any known format")

    def get_employee_id(self, employee_name):
        employee_name = employee_name.strip()
        self.cur.execute("SELECT id FROM employees WHERE name=?", (employee_name,))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return None

    def export_employees(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        file_name = f"employees_balances_{today}.csv"
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Start Date", "balance"])
            self.cur.execute("SELECT * FROM employees")
            employees = self.cur.fetchall()
            for employee in employees:
                emp_id, name, start_date = employee
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                balance = self.calculate_pto_balance(emp_id, start_date, datetime.now().date())
                writer.writerow([name, start_date, balance])

        messagebox.showinfo("Export Successful", f"Employees exported to {file_name}")

    def export_employees_all(self):
            folder_name = rf"output/{datetime.now().date().strftime('%Y-%m-%d')}/"
            os.makedirs(folder_name, exist_ok=True)
            # get all employee ids
            self.cur.execute("SELECT * FROM employees")
            employees = self.cur.fetchall()
            for employee in employees:
                emp_id, name, start_date = employee
                self.export_vacations(name=f'{folder_name}{name}',id=emp_id,silent=True)
            messagebox.showinfo("Export Successful", f"Employees exported to {folder_name}")


    def export_vacations(self, name="vacations",id=None,silent=False):
        with open(f'{name}.csv', "w", newline="") as file:
            writer = csv.writer(file)
            if id:
                # write in the write the balance for this employee
                self.cur.execute("SELECT name, start_date FROM employees WHERE id=?", (id,))
                employee_info = self.cur.fetchone()
                if employee_info:
                    employee_name, start_date_str = employee_info
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    balance = self.calculate_pto_balance(id, start_date, datetime.now().date())
                    writer.writerow(["Name", "Start Date", "balance"])
                    writer.writerow([employee_name, start_date_str, balance])
                    writer.writerow([''])
                
                self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id WHERE e.id=?", (id,))
            else:
                self.cur.execute("SELECT e.name, v.date FROM vacations v JOIN employees e ON v.employee_id = e.id")
            writer.writerow(["Employee Name", "Vacation Date"])
            vacation_records = self.cur.fetchall()
            for record in vacation_records:
                writer.writerow(record)
        
        if not silent:
            messagebox.showinfo("Export Successful", f"Vacations exported to {name}.csv")

def main():
    root = tk.Tk()
    app = EmployeeVacationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
