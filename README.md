# IDataMig
---

## Overview

This project is a Python-based Database Migration System built using Flask. It facilitates database migrations for seamless transitions and updates. The system utilizes a `pyproject.toml` file for dependency management and is structured to be executed as a Flask application via `app.py`.

## Installation and Setup

### Dependencies

This project employs Poetry for dependency management. Ensure you have Poetry installed in your environment. If not, you can install it by following the instructions on the [Poetry documentation](https://python-poetry.org/docs/).

### Installation Steps

1. **Clone the Repository:**

```bash
git clone https://gitlab.com/ggustavo/ipq-migration.git
```

2. **Navigate to the Project Directory:**

```bash
cd IDataMig
```

3. **Install Dependencies:**

```bash
poetry install
```

### Configuration

Before running the application, you need to set up a `.env` file with the necessary database credentials. Create a file named `.env` in the project root directory and populate it with the following details:

```plaintext
# PostgreSQL Credentials
POSTGRES_DBNAME="database"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD=""
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

# MySQL Credentials
MYSQL_DATABASE="database"
MYSQL_USER="user"
MYSQL_PASSWORD=""
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
```

## Running the Application

### Development Environment

To run the application in a development environment, execute the following command:

```bash
poetry run python app.py
```

This will start the Flask development server, and the application will be accessible at http://localhost:5000.
