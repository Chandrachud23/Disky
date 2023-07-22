import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import datetime
import webbrowser

class Disky:
    def __init__(self,root):
        self.root = root
        self.root.title("Disky")
        self.root.configure(bg="dark blue")
        self.found_duplicates = set()
        self.file_list = {}
        
        # frame to hold the buttons
        buttons_frame = ttk.Frame(self.root, padding=(15, 15, 15, 0), style='Custom.TFrame')
        buttons_frame.pack(fill=tk.X)
        
        select_button = ttk.Button(buttons_frame, text="Select Folder", command=self.select_folder)
        select_button.pack(side=tk.LEFT, pady=15)
        
        # selected folder path label
        self.folder_path_label = ttk.Label(buttons_frame, text="No folder selected", style='Custom.TLabel')
        self.folder_path_label.pack(side=tk.LEFT, padx=(15, 0))
        
        remove_button = ttk.Button(buttons_frame, text="Remove Duplicates", command=self.remove_duplicates)
        remove_button.pack(side=tk.RIGHT, pady=15)
        
        preview_selected_button = ttk.Button(buttons_frame, text="Preview", command=self.preview_selected_duplicate)
        preview_selected_button.pack(side=tk.RIGHT, padx=10, pady=15)

        # separator between buttons and treeview
        separator = ttk.Separator(self.root, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=10)

        # treeview frame
        treeview_frame = ttk.Frame(self.root)
        treeview_frame.pack(fill=tk.BOTH, expand=True)

        # treeview to display the folder structure and duplicate files
        self.treeview = ttk.Treeview(treeview_frame)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # treeview scrollbars
        vertical_scrollbar = ttk.Scrollbar(treeview_frame, orient=tk.VERTICAL, command=self.treeview.yview)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=vertical_scrollbar.set)

        # treeview columns
        self.treeview['columns'] = ('Location', 'Size', 'HashCode')
        self.treeview.column('#0', width=250, minwidth=100, anchor=tk.W)
        self.treeview.column('Location', width=350, minwidth=150, anchor=tk.W)
        self.treeview.column('Size', width=50, anchor=tk.CENTER)
        self.treeview.column('HashCode', width=150, anchor=tk.W)

        # treeview headings
        self.treeview.heading('#0', text='Name', anchor=tk.W)
        self.treeview.heading('Location', text='Location', anchor=tk.W)
        self.treeview.heading('Size', text='Size', anchor=tk.CENTER)
        self.treeview.heading('HashCode', text='HashCode', anchor=tk.W)

    def select_folder(self):
        messagebox.showinfo("Select Folder", "Select the folder to remove duplicates from")
    def remove_duplicates(self):
        messagebox.showinfo("Remove Duplicates", "Remove the selected duplicates")
    
    def preview_selected_duplicate(self):
        messagebox.showinfo("Preview", "Preview the selected duplicate")

def main():
    root = tk.Tk()
    root.geometry("1024x768")
    root.resizable(True, True)

    style = ttk.Style()
    style.configure('Custom.TLabel', foreground='white', background='dark blue')
    style.configure('Custom.TFrame', background='dark blue')
    style.configure('Red.Treeview', foreground='white', background='sky blue')

    Disky(root)

    root.mainloop()

if __name__ == "__main__":
    main()