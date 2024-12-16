import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog


class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SGFM - Simple GUI File Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="#e0e8f0")

        self.current_path_left = os.getcwd()
        self.current_path_right = os.getcwd()

        self.pinned_directories = [
            os.path.expanduser("~"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
        ]

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=5, relief="flat", background="#1e90ff", foreground="white")
        self.style.map("TButton", background=[("active", "#187bcd")])
        self.style.configure("TFrame", background="#e0e8f0")
        self.style.configure("Treeview", background="#ffffff", foreground="#000000", fieldbackground="#ffffff")
        self.style.map("Treeview", background=[("selected", "#1e90ff")], foreground=[("selected", "white")])

        self.create_widgets()

    def create_widgets(self):
        left_frame = ttk.Frame(self.root, style="TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        pinned_label = ttk.Label(left_frame, text="Pinned Directories", font=("Arial", 10, "bold"), background="#e0e8f0")
        pinned_label.pack(fill=tk.X, pady=5)

        self.pinned_listbox = tk.Listbox(left_frame, bg="#f0f8ff", fg="#000000", selectbackground="#1e90ff", selectforeground="white")
        self.pinned_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.pinned_listbox.bind("<Double-1>", self.open_pinned_directory)

        self.update_pinned_list()

        btn_add_pinned = ttk.Button(left_frame, text="Add Directory", command=self.add_pinned_directory)
        btn_add_pinned.pack(fill=tk.X, padx=5, pady=5)

        toolbar = ttk.Frame(self.root, style="TFrame")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        btn_back = ttk.Button(toolbar, text="←", command=self.go_back_left)
        btn_back.pack(side=tk.LEFT, padx=2, pady=2)

        btn_home = ttk.Button(toolbar, text="⌂", command=self.go_home_left)
        btn_home.pack(side=tk.LEFT, padx=2, pady=2)

        btn_create_dir = ttk.Button(toolbar, text="Create Folder", command=self.create_directory_left)
        btn_create_dir.pack(side=tk.LEFT, padx=2, pady=2)

        btn_delete = ttk.Button(toolbar, text="Delete", command=self.delete_item_left)
        btn_delete.pack(side=tk.LEFT, padx=2, pady=2)

        self.path_entry_left = ttk.Entry(toolbar, font=("Arial", 10))
        self.path_entry_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        self.path_entry_left.insert(0, self.current_path_left)
        self.path_entry_left.bind("<Return>", self.change_path_left)

        separator = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=5)

        self.create_file_panels()

    def create_file_panels(self):
        right_frame = ttk.Frame(self.root, style="TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_right = ttk.Treeview(right_frame, columns=("Name", "Type"), show="headings")
        self.tree_right.heading("Name", text="Name")
        self.tree_right.heading("Type", text="Type")
        self.tree_right.column("Name", width=300)
        self.tree_right.column("Type", width=100)
        self.tree_right.pack(fill=tk.BOTH, expand=True)
        self.tree_right.bind("<Double-1>", self.open_item_right)

        self.update_tree(self.tree_right, self.current_path_right)

    def update_pinned_list(self):
        self.pinned_listbox.delete(0, tk.END)
        for directory in self.pinned_directories:
            if os.path.isdir(directory):
                self.pinned_listbox.insert(tk.END, os.path.basename(directory))

    def open_pinned_directory(self, event=None):
        selected_index = self.pinned_listbox.curselection()
        if selected_index:
            selected_dir = self.pinned_directories[selected_index[0]]
            self.current_path_right = selected_dir
            self.update_tree(self.tree_right, self.current_path_right)

    def add_pinned_directory(self):
        new_dir = filedialog.askdirectory()
        if new_dir:
            self.pinned_directories.append(new_dir)
            self.update_pinned_list()

    def update_tree(self, tree, path):
        tree.delete(*tree.get_children())
        try:
            items = os.listdir(path)
            for item in items:
                full_path = os.path.join(path, item)
                item_type = "[D]" if os.path.isdir(full_path) else "[F]"
                tree.insert("", tk.END, values=(item, item_type))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_item_right(self, event=None):
        self.open_item(self.tree_right, self.current_path_right)

    def open_item(self, tree, current_path):
        selected_item = tree.item(tree.focus())
        if selected_item:
            item_name = selected_item["values"][0]
            full_path = os.path.join(current_path, item_name)
            if os.path.isdir(full_path):
                self.current_path_right = full_path
                self.update_tree(tree, self.current_path_right)
            else:
                self.open_file_with_default_app(full_path)

    def go_back_left(self):
        if self.current_path_left != "/":
            self.current_path_left = os.path.dirname(self.current_path_left)
            self.path_entry_left.delete(0, tk.END)
            self.path_entry_left.insert(0, self.current_path_left)
            self.update_tree(self.tree_right, self.current_path_left)

    def go_home_left(self):
        self.current_path_left = os.path.expanduser("~")
        self.path_entry_left.delete(0, tk.END)
        self.path_entry_left.insert(0, self.current_path_left)
        self.update_tree(self.tree_right, self.current_path_left)

    def change_path_left(self, event=None):
        new_path = self.path_entry_left.get()
        if os.path.isdir(new_path):
            self.current_path_left = new_path
            self.update_tree(self.tree_right, self.current_path_left)
        else:
            messagebox.showerror("Error", "Invalid directory path")

    def delete_item_left(self):
        self.delete_item(self.tree_right, self.current_path_left)

    def delete_item(self, tree, current_path):
        selected_item = tree.item(tree.focus())
        if selected_item:
            item_name = selected_item["values"][0]
            full_path = os.path.join(current_path, item_name)
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_name}'?"):
                try:
                    if os.path.isdir(full_path):
                        os.rmdir(full_path)
                    else:
                        os.remove(full_path)
                    self.update_tree(tree, current_path)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def create_directory_left(self):
        self.create_directory(self.current_path_left, self.tree_right)

    def create_directory(self, current_path, tree):
        dir_name = simpledialog.askstring("Input", "Enter directory name:")
        if dir_name:
            full_path = os.path.join(current_path, dir_name)
            try:
                os.mkdir(full_path)
                self.update_tree(tree, current_path)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def open_file_with_default_app(self, path):
        try:
            subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()
