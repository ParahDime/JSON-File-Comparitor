import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
from rapidfuzz import fuzz #old package
import os
from urllib.parse import urlparse

import pandas as pd


class DirectoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Link Directory Input")
        self.root.geometry("600x500")

        #JSON name files
        self.data_file = "directory.json"
        self.category_data = self.load_json('categories.json')
        self.queue_file = "queue.json"
              
        self.excel_queue = self.load_json(self.queue_file)

        self.read_in_btn = tk.Button(
            root, text="Select File", 
            bg="#33493c", fg="white", font=('Arial', 10, 'bold'),
            command=self.select_excel_file
        )
        self.read_in_btn.pack(pady=10)

        self.process_btn = tk.Button(
            root, text="Process Staged Data (0 remaining)", 
            bg="#1d5c38", fg="white", font=('Arial', 10, 'bold'),
            command=self.open_process_popup
        )
        #Check if items in read in queue
        

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

        self.update_process_button()

    #save the queue
    def save_queue_to_disk(self):
        with open(self.queue_file, 'w') as f:
            json.dump(self.excel_queue, f, indent=4)

    # ADDED: Remove single item from queue and rewrite queue.json
    def remove_from_queue_disk(self, index=0):
        if self.excel_queue:
            self.excel_queue.pop(index)
            self.save_queue_to_disk()

    def select_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            sheets_dict = pd.read_excel(file_path, sheet_name=None, header=None)
            new_items_count = 0

            for sheet_name, df in sheets_dict.items():
                df = df.dropna(how='all')
                for _, row in df.iterrows():
                    subsec = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                    raw_url = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                    desc = str(row.iloc[3]).strip() if len(row) > 3 and pd.notna(row.iloc[3]) else ""

                    if raw_url:
                        # CHANGED: Appends to existing list so multiple Excel files stack together
                        self.excel_queue.append({
                            "section": str(sheet_name).strip(),
                            "subsection": subsec,
                            "url": raw_url,
                            "description": desc
                        })
                        new_items_count += 1

            if new_items_count > 0:
                # CHANGED: Persists entire updated queue array to queue.json once reading completes
                self.save_queue_to_disk()
                self.update_process_button()
                messagebox.showinfo("Success", f"Added {new_items_count} items to queue. Total staged: {len(self.excel_queue)}")
            else:
                messagebox.showwarning("Warning", "No valid link entries found in the file.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse Excel file:\n{str(e)}")

    def update_process_button(self):
        count = len(self.excel_queue)
        if count > 0:
            self.process_btn.config(text=f"Process Staged Data ({count} remaining)")
            self.process_btn.pack(pady=(0, 10), before=self.add_btn)
        else:
            self.process_btn.pack_forget()

    def open_process_popup(self):
        if not self.excel_queue:
            return

        popup = tk.Toplevel(self.root)
        popup.title("Review & Process Staged Data")
        popup.geometry("500x250")
        popup.grab_set()

        item = self.excel_queue[0]

        tk.Label(popup, text=f"Items Remaining in Queue: {len(self.excel_queue)}", font=('Arial', 10, 'bold')).pack(pady=5)

        # Editable URL
        tk.Label(popup, text="URL:").pack()
        p_url_entry = tk.Entry(popup, width=65)
        p_url_entry.insert(0, item['url'])
        p_url_entry.pack(pady=2)

        # Editable Description
        tk.Label(popup, text="Description:").pack()
        p_desc_entry = tk.Text(popup, width=50, height=3)
        p_desc_entry.insert("1.0", item['description'])
        p_desc_entry.pack(pady=2)

        # --- SECTION / SUBSECTION DROPDOWN BLOCK ---
        tk.Label(popup, text="Section / Subsection:").pack()
        frame_cat = tk.Frame(popup)
        frame_cat.pack(pady=2)

        initial_sec = item['section'] if item['section'] in self.category_data else "Section"
        sec_var = tk.StringVar(value=initial_sec)
        
        initial_sub = item['subsection'] if item['subsection'] else "Select Subsection"
        sub_var = tk.StringVar(value=initial_sub)

        #Callback to update subsections when section changes
        def update_subsections(selected_section):
            sec_var.set(selected_section)
            sub_var.set("Select Subsection")
            menu = p_sub_menu["menu"]
            menu.delete(0, "end")
            
            options = self.category_data.get(selected_section, [])
            for option in options:
                menu.add_command(label=option, command=lambda v=option: sub_var.set(v))

        p_sec_menu = ttk.OptionMenu(
            frame_cat, sec_var, initial_sec, 
            *self.category_data.keys(), 
            command=update_subsections
        )
        p_sec_menu.grid(row=0, column=0, padx=5)

        p_sub_menu = ttk.OptionMenu(frame_cat, sub_var, initial_sub)
        p_sub_menu.grid(row=0, column=1, padx=5)

        # Populate subsection options on initial load
        if initial_sec in self.category_data:
            menu = p_sub_menu["menu"]
            menu.delete(0, "end")
            for option in self.category_data[initial_sec]:
                menu.add_command(label=option, command=lambda v=option: sub_var.set(v))

        #Commit item
        def commit_and_next():
            raw_url = p_url_entry.get().strip()
            if not raw_url:
                messagebox.showerror("Error", "URL cannot be empty.", parent=popup)
                return

            norm_url = self.normalise_url(raw_url)
            data = self.load_json(self.data_file)

            exact_match = next((e for e in data if e['url'] == norm_url), None)
            if exact_match:
                messagebox.showerror("Duplicate URL", 
                    f"Exact URL exists:\n{exact_match['section']} > {exact_match['subsection']}\n"
                    f"Desc: {exact_match['description']}", parent=popup)
                return

            domain = self.get_base_domain(norm_url)
            matches = [e for e in data if self.get_base_domain(e['url']) == domain]
            if matches and not self.show_matches_popup(matches):
                return

            #Save item to directory.json
            new_entry = {
                "url": norm_url,
                "description": p_desc_entry.get("1.0", tk.END).strip(),
                "section": sec_var.get(),
                "subsection": sub_var.get()
            }
            data.append(new_entry)
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)

            #Delete from queue.json
            self.remove_from_queue_disk(0)

            self.refresh_recent()
            self.update_entry_count()
            self.update_process_button()
            popup.destroy()

            if self.excel_queue:
                self.open_process_popup()

        # delete item from queue.json
        def discard_item():
            self.remove_from_queue_disk(0)
            self.update_process_button()
            popup.destroy()
            if self.excel_queue:
                self.open_process_popup()

        #Close popup without deleting the current item from queue.json
        def skip_for_later():
            popup.destroy()

        #POPUP BUTTON LAYOUT
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="Verify & Add", bg="#33493c", fg="white", 
            font=('Arial', 9, 'bold'), width=12, command=commit_and_next
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame, text="Discard Item", bg="#8b0000", fg="white", 
            font=('Arial', 9, 'bold'), width=12, command=discard_item
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            btn_frame, text="Close Window", bg="#555555", fg="white", 
            font=('Arial', 9, 'bold'), width=12, command=skip_for_later
        ).grid(row=0, column=2, padx=5)   
        
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

    #Load the unsorted stored data
    def load_queue(self):
        if not os.path.exists("queue.json"):
            return []
        try:
            with open("queue.json", "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    #Save the queue whenever a state changes
    def save_queue(self):
        with open("queue.json", "w") as f:
            json.dump(self.excel_queue, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryManager(root)
    root.mainloop()
