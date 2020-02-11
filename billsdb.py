import logging
from database_connection import DatabaseConnection
from sqlite3 import IntegrityError, OperationalError
from tkinter import messagebox


class BillTracker:
    """
    Class to keep track of user inputted bills like
    House payments
    Car payments

    No personal or bank credentials collected ever
    """

    def __init__(self):
        self.bills_db = "bills.db"
        logging.basicConfig(format='%(asctime)s %(name)s : %(message)s',
                            filename='log.log',
                            level=logging.INFO,
                            datefmt='%m-%d-%Y %H:%M:%S')
        self.logger = logging.getLogger('Payment')

    def create_table(self):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            cursor.execute("CREATE TABLE IF NOT EXISTS bills(name text primary key, total real, payment real, "
                           "remaining real, paid real, complete BIT)")

    def add_bill(self, name, payment, total):
        try:
            with DatabaseConnection(self.bills_db) as connection:
                cursor = connection.cursor()

                cursor.execute('INSERT INTO bills VALUES(?, ?, ?, ?, ?, ?)', (name, total, payment, total, 0, 0))
        except IntegrityError:
            print(f'!! Bill with name {name.title()} already exists !!')
        else:
            message = f'Added {name.title()} payment with balance of ${total:,.2f} ' \
                      f'and monthly payments of ${payment:,.2f}'
            self.logger.info(message)

    def make_payment(self, oid, amount):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            try:
                cursor.execute('SELECT remaining FROM bills WHERE oid=?', (oid,))
                expense_remaining = cursor.fetchone()[0]
                cursor.execute('SELECT paid FROM bills WHERE oid=?', (oid,))
                expense_paid = cursor.fetchone()[0]
                cursor.execute('SELECT name FROM bills WHERE oid-?', (oid,))
                name = cursor.fetchone()[0]
            except TypeError:
                messagebox.showerror(title='Invalid Selection',
                                     message='You have made an invalid selection. Please select again')
                # print('!! Invalid Query !!')
                return
            else:
                self._write_payment_log(name, amount)

            expense_remaining -= amount
            if expense_remaining <= 0:
                cursor.execute('UPDATE bills SET complete=? WHERE oid=?', (1, oid))
                self.logger.info(f'{name.title()} PAID IN FULL')
            else:
                expense_paid += amount
                cursor.execute('UPDATE bills SET remaining=? WHERE oid=?', (expense_remaining, oid))
                cursor.execute('UPDATE bills SET paid=? WHERE oid=?', (expense_paid, oid))
                cursor.execute('UPDATE bills SET payment=? WHERE oid=?', (amount, oid))

    def quick_pay(self, name):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            try:
                cursor.execute('SELECT remaining FROM bills WHERE name=?', (name,))  # finish quick pay method
                bill_remaining = cursor.fetchone()[0]
                cursor.execute('SELECT payment FROM bills WHERE name=?', (name,))
                bill_payment = cursor.fetchone()[0]
                cursor.execute('SELECT paid FROM bills WHERE name=?', (name,))
                bill_paid = cursor.fetchone()[0]
            except TypeError:
                print('!! Invalid Query !!')
                return
            else:
                self._write_payment_log(name, bill_payment)

            bill_remaining -= bill_payment
            if bill_remaining <= 0:
                cursor.execute('UPDATE bills SET complete=? WHERE name=?', (1, name))
                self.logger.info(f'{name.title()} PAID IN FULL')
            else:
                bill_paid += bill_payment
                cursor.execute('UPDATE bills SET remaining=? WHERE name=?', (bill_remaining, name))
                cursor.execute('UPDATE bills SET paid=? WHERE name=?', (bill_paid, name))

    def remove(self, name):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            cursor.execute('DELETE FROM bills WHERE name=?', (name,))

    def update_bill(self, name):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            update_string = """What property do you want to update
    --> 1 - name
    --> 2 - remaining
    --> 3 - payment
    --> 0 - back
Selection: """
            if self._get_bill(name) is not None:
                updated_field = ''
                while updated_field != 0:
                    try:
                        updated_field = int(input(update_string))
                    except ValueError:
                        updated_field = 99999999
                    if updated_field == 1:
                        new_name = input('New name: ').lower()
                        cursor.execute('UPDATE bills SET name=? WHERE name=?', (new_name, name))
                    elif updated_field == 2:
                        new_total = self._to_float(input('Amount spent: $'))
                        if new_total is not None:
                            self._add_expense(name, new_total)
                    elif updated_field == 3:
                        new_payment = self._to_float(input('New payment: $'))
                        if new_payment is not None:
                            cursor.execute('UPDATE bills SET payment=? WHERE name=?', (new_payment, name))
                        else:
                            pass
                    else:
                        print('!! Invalid Selection !!')
            else:
                print("!! Invalid Query !!")

    def _add_expense(self, name, amount):
        bill = self._get_bill(name)
        bill_remaining = bill['remaining']
        bill_remaining += amount

        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            cursor.execute('UPDATE bills SET remaining=? WHERE name=?', (bill_remaining, name))

    @staticmethod
    def get_bills() -> list:
        with DatabaseConnection('bills.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT *, oid FROM bills')
            entries = cursor.fetchall()
        return entries

    def _get_bill(self, name):
        with DatabaseConnection(self.bills_db) as connection:
            connection.text_factory = str
            cursor = connection.cursor()

            try:
                cursor.execute('SELECT * FROM bills WHERE name=?', (name,))
                expense = cursor.fetchone()
                expense = {'name': expense[0], 'total': expense[1], 'payment': expense[2],
                           'remaining': expense[3], 'paid': expense[4], 'complete': expense[5]}
            except TypeError:
                return None

        return expense

    @staticmethod
    def _to_float(variable):
        variable = variable.split(',')
        variable = ''.join(variable)

        try:
            variable = float(variable)
        except ValueError:
            return None

        return variable

    def _write_payment_log(self, name: str, amount: float):
        log_message = f'{name} for amount ${amount:,.2f} made.'
        self.logger.info(log_message)

    @staticmethod
    def reset():
        try:
            with DatabaseConnection('bills.db') as connection:
                cursor = connection.cursor()

                cursor.execute('DROP TABLE bills')
        except OperationalError:
            pass
