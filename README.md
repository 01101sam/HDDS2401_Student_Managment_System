# Student Management System

# Description

This is a simple student management system that allows you to add, delete, update and view students.
\
It is a web application that uses MySQL to store the student data.

# Develop Approach

The software is developed using the following approach:

1. **Programming Language**: Python
    - **Reason**: Python is a versatile and widely-used language, especially suitable for web development and data
      manipulation. It has a rich ecosystem of libraries and frameworks that facilitate rapid development.

2. **Framework**: Sanic
    - **Reason**: Sanic is an asynchronous web framework for Python that is designed for quick HTTP responses. It is
      suitable for building high-performance web applications.

3. **Template Engine**: Jinja2
    - **Reason**: Jinja2 is a fast, expressive, and extensible templating engine for Python. It allows for the
      separation of HTML presentation from Python code, making the codebase cleaner and more maintainable.

4. **ORM**: SQLAlchemy with aiomysql
    - **Reason**: SQLAlchemy is a powerful and flexible ORM that supports asynchronous operations with aiomysql. This
      combination allows for efficient database interactions in an asynchronous environment.

5. **Cloud Service Model**: Infrastructure as a Service (IaaS)
    - **Reason**: IaaS provides the most control over the infrastructure, allowing for custom configurations and
      optimizations. It is suitable for applications that require specific setups or have high performance and
      scalability needs.

6. **Database**: MySQL
    - **Reason**: MySQL is a reliable and widely-used relational database management system. It is well-supported and
      integrates seamlessly with SQLAlchemy and aiomysql for asynchronous operations.

This approach ensures a robust, scalable, and maintainable web application that leverages modern asynchronous
programming techniques for high performance.

# Features

The student management system provides the following features:

- [X] Add a new student
- [X] Delete an existing student
- [X] Update student information
- [X] View all students

# Installation

## Prerequisites

- Python 3.9+
- MySQL (In this case, Azure Database for MySQL is used)

To install and run the student management system, follow these steps:

1. Clone the repository:

```bash
git clone <repository-url>
cd student-management-system
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```
