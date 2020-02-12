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
            messagebox.showerror(title='Already Exists', message='Another entry with the same name already exists')
            return None
        else:
            message = f'Added {name.title()} payment with balance of ${total:,.2f} ' \
                      f'and monthly payments of ${payment:,.2f}'
            self.logger.info(message)
            return 1

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
                return None
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
        return 1

    def quick_pay(self, oid):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            try:
                cursor.execute('SELECT remaining FROM bills WHERE oid=?', (oid,))  # finish quick pay method
                bill_remaining = cursor.fetchone()[0]
                cursor.execute('SELECT payment FROM bills WHERE oid=?', (oid,))
                bill_payment = cursor.fetchone()[0]
                cursor.execute('SELECT paid FROM bills WHERE oid=?', (oid,))
                bill_paid = cursor.fetchone()[0]
                cursor.execute('SELECT name FROM bills WHERE oid=?', (oid,))
                name = cursor.fetchone()[0]
            except TypeError:
                messagebox.showerror(title='Invalid Selection',
                                     message='You have made an invalid selection. Please select again')
                return None
            else:
                self._write_payment_log(name, bill_payment)

            bill_remaining -= bill_payment
            if bill_remaining <= 0:
                cursor.execute('UPDATE bills SET complete=? WHERE oid=?', (1, oid))
                self.logger.info(f'{name.title()} PAID IN FULL')
            else:
                bill_paid += bill_payment
                cursor.execute('UPDATE bills SET remaining=? WHERE oid=?', (bill_remaining, oid))
                cursor.execute('UPDATE bills SET paid=? WHERE oid=?', (bill_paid, oid))
        return 1

    def remove(self, oid):
        with DatabaseConnection(self.bills_db) as connection:
            cursor = connection.cursor()

            try:
                cursor.execute('DELETE FROM bills WHERE oid=?', (oid,))
            except TypeError:
                messagebox.showerror(title='Invalid Selection',
                                     message='You have made an invalid selection. Please select again')
                return None
            else:
                return 1

    @staticmethod
    def get_bills() -> list:
        with DatabaseConnection('bills.db') as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT *, oid FROM bills')
            entries = cursor.fetchall()
        return entries

    def get_bill(self, oid):
        with DatabaseConnection(self.bills_db) as connection:
            connection.text_factory = str
            cursor = connection.cursor()

            try:
                cursor.execute('SELECT * FROM bills WHERE oid=?', (oid,))
                expense = cursor.fetchone()
            except TypeError:
                messagebox.showerror(title='Invalid Selection',
                                     message='You have made an invalid selection. Please select again')
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
