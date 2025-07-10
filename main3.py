from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import sqlite3

# Database setup
conn = sqlite3.connect('budget_tracker.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    item TEXT DEFAULT 'Balance Update',
    cost REAL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    added REAL,
    total REAL
)''')

def balance(entry_widget, modal):
    value = entry_widget.get()
    balance = balance_box.get()
    date = date_entry.get()

    try:
        balance_float = float(value) + float(balance)
        balance_box.config(state="normal")
        balance_box.delete(0, END)
        balance_box.insert(0, f"{balance_float:.2f}")
        cursor.execute("INSERT INTO budget (date, added, total) VALUES (?, ?, ?)",
                   (date, value, balance_float))
        conn.commit()
        load_data()
    except ValueError:
        messagebox.showerror("Invalid Input", "Balance must be a number/decimal.")
        return  # Stop here if invalid
    
    messagebox.showinfo("Success", f"Balance entered: {balance_float}")
    modal.destroy()  # Close only on success

    readOnlyState()

def editBalanceWindow():
    modal = Toplevel(root)
    modal.title("Input Balance")
    modal.geometry("300x150")

    # Make it modal
    modal.grab_set()

    # Load and display an image
    image = Image.open("Untitled (1).png")   # Replace with your image file
    image = image.resize((300, 150))
    photo = ImageTk.PhotoImage(image)

    image1 = Image.open("Enter button.png")   # Replace with your image file
    image1 = image1.resize((110, 29))
    photo1 = ImageTk.PhotoImage(image1)

    image2 = Image.open("Cancel Button.png")   # Replace with your image file
    image2 = image2.resize((110, 29))
    photo2= ImageTk.PhotoImage(image2)

    label = Label(modal, image=photo)
    label.image = photo  # Keep reference
    label.place(x=0, y=0)

    balance2_box = Entry(modal, borderwidth=0, bg="#D9D9D9", font=("Poppins", 14))
    balance2_box.place(x=80, y=40, width=170, height=35)

    enter_button = Button(modal, image=photo1, borderwidth=0, bg="white", activebackground="white", command=lambda: balance(balance2_box, modal))
    enter_button.place(x=40, y=89)

    cancel_button = Button(modal, image=photo2, borderwidth=0, bg="white", activebackground="white")
    cancel_button.place(x=155, y=89)
    
    modal.wait_window()

# Load data into Treeview
def load_data():

    for item in tree.get_children():
        tree.delete(item)
    for item in tree2.get_children():
        tree2.delete(item)

    cursor.execute("SELECT id, date, item, cost FROM expenses ORDER BY id DESC")
    rows = cursor.fetchall()
    for index, row in enumerate(rows):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", "end", values=row, tags=(tag,))

    cursor.execute("SELECT id, date, added, total FROM budget ORDER BY id DESC")
    rows = cursor.fetchall()
    for index, row in enumerate(rows):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree2.insert("", "end", values=row, tags=(tag,))

def normalState():
    expense_box.config(state="normal")
    balance_box.config(state="normal")

def readOnlyState():
    expense_box.config(state="readonly", readonlybackground="#D9D9D9")
    balance_box.config(state="readonly", readonlybackground="#D9D9D9")

def calculate_bal_from_db():
    cursor.execute("SELECT * FROM budget ORDER BY id DESC")
    rows = cursor.fetchone()
    
    normalState()

    if rows:
        balance_box.insert(0, rows[3])
    else:
        balance_box.insert(0, "0.00")

    readOnlyState()

# Calculate total expense from DB
def calculate_total_from_db():
    cursor.execute("SELECT SUM(cost) FROM expenses")
    result = cursor.fetchone()
    
    if result[0] is not None:
        total=result[0]
    else:
        total=0.0

    normalState()

    expense_box.insert(0, f"{total:.2f}")

    readOnlyState()    

# Calculate sum from Treeview
def sum():
    total_exp = 0.0
    normalState()
    expense_box.delete(0, END) 

    for item in tree.get_children():
        values = tree.item(item)["values"]
        try:
            total_exp += float(values[3])
        except (ValueError, TypeError):
            continue

    expense_box.insert(0, f"{total_exp:.2f}")
    readOnlyState()

# Add entry
def add():
    date = date_entry.get()
    item = name_box.get()
    cost = cost_box.get()
    balance = balance_box.get()
    neg_cost= -float(cost)

    if not item or not cost:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return

    try:
        cost_float = float(cost)
        total_bal = float(balance) - cost_float
    except ValueError:
        messagebox.showerror("Invalid Input", "Cost must be a number/decimal.")
        return

    cursor.execute("INSERT INTO expenses (date, item, cost) VALUES (?, ?, ?)",
                   (date, item, cost))
    conn.commit()
    
    normalState()


    cursor.execute("INSERT INTO budget (date, added, total) VALUES(?, ?, ?)",
                   (date, neg_cost, total_bal))
    conn.commit()
    
    name_box.delete(0, END)
    cost_box.delete(0, END)
    balance_box.delete(0, END)
    balance_box.insert(0, total_bal)

    readOnlyState()
    load_data()
    sum()

# Remove selected row
def remove():
    selected = tree.selection()
    if selected:
        messagebox.askokcancel("Confirm", "Do you want to Remove?")    
        for item_id in selected:
            row_id = tree.item(item_id)["values"][0]  # id is first column
            cursor.execute("DELETE FROM expenses WHERE id=?", (row_id,))
            conn.commit()
            tree.delete(item_id)
    sum()

# Clear all rows
def clear():
    result = messagebox.askokcancel("Confirm", "Do you want to Delete all data?")
    if result:
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute("DELETE FROM expenses")
        conn.commit()
    sum()

# GUI Setup
root = Tk()
root.title("Budget Tracker")
root.geometry("700x475")

# Load images
bg_image = Image.open("Desktop - 1.png").resize((700, 475), Image.LANCZOS)
edit_img = Image.open("balanceEdit.png").resize((33, 31), Image.LANCZOS)
add_img = Image.open("add.png").resize((225, 40), Image.LANCZOS)
rmv_img = Image.open("remove.png").resize((225, 40), Image.LANCZOS)
clr_img = Image.open("clear.png").resize((225, 40), Image.LANCZOS)

bg_photo = ImageTk.PhotoImage(bg_image)
add_btn_img = ImageTk.PhotoImage(add_img)
edit_btn_img = ImageTk.PhotoImage(edit_img)
rmv_btn_img = ImageTk.PhotoImage(rmv_img)
clr_btn_img = ImageTk.PhotoImage(clr_img)

bg_label = Label(root, image=bg_photo)
bg_label.place(x=1, y=1)

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", background="#2FAE55", foreground="black", font=("Poppins", 10))
style.map("Treeview", background=[("selected", "#2FAE55")], foreground=[("selected", "white")])
style.map('Custom.DateEntry', fieldbackground=[('readonly', 'white')], foreground=[('readonly', 'black')])

# Create Notebook (tab container)
notebook = ttk.Notebook(root)
notebook.place(x=25, y=160, width=425, height=300)

# Create tabs (frames)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Expenses")
notebook.add(tab2, text="Balance")

# Treeview setup
columns = ("ID", "Date", "Item", "Cost")
tree =  ttk.Treeview(tab1, columns=columns, show="headings")
tree.heading("ID", text="ID")
tree.heading("Date", text="Date")
tree.heading("Item", text="Item")
tree.heading("Cost", text="Cost")
tree.column("ID", width=0, stretch=False)
tree.column("Date", width=50)
tree.column("Item", width=50)
tree.column("Cost", width=50)
tree.tag_configure("oddrow", background="#f5f5f5")
tree.tag_configure("evenrow", background="#e0e0e0")
tree.pack(fill=BOTH, expand=True)

columns2 = ("ID", "Date", "Added", "Total")
tree2 =  ttk.Treeview(tab2, columns=columns2, show="headings")
tree2.heading("ID", text="ID")
tree2.heading("Date", text="Date")
tree2.heading("Added", text="Added Balance")
tree2.heading("Total", text="Total Balance")

tree2.column("ID", width=0, stretch=False)
tree2.column("Date", width=50)
tree2.column("Added", width=50)
tree2.column("Total", width=50)

tree2.tag_configure("oddrow", background="#f5f5f5")
tree2.tag_configure("evenrow", background="#e0e0e0")
tree2.pack(fill=BOTH, expand=True)


# Inputs
date_entry = DateEntry(root, width=32, background="#2FAE55", foreground="white",
                       borderwidth=2, date_pattern="mm-dd-yyyy",  state="readonly", style="Custom.DateEntry")
date_entry.place(x=476, y=107, height=30)

balance_box = Entry(root, borderwidth=0, bg="#D9D9D9", font=("Poppins", 14))
balance_box.place(x=55, y=105, width=120, height=35)

expense_box = Entry(root, borderwidth=0, bg="#D9D9D9",  font=("Poppins", 14))
expense_box.place(x=275, y=105, width=170, height=35)

name_box = Entry(root, borderwidth=0, bg="#D9D9D9", font=("Poppins", 14))
name_box.place(x=480, y=187, width=200, height=35)

cost_box = Entry(root, borderwidth=0, bg="#D9D9D9", font=("Poppins", 14))
cost_box.place(x=510, y=267, width=170, height=35)

# Buttons
edit_btn = Button(root, image=edit_btn_img, borderwidth=0, bg="white", activebackground="#D9D9D9", command=editBalanceWindow)
edit_btn.place(x=193, y=108, width=31, height=31)

add_btn = Button(root, image=add_btn_img, borderwidth=0, bg="white", activebackground="white", command=add)
add_btn.place(x=469, y=322, width=225, height=45)

remove_btn = Button(root, image=rmv_btn_img, borderwidth=0, bg="white", activebackground="white", command=remove)
remove_btn.place(x=469, y=372, width=225, height=45)

clrAll_btn = Button(root, image=clr_btn_img, borderwidth=0, bg="white", activebackground="white", command=clear)
clrAll_btn.place(x=469, y=423, width=225, height=45)

calculate_bal_from_db()
calculate_total_from_db()
load_data()

root.mainloop()
