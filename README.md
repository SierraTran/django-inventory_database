# Inventory Database

![Python Version](https://img.shields.io/badge/python-3.13.2-blue)
![Django Version](https://img.shields.io/badge/django-5.1.5-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-69%-A8FF00)

This is a Django-based web application for managing an inventory database. The application allows users to browse, search, and manage items in the inventory. It also includes user authentication and authorization features.

## Table of Contents

- [Inventory Database](#inventory-database)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [User Roles](#user-roles)
  - [Technologies Used](#technologies-used)
    - [Python](#python)
    - [Django](#django)
    - [Haystack and Whoosh](#haystack-and-whoosh)
    - [OpenPyXL](#openpyxl)
  - [Required Software](#required-software)
  - [Required Packages](#required-packages)
  - [Installation and Setup Instructions](#installation-and-setup-instructions)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [Author](#author)
  - [License](#license)

## Features

- **User Authentication**: Secure login and role-based access control
- **User Management**: Create, view, and delete users (Superuser only)
- **Item Management**: Create, update, use, and delete for items
- **Item Browsing**: Look through items with the search bar
- **Item Requests**: Make requests for new or existing items
- **Data Import**: Import item data from Excel Files
- **Purchase Orders**: Make a list of items to write to a purchase order Excel file
- **Notifications**: Mark notifications as read or delete them

## User Roles

| Role | Permissions |
|------|-------------|
| Superuser | Full access to all features, including user management and item creation. |
| Technician | Can create, delete, and update items. Can create and delete their own item requests. |
| Intern | Limited access to update items (only quantity). |
| Viewer | Can only view items and their details. |

## Technologies Used

### Python

This is the main programming language for the project. It is used for the backend logic, database interactions, and server-side scripting. Python is a versatile, easy-to-learn, and easy-to-use programming language that is widely used in web development.

More info about [Python](https://www.python.org/)

### Django

This is the web framework used to build the application. Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It provides a robust set of features for building web applications, including an ORM (Object-Relational Mapping) system, authentication, and an admin interface.

More info about [Django](https://www.djangoproject.com/)

### Haystack and Whoosh

For database searching, the Haystack search framework has been implemented with the Whoosh backend. Whoosh is easy to set up and well-suited for small applications, which makes it an ideal choice for this application.

More info about [Haystack](https://django-haystack.readthedocs.io/en/master/) and [Whoosh](https://whoosh.readthedocs.io/en/latest/)

### OpenPyXL

For writing to Excel files, OpenPyXL is used. It is a powerful library that allows for easy manipulation of Excel files in Python. This is mainly used for writing item data to an Excel file for purchase orders.

More info about [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)

## Required Software

- Python 3.13.2

## Required Packages

The list of required software below will also be included in the `requirements.txt` file.

- Django
- django-haystack
- openpyxl
- whitenoise
- Whoosh

## Installation and Setup Instructions

### Step 1: Download the Application

1. Go to the [GitHub repository](https://github.com/SierraTran/django-inventory_database).
2. Click the **Code** button and select **Download ZIP**.

### Step 2: Extract the Files

1. Locate the downloaded ZIP file (usually in your "Downloads" folder).
2. Extract all the files to a location of your choice.

### Step 3: Install Required Software

1. Download and install Python from the [official Python website](https://www.python.org/downloads/). At the time of writing this, the latest version of Python is 3.13.2.
2. During installation, make sure to check the box that says **Add Python to PATH**.

### Step 4: Start and Run the Application

1. Open the folder where you extracted the files.
2. Double-click the app.bat file. This will automatically install all the required packages and set up the application for you.

## Usage

- **Home Page**: Displays links to browse items, create new items, import item data, and manage users (based on user permissions).
- **Items Page**: Lists all available items with search functionality.
- **Item Detail Page**: Shows detailed information about a specific item.
- **User Management**: Superusers can create, view, and delete users.

## Future Enhancements

This list contains features that may possibly be added to the application in the future.

- Allow all users access to *only* view the list of all users and their details
- More seamless notification marking and deleting
- Extensive help page and/or contextual help messages
- "Shopping cart" feature for saving a list of items to purchase for purchase order form
- Export items in the inventory to an Excel File

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Author

Sierra Tran

### Contact Info

Email: <sierra.tran@mail.com>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
