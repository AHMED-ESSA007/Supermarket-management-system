
import sqlite3
from datetime import datetime

class SupermarketDB:
    def __init__(self, db_name="supermarket.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
        """)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_sold INTEGER,
            total_price REAL,
            sale_date TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """)
        self.conn.commit()

    def add_product(self, name, price, quantity):
        self.cur.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                         (name, price, quantity))
        self.conn.commit()

    def get_all_products(self):
        self.cur.execute("SELECT * FROM products")
        return self.cur.fetchall()

    def update_product(self, prod_id, new_price, new_quantity):
        self.cur.execute("UPDATE products SET price = ?, quantity = ? WHERE id = ?",
                         (new_price, new_quantity, prod_id))
        self.conn.commit()

    def delete_product(self, prod_id):
        self.cur.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        self.conn.commit()

    def get_product(self, prod_id):
        self.cur.execute("SELECT name, price, quantity FROM products WHERE id = ?", (prod_id,))
        return self.cur.fetchone()

    def update_quantity(self, prod_id, new_quantity):
        self.cur.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, prod_id))
        self.conn.commit()

    def record_sale(self, prod_id, quantity_sold, total_price):
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("INSERT INTO sales (product_id, quantity_sold, total_price, sale_date) VALUES (?, ?, ?, ?)",
                         (prod_id, quantity_sold, total_price, sale_date))
        self.conn.commit()

    def get_sales_summary(self):
        self.cur.execute("""
        SELECT s.id, p.name, s.quantity_sold, s.total_price, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
        """)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()


class SupermarketApp:
    def __init__(self):
        self.db = SupermarketDB()

    def add_product(self):
        name = input("Enter product name: ")
        price = float(input("Enter product price: "))
        quantity = int(input("Enter product quantity: "))
        self.db.add_product(name, price, quantity)
        print("✅ Product added successfully.\n")

    def view_products(self):
        products = self.db.get_all_products()
        print("\n📦 Inventory:")
        print("-" * 40)
        for prod in products:
            print(f"ID: {prod[0]} | Name: {prod[1]} | Price: ${prod[2]} | Quantity: {prod[3]}")
        print("-" * 40)

    def update_product(self):
        self.view_products()
        prod_id = int(input("Enter product ID to update: "))
        new_price = float(input("Enter new price: "))
        new_quantity = int(input("Enter new quantity: "))
        self.db.update_product(prod_id, new_price, new_quantity)
        print("🔁 Product updated successfully.\n")

    def delete_product(self):
        self.view_products()
        prod_id = int(input("Enter product ID to delete: "))
        self.db.delete_product(prod_id)
        print("❌ Product deleted successfully.\n")

    def make_sale(self):
        self.view_products()
        prod_id = int(input("Enter product ID to sell: "))
        quantity = int(input("Enter quantity to sell: "))

        product = self.db.get_product(prod_id)
        if not product:
            print("❗ Product not found.\n")
            return

        name, price, stock = product
        if quantity > stock:
            print("❗ Not enough stock available.\n")
            return

        total = price * quantity
        new_stock = stock - quantity

        self.db.update_quantity(prod_id, new_stock)
        self.db.record_sale(prod_id, quantity, total)
        print(f"🛒 Sale complete! Total: ${total:.2f}\n")

    def view_sales_summary(self):
        sales = self.db.get_sales_summary()
        print("\n📈 Sales Summary:")
        print("-" * 60)
        for sale in sales:
            print(f"Sale ID: {sale[0]} | Product: {sale[1]} | Qty: {sale[2]} | Total: ${sale[3]} | Date: {sale[4]}")
        print("-" * 60)

    def run(self):
        while True:
            print("""
========= Supermarket Management =========
1. Add New Product
2. View Products
3. Update Product
4. Delete Product
5. Make Sale
6. View Sales Summary
7. Exit
""")
            choice = input("Enter your choice (1-7): ")

            if choice == '1':
                self.add_product()
            elif choice == '2':
                self.view_products()
            elif choice == '3':
                self.update_product()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                self.make_sale()
            elif choice == '6':
                self.view_sales_summary()
            elif choice == '7':
                print("👋 Exiting... Goodbye!")
                self.db.close()
                break
            else:
                print("❗ Invalid choice, try again.\n")


# Run the app
if __name__ == "__main__":
    app = SupermarketApp()
    app.run()
