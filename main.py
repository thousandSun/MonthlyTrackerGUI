""""TODO: Start implementing GUI with the backend BillTracker and CatTracker classes * already imported *
TODO: properly deal with entry if its `PAID IN FULL`
TODO: make the `help` cascade menu options work
TODO: look for way to update windows with appropriate information, ask StackOverFlow if needed * can wait till end *"""
import tkinter as tk
from billsdb import BillTracker
from categoriesdb import CatTracker
from database_connection import DatabaseConnection
from tkinter import messagebox
from tzlocal import get_localzone

bill_tracker = BillTracker()
cat_tracker = CatTracker()
tz = get_localzone()


def get_entries() -> list:
    with DatabaseConnection('bills.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT *, oid FROM bills')
        entries = cursor.fetchall()
    return entries


def _get_entry(oid: int) -> tuple:
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
    confirm = messagebox.askokcancel(title='Confirm Delete', message='Proceed with deletion?')
    if confirm:
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
        pass_fail = bill_tracker.add_bill(name, payment, total)
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
    add_ui.resizable(False, False)

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
    bill_tracker.create_table()
    entries = bill_tracker.get_bills()
    clear_frame(show_frame)
    show_frame['text'] = 'Bills'
    show_frame.grid(row=0, column=0)
    listbox = tk.Listbox(show_frame)
    listbox.config(bd=0)
    listbox.place(x=0, y=0, relwidth=1.0, relheight=0.8)

    for entry in entries:
        name, total, payment, remaining, paid, complete, oid = entry
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
    add_btn.place(x=0, rely=0.88)

    payment_btn = tk.Button(show_frame, text='Payment', command=lambda: payment_window(listbox), width=20)
    payment_btn.place(x=190, rely=0.88)

    quick_pay_btn = tk.Button(show_frame, text='Quick Pay', command=lambda: quick(listbox), width=20)
    quick_pay_btn.place(x=380, rely=0.88)

    delete_btn = tk.Button(show_frame, text='Delete', command=lambda: delete_window(listbox), width=20)
    delete_btn.place(x=570, rely=0.88)


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


def add_cat(name: str):
    confirm = messagebox.askokcancel(title='Adding', message=f'Adding {name.title()}')
    if confirm:
        success = cat_tracker.add_category(name)
        if success:
            messagebox.showinfo(title='Added', message=f'Successfully added {name.title()}')
            cat_add_ui.destroy()
            return


def cat_add():
    global cat_add_ui
    cat_add_ui = tk.Toplevel()
    cat_add_ui.title('Add Category')
    cat_add_ui.geometry('300x200')
    cat_add_ui.resizable(False, False)

    add_frame = tk.LabelFrame(cat_add_ui, text='Add', width=300, height=200)
    add_frame.grid(row=0, column=0)
    add_frame.grid_propagate(False)

    tk.Label(add_frame, text='Name').grid(row=0, column=0, sticky=tk.E)

    name_entry = tk.Entry(add_frame)
    name_entry.grid(row=0, column=1, sticky=tk.W)

    add_btn = tk.Button(add_frame, text='Add', command=lambda: add_cat(name_entry.get()), width=25)
    add_btn.grid(row=1, columnspan=2, sticky=tk.W, pady=(10, 0))


def remove_cat(lb: tk.Listbox):
    selected = lb.curselection()
    if len(selected) < 1:
        messagebox.showwarning(title='Invalid selection', message='Please select an entry to proceed')
        return

    oid = selected[0] + 1
    confirm = messagebox.askokcancel(title='Confirm Delete', message='Proceed with deletion?')
    if confirm:
        success = cat_tracker.remove(oid)
        if success:
            messagebox.showinfo(title='Success', message='Successfully removed entry')


def category():
    cat_tracker.create_table()
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

    add_btn = tk.Button(show_frame, text='Add', command=cat_add, width=20)
    add_btn.place(x=0, rely=0.88)

    spent_btn = tk.Button(show_frame, text='Spend', command=lambda: spending_window(listbox), width=20)
    spent_btn.place(x=190, rely=0.88)

    remove_btn = tk.Button(show_frame, text='Delete', command=lambda: remove_cat(listbox), width=20)
    remove_btn.place(x=380, rely=0.88)


def show_logs():
    bills_logs = BillTracker.get_logs()
    cat_logs = CatTracker.get_logs()

    log_ui = tk.Toplevel()
    log_ui.title('Logs')
    log_ui.geometry('700x400')
    log_ui.resizable(False, False)

    bill_log_frame = tk.LabelFrame(log_ui, text='Bills Logs', width=700, height=200)
    bill_log_frame.grid(row=0, column=0)
    bill_log_frame.grid_propagate(False)

    cat_log_frame = tk.LabelFrame(log_ui, text='Category Logs', width=700, height=200)
    cat_log_frame.grid(row=1, column=0)
    cat_log_frame.grid_propagate(False)

    bill_log_box = tk.Listbox(bill_log_frame)
    bill_log_box.place(x=0, y=0, relwidth=1.0, relheight=1.0)

    cat_log_box = tk.Listbox(cat_log_frame)
    cat_log_box.place(x=0, y=0, relwidth=1.0, relheight=1.0)

    for i, log in enumerate(bills_logs):
        date_time, message = log
        date_time = date_time.split(' ')
        date, time = date_time
        log_message = f'Payment: {message} made on {date}@{time}({tz})'
        bill_log_box.insert(i, log_message)

    for i, log in enumerate(cat_logs):
        date_time, message = log
        date_time = date_time.split(' ')
        date, time = date_time
        log_message = f'Category: {message} made on {date}@{time}({tz})'
        cat_log_box.insert(i, log_message)


def reset_bills():
    confirm = get_reset_confirm()
    if confirm == 'ok':
        BillTracker.reset()


def reset_cat():
    confirm = get_reset_confirm()
    if confirm == 'ok':
        CatTracker.reset()


def reset_logs():
    confirm = get_reset_confirm()
    if confirm == 'ok':
        open('log.log', 'w').close()


def reset_all():
    if get_reset_confirm() == 'ok':
        BillTracker.reset()
        CatTracker.reset()
        open('log.log', 'w').close()


def get_reset_confirm():
    return messagebox.showwarning(title='!!! Reset Data !!!',
                                  message='YOU ARE ABOUT TO RESET DATA\nTHIS ACTION IS IRREVERSIBLE')


def about():
    messagebox.showinfo(title='About',
                        message='This application is still a work in progress.\n'
                                'It is a means to help you become more expense conscious '
                                'and help manage spending habits. There are some subtle psychological '
                                'constructs to help achieve that goal\n'
                                '\n!!! DOES NOT COLLECT ANY FINANCIAL INSTITUTION INFORMATION !!!')


def use():
    messagebox.showinfo(title='How to Use',
                        message='The use of this app seems fairly intuitive\n'
                                '♠ The Bills mode allows you to monitor your monthly bills\n'
                                '♠ The Category mode allows you to keep track of how much you spend on various things\n'
                                '♠ When adding a category, it will default to $0 spent\n'
                                '♠ Resetting data is a permanent process, think twice before doing so')


root = tk.Tk()
root.option_add('*tearOff', False)
root.title('Monthly Tracker')
root.geometry('760x250')
root.resizable(False, False)

# creates the main frame for placing all other options
main_frame = tk.Frame(root)
main_frame.grid()

# frame for placing appropriate labels and entries
show_frame = tk.LabelFrame(main_frame, width=760, height=250)

# creates a menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)
mode_menu = tk.Menu(menubar)
help_menu = tk.Menu(menubar)
reset_menu = tk.Menu(help_menu)
menubar.add_cascade(label='Mode', menu=mode_menu)
menubar.add_cascade(label='Help', menu=help_menu)

mode_menu.add_command(label='Bills', command=bills)
mode_menu.add_command(label='Categories', command=category)

help_menu.add_command(label='About', command=about)
help_menu.add_command(label='How to Use', command=use)
help_menu.add_command(label='Show logs', command=show_logs)
help_menu.add_cascade(label='Reset Data', menu=reset_menu)
reset_menu.add_command(label='Bills', command=reset_bills)
reset_menu.add_command(label='Categories', command=reset_cat)
reset_menu.add_command(label='Logs', command=reset_logs)
reset_menu.add_command(label='All', command=reset_all)

bills()

root.mainloop()
