import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("SGFM - Simple GUI File Manager")
        self.root.geometry("800x600")
        self.current_path = os.getcwd()

        self.create_widgets()

    def create_widgets(self):
        toolbar = tk.Frame(self.root, bg="lightgray")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        btn_open = tk.Button(toolbar, text="Open", command=self.open_item)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)

        btn_back = tk.Button(toolbar, text="Back", command=self.go_back)
        btn_back.pack(side=tk.LEFT, padx=2, pady=2)

        btn_home = tk.Button(toolbar, text="Home", command=self.go_home)
        btn_home.pack(side=tk.LEFT, padx=2, pady=2)

        btn_delete = tk.Button(toolbar, text="Delete", command=self.delete_item)
        btn_delete.pack(side=tk.LEFT, padx=2, pady=2)

        btn_create_dir = tk.Button(toolbar, text="Create Dir", command=self.create_directory)
        btn_create_dir.pack(side=tk.LEFT, padx=2, pady=2)

        btn_create_file = tk.Button(toolbar, text="Create File", command=self.create_text_file)
        btn_create_file.pack(side=tk.LEFT, padx=2, pady=2)

        btn_edit = tk.Button(toolbar, text="Edit", command=self.edit_file)
        btn_edit.pack(side=tk.LEFT, padx=2, pady=2)

        self.tree = ttk.Treeview(self.root, columns=("Name", "Type"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.column("Name", width=300)
        self.tree.column("Type", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.open_item)

        self.update_tree()

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        try:
            items = os.listdir(self.current_path)
            for item in items:
                full_path = os.path.join(self.current_path, item)
                item_type = "Folder" if os.path.isdir(full_path) else "File"
                self.tree.insert("", tk.END, values=(item, item_type))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_item(self, event=None):
        selected_item = self.tree.item(self.tree.focus())
        if selected_item:
            item_name = selected_item["values"][0]
            full_path = os.path.join(self.current_path, item_name)
            if os.path.isdir(full_path):
                self.current_path = full_path
                self.update_tree()
            else:
                self.open_file_with_default_app(full_path)

    def go_back(self):
        if self.current_path != "/":
            self.current_path = os.path.dirname(self.current_path)
            self.update_tree()

    def go_home(self):
        self.current_path = os.path.expanduser("~")
        self.update_tree()

    def delete_item(self):
        selected_item = self.tree.item(self.tree.focus())
        if selected_item:
            item_name = selected_item["values"][0]
            full_path = os.path.join(self.current_path, item_name)
            if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{item_name}'?"):
                try:
                    if os.path.isdir(full_path):
                        os.rmdir(full_path)
                    else:
                        os.remove(full_path)
                    self.update_tree()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def create_directory(self):
        dir_name = simpledialog.askstring("Input", "Enter directory name:")
        if dir_name:
            full_path = os.path.join(self.current_path, dir_name)
            try:
                os.mkdir(full_path)
                self.update_tree()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_text_file(self):
        file_name = simpledialog.askstring("Input", "Enter file name:")
        if file_name:
            full_path = os.path.join(self.current_path, file_name)
            try:
                with open(full_path, "w") as file:
                    pass
                self.update_tree()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def edit_file(self):
        selected_item = self.tree.item(self.tree.focus())
        if selected_item:
            item_name = selected_item["values"][0]
            full_path = os.path.join(self.current_path, item_name)
            if os.path.isfile(full_path):
                try:
                    subprocess.run(["nano", full_path])
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
