import blessed
import sys
import os
import math
from linux_user_management import *

class UserManagementCLI:
    ITEMS_PER_PAGE = 5
    NAVIGATION_INSTRUCTIONS = "↑/↓: Navigate | ←/→: Change page | N: New user | Backspace: Delete | L: Lock | U: Unlock | Q: Quit"

    def __init__(self):
        self.term = blessed.Terminal()
        self.users = get_users()
        self.page = 1
        self.selected_index = 0
        self.message = ""
        self.update_pagination()

    def update_pagination(self):
        self.total_pages = math.ceil(len(self.users) / self.ITEMS_PER_PAGE)

    def draw(self):
        print(self.term.clear)
        self.draw_table_header()
        self.draw_user_list()
        self.draw_message()
        self.draw_navigation_instructions()
        self.draw_page_info()

    def draw_table_header(self):
        print(self.term.bold(f"{'#':<5}{'Username':<20}{'Full Name':<30}{'Locked':<10}"))

    def draw_user_list(self):
        start_index = (self.page - 1) * self.ITEMS_PER_PAGE
        end_index = min(start_index + self.ITEMS_PER_PAGE, len(self.users))
        for idx, user in enumerate(self.users[start_index:end_index], start=start_index):
            line = f"{idx+1:<5}{user['username']:<20}{user['fullname']:<30}{'Yes' if user['locked'] else 'No':<10}"
            print(self.term.black_on_white(line) if idx == self.selected_index else line)

    def draw_message(self):
        print(self.term.move_y(self.term.height - 6) + self.message)

    def draw_navigation_instructions(self):
        print(self.term.move_y(self.term.height - 3) + self.NAVIGATION_INSTRUCTIONS)

    def draw_page_info(self):
        print(self.term.move_y(self.term.height - 2) + f"Page {self.page}/{self.total_pages}")

    def get_input(self, prompt, hide=False):
        print(self.term.move_y(self.term.height - 1) + self.term.clear_eol + prompt, end='', flush=True)
        result = []
        while True:
            char = self.term.inkey()
            if char.name == 'KEY_ENTER':
                print()
                return ''.join(result)
            elif char.name == 'KEY_BACKSPACE':
                if result:
                    result.pop()
                    print(self.term.move_left + ' ' + self.term.move_left, end='', flush=True)
            elif not char.is_sequence:
                result.append(char)
                print('*' if hide else char, end='', flush=True)

    def handle_input(self, key):
        if key.lower() == 'q':
            return False
        elif key.name == 'KEY_DOWN':
            self.move_selection(1)
        elif key.name == 'KEY_UP':
            self.move_selection(-1)
        elif key.name == 'KEY_RIGHT':
            self.change_page(1)
        elif key.name == 'KEY_LEFT':
            self.change_page(-1)
        elif key.lower() == 'n':
            self.add_user()
        elif key.name == 'KEY_BACKSPACE':
            self.delete_user()
        elif key.lower() == 'l':
            self.lock_user()
        elif key.lower() == 'u':
            self.unlock_user()
        return True

    def move_selection(self, direction):
        new_index = self.selected_index + direction
        if new_index >= (self.ITEMS_PER_PAGE * self.page):
            self.change_page(1)
            self.selected_index = (self.page - 1) * self.ITEMS_PER_PAGE
        elif new_index < (self.page - 1) * self.ITEMS_PER_PAGE:
            self.change_page(-1)
            self.selected_index = min(len(self.users) - 1, self.page * self.ITEMS_PER_PAGE - 1)
        else:
            self.selected_index = new_index

    def change_page(self, direction):
        new_page = self.page + direction
        if 1 <= new_page <= self.total_pages:
            self.page = new_page
            self.selected_index = min(self.selected_index, len(self.users) - 1)

    def run(self):
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            while True:
                self.draw()
                if not self.handle_input(self.term.inkey()):
                    break
                self.refresh_users()

    def refresh_users(self):
        self.users = get_users()
        self.update_pagination()
        if self.selected_index >= len(self.users):
            self.selected_index = len(self.users) - 1

    def add_user(self):
        username = self.get_input("Enter username: ")
        fullname = self.get_input("Enter full name: ")
        password = self.get_input("Enter password: ", hide=True)
        
        if create_user(username, fullname, password):
            self.message = f"User {username} created successfully."
        else:
            self.message = f"Failed to create user {username}."

    def delete_user(self):
        user = self.users[self.selected_index]
        confirm = self.get_input(f"Are you sure you want to delete {user['username']}? (y/n): ")

        if confirm.lower() == 'y':
            if delete_user(user['username']):
                self.message = f"User {user['username']} deleted successfully."
            else:
                self.message = f"Failed to delete user {user['username']}."
        else:
            self.message = "Deletion cancelled."

    def lock_user(self):
        user = self.users[self.selected_index]
        if lock_user(user['username']):
            self.message = f"User {user['username']} locked successfully."
        else:
            self.message = f"Failed to lock user {user['username']}."

    def unlock_user(self):
        user = self.users[self.selected_index]
        if unlock_user(user['username']):
            self.message = f"User {user['username']} unlocked successfully."
        else:
            self.message = f"Failed to unlock user {user['username']}."

def main():
    if os.geteuid() != 0:
        print("This script must be run with sudo privileges.")
        sys.exit(1)
    
    cli = UserManagementCLI()
    cli.run()
  
if __name__ == "__main__":
    main()