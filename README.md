# Inventory Database

This project was made to simplify the process of keeping inventory. It stores information about parts and units in the company.

## Table of Contents

- [Inventory Database](#inventory-database)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
    - [Python](#python)
    - [Django](#django)
  - [Required Software](#required-software)
  - [Required Packages](#required-packages)
  - [Setup Instructions](#setup-instructions)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [Author](#author)

## Features

- User Authentication
- Search
- Editing Item Information

## Technologies Used

### Python

This is the main programming language for the project.

More info about [Python](https://www.python.org/)

### Django

This is the web framework used to build the application.

More info about [Django](https://www.djangoproject.com/)

## Required Software

- Python 3.13.1
- Django 5.1.5
- SQL Anywhere 12

## Required Packages

The list of required software below will also be included in the `requirements.txt` file.

- Django
- dajngo-haystack
- PyYAML
- sqlany-django
- sqlanydb
- Whoosh

## Setup Instructions

1. Clone the repository:

    ```bash
    git clone https://github.com/SierraTran/django-inventory_database.git
    ```

2. Navigate to the project directory:

    ```bash
    cd django-inventory_database
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Django migrations:

    ```bash
    python manage.py migrate
    ```

5. Start the development server:

    ```bash
    python manage.py runserver
    ```

## Installation

Follow the setup instructions to install the project.

## Usage

1. Open your web browser and go to `http://127.0.0.1:8000/inventory_database`.
2. Log in with your credentials.
3. Use the search feature to find parts and units.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Author

Sierra Tran
