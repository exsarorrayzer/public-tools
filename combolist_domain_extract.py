import os
import tkinter as tk
from tkinter import filedialog, messagebox

class CredentialFilterApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Credential Stream Filter")
        self.root.geometry("560x380")
        self.root.resizable(False, False)
        
        self.theme_background = "#1a1a24"
        self.theme_surface = "#222232"
        self.theme_text = "#e2e8f0"
        self.theme_accent = "#3b82f6"
        self.theme_success = "#10b981"
        self.theme_hover = "#60a5fa"
        
        self.root.configure(bg=self.theme_background)
        self.source_file_path = ""
        self.initialize_interface()

    def initialize_interface(self):
        title_label = tk.Label(
            self.root, 
            text="Enterprise Credential Filter", 
            font=("Segoe UI", 16, "bold"), 
            bg=self.theme_background, 
            fg=self.theme_accent
        )
        title_label.pack(pady=15)
        
        container_frame = tk.Frame(self.root, bg=self.theme_surface, bd=0)
        container_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        io_frame = tk.Frame(container_frame, bg=self.theme_surface)
        io_frame.pack(fill="x", padx=15, pady=15)
        
        self.button_browse = tk.Button(
            io_frame, 
            text="Select Source File", 
            command=self.execute_file_browser,
            font=("Segoe UI", 10, "bold"),
            bg=self.theme_accent,
            fg="#ffffff",
            activebackground=self.theme_hover,
            activeforeground="#ffffff",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2"
        )
        self.button_browse.pack(side="left")
        
        self.label_file_status = tk.Label(
            io_frame, 
            text="No source file selected...", 
            font=("Segoe UI", 9, "italic"),
            bg=self.theme_surface, 
            fg="#94a3b8",
            anchor="w"
        )
        self.label_file_status.pack(side="left", padx=10, fill="x", expand=True)
        
        self.label_metrics = tk.Label(
            container_frame,
            text="",
            font=("Segoe UI", 10),
            bg=self.theme_surface,
            fg=self.theme_text,
            justify="left"
        )
        self.label_metrics.pack(pady=5, padx=15, anchor="w")
        
        configuration_frame = tk.Frame(container_frame, bg=self.theme_surface)
        configuration_frame.pack(fill="x", padx=15, pady=10)
        
        label_criterion = tk.Label(
            configuration_frame, 
            text="Target Domain Pattern:", 
            font=("Segoe UI", 10),
            bg=self.theme_surface, 
            fg=self.theme_text
        )
        label_criterion.pack(anchor="w", pady=2)
        
        self.entry_criterion = tk.Entry(
            configuration_frame, 
            font=("Segoe UI", 11), 
            bg=self.theme_background, 
            fg=self.theme_text,
            insertbackground=self.theme_text,
            bd=1,
            relief="solid"
        )
        self.entry_criterion.pack(fill="x", ipady=4)
        
        self.button_process = tk.Button(
            container_frame, 
            text="Execute Filter & Export", 
            command=self.process_dataset,
            font=("Segoe UI", 11, "bold"),
            bg=self.theme_success,
            fg="#ffffff",
            activebackground="#34d399",
            activeforeground="#ffffff",
            bd=0,
            pady=8,
            cursor="hand2"
        )
        self.button_process.pack(fill="x", padx=15, side="bottom", pady=20)

    def execute_file_browser(self):
        selected_path = filedialog.askopenfilename(
            title="Open Target Dataset",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if selected_path:
            self.source_file_path = selected_path
            filename = os.path.basename(selected_path)
            self.label_file_status.config(text=filename, font=("Segoe UI", 9, "bold"), fg=self.theme_text)
            self.evaluate_source_file()

    def evaluate_source_file(self):
        try:
            with open(self.source_file_path, "r", encoding="utf-8", errors="ignore") as target_file:
                records = target_file.readlines()
            
            structured_records = 0
            for record in records:
                record = record.strip()
                if not record or ":" not in record:
                    continue
                structured_records += 1
                
            self.label_metrics.config(
                text=f"Total Records: {len(records)} | Well-Formed: {structured_records}"
            )
        except Exception as execution_error:
            messagebox.showerror("I/O Error", f"Failure during file analysis:\n{str(execution_error)}")

    def process_dataset(self):
        if not self.source_file_path:
            messagebox.showwarning("Validation Error", "Target source file selection is mandatory.")
            return
            
        search_criterion = self.entry_criterion.get().strip().lower()
        if not search_criterion:
            messagebox.showwarning("Validation Error", "Search criterion parameter cannot be null.")
            return
            
        try:
            filtered_dataset = []
            
            with open(self.source_file_path, "r", encoding="utf-8", errors="ignore") as target_file:
                for record in target_file:
                    record = record.strip()
                    if not record or ":" not in record:
                        continue
                    
                    data_segments = record.split(":", 1)
                    identity_segment = data_segments[0].strip()
                    
                    if "@" in identity_segment:
                        domain_segment = identity_segment.split("@")[-1].lower()
                        
                        if search_criterion in domain_segment:
                            filtered_dataset.append(record)
            
            if not filtered_dataset:
                messagebox.showinfo("Operation Result", f"Zero matches identified for criterion: '{search_criterion}'")
                return
                
            destination_path = filedialog.asksaveasfilename(
                title="Export Filtered Dataset",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")],
                initialfile=f"filtered_output_{search_criterion}.txt"
            )
            
            if destination_path:
                with open(destination_path, "w", encoding="utf-8") as destination_file:
                    for qualified_record in filtered_dataset:
                        destination_file.write(qualified_record + "\n")
                        
                messagebox.showinfo(
                    "Operation Successful", 
                    f"Successfully exported {len(filtered_dataset)} matching records.\nDestination: {os.path.basename(destination_path)}"
                )
                
        except Exception as execution_error:
            messagebox.showerror("Execution Failure", f"Critical failure during data filtering:\n{str(execution_error)}")

if __name__ == "__main__":
    interface_root = tk.Tk()
    application_instance = CredentialFilterApplication(interface_root)
    interface_root.mainloop()
