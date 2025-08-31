import pandas as pd
from datetime import datetime
import os
import tkinter as tk
from tkinter import messagebox


csv_file = 'attendance_log.csv'


if not os.path.exists(csv_file):
    messagebox.showerror("Error",
                         "The 'attendance_log.csv' file was not found. Please run the face_authenticator.py script first.")
    exit()


students_df = None
student_list = []
selected_student = None


def get_unique_students():

    global students_df
    try:
        students_df = pd.read_csv(csv_file)
        if 'Authenticated' not in students_df.columns:
            students_df['Authenticated'] = 'No'
        if 'Status' not in students_df.columns:
            students_df['Status'] = ''

        global student_list
        student_list = students_df['Name'].str.lower().unique().tolist()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the CSV file: {e}")
        exit()


def select_student(name):

    global selected_student
    selected_student = name
    status_label.config(text=f"Selected: {name.title()}")


def mark_attendance(status):

    global students_df
    global selected_student

    if not selected_student:
        messagebox.showwarning("Warning", "Please select a student first.")
        return


    row_to_update = students_df[students_df['Name'].str.lower() == selected_student].index

    if not row_to_update.empty:
  
        is_authenticated = students_df.loc[row_to_update, 'Authenticated'].iloc[0] == 'Yes'

        if status == 'Present' and not is_authenticated:
            messagebox.showwarning("Warning",
                                   f"{selected_student.title()} has not been authenticated. Cannot mark as Present.")
            return

        students_df.loc[row_to_update, 'Status'] = status
        students_df.to_csv(csv_file, index=False)
        messagebox.showinfo("Success", f"Attendance for '{selected_student.title()}' marked as '{status}'.")
    else:
        messagebox.showerror("Error", f"No record was found for '{selected_student.title()}' in the attendance file.")


    selected_student = None
    status_label.config(text="Selected: None")



if __name__ == "__main__":
    get_unique_students()

    if not student_list:
        messagebox.showwarning("No Students",
                               "No students found in the attendance file. Please run the face_authenticator.py script first to initialize the student list.")
        exit()

    root = tk.Tk()
    root.title("Attendance Marker")
    root.geometry("400x400")

  
    student_frame = tk.Frame(root)
    student_frame.pack(pady=10)

    
    status_label = tk.Label(root, text="Selected: None", font=("Helvetica", 14))
    status_label.pack(pady=10)

   
    for name in student_list:
        btn = tk.Button(student_frame, text=name.title(), command=lambda n=name: select_student(n), width=20)
        btn.pack(pady=5)

    
    attendance_frame = tk.Frame(root)
    attendance_frame.pack(pady=20)

    present_button = tk.Button(attendance_frame, text="Present", command=lambda: mark_attendance('Present'), bg='green',
                               fg='white', font=("Helvetica", 12))
    present_button.pack(side=tk.LEFT, padx=10)

    absent_button = tk.Button(attendance_frame, text="Absent", command=lambda: mark_attendance('Absent'), bg='red',
                              fg='white', font=("Helvetica", 12))
    absent_button.pack(side=tk.LEFT, padx=10)

    root.mainloop()
