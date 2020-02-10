""""TODO: Start implementing GUI with the backend BillTracker and CatTracker classes * already imported *
TODO: may not need `pay()` method in gui file, look to process everything using the appropriate classes
For testing purposes will not use DataBase yet
Therefore, whenever there is a `print()` statement
that will be replaced by the proper write functions"""
# import logging
import tkinter as tk
from billsdb import BillTracker
from categoriesdb import CatTracker
from database_connection import DatabaseConnection
from tkinter import messagebox


def get_entries() -> list:
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT *, oid FROM bills')
        entries = cursor.fetchall()
    # print(entries)
    return entries


def _get_entry(oid: int):
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM bills WHERE oid=?', (oid,))
        entry = cursor.fetchone()
    print(entry)
    return entry


def clear_frame(frame: tk.LabelFrame):
    for widget in frame.winfo_children():
        widget.destroy()


def pay(amount: float, oid: int):
    if amount is None:
        messagebox.showwarning(title='Invalid Payment', message='Please enter a valid payment amount')
        return

    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()

        cursor.execute()


def payment_window(lb: tk.Listbox):
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return
    payment_ui = tk.Toplevel()
    payment_ui.geometry('300x200')
    payment_ui.title('Payment')
    payment_ui.resizable(False, False)
    oid = selected[0] + 1
    entry = _get_entry(oid)
    payment_frame = tk.LabelFrame(payment_ui, text=f'{entry[0].title()}', width=300, height=200)
    payment_frame.grid(row=0, column=0)
    payment_frame.grid_propagate(False)

    tk.Label(payment_frame, text='Total $').grid(row=0, column=0, sticky=tk.E)
    tk.Label(payment_frame, text='Payment $').grid(row=1, column=0, sticky=tk.E)
    tk.Label(payment_frame, text='Remaining $').grid(row=2, column=0, sticky=tk.E)
    tk.Label(payment_frame, text='Paid to Date $').grid(row=3, column=0, sticky=tk.E)

    total_entry = tk.Entry(payment_frame)
    total_entry.grid(row=0, column=1, sticky=tk.W)
    total_entry.insert(0, f'{entry[1]:,.2f}')
    total_entry.config(state='readonly')

    payment_entry = tk.Entry(payment_frame)
    # to get value of entry box to process, .get() returns str, need to convert to float to continue
    payment_entry.insert(0, f'{entry[2]:,.2f}')
    payment_entry.grid(row=1, column=1, sticky=tk.W)

    remaining_entry = tk.Entry(payment_frame)
    remaining_entry.insert(0, f'{entry[3]:,.2f}')
    remaining_entry.config(state='readonly')
    remaining_entry.grid(row=2, column=1, sticky=tk.W)

    ptd_entry = tk.Entry(payment_frame)
    ptd_entry.insert(0, f'{entry[4]:,.2f}')
    ptd_entry.config(state='readonly')
    ptd_entry.grid(row=3, column=1, sticky=tk.W)

    payment_btn = tk.Button(payment_frame,text='Pay',width=25, command=lambda: pay(_to_float(payment_entry.get()), oid))
    payment_btn.grid(row=4, columnspan=3, sticky=tk.W, pady=(10, 0))


def _to_float(variable):
    variable = variable.split(',')
    variable = ''.join(variable)

    try:
        variable = float(variable)
    except ValueError:
        return None

    return variable


def bills():
    entries = get_entries()
    clear_frame(show_frame)
    show_frame['text'] = 'Bills'
    show_frame.grid(row=0, column=0)
    listbox = tk.Listbox(show_frame)
    listbox.config(bd=0)
    listbox.place(x=0, y=0, relwidth=1.0, relheight=0.8)

    for entry in entries:
        name, total, payment, remaining, paid, complete, oid = entry
        # print(oid)
        if not bool(complete):
            listbox.insert(
                oid,
                f'{name.title()}: Total: ${total:,.2f}    Payment: ${payment:,.2f}    Remaining: ${remaining:,.2f}'
                f'    Paid to Date: ${paid:,.2f}'
            )
        else:
            listbox.insert(
                oid,
                f'{name.capitalize()}: PAID IN FULL'
            )

    add_btn = tk.Button(show_frame, text='Add', command=lambda: payment_window(listbox), width=20)
    add_btn.place(x=0, rely=0.9)

    edit_btn = tk.Button(show_frame, text='Payment', command=lambda: payment_window(listbox), width=20)
    edit_btn.place(x=190, rely=0.9)

    delete_btn = tk.Button(show_frame, text='Delete', command=lambda: payment_window(listbox), width=20)
    delete_btn.place(x=380, rely=0.9)


def category():
    clear_frame(show_frame)
    show_frame['text'] = 'Categories'
    show_frame.grid(row=0, column=0, padx=5, pady=5)


root = tk.Tk()
root.option_add('*tearOff', False)
root.title('Monthly Tracker')
root.geometry('680x250')
# root.resizable(False, False)

# creates the main frame for placing all other options
main_frame = tk.Frame(root)
main_frame.grid()

show_frame = tk.LabelFrame(main_frame, width=680, height=250)

selection = tk.IntVar()

# creates a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)
mode_menu = tk.Menu(menubar)
help_menu = tk.Menu(menubar)
menubar.add_cascade(label='Mode', menu=mode_menu)
menubar.add_cascade(label='Help', menu=help_menu)

mode_menu.add_command(label='Bills', command=bills)
mode_menu.add_command(label='Categories', command=category)

help_menu.add_command(label='About')
help_menu.add_command(label='Show logs')
help_menu.add_command(label='How to Use')
help_menu.add_command(label='Reset Data')

bills()

# customize_frame = LabelFrame(root, text='Make Changes', relief=SUNKEN)
# customize_frame.pack(side='bottom', fill='both', expand=True, padx=2, pady=2)
#
# # `show_frame` logic goes here
#
#
# def clicked():
#     print(action.get())
#
#
# # `customize_frame` logic
# label = Label(customize_frame, text='Today I')
# label.grid(row=0, column=0)
# action = IntVar()
# amount = DoubleVar()
# r1 = Radiobutton(customize_frame, text='Made a Payment', value=1, variable=action, command=clicked)
# r2 = Radiobutton(customize_frame, text='Spent $', value=2, variable=action, command=clicked)
# r1.grid(row=0, column=1)
# r2.grid(row=0, column=2)
# amount_entry = Entry(customize_frame, text='$', textvariable=amount, width=20)
# amount_entry.grid(row=0, column=3)
# Label(customize_frame, text='on').grid(row=0, column=4)
# selection = StringVar()
# selection.set(test_list[0])
# choices = OptionMenu(customize_frame, selection, *test_list)
# choices.grid(row=0, column=5)
#
#
# def make_payment():
#     if action.get() == 1:
#         confirm = messagebox.askokcancel(
#             title='Confirm Changes',
#             message=f'You will be making a payment for amount ${amount.get():.2f} on {selection.get()}'
#         )
#         print(confirm)
#         if confirm:
#             messagebox.showinfo(title='Changes Made',
#                                 message=f'Payment ${amount.get():.2f} for {selection.get()} recorded')
#     elif action.get() == 2:
#         confirm = messagebox.askokcancel(
#             title='Confirm Changes',
#             message=f'You have added ${amount.get():.2f} onto {selection.get()}'
#         )
#         if confirm:
#             messagebox.showinfo(title='Changes Made',
#                                 message=f'Added ${amount.get():.2f} to {selection.get()} recorded')
#     else:
#         messagebox.showwarning(title='No Selection',
#                                message='Please make a selection')
#
#
# btn = Button(customize_frame, text='Make Changes', relief='groove', command=make_payment)
# btn.grid(row=0, column=6, columnspan=2, padx=20)


root.mainloop()
