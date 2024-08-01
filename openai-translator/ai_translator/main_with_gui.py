import tkinter as tk
from tkinter import filedialog
# Import translation service client (example: Google Cloud Translation API client)
import shutil, subprocess
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main

translate_button = None
download_button = None
def update_gui_after_selected():
    global pdf_path, translate_button, download_button
    print(pdf_path)
    if pdf_path:  # Ensure a file was selected
            # Pass the returned destination_path to the translation function.
        #translate_button = tk.Button(app, text="Translate", command=translate_pdf)
        #translate_button.pack(pady=10)
        status_label.config(text=pdf_path)
        #if 'translate_button' in globals():
                #if 'translate_button' in globals():
        print('aaaaaaaaaaaaa')
        print(translate_button)
        print(download_button)

        try:
            if translate_button:
                translate_button.destroy()
            if download_button:
                download_button.destroy()
        except tk.TclError as e:
            print(f"Error: {e}")
        translate_button = tk.Button(app, text="Translate", command=translate_pdf)
        translate_button.pack(pady=10)
        #else:
        # Use existing Translate button
            #translate_button.pack()        
    else:
        status_label.config(text="No file selected.") 

def update_gui_after_translated():
    global download_button
    # try:
    #     if download_button:
    #         download_button.destroy()
    # except tk.TclError as e:
    #     print(f"Error: {e}")
    download_button = tk.Button(app, text="Download", command=download_file)
    download_button.pack(pady=10)
def select_and_save_file():
    # Open file dialog for PDF selection
    filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    global pdf_path
    if filepath:
        # Define the destination path in the "test" folder
        destination_folder = r"tests"
        
        # Ensure the "test" folder exists
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        # Construct the full destination path
        destination_path = os.path.join(destination_folder, os.path.basename(filepath))
        
        # Copy the selected file to the "test" folder
        try:
            shutil.copy2(filepath, destination_path)
            #print("File copied successfully.")
            print(f"File saved to: {destination_path}")
        except shutil.SameFileError:
            print(f"Warning: Source and destination files are the same")
        except Exception as e:
            print(f"Failed to copy file. Error: {e}")
        pdf_path = destination_path
        pdf_name = filepath.split('/')[-1]
        status_label.config(text=pdf_name) 
        update_gui_after_selected()
def translate_pdf():
    global pdf_path
    # Implement translation logic here using your chosen service
        # Set the environment variable for the subprocess
    env = os.environ.copy()
    env['OPENAI_API_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyTmFtZSI6IlJBTkJUU1BrZ0J1aWxkRXJyb3JBdXRvZGV0ZWN0aW9uQW5kVHJ1bmtUb29sIiwiT2JqZWN0SUQiOiI0QjQ2NUY0Qy1GQjQ0LTRDRDItQkIzMi0yNUEyMjFDQjY4NTQiLCJ3b3JrU3BhY2VOYW1lIjoiVlIwMzEyUkFOQlRTUGFja2FnZUJ1aWxkRXJyb3JBdXRvZGV0ZWN0aW9uQW5kVHJ1bmsiLCJuYmYiOjE3MTE2MzAyNDAsImV4cCI6MTc0MzE2NjI0MCwiaWF0IjoxNzExNjMwMjQwfQ.MqM4BGaEuPG-LdYW_tEDlkyfM9pSdR1JEkFbhevR0xs'
    #script_dir = Path(__file__).resolve().parent  # Get the directory of the current script
    #main_script_path = script_dir / 'openai-translator' / 'ai_translator'
    # Define the command and arguments as a list
    command = ['python', 'ai_translator\main.py', 
               '--model_type', 'OpenAIModel',
               '--file_format', 'markdown',
               '--book', pdf_path,
               '--openai_model', 'gpt-3.5-turbo',
               #'--openai_api_key', 'env['OPENAI_API_KEY']', 
               '--language', 'Chinese']
    
    try:
        # Execute the command using the modified environment
        subprocess.run(command, env=env, check=True)
        print("Translation task executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

    #translated_pdf_link = "https://example.com/translated_pdf"
    status_label.config(text=pdf_path + " translation Complete.")
    #download_link.config(text="Download Translated PDF", fg="blue", cursor="hand2")
    #download_link.bind("<Button-1>", lambda e: webbrowser.open(translated_pdf_link))
    update_gui_after_translated()


def download_file():
   global pdf_path
   translated_path = pdf_path.replace('.pdf', '_translated.md')
   # 使用filedialog来让用户选择保存文件的路径
   save_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(translated_path)[1],
                                            initialfile=os.path.basename(translated_path),
                                            title="保存文件",
                                            initialdir="~/Downloads")
   if save_path:
       try:
           # 将文件复制到用户指定的路径
           shutil.copy2(translated_path, save_path)
           tk.messagebox.showinfo("下载完成", f"文件已保存到: {save_path}")
           #pdf_path = ''
           #update_gui_after_selected()
       except Exception as e:
           tk.messagebox.showerror("错误", f"保存失败: {e}")


"""def on_browse_click():
    Callback function for the browse button.
    # Call the select_and_save_file function and capture its return value.
    pdf_path = select_and_save_file()

     if pdf_path:  # Ensure a file was selected
        # Pass the returned destination_path to the translation function.
        translate_button = tk.Button(app, text="Translate", command=translate_pdf(pdf_path))
        translate_button.pack(pady=10)
    else:
        status_label.config(text="No file selected.") """

pdf_path = ''
app = tk.Tk()
app.title("PDF Translation Service")

status_label = tk.Label(app, text="Please select a PDF file.")
status_label.pack()

select_button = tk.Button(app, text="Select PDF", command=select_and_save_file)
select_button.pack(pady=10)
print(pdf_path)



#download_link = tk.Label(app, text="")
#download_link.pack()

app.mainloop()