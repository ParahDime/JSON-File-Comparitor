import tkinter as tk
from tkinter import messagebox, ttk
import json
from rapidfuzz import fuzz #old package
import os
from urllib.parse import urlparse

class DirectoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Link Directory Input")
        self.root.geometry("600x400")

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
        self.desc_entry = tk.Text(root, width=60, height=2)
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
        self.subsection_menu = ttk.OptionMenu(dropdown_frame, self.sub_var, "Select Subsection", style="Custom.TMenubutton")
        self.subsection_menu.config(width=15)
        self.subsection_menu.grid(row=0, column=1, padx=5) # Column 1

        #recent entries
        tk.Label(root, text="Recent Entries:", font=('Arial', 9, 'bold')).pack(pady=(10,0))
        self.recent_box = tk.Text(root, width=60, height=4, state='disabled', bg='#f0f0f0')
        self.recent_box.pack(pady=5)
        self.refresh_recent()

        self.entry_count_label = tk.Label(root, text="", font=('Arial', 9, 'italic'))
        self.entry_count_label.pack(pady=(0,5))
        self.update_entry_count()

        #Add to JSON button
        self.add_btn = tk.Button(
            root, text="Verify & Add", 
            bg="#33493c", fg="white", font=('Arial', 10, 'bold'),
            command=self.validate_and_check
        )
        self.add_btn.pack(pady=20)
        #keybind to also add to JSON
        self.root.bind('<Return>', lambda e: self.validate_and_check())

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
        self.sub_var.set("Select Subsection")
        menu = self.subsection_menu["menu"]
        menu.delete(0, "end")

        #creation of new menu
        new_options = self.category_data.get(selection, [])
        for option in new_options:
            menu.add_command(
                label=option, 
                command=lambda v=option: self.sub_var.set(v)
            )
    
    #compare input to other inputs in the same section
    def validate_and_check(self):
        #clean url entry
        url = self.url_entry.get().strip()
        url = self.normalise_url(url)
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)

        section = self.sec_var.get()
        subsection = self.sub_var.get()

        if not url or section == "Select Section" or subsection == "Select Subsection":
            messagebox.showerror("Error", "Please fill in the URL and select both categories.")
            return

        #comparison search here
        print(f"Checking {url} against your 2000+ entries...")

        data = self.load_json(self.data_file)

        #check for an exact match on the url
        exact_match = next((e for e in data if e['url'] == url), None)
        if exact_match:
            messagebox.showerror("Duplicate URL", 
                f"This exact URL already exists:\n\n"
                f"Section: {exact_match['section']} > {exact_match['subsection']}\n"
                f"Description: {exact_match['description']}")
            self.clearFields()
            return 
        
        
        input_domain = self.get_base_domain(url)
        matches = [e for e in data if self.get_base_domain(e['url']) == input_domain]

        if matches:
        #show custom popup, stop if user cancels
            if not self.show_matches_popup(matches):
                return

        success = self.addToFile()
        print(success)
        #clear fields and update recent files added if added correctly
        if success:
            self.clearFields()
            self.refresh_recent()
            self.update_entry_count()

    #get the first part of the domain
    def get_base_domain(self, url):
        if not url.startswith("http"):
            url = "https://" + url
        return urlparse(url).netloc

    #sanitise and normalise the url (ensuring https and www are added)
    def normalise_url(self, url):
        url = url.strip()
        
        # add https:// if no protocol present
        if not url.startswith(("http://", "https://", "ftp://")):
            url = "https://" + url
        
        # add www. if no subdomain present
        parsed = urlparse(url)
        if not parsed.netloc.startswith("www."):
            url = url.replace(parsed.netloc, "www." + parsed.netloc)
        
        return url

    #popup window to show potential matches
    def show_matches_popup(self, matches):
        popup = tk.Toplevel(self.root)
        popup.title("Similar Entries Found")
        popup.geometry("500x250")
        popup.grab_set()                                # locks focus to popup

        tk.Label(popup, text="Multiple similar entries found:", font=('Arial', 10, 'bold')).pack(pady=(10,0))

        # scrollable list
        frame = tk.Frame(popup)
        frame.pack(fill='both', expand=True, padx=10, pady=5)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side='right', fill='y')
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=70, height=10)
        for e in matches:
            listbox.insert(tk.END, f"{e['url']}  |  {e['section']} > {e['subsection']}")
        listbox.pack(side='left', fill='both')
        scrollbar.config(command=listbox.yview)

        # result tracks whether user clicked Add or Cancel
        result = tk.BooleanVar(value=False)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Anyway", bg="#33493c", fg="white",
                command=lambda: [result.set(True), popup.destroy()]).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Cancel", bg="#8b0000", fg="white",
                command=lambda: [result.set(False), popup.destroy()]).grid(row=0, column=1, padx=10)

        self.root.wait_window(popup)                    # waits for popup to close before continuing
        return result.get()
    
    #get the data then add the data to the JSON
    def addToFile(self):
        entry = {
            "url": self.url_entry.get().strip(),
            "description": self.desc_entry.get("1.0", tk.END).strip(),
            "section": self.sec_var.get(),
            "subsection": self.sub_var.get()
        }

        #append the data into the file
        data = self.load_json(self.data_file)
        data.append(entry)                     

        #write to file
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)       

        messagebox.showinfo("Saved", f"Entry added to {self.data_file}")
        return True

    #clear each field, use after a successful entry
    def clearFields(self):
        self.url_entry.delete(0, tk.END)
        self.desc_entry.delete("1.0", tk.END)
        self.sec_var.set("Section")
        self.sub_var.set("Select Subsection")
        
        self.subsection_menu["menu"].delete(0, "end")

    #update the entry count
    def update_entry_count(self):
        data = self.load_json(self.data_file)
        count = len(data)
        self.entry_count_label.config(text=f"Total entries: {count:,}")

    #refresh the list of 3 most recent url additions
    def refresh_recent(self):
        data = self.load_json(self.data_file)
        last_three = data[-3:]                          
        
        self.recent_box.config(state='normal')
        self.recent_box.delete("1.0", tk.END)
        
        for entry in reversed(last_three):
            line = f"{entry['url']} | {entry['section']} > {entry['subsection']}\n"
            self.recent_box.insert(tk.END, line)
        
        self.recent_box.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryManager(root)
    root.mainloop()