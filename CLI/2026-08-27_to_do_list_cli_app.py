"""
A simple command-line interface (CLI) application for managing a To-Do list.

This script allows users to:
- Add new tasks to their To-Do list.
- View all existing tasks, showing their status (completed or pending).
- Mark tasks as completed.
- Delete tasks from the list.
- Tasks are persisted to a file named 'todo.txt' in the same directory as the script.
"""

import os # Used to check if the todo file exists.

class TodoApp:
    def __init__(self, filename="todo.txt"):
        """
        Initializes the To-Do list application.
        Loads tasks from the specified file or creates an empty list if the file doesn't exist.
        """
        self.filename = filename
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        """
        Loads tasks from the todo.txt file.
        Each line in the file represents a task.
        Format expected: "[X] Task description" for completed, "[ ] Task description" for pending.
        """
        # Check if the todo file exists. If not, there are no tasks to load.
        if not os.path.exists(self.filename):
            return

        with open(self.filename, 'r') as f:
            for line in f:
                line = line.strip() # Remove leading/trailing whitespace, including newline characters
                if not line: # Skip any completely empty lines
                    continue
                
                # Determine completion status from the beginning of the line
                # '[X]' indicates completed, '[ ]' indicates pending
                completed = line.startswith('[X]')
                
                # Extract the task description by slicing the string after the status tag
                # '[ ] ' or '[X] ' both take up 4 characters.
                task_description = line[4:] 
                self.tasks.append({'task': task_description, 'completed': completed})

    def _save_tasks(self):
        """
        Saves the current list of tasks to the todo.txt file.
        Each task is written on a new line with its completion status.
        """
        with open(self.filename, 'w') as f:
            for task in self.tasks:
                # Choose 'X' for completed, ' ' for pending
                status_char = 'X' if task['completed'] else ' '
                f.write(f"[{status_char}] {task['task']}\n")

    def add_task(self, description):
        """
        Adds a new task to the list.
        New tasks are always added as pending.
        """
        if not description.strip(): # Ensure the description is not just whitespace
            print("Task description cannot be empty.")
            return

        self.tasks.append({'task': description.strip(), 'completed': False})
        self._save_tasks() # Save changes to file immediately
        print(f"Task added: '{description}'")

    def list_tasks(self):
        """
        Displays all tasks in the list with their index and status.
        """
        if not self.tasks:
            print("Your To-Do list is empty!")
            return

        print("\n--- Your To-Do List ---")
        for i, task in enumerate(self.tasks):
            # Display '[X]' for completed tasks, '[ ]' for pending tasks
            status = "[X]" if task['completed'] else "[ ]"
            # Task numbers are 1-based for user friendliness
            print(f"{i + 1}. {status} {task['task']}")
        print("-----------------------\n")

    def complete_task(self, task_index_str):
        """
        Marks a task as completed.
        Handles invalid task indices (non-numeric input, out-of-bounds numbers).
        """
        try:
            # Convert user input string to an integer
            task_index = int(task_index_str)
            # Adjust index from 1-based (user input) to 0-based (list index)
            actual_index = task_index - 1

            # Validate the index to ensure it's within the bounds of the tasks list
            if 0 <= actual_index < len(self.tasks):
                if not self.tasks[actual_index]['completed']:
                    self.tasks[actual_index]['completed'] = True
                    self._save_tasks() # Save changes to file immediately
                    print(f"Task '{self.tasks[actual_index]['task']}' marked as complete.")
                else:
                    print(f"Task '{self.tasks[actual_index]['task']}' is already complete.")
            else:
                print(f"Invalid task number: '{task_index_str}'. Please enter a number from the list.")
        except ValueError:
            print(f"Invalid input: '{task_index_str}'. Please enter a valid number.")

    def delete_task(self, task_index_str):
        """
        Deletes a task from the list.
        Handles invalid task indices (non-numeric input, out-of-bounds numbers).
        """
        try:
            # Convert user input string to an integer
            task_index = int(task_index_str)
            # Adjust index from 1-based (user input) to 0-based (list index)
            actual_index = task_index - 1

            # Validate the index to ensure it's within the bounds of the tasks list
            if 0 <= actual_index < len(self.tasks):
                removed_task = self.tasks.pop(actual_index) # Remove task from the list
                self._save_tasks() # Save changes to file immediately
                print(f"Task '{removed_task['task']}' deleted.")
            else:
                print(f"Invalid task number: '{task_index_str}'. Please enter a number from the list.")
        except ValueError:
            print(f"Invalid input: '{task_index_str}'. Please enter a valid number.")

    def run(self):
        """
        Runs the main interactive loop of the To-Do list application.
        Presents a menu to the user and processes their commands.
        """
        while True:
            print("\n--- To-Do List CLI App ---")
            print("1. Add a new task")
            print("2. List all tasks")
            print("3. Mark task as complete")
            print("4. Delete a task")
            print("5. Exit")
            print("--------------------------")

            choice = input("Enter your choice: ")

            if choice == '1':
                description = input("Enter task description: ")
                self.add_task(description)
            elif choice == '2':
                self.list_tasks()
            elif choice == '3':
                self.list_tasks() # Show tasks first to help the user pick
                if self.tasks: # Only prompt for input if there are tasks to complete
                    task_num_to_complete = input("Enter the number of the task to mark as complete: ")
                    self.complete_task(task_num_to_complete)
            elif choice == '4':
                self.list_tasks() # Show tasks first to help the user pick
                if self.tasks: # Only prompt for input if there are tasks to delete
                    task_num_to_delete = input("Enter the number of the task to delete: ")
                    self.delete_task(task_num_to_delete)
            elif choice == '5':
                print("Exiting To-Do App. Goodbye!")
                break # Exit the main loop, ending the application
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    # This block ensures that the `run()` method is called only when the script
    # is executed directly (not when imported as a module).
    
    # Create an instance of the ToDoApp.
    # By default, it will use 'todo.txt' to store tasks.
    app = TodoApp()
    
    # Start the interactive To-Do list application.
    app.run()
