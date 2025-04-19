# Inventory Database

![Python Version](https://img.shields.io/badge/python-3.13.2-blue)
![Django Version](https://img.shields.io/badge/django-5.2-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-74%25-2BFF00)

This is a Django-based web application for managing an inventory. The application allows users to browse, search, and manage items in the inventory. It also includes user authentication and authorization features. It is specifically tailored for [Hayes Instrument Service](https://hayesinstruments.com/) to make keeping inventory much easier.

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

|Software|Version|
|--------|-------|
|Python|3.13.2|

## Required Packages

The list of required software below will also be included in the `requirements.txt` file.

|Package|Version|
|-------|-------|
|coverage|7.6.12|
|Django|5.2|
|django-haystack|3.3.0|
|django-model-utils|5.0.0|
|freezegun|1.5.1|
|gunicorn|23.0.0|
|openpyxl|3.1.5|
|waitress|3.0.2|
|whitenoise|6.9.0|
|Whoosh|2.7.4|

## Installation and Setup Instructions

### Step 1: Download the Application

1. Go to the [GitHub repository](https://github.com/SierraTran/inventory_database). (You're already here if the URL in your browser starts with "<https://github.com/SierraTran/inventory_database>"!)
2. Click the **Code** button on the right side of the page.
3. Select **Download ZIP**.

### Step 2: Extract the Files

1. Locate the downloaded ZIP file (usually in your "Downloads" folder).
2. Extract all the files to a location of your choice.

### Step 3: Install Required Software

1. Download and install Python from the [official Python website](https://www.python.org/downloads/). At the time of writing this, the latest version of Python is 3.13.2.
2. During installation, make sure to check the box that says **Add Python to PATH**.

### Step 4: Configure Environment Variables

1. Create a file named `.env` in the root directory of the project (where `manage.py` is located).
2. Add the following environment variables to the `.env` file:

   ```plaintext
   DJANGO_SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. Replace `your-secret-key` with a strong, unique key. To generate this key:
  
    - Open a terminal or command prompt. You can do this by pressing `Win + R`, typing `cmd`, and pressing Enter on Windows. On Mac, you can open the Terminal app from the Applications folder. If you're using Linux, open the terminal from your applications menu.
    - Copy and paste the following command and press Enter:

        ```shell
        py -c "import secrets; print(secrets.token_urlsafe(50))"
        ```

      - *Note: This command uses `py` to run Python on Windows. If you're using Linux or Mac, you can use `python3` or `python` instead.*

    - This will output a long, random string. it will look somehting like this:

        ```plaintext
        n3w5tr0ng53cr3tK3y-EXAMPLE-1234567890
        ```

    - Copy this string and paste it into the `DJANGO_SECRET_KEY` variable in the `.env` file. The variable should look something like this now:

        ```plaintext
        DJANGO_SECRET_KEY=n3w5tr0ng53cr3tK3y-EXAMPLE-1234567890
        ```

4. Set `DEBUG` to `True` for development and debugging. For production, set to `False`

5. Update `ALLOWED_HOSTS` with the domain names or IP addresses you want the application to run on.

    - For local development: `localhost,127.0.0.1`
    - For production: Add your domain name (e.g., `example.com`)

6. Save the `.env` file.

### Step 5: Start and Run the Application

1. Open the folder where you extracted the files.
2. There are two files: `deploy.bat` and `deploy.sh`. These files are used to run the application. Choose the one that matches your operating system:

   - For Windows: Double-click `deploy.bat` to run the application.
   - For Mac/Linux: Open a terminal, navigate to the folder where you extracted the files, and run the following command:

     ```bash
     chmod +x deploy.sh
     ./deploy.sh
     ```

## Usage
<!-- TODO: Expand this section -->
<!-- TODO: Add screenshots and usage instructions -->
- **Home Page**: Displays links to browse items, create new items, import item data, and manage users (based on user permissions).
- **Items Page**: Lists all available items with search functionality.
- **Item Detail Page**: Shows detailed information about a specific item.
- **User Management**: Superusers can create, view, and delete users.

## Future Enhancements

### UI Improvements

- **Seamless Notification Management**: Users can mark and delete notifications directly from the notifications page, avoiding unnecessary navigation.
- **Help page and/or messages**: Users can refer to an extensive page or contextual messages throughout the application for guidance. 

### Inventory Management Features

- **Users Page Access for Everyone**: All users can access the users page and user details for improved transparency.
- **"Shopping Cart for Items**: Users can add items to a list for purchasing, which will be used to populate purchase order forms on the application.
- **Export Inventory to Excel**: Users can generate an Excel file for reports, audits, and inventory tracking without manual data entry.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Author

Sierra Tran

### Contact Info

Email: <sierra.tran@mail.com>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[Back to Top](#inventory-database)
