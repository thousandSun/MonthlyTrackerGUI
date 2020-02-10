import logging
from sqlite3 import IntegrityError, OperationalError

from database_connection import DatabaseConnection


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

    def show_categories(self):
        categories = self._get_categories()

        for category in categories:
            name = category['category']
            total = category['total']

            cat_str = f'| {name.title()}: ${total:,.2f} |'
            print('-'*len(cat_str))
            print(cat_str)
            print('-'*len(cat_str))

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

    def update_category(self, name, amount):
        category = self._get_category(name)

        try:
            total = category['total']
            total += amount
            with DatabaseConnection(self.categories_database) as connection:
                cursor = connection.cursor()

                cursor.execute('UPDATE categories SET total=? WHERE name=?', (total, name))
        except TypeError:
            print('!! Invalid Query !!')
        else:
            self._write_log(name, amount)

    def remove(self, name):
        with DatabaseConnection(self.categories_database) as connection:
            cursor = connection.cursor()

            cursor.execute('DELETE FROM categories WHERE name=?', (name,))

    def _get_category(self, name):
        with DatabaseConnection(self.categories_database) as connection:
            connection.text_factory = str
            cursor = connection.cursor()
            try:
                cursor.execute('SELECT * FROM categories WHERE name=?', (name,))
                category = cursor.fetchone()
                category = {'category': category[0], 'total': category[1]}

                return category
            except TypeError:
                return None

    def _get_categories(self):
        with DatabaseConnection(self.categories_database) as connection:
            connection.text_factory = str
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM categories')

            categories = [{'category': row[0], 'total': row[1]} for row in cursor.fetchall()]

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
