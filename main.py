import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import hashlib
import threading  
import os

class DuplicatesDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Finding Duplicates...")

        self.current_folder = ttk.Label(self, text="Indexing folders and files...", style='Custom.TLabel')
        self.current_folder.pack(padx=10, pady=10)

        self.folder_list = tk.Listbox(self, width=60, height=10)
        self.folder_list.pack(padx=10, pady=(0, 10))

        self.processed_files_display = ttk.Label(self, text="Indexed folders and Files: 0", style='Custom.TLabel')
        self.processed_files_display.pack(padx=10, pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var)
        self.progress_bar.pack(padx=10, pady=(0, 10), fill=tk.X)

    def set_current_folder(self, text):
        self.current_folder.configure(text=text)

    def add_folder(self, folder_location):
        self.folder_list.insert(tk.END, folder_location)

    def refresh_processed_files_display(self, count):
        self.processed_files_display.configure(text=f"Indexed Files: {count}")

    def set_progress(self, value):
        self.progress_var.set(value)

class Disky:
    def __init__(self,root):
        self.root = root
        self.root.title("Disky")
        self.root.configure(bg="royal blue")
        self.found_duplicates = set()
        self.file_list = {}
        
        # frame to hold the buttons
        buttons_frame = ttk.Frame(self.root, padding=(15, 0, 15, 10), style='Custom.TFrame')
        buttons_frame.pack(fill=tk.X, padx=15, pady=(20, 0))
        
        select_button = ttk.Button(buttons_frame, text="Select Folder", command=self.select_folder)
        select_button.pack(side=tk.LEFT, padx=(0, 10), pady=10)
        
        self.view_space_display = ttk.Label(buttons_frame, text="0 MB", style='Custom.TLabel')
        self.view_space_display.pack(side=tk.LEFT, padx=(15, 0))
        
        remove_button = ttk.Button(buttons_frame, text="Remove Duplicates", command=self.remove_duplicates)
        remove_button.pack(side=tk.RIGHT, pady=15)
        
        preview_selected_button = ttk.Button(buttons_frame, text="Preview", command=self.preview_selected_duplicate)
        preview_selected_button.pack(side=tk.RIGHT, padx=10, pady=15)

        # treeview frame
        treeview_frame = ttk.Frame(self.root)
        treeview_frame.pack(fill=tk.BOTH, expand=True)

        # treeview to display the folder structure and duplicate files
        self.treeview = ttk.Treeview(treeview_frame, style='Red.Treeview')
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # treeview scrollbars
        vertical_scrollbar = ttk.Scrollbar(treeview_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=vertical_scrollbar.set)

        # treeview columns
        self.treeview['columns'] = ('Location', 'Size', 'HashCode')
        self.treeview.column('Location', width=350, minwidth=150, anchor=tk.W)
        self.treeview.column('Size', width=50, anchor=tk.CENTER)
        self.treeview.column('HashCode', width=150, anchor=tk.W)

        # treeview headings
        self.treeview.heading('#0', text='Name', anchor=tk.W)
        self.treeview.heading('Location', text='Location', anchor=tk.W)
        self.treeview.heading('Size', text='Size', anchor=tk.CENTER)
        self.treeview.heading('HashCode', text='HashCode', anchor=tk.W)
    
    def convert_size_to_readable(self, size_bytes):
        # Function to convert size in bytes to human-readable format (MB/KB/GB)
        # Adapted from: https://stackoverflow.com/a/1094933/12109725
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB" 
        
    def explore_folder(self, folder_location):
        #Go through a folder and find duplicate files
        self.treeview.delete(*self.treeview.get_children())
        self.found_duplicates.clear()

        processed_files = 0
        total_files = 0
        progress_parameter = 0

        duplicates_dialog = DuplicatesDialog(self.root)
        duplicates_dialog.geometry("400x300")
        duplicates_dialog.resizable(False, False)

        def refresh_processed_files_display(count):
            duplicates_dialog.refresh_processed_files_display(count)
            self.root.update_idletasks()

        def refresh_progress(value):
            duplicates_dialog.set_progress(value)
            self.root.update_idletasks()
            
        def generate_hash(path, algorithm='sha256'):
            hash_obj = hashlib.new(algorithm)
            with open(path, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()

        def index_files_folders(folder_location):
            nonlocal processed_files, progress_parameter, total_files

            for root, _, files in os.walk(folder_location):
                duplicates_dialog.add_folder(root)
                refresh_processed_files_display(processed_files)

                for file in files:
                    path = os.path.join(root, file)
                    size_bytes = os.path.getsize(path)
                    size = self.convert_size_to_readable(size_bytes)
                    hash = generate_hash(path)

                    if hash in self.file_list:
                        self.file_list[hash].append((file, path, size, root))
                        self.found_duplicates.add(hash)
                    else:
                        self.file_list[hash] = [(file, path, size, root)]

                    processed_files += 1
                    progress_parameter = (processed_files / total_files) * 100
                    refresh_progress(progress_parameter)

                    # update treeview as files are indexed
                    self.treeview.insert('', 'end', text=file, values=(path, size, hash))
                    self.treeview.update_idletasks()

                    # auto scroll down the treeview
                    self.treeview.yview_moveto(1)
                    
        def populate_treeview(file_list):
            # sort file_list by hash value and mark duplicates with red
            for hash, duplicates in sorted(file_list.items(), key=lambda x: x[0]):
                parent = ''
                for file, path, size, _ in duplicates:
                    tags = ()
                    if len(duplicates) > 1:
                        tags = ('red',)

                    if parent == '':
                        parent = self.treeview.insert('', 'end', text=file, values=(path, size, hash), tags=tags)
                    else:
                        self.treeview.insert(parent, 'end', text=file, values=(path, size, hash), tags=tags)
            
            # Apply default style to all other items without the 'red' tag
            for item in self.treeview.get_children():
                if 'red' not in self.treeview.item(item, 'tags'):
                    self.treeview.tag_configure(item, background='', foreground='black')

        total_files = sum(len(files) for _, _, files in os.walk(folder_location))
        threading.Thread(target=index_files_folders, args=(folder_location,), daemon=True).start()
        self.root.wait_window(duplicates_dialog)

        populate_treeview(self.file_list)
        
        if processed_files == total_files:
            messagebox.showinfo("Indexing Complete", f"Successfully Indexed {processed_files} files.")
        else:
            messagebox.showinfo("Indexing Cancelled", "Indexing process was cancelled.")
    
    def view_space(self, folder_location):
        # View the space occupied by the selected folder.
        total_size = 0

        for dirpath, dirnames, filenames in os.walk(folder_location):
            for file in filenames:
                filepath = os.path.join(dirpath, file)
                total_size += os.path.getsize(filepath)
                
        # Round the total size to two decimal places for a cleaner display.
        formatted_size = self.convert_size_to_readable(total_size)

        # Display the folder location and its occupied space.
        self.view_space_display.configure(text=formatted_size)
        
    def select_folder(self):
        #open a 'select a folder' dialog and update the label.
        folder_location = filedialog.askdirectory()

        if folder_location:
            self.view_space(folder_location)
            threading.Thread(target=self.explore_folder, args=(folder_location,), daemon=True).start()
            
    def remove_duplicates(self):
        # Remove the selected duplicate files, keeping one copy of each
        if not self.found_duplicates:
            messagebox.showinfo("Error", "No duplicates found!")
            return

        deleted_paths = set()

        for hash_val in self.found_duplicates:
            duplicates = self.file_list[hash_val]
            # Keep the first duplicate, remove the rest
            for i in range(1, len(duplicates)):
                _, path, _, _ = duplicates[i]
                try:
                    if path not in deleted_paths:
                        os.remove(path)
                        deleted_paths.add(path)
                except OSError:
                    pass

        self.treeview.delete(*self.treeview.get_children())
        self.found_duplicates.clear()
        messagebox.showinfo("Duplicates Removed!", f"{len(deleted_paths)} indexed duplicate files have been removed.")

    
    def preview_selected_duplicate(self):
        #preview the selected duplicate file.
        selected_item = self.treeview.focus()

        if selected_item:
            path = self.treeview.item(selected_item)['values'][0]
            if os.path.isfile(path):
                try:
                    os.startfile(path)
                except Exception as e:
                    messagebox.showinfo("Error", f"Failed to preview the file: {str(e)}")
            else:
                messagebox.showinfo("Error", "The file doesn't exists.")
                
    
        
    
def main():
    root = tk.Tk()
    root.geometry("720x540")
    root.resizable(True, True)

    style = ttk.Style()
    style.configure('Custom.TLabel', foreground='white', background='black', font=('Helvetica', 12))
    style.configure('Custom.TFrame', background='royal blue')
    style.configure('Red.Treeview', foreground='white', background='red')

    Disky(root)

    root.mainloop()

if __name__ == "__main__":
    main()