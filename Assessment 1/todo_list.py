todo_List = []

print("Select the operation to be performed:")
print("1. Add an element to the list.")
print("2. Show the list.")
print("3. Mark an element from the list.")
print("4. Exit.")

def add_element():
    task = input("Enter the task: ")
    todo_List.append({"task": task, "completed": False})
    print("Task added.")

def show_list():
    if not todo_List:
        print("The list is empty!")
    else:
        print("\nYour To-Do List:")
        for i, item in enumerate(todo_List, start=1):
            status = "Completed" if item["completed"] else "Pending"
            print(f"{i}. [{status}] {item['task']}")


def mark_element():
    show_list()
    if not todo_List:
        return
    try:
        index = int(input("Enter the task number to mark as completed: "))
        if 1 <= index <= len(todo_List):
            todo_List[index - 1]["completed"] = True
            print("Task marked as completed!")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

while True:
    choice = input("\nEnter your choice (1/2/3/4): ")

    if choice == '1':
        add_element()
    elif choice == '2':
        show_list()
    elif choice == '3':
        mark_element()
    elif choice == '4':
        print("Exiting... Goodbye!")
        break
    else:
        print("Invalid choice!")
