import tkinter as tk
from tkinter import messagebox

class EmployeeVacationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Employee Vacation Tracker")
        self.master.geometry("400x500")

        self.employee_list = []

        self.create_widgets()

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

    def add_employee(self):
        employee_name = self.entry_employee_name.get()
        if employee_name:
            self.employee_list.append(employee_name)
            self.listbox_employees.insert(tk.END, employee_name)
            self.entry_employee_name.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter employee name.")

    def record_vacation(self):
        selected_employee = self.listbox_employees.curselection()
        if selected_employee:
            selected_employee_index = selected_employee[0]
            vacation_date = self.entry_vacation_date.get()
            if vacation_date:
                self.listbox_vacation_records.insert(tk.END, f"{self.employee_list[selected_employee_index]} - {vacation_date}")
                self.entry_vacation_date.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Please enter vacation date.")
        else:
            messagebox.showerror("Error", "Please select an employee.")

def main():
    root = tk.Tk()
    app = EmployeeVacationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
