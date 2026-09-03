import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import os
import sys
import subprocess
from pathlib import Path

class StartupManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Startup Manager")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")
        
        self.startup_items = []
        self.registry_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run")
        ]
        
        self.folder_paths = [
            os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.join(os.getenv("PROGRAMDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
        ]
        
        self.setup_ui()
        self.load_startup_items()
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg="#2d2d2d", height=60)
        header.pack(fill="x", padx=0, pady=0)
        
        title = tk.Label(header, text="Startup Manager", font=("Segoe UI", 18, "bold"), 
                        fg="#ffffff", bg="#2d2d2d")
        title.pack(side="left", padx=20, pady=15)
        
        refresh_btn = tk.Button(header, text="⟳ Refresh", font=("Segoe UI", 10), 
                               bg="#0d7377", fg="#ffffff", bd=0, padx=20, pady=8,
                               cursor="hand2", command=self.refresh)
        refresh_btn.pack(side="right", padx=20, pady=15)
        
        tree_frame = tk.Frame(self.root, bg="#1e1e1e")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2d2d2d", foreground="#ffffff", 
                       fieldbackground="#2d2d2d", borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#0d7377", foreground="#ffffff", 
                       borderwidth=0, font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#14a085")])
        
        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Location", "Command", "Type"), 
                                show="tree headings", yscrollcommand=scrollbar.set, 
                                selectmode="browse")
        
        self.tree.heading("#0", text="")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Command", text="Command")
        self.tree.heading("Type", text="Type")
        
        self.tree.column("#0", width=40, stretch=False)
        self.tree.column("Name", width=200, stretch=True)
        self.tree.column("Location", width=250, stretch=True)
        self.tree.column("Command", width=300, stretch=True)
        self.tree.column("Type", width=100, stretch=False)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.bind("<Double-Button-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
    def load_startup_items(self):
        self.startup_items.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for hive, key_path in self.registry_keys:
            try:
                key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        hive_name = "HKCU" if hive == winreg.HKEY_CURRENT_USER else "HKLM"
                        location = f"{hive_name}\\{key_path}"
                        
                        item_id = self.tree.insert("", "end", text="✕", 
                                                   values=(name, location, value, "Registry"))
                        self.startup_items.append({
                            "id": item_id,
                            "name": name,
                            "location": location,
                            "command": value,
                            "type": "registry",
                            "hive": hive,
                            "key_path": key_path
                        })
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
            except PermissionError:
                pass
        
        for folder_path in self.folder_paths:
            if os.path.exists(folder_path):
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    if os.path.isfile(file_path):
                        item_id = self.tree.insert("", "end", text="✕", 
                                                   values=(file_name, folder_path, file_path, "Folder"))
                        self.startup_items.append({
                            "id": item_id,
                            "name": file_name,
                            "location": folder_path,
                            "command": file_path,
                            "type": "folder",
                            "file_path": file_path
                        })
    
    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree":
            item_id = self.tree.identify_row(event.y)
            if item_id:
                self.remove_startup_item(item_id)
    
    def remove_startup_item(self, item_id):
        item_data = None
        for item in self.startup_items:
            if item["id"] == item_id:
                item_data = item
                break
        
        if not item_data:
            return
        
        response = messagebox.askyesno(
            "Confirmation",
            f"Are you sure you want to remove this startup item?\n\n{item_data['name']}"
        )
        
        if not response:
            return
        
        try:
            if item_data["type"] == "registry":
                key = winreg.OpenKey(item_data["hive"], item_data["key_path"], 
                                    0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(key, item_data["name"])
                winreg.CloseKey(key)
                messagebox.showinfo("Success", f"Removed: {item_data['name']}")
            elif item_data["type"] == "folder":
                os.remove(item_data["file_path"])
                messagebox.showinfo("Success", f"Removed: {item_data['name']}")
            
            self.refresh()
        except PermissionError:
            messagebox.showerror("Error", "Permission denied. Run as administrator.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove: {str(e)}")
    
    def refresh(self):
        self.load_startup_items()
    
    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        
        self.tree.selection_set(item_id)
        
        menu = tk.Menu(self.root, tearoff=0, bg="#2d2d2d", fg="#ffffff", 
                      activebackground="#0d7377", activeforeground="#ffffff", bd=0)
        menu.add_command(label="Open in Explorer", command=lambda: self.open_in_explorer(item_id))
        menu.add_separator()
        menu.add_command(label="Remove", command=lambda: self.remove_startup_item(item_id))
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def open_in_explorer(self, item_id):
        item_data = None
        for item in self.startup_items:
            if item["id"] == item_id:
                item_data = item
                break
        
        if not item_data:
            return
        
        try:
            if item_data["type"] == "folder":
                subprocess.run(["explorer", "/select,", item_data["file_path"]])
            elif item_data["type"] == "registry":
                subprocess.run(["regedit"])
                messagebox.showinfo("Registry Path", 
                    f"Registry Editor opened.\n\nNavigate to:\n{item_data['location']}\n\nValue: {item_data['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StartupManager()
    app.run()
