# OmniSale

OmniSale is a comprehensive Django web application designed for efficient inventory management and sales tracking. It provides a user-friendly interface for managing grocery products, handling sales, tracking purchases, and generating insightful analytics.

## Features

- **Analytics Dashboard**: The homepage features interactive graphs and charts that display sales data, allowing you to monitor your business performance at a glance. Additionally, it provides alerts for items with low inventory levels.

- **Inventory Management**: Easily manage your grocery products through a dedicated inventory module. Perform CRUD (Create, Read, Update, Delete) operations on products, ensuring accurate inventory tracking.

- **Sales Module**: Streamline your sales process by utilizing the sales page. Select items from the inventory, process sales transactions, and automatically update the inventory levels.

- **Sales History**: Keep track of all your past sales with the sales list feature. View detailed information about each transaction, including the items sold and the corresponding bills.

- **Supplier Management**: Efficiently manage your suppliers through the dedicated suppliers page. Add new suppliers, update their details, or remove them as needed. Access the list of all registered suppliers for easy reference.

- **Purchase Module**: Replenish your inventory by making purchases from suppliers. The purchase module allows you to select products, specify quantities, and generate purchase orders.

- **Purchase History**: Maintain a comprehensive record of all your purchases from suppliers, including the purchased items and corresponding bills.

- **CSV Export**: Export your sales data into a CSV file for further analysis or record-keeping purposes.

## Getting Started

1. Clone the repository: `git clone https://github.com/your-username/omnisale.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Configure the database settings in `settings.py`
4. Run database migrations: `python manage.py migrate`
5. Start the development server: `python manage.py runserver`