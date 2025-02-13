# Inventory Database

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
  - [Required Software](#required-software)
  - [Required Packages](#required-packages)
  - [Setup Instructions](#setup-instructions)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Running Tests](#running-tests)
  - [Contributing](#contributing)
  - [Author](#author)
  - [License](#license)

## Features

- User authentication and authorization
- Browse available items
- Search items
- View item details
- Create, update, and delete items (based on user permissions)
- Import item data
- Manage item requests

## User Roles

- **Superuser**: Full access to all features, including user management and item creation.
- **Technician**: Can create and update items, and request more items.
- **Intern**: Limited access to update items.
- **Viewer**: Can only view items and their details.

## Technologies Used

### Python

This is the main programming language for the project.

More info about [Python](https://www.python.org/)

### Django

This is the web framework used to build the application.

More info about [Django](https://www.djangoproject.com/)

#### Haystack and Whoosh

For searching through the database, Haystack has been implemented with the Whoosh backend.

## Required Software

- Python 3.13.1

## Required Packages

The list of required software below will also be included in the `requirements.txt` file.

- Django
- django-haystack
- openpyxl
- Whoosh

## Setup Instructions

1. Download the zip file.
2. Extract the files into another folder with a name that appropriately matches the application.
3. Click the `app.bat` file.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/jimmyd/django-inventory_database.git
    cd django-inventory_database
    ```

2. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Apply the migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

5. Run the development server:

    ```bash
    python manage.py runserver
    ```

6. Open your web browser and go to `http://127.0.0.1:8000/`.

## Usage

- **Home Page**: Displays links to browse items, create new items, import item data, and manage users (based on user permissions).
- **Items Page**: Lists all available items with search functionality.
- **Item Detail Page**: Shows detailed information about a specific item.
- **User Management**: Superusers can create, view, and delete users.

## Running the Application

You can use the provided `app.bat` file to start the application easily. Just double-click the file, and it will handle the setup and start the server for you.

## Running Tests

To run the tests, use the following command:

```bash
python manage.py test
```

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Author

Sierra Tran

### Contact Info

Email: <sierra.tran@mail.com>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
