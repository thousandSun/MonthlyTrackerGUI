""""TODO: Start implementing GUI with the backend BillTracker and CatTracker classes * already imported *
TODO: properly deal with entry if its `PAID IN FULL`
TODO: finish `cat_add()` to add more categories
TODO: make a remove button for categories
TODO: make the `help` cascade menu options work
TODO: look for way to update windows with appropriate information, ask StackOverFlow if needed * can wait till end *"""
import tkinter as tk
from billsdb import BillTracker
from categoriesdb import CatTracker
from database_connection import DatabaseConnection
from tkinter import messagebox

bill_tracker = BillTracker()
bill_tracker.create_table()
cat_tracker = CatTracker()
cat_tracker.create_table()


def get_entries() -> list:
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT *, oid FROM bills')
        entries = cursor.fetchall()
    return entries


def _get_entry(oid: int):
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM bills WHERE oid=?', (oid,))
        entry = cursor.fetchone()
    return entry


def clear_frame(frame: tk.LabelFrame):
    for widget in frame.winfo_children():
        widget.destroy()


# intermediary method to deal with invalid GUI payment input before sending amount to BillTracker
def pay(amount: float, oid: int):
    if amount is None:
        messagebox.showwarning(title='Invalid Payment', message='Please enter a valid payment amount')
        return

    confirm = messagebox.askokcancel(
        title='Confirm Payment',
        message=f'Making payment of amount: ${amount:,.2f}'
    )
    if confirm:
        pass_fail = bill_tracker.make_payment(oid, amount)
        if pass_fail is not None:
            messagebox.showinfo(title='Payment Made',
                                message=f'Your payment of amount ${amount:,.2f} made successfully')
            payment_ui.destroy()
            return


def payment_window(lb: tk.Listbox):
    global payment_ui
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return
    payment_ui = tk.Toplevel()
    payment_ui.geometry('300x200')
    payment_ui.title('Payment')
    payment_ui.resizable(False, False)
    oid = selected[0] + 1
    entry = bill_tracker.get_bill(oid)
    if entry is not None:
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

        payment_btn = tk.Button(payment_frame,
                                text='Pay',
                                width=25,
                                command=lambda: pay(_to_float(payment_entry.get()), oid))
        payment_btn.grid(row=4, columnspan=3, sticky=tk.W, pady=(10, 0))


def _to_float(variable):
    variable = variable.split(',')
    variable = ''.join(variable)

    try:
        variable = float(variable)
    except ValueError:
        return None

    return variable


def delete_window(lb: tk.Listbox):
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return

    oid = selected[0] + 1
    success = bill_tracker.remove(oid)
    if success:
        messagebox.showinfo(title='Success', message='Successfully removed entry')


def add(name: str, total: float, payment: float):
    if total is None or payment is None:
        messagebox.showerror(title='Invalid Entries', message='Invalid entries, try again')
        return

    confirm = messagebox.askokcancel(
        title='Confirm Entry',
        message=f'Adding {name.title()} with total of ${total:,.2f} with payments of ${payment:,.2f}'
    )
    if confirm:
        pass_fail = bill_tracker.add_bill(name, total, payment)
        if pass_fail is not None:
            messagebox.showinfo(
                title='Added Successfully',
                message=f'Added {name.title()} with total of ${total:,.2f} with payments of ${payment:,.2f}'
            )
            add_ui.destroy()
            return


def add_window():
    global add_ui
    add_ui = tk.Toplevel()
    add_ui.title('Add Entry')
    add_ui.geometry('400x400')

    add_frame = tk.LabelFrame(add_ui, text='Add', width=400, height=400)
    add_frame.grid(row=0, column=0)
    add_frame.grid_propagate(False)

    tk.Label(add_frame, text='Name:').grid(row=0, column=0, sticky=tk.E)
    tk.Label(add_frame, text='Total: $').grid(row=1, column=0, sticky=tk.E)
    tk.Label(add_frame, text='Payment: $').grid(row=2, column=0, sticky=tk.E)

    name = tk.StringVar()
    name_entry = tk.Entry(add_frame, textvariable=name)
    name_entry.grid(row=0, column=1, sticky=tk.W)

    total_entry = tk.Entry(add_frame)
    total_entry.grid(row=1, column=1, sticky=tk.W)

    payment_entry = tk.Entry(add_frame)
    payment_entry.grid(row=2, column=1, sticky=tk.W)

    add_btn = tk.Button(
        add_frame,
        text='Add',
        width=20,
        command=lambda: add(name.get(), _to_float(total_entry.get()), _to_float(payment_entry.get()))
    )
    add_btn.grid(row=3, columnspan=2, sticky=tk.W, pady=(10, 0))


def quick(lb: tk.Listbox):
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return

    oid = selected[0] + 1
    success = bill_tracker.quick_pay(oid)
    if success is not None:
        messagebox.showinfo(title='Success', message='Quick Pay Succeeded')


def bills():
    entries = bill_tracker.get_bills()
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

    add_btn = tk.Button(show_frame, text='Add', command=add_window, width=20)
    add_btn.place(x=0, rely=0.9)

    payment_btn = tk.Button(show_frame, text='Payment', command=lambda: payment_window(listbox), width=20)
    payment_btn.place(x=190, rely=0.9)

    delete_btn = tk.Button(show_frame, text='Delete', command=lambda: delete_window(listbox), width=20)
    delete_btn.place(x=380, rely=0.9)

    quick_pay_btn = tk.Button(show_frame, text='Quick Pay', command=lambda: quick(listbox), width=20)
    quick_pay_btn.place(x=570, rely=0.9)


def spend(amount: float, oid: int):
    if amount is None:
        messagebox.showerror(title='Invalid Amount', message='Invalid spending amount')
        return

    confirm = messagebox.askokcancel(title='Confirm Spending', message=f'Spending ${amount:,.2f}')
    if confirm:
        success = cat_tracker.update_category(oid, amount)
        if success:
            messagebox.showinfo(title='Success', message=f'Spent ${amount:,.2f}')
            spending_ui.destroy()
            return


def spending_window(lb: tk.Listbox):
    global spending_ui
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return
    spending_ui = tk.Toplevel()
    spending_ui.geometry('300x200')
    spending_ui.title('Spending')
    spending_ui.resizable(False, False)
    oid = selected[0] + 1
    entry = cat_tracker.get_category(oid)
    if entry is not None:
        spending_frame = tk.LabelFrame(spending_ui, text=f'{entry[0].title()}', width=300, height=200)
        spending_frame.grid(row=0, column=0)
        spending_frame.grid_propagate(False)

        tk.Label(spending_frame, text='Total: $').grid(row=0, column=0, sticky=tk.E)
        tk.Label(spending_frame, text='Spending: $').grid(row=1, column=0, sticky=tk.E)

        total_entry = tk.Entry(spending_frame)
        total_entry.grid(row=0, column=1, sticky=tk.W)
        total_entry.insert(0, entry[1])
        total_entry.config(state='readonly')

        spending_entry = tk.Entry(spending_frame)
        spending_entry.grid(row=1, column=1, sticky=tk.W)

        spend_btn = tk.Button(spending_frame,
                              text='Spend', width=25,
                              command=lambda: spend(_to_float(spending_entry.get()), oid)
                              )
        spend_btn.grid(row=2, columnspan=2, sticky=tk.W, pady=(10, 0))


def cat_add():
    pass


def category():
    entries = cat_tracker.get_categories()
    clear_frame(show_frame)
    show_frame['text'] = 'Categories'
    show_frame.grid(row=0, column=0, padx=5, pady=5)
    listbox = tk.Listbox(show_frame)
    listbox.config(bd=0)
    listbox.place(x=0, y=0, relwidth=1.0, relheight=0.8)

    for entry in entries:
        name, total, oid = entry
        listbox.insert(oid, f'{name.title()}: ${total:,.2f}')

    spent_btn = tk.Button(show_frame, text='Spend', command=lambda: spending_window(listbox), width=20)
    spent_btn.place(x=0, rely=0.88)

    add_btn = tk.Button(show_frame, text='Add', command=cat_add)


root = tk.Tk()
root.option_add('*tearOff', False)
root.title('Monthly Tracker')
root.geometry('760x250')
# root.resizable(False, False)

# creates the main frame for placing all other options
main_frame = tk.Frame(root)
main_frame.grid()

show_frame = tk.LabelFrame(main_frame, width=760, height=250)

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

root.mainloop()
