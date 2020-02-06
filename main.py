""""TODO: `show_frame` logic
For testing purposes will not use DataBase yet
Therefore, whenever there is a `print()` statement
that will be replaced by the proper write functions"""
# import logging
import tkinter as tk
from database_connection import DatabaseConnection
from tkinter import ttk, messagebox


def get_entries() -> list:
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT *, oid FROM bills')
        entries = cursor.fetchall()
    # print(entries)
    return entries


def clear_frame(frame: tk.LabelFrame):
    for widget in frame.winfo_children():
        widget.destroy()


def edit(lb: tk.Listbox):
    pass


def bills():
    entries = get_entries()
    clear_frame(show_frame)
    show_frame['text'] = 'Bills'
    show_frame.grid(row=0, column=0)
    customize_frame.grid(row=1, column=0, padx=5, pady=5)
    listbox = tk.Listbox(show_frame)
    listbox.place(x=0, y=0, relwidth=1.0)

    for entry in entries:
        name, total, payment, remaining, paid, complete, oid = entry
        if not bool(complete):
            listbox.insert(
                oid,
                f'{name.capitalize()}: Total: ${total:,.2f} Payment: ${payment:,.2f} Remaining: ${remaining:,.2f} '
                f'Paid to Date: ${paid:,.2f}'
            )
        else:
            listbox.insert(
                'END',
                f'{name.capitalize()}: PAID IN FULL'
            )
    edit_btn = tk.Button(show_frame, text='Edit', command=lambda: edit(listbox))
    edit_btn.pack(side='bottom')

    # entry_button = tk.Radiobutton(
    #     show_frame,
    #     text=f'{name.capitalize()}: Total: ${total:,.2f} Payment: ${payment:,.2f} Remaining: ${remaining:,.2f} '
    #          f'Paid to Date: ${paid:,.2f} Complete: {bool(complete)}',
    #     variable=selection,
    #     value=oid,
    #     command=lambda: test_clicked(entry_button['text'])
    # )
    # entry_button.place(x=10, y=5)
    # for i, entry in enumerate(entries[1:]):
    #     name, total, payment, remaining, paid, complete, oid = entry
    #     entry_button = tk.Radiobutton(
    #         show_frame,
    #         text=f'{name.capitalize()}: Total: ${total:,.2f} Payment: ${payment:,.2f} Remaining: ${remaining:,.2f} '
    #              f'Paid to Date: ${paid:,.2f} Complete: {bool(complete)}',
    #         variable=selection,
    #         value=oid,
    #         command=lambda: test_clicked(entry_button['text']),
    #         wraplength=600
    #     )
    #     entry_button.place(x=10, y=((i+1)*30))


def category():
    clear_frame(show_frame)
    show_frame['text'] = 'Categories'
    show_frame.grid(row=0, column=0, padx=5, pady=5)
    customize_frame.grid(row=1, column=0)


root = tk.Tk()
root.option_add('*tearOff', False)
root.title('Monthly Tracker')
root.geometry('700x400')
# root.resizable(False, False)

# creates the main frame for placing all other options
main_frame = tk.Frame(root)
main_frame.grid()

show_frame = tk.LabelFrame(main_frame, width=680, height=250)
customize_frame = tk.LabelFrame(main_frame, width=680, height=140, text='Customize')


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
