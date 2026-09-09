import sqlite3

"""
A simple command-line interface (CLI) application for performing
CRUD (Create, Read, Update, Delete) operations on a SQLite database.
It manages a list of tasks with descriptions and a status (e.g., 'pending', 'completed').

This script is fully self-contained and uses only the standard library.
It's designed to be beginner-friendly, demonstrating basic SQLite interactions.
"""

DATABASE_NAME = 'tasks.db' # The name of our SQLite database file

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    # This line allows us to access columns by name instead of by index
    conn.row_factory = sqlite3.Row
    return conn

def create_tasks_table():
    """Creates the 'tasks' table in the database if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' -- e.g., 'pending', 'completed'
        )
    ''')
    conn.commit() # Save changes to the database
    conn.close() # Close the connection

def add_task(description):
    """Adds a new task to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tasks (description, status) VALUES (?, ?)",
                       (description, 'pending'))
        conn.commit()
        print(f"Task '{description}' added successfully with status 'pending'.")
    except sqlite3.Error as e:
        print(f"Error adding task: {e}")
    finally:
        conn.close()

def view_tasks(status=None):
    """Retrieves and displays tasks from the database.
    
    Args:
        status (str, optional): If provided, filters tasks by this status
                                (e.g., 'pending', 'completed').
                                If None, all tasks are displayed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute("SELECT id, description, status FROM tasks WHERE status = ?", (status,))
        print(f"\n--- {status.capitalize()} Tasks ---")
    else:
        cursor.execute("SELECT id, description, status FROM tasks ORDER BY id DESC")
        print("\n--- All Tasks ---")
        
    tasks = cursor.fetchall()
    
    if tasks:
        for task in tasks:
            # task is a sqlite3.Row object, allowing access by column name
            print(f"ID: {task['id']}, Description: {task['description']}, Status: {task['status']}")
    else:
        print("No tasks found.")
        
    conn.close()

def update_task_status(task_id, new_status):
    """Updates the status of an existing task."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        if cursor.rowcount > 0: # Check if any row was actually updated
            conn.commit()
            print(f"Task ID {task_id} status updated to '{new_status}'.")
        else:
            print(f"Task ID {task_id} not found.")
    except sqlite3.Error as e:
        print(f"Error updating task: {e}")
    finally:
        conn.close()

def delete_task(task_id):
    """Deletes a task from the database by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount > 0: # Check if any row was actually deleted
            conn.commit()
            print(f"Task ID {task_id} deleted successfully.")
        else:
            print(f"Task ID {task_id} not found.")
    except sqlite3.Error as e:
        print(f"Error deleting task: {e}")
    finally:
        conn.close()

def display_menu():
    """Prints the main menu options to the console."""
    print("\n--- SQLite Task Manager ---")
    print("1. Add a new task")
    print("2. View all tasks")
    print("3. View pending tasks")
    print("4. View completed tasks")
    print("5. Mark task as completed")
    print("6. Mark task as pending")
    print("7. Delete a task")
    print("8. Exit")
    print("---------------------------")

def main():
    """Main function to run the CLI application."""
    create_tasks_table() # Ensure the table exists when the app starts

    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            description = input("Enter task description: ")
            if description:
                add_task(description)
            else:
                print("Task description cannot be empty.")
        elif choice == '2':
            view_tasks()
        elif choice == '3':
            view_tasks(status='pending')
        elif choice == '4':
            view_tasks(status='completed')
        elif choice == '5':
            try:
                task_id = int(input("Enter the ID of the task to mark as completed: "))
                update_task_status(task_id, 'completed')
            except ValueError:
                print("Invalid input. Please enter a number for the task ID.")
        elif choice == '6':
            try:
                task_id = int(input("Enter the ID of the task to mark as pending: "))
                update_task_status(task_id, 'pending')
            except ValueError:
                print("Invalid input. Please enter a number for the task ID.")
        elif choice == '7':
            try:
                task_id = int(input("Enter the ID of the task to delete: "))
                delete_task(task_id)
            except ValueError:
                print("Invalid input. Please enter a number for the task ID.")
        elif choice == '8':
            print("Exiting Task Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main() # Run the main application loop
