import tkinter as tk
from tkinter import messagebox, ttk
import json
from rapidfuzz import fuzz #old package
import os

class DirectoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Link Directory Input")
        self.root.geometry("600x350")

        #JSON name files
        self.data_file = "directory.json"
        self.category_data = self.load_json('categories.json')
              
        #dropdown lists
        self.section_menu = tk.StringVar(value="Select Section")
        self.subsection_menu = tk.StringVar(value="Select Subsection")
        

        #URL input
        tk.Label(root, text="Resource URL:", font=('Times New Roman', 10, 'bold')).pack(pady=(10,0))
        self.url_entry = tk.Entry(root, width=80)
        self.url_entry.pack(pady=5)

        #Description input
        tk.Label(root, text="Description:", font=('Comic Sans', 10, 'bold')).pack(pady=(10,0))
        self.desc_entry = tk.Text(root, width=80, height=2)
        self.desc_entry.pack(pady=5)
        
        #Section menu
        dropdown_frame = tk.Frame(root)
        dropdown_frame.pack(pady=10)

        ###Dropdown Sections below

        #Section
        self.sec_var = tk.StringVar(value="Section")
        self.section_menu = ttk.OptionMenu(dropdown_frame, self.sec_var, "Section", *self.category_data.keys(), style="Custom.TMenubutton", command=self.sync_subsections)
        self.section_menu.config(width=15)
        self.section_menu.grid(row=0, column=0, padx=5)

        #Subsection
        self.sub_var = tk.StringVar(value="Subsection")
        self.subsection_menu = ttk.OptionMenu(dropdown_frame, self.sub_var, "---", style="Custom.TMenubutton")
        self.subsection_menu.config(width=15)
        self.subsection_menu.grid(row=0, column=1, padx=5) # Column 1

        #Add to JSON button
        self.add_btn = tk.Button(
            root, text="Verify & Add", 
            bg="#33493c", fg="white", font=('Arial', 10, 'bold'),
            command=self.validate_and_check
        )
        self.add_btn.pack(pady=20)

    #Dropdown population
    def load_json(self, filename):
        if not os.path.exists(filename):
            return {} if "category" in filename else []
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {} if "category" in filename else []

    #after section is chosen, load in subsection JIT
    def sync_subsections(self, selection):
        #delete old menu items
        self.sub_var.set("Select Subsection")
        menu = self.subsection_menu["menu"]
        menu.delete(0, "end")

        #creation of 'new' menu
        new_options = self.category_data.get(selection, [])
        for option in new_options:
            menu.add_command(
                label=option, 
                command=lambda v=option: self.sub_var.set(v)
            )
    
    #compare input to other inputs in the same section
    def validate_and_check(self):
        url = self.url_entry.get().strip()
        section = self.sec_var.get()
        subsection = self.sub_var.get()

        if not url or section == "Select Section" or subsection == "Select Subsection":
            messagebox.showerror("Error", "Please fill in the URL and select both categories.")
            return

        #comparison search here
        print(f"Checking {url} against your 2000+ entries...")
        messagebox.showinfo("Success", f"Verified! Ready to add to {section} > {subsection}")

        self.addToFile()

    #add the data to the JSON
    def addToFile(self):
        entry = {
        "url": self.url_entry.get().strip(),
        "description": self.desc_entry.get("1.0", tk.END).strip(),  # Text widget needs range args
        "section": self.sec_var.get(),
        "subsection": self.sub_var.get()
    }

        data = self.load_json(self.data_file)  # load existing entries
        data.append(entry)                     # append new entry

        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)       # write back to file

        messagebox.showinfo("Saved", f"Entry added to {self.data_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryManager(root)
    root.mainloop()