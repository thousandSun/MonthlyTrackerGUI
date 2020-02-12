import logging
from database_connection import DatabaseConnection
from sqlite3 import IntegrityError, OperationalError
from tkinter import messagebox


class CatTracker:
    """
    Class to keep track of categorical expenses like
    grocery expenses
    shopping expenses
    movie expenses
    gas expenses

    No personal or bank credentials collected ever
    """

    def __init__(self):
        self.categories_database = "categories.db"
        logging.basicConfig(format='%(asctime)s %(name)s : %(message)s',
                            filename='log.log',
                            level=logging.INFO,
                            datefmt='%m-%d-%Y %H:%M:%S')
        self.logger = logging.getLogger('Category')

    def create_table(self):
        with DatabaseConnection(self.categories_database) as connection:
            cursor = connection.cursor()

            cursor.execute('CREATE TABLE IF NOT EXISTS categories(name text primary key, total real)')

    # def show_categories(self):
    #     categories = self._get_categories()
    #
    #     for category in categories:
    #         name = category['category']
    #         total = category['total']
    #
    #         cat_str = f'| {name.title()}: ${total:,.2f} |'
    #         print('-'*len(cat_str))
    #         print(cat_str)
    #         print('-'*len(cat_str))

    def add_category(self, name):
        try:
            with DatabaseConnection(self.categories_database) as connection:
                cursor = connection.cursor()

                cursor.execute('INSERT INTO categories VALUES(?, ?)', (name, 0))
        except IntegrityError:
            print(f'!! Category with name {name.title()} already exists !!')
        else:
            message = f'{name.title()} added'
            self.logger.info(message)

    def update_category(self, oid, amount):
        try:
            with DatabaseConnection(self.categories_database) as connection:
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM categories WHERE oid=?', (oid,))
                entry = cursor.fetchone()
                name, total = entry
                total += amount
                cursor.execute('UPDATE categories SET total=? WHERE oid=?', (total, oid))
        except TypeError:
            messagebox.showerror(title='Invalid Query', message='You have made an invalid Query')
            return
        else:
            self._write_log(name, amount)
            return 1

    def remove(self, name):
        with DatabaseConnection(self.categories_database) as connection:
            cursor = connection.cursor()

            cursor.execute('DELETE FROM categories WHERE name=?', (name,))

    def get_category(self, oid):
        with DatabaseConnection(self.categories_database) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute('SELECT * FROM categories WHERE oid=?', (oid,))
                category = cursor.fetchone()
                return category
            except TypeError:
                messagebox.showerror(title='Invalid Selection',
                                     message='You have made an invalid selection. Please select again')
                return None

    def get_categories(self):
        with DatabaseConnection(self.categories_database) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT *, oid FROM categories')
            categories = cursor.fetchall()
        return categories

    def _write_log(self, name: str, amount: float):
        message = f'Spent ${amount:,.2f} for {name}'
        self.logger.info(message)

    @staticmethod
    def reset():
        try:
            with DatabaseConnection('categories.db') as connection:
                cursor = connection.cursor()

                cursor.execute('DROP TABLE categories')
        except OperationalError:
            pass

        open('log.log', 'w').close()
