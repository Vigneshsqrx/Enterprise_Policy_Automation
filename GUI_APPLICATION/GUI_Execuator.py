import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
from tkinter import ttk
from dotenv import load_dotenv

# Global variable to store the selected folder path
selected_folder = ""


# Load environment variables from the .env file
env_file = "config_data.env"
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    messagebox.showerror("Error", f"{env_file} not found!")


def execute_script(script_path):
    if script_path:

        # Reload environment variables
        load_dotenv(env_file, override=True)


        # Switch to the output tab and clear previous output
        notebook.select(output_tab)
        output_text.delete(1.0, tk.END)

        # Create the output directory in the same directory as the application
        output_dir = os.path.join(os.getcwd(), "Automation_output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define the output file path
        script_name = os.path.splitext(os.path.basename(script_path))[0]

        current_policy_var = policy_var_field.get()
        if current_policy_var == "RULER":
            output_file_path = os.path.join(output_dir, f"{script_name}_RULER_output.txt")
        else:
            output_file_path = os.path.join(output_dir, f"{script_name}_LUA_output.txt")

        try:
            # Use subprocess.Popen to execute the script
            process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)

            def read_output():
                try:
                    # Open the output file in the thread
                    with open(output_file_path, 'w') as output_file:
                        for line in process.stdout:
                            output_text.insert(tk.END, line)
                            output_text.see(tk.END)
                            output_file.write(line)  # Write output to file
                        for line in process.stderr:
                            output_text.insert(tk.END, "\nError:\n" + line)
                            output_text.see(tk.END)
                            output_file.write("\nError:\n" + line)  # Write error to file
                        process.wait()
                        output_text.insert(tk.END, "\nExecution finished.")
                        output_file.write("\nExecution finished.")
                except Exception as e:
                    output_text.insert(tk.END, f"\nError in output handling: {e}")

            # Start a thread to read the output and error
            threading.Thread(target=read_output, daemon=True).start()
        except Exception as e:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"An error occurred: {e}")


def extract_metadata_from_script(script_path):
    tag = ""
    ai_prompt = ""

    try:
        with open(script_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("tag = "):
                    tag = line.split("tag = ")[1].strip().strip('"')
                elif line.startswith("ai_prompt = "):
                    ai_prompt = line.split("ai_prompt = ")[1].strip().strip('"')
    except Exception as e:
        print(f"Error reading script {script_path}: {e}")

    return tag, ai_prompt

def browse_folder():
    global selected_folder
    foldername = filedialog.askdirectory()
    if foldername:
        selected_folder = foldername
        # Clear the existing content in the Treeview
        for item in script_tree.get_children():
            script_tree.delete(item)

        for filename in os.listdir(foldername):
            if filename.endswith(".py"):
                script_path = os.path.join(foldername, filename)
                tag, ai_prompt = extract_metadata_from_script(script_path)
                # Insert the filename, tag, and ai_Prompt into the Treeview
                script_tree.insert('', tk.END, values=(filename, tag, ai_prompt))

def browse_extension_folder():
    foldername = filedialog.askdirectory()
    if foldername:
        entry_chrome_ext.delete(0, tk.END)
        entry_chrome_ext.insert(0, foldername)


def execute_selected_script():
    selected_item = script_tree.selection()
    if selected_item:
        selected_script = script_tree.item(selected_item)['values'][0]
        script_path = os.path.join(selected_folder, selected_script)
        execute_script(script_path)
    else:
        messagebox.showwarning("No Script Selected", "Please select a script to execute.")

def save_data():
    data = {
        "ADMIN_USERNAME": entry_admin_user.get(),
        "ADMIN_PASSWORD": entry_admin_pass.get(),
        "TENANT_NAME": entry_tenant_name.get(),
        "TENANT_URL": entry_tenant_url.get(),
        "ASSIGNED_USERNAME": entry_emp_user.get(),
        "ASSIGNED_PASSWORD": entry_emp_pass.get(),
        "EXTENSION_PATH": entry_chrome_ext.get(),
        "BROWSER": entry_browser.get(),
        "POLICY_TYPE": policy_var_field.get(),
    }

    with open(env_file, 'w') as f:
        for key, value in data.items():
            # Escape any special characters (optional)
            value = value.replace("\n", "\\n")  # Handle multi-line values
            f.write(f"{key}={value}\n")

def load_data():
            entry_admin_user.insert(0, os.getenv("ADMIN_USERNAME", ""))
            entry_admin_pass.insert(0, os.getenv("ADMIN_PASSWORD", ""))
            entry_tenant_name.insert(0, os.getenv("TENANT_NAME", ""))
            entry_tenant_url.insert(0, os.getenv("TENANT_URL", ""))
            entry_emp_user.insert(0, os.getenv("ASSIGNED_USERNAME", ""))
            entry_emp_pass.insert(0, os.getenv("ASSIGNED_PASSWORD", ""))
            entry_chrome_ext.insert(0, os.getenv("EXTENSION_PATH", ""))
            entry_browser.insert(0, os.getenv("BROWSER", ""))
            policy_var_field.insert(0, os.getenv("POLICY_TYPE", ""))


def on_closing():
    save_data()  # Save data before closing
    root.destroy()  # Close the window

def on_tree_selection(event):
    selected_item = script_tree.selection()
    if selected_item:
        selected_script = script_tree.item(selected_item)['values'][0]
        script_path = os.path.join(selected_folder, selected_script)
        _, ai_prompt = extract_metadata_from_script(script_path)
        ai_prompt_text.delete(1.0, tk.END)
        ai_prompt_text.insert(tk.END, ai_prompt)

# Create the main window
root = tk.Tk()
root.title("Square-X Automation Tool")

# Set custom maximum size
max_width = 700  # Example width
max_height = 750  # Example height
root.geometry(f"{max_width}x{max_height}")

# Optionally, prevent the window from being resized beyond the maximum size
root.maxsize(max_width, max_height)

# Create a Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create the main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main Tab")

# Create the output tab
output_tab = ttk.Frame(notebook)
notebook.add(output_tab, text="Output Tab")

# Create a frame for the scrollable area in the main tab
scrollable_frame = tk.Frame(main_tab)
scrollable_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a scrollbar
scrollbar = tk.Scrollbar(scrollable_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a canvas to hold the scrollable content
canvas = tk.Canvas(scrollable_frame, yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure the scrollbar
scrollbar.config(command=canvas.yview)

# Create a frame inside the canvas
content_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor='nw')

# Update the scroll region
def update_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

content_frame.bind("<Configure>", update_scroll_region)

# Create and place widgets for fields inside the content frame
tk.Label(content_frame, text="Admin Username:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
entry_admin_user = tk.Entry(content_frame, width=50)
entry_admin_user.grid(row=0, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Admin Password:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
entry_admin_pass = tk.Entry(content_frame, width=50, show="*")
entry_admin_pass.grid(row=1, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Tenant Name:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
entry_tenant_name = tk.Entry(content_frame, width=50)
entry_tenant_name.grid(row=2, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Tenant URL:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
entry_tenant_url = tk.Entry(content_frame, width=50)
entry_tenant_url.grid(row=3, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Assigned Username:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
entry_emp_user = tk.Entry(content_frame, width=50)
entry_emp_user.grid(row=4, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Assigned User Password:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
entry_emp_pass = tk.Entry(content_frame, width=50, show="*")
entry_emp_pass.grid(row=5, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Chrome Extension Path:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
entry_chrome_ext = tk.Entry(content_frame, width=50)
entry_chrome_ext.grid(row=6, column=1, padx=10, pady=5)
tk.Button(content_frame, text="Browse", command=browse_extension_folder).grid(row=6, column=2, padx=10, pady=5)

tk.Label(content_frame, text="Browser:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
entry_browser = tk.Entry(content_frame, width=50)
entry_browser.grid(row=7, column=1, padx=10, pady=5)

tk.Label(content_frame, text="Policy Type:").grid(row=8, column=0, padx=10, pady=5, sticky='e')
policy_var_field= tk.Entry(content_frame, width=50)
policy_var_field.grid(row=8, column=1, padx=10, pady=5)

# Radio buttons for selecting LUA or RULER without default selection
policy_var = tk.StringVar()  # No default value set

tk.Button(content_frame, text="Browse Folder", command=browse_folder).grid(row=9, column=0, padx=10, pady=5)
tk.Button(content_frame, text="Execute Script", command=execute_selected_script).grid(row=9, column=1, padx=10, pady=5)
tk.Button(content_frame, text="Save Data", command=save_data).grid(row=9, column=2, padx=10, pady=5)

# Add the Treeview to the scrollable frame
script_tree = ttk.Treeview(content_frame, columns=("Filename", "Tag", "AI Prompt"), show="headings")
script_tree.heading("Filename", text="Filename")
script_tree.heading("Tag", text="Tag")
script_tree.heading("AI Prompt", text="AI Prompt")
script_tree.grid(row=10, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

# Bind the Treeview selection event to the update function
script_tree.bind("<<TreeviewSelect>>", on_tree_selection)

# Create a text widget for displaying AI Prompts below the Treeview
ai_prompt_text = tk.Text(content_frame, height=8, width=80)
ai_prompt_text.grid(row=11, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')

# Add the text widget to the output tab
output_text = tk.Text(output_tab, wrap=tk.WORD)
output_text.pack(fill=tk.BOTH, expand=True)

# Load saved data
load_data()

# Set the window close protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the application
root.mainloop()
