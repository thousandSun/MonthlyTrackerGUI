""""TODO: `show_frame` logic
For testing purposes will not use DataBase yet
Therefore, whenever there is a `print()` statement
that will be replaced by the proper write functions"""
# import sqlite3
# import logging
import tkinter as tk
from tkinter import ttk, messagebox

test_list = [
    'Credit Card',
    'House',
    'Car'
]


def test_clicked():
    print()


def bills():
    show_frame['text'] = 'Bills'
    show_frame.grid(row=0, column=0)
    customize_frame.grid(row=1, column=0, padx=5, pady=5)
    entry_label = tk.Radiobutton(
        show_frame,
        text=f'{"Name"}: Total: ${200000:.2f} Payment: ${1145:.2f} Remaining: ${200000:.2f} Paid to Date: ${0:.2f}',
        variable=selection,
        value=1,
        command=test_clicked
    )
    entry_label.place(x=10, y=5)
    for i in range(1, 5):
        entry_label = tk.Radiobutton(
            show_frame,
            text=f'{"Name"}: Total: ${200000:.2f} Payment: ${1145:.2f} Remaining: ${200000:.2f} Paid to Date: ${0:.2f}',
            variable=selection,
            value=(i+1),
            command=test_clicked
        )
        entry_label.place(x=10, y=(i*30))


def category():
    show_frame['text'] = 'Categories'
    show_frame.grid(row=0, column=0, padx=5, pady=5)
    customize_frame.grid(row=1, column=0)


root = tk.Tk()
root.option_add('*tearOff', False)
root.title('Monthly Tracker')
root.geometry('610x410')
root.resizable(False, False)

# creates the main frame for placing all other options
main_frame = tk.Frame(root)
main_frame.grid()

show_frame = tk.LabelFrame(main_frame, width=600, height=250)
customize_frame = tk.LabelFrame(main_frame, width=600, height=140, text='Customize')

selection = tk.IntVar()
selection.set(1)

# creates a menu bar
menubar = tk.Menu()
root.config(menu=menubar)

# adds drop down
mode_menu = tk.Menu(menubar)
menubar.add_cascade(menu=mode_menu, label='Mode')

mode_menu.add_command(label='Bills', command=bills)
mode_menu.add_command(label='Categories', command=category)


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
