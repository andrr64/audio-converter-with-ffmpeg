import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
from pathlib import Path

class AudioConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter - Batch Processing")
        self.root.geometry("800x650") # Adjusted height slightly for the new label
        self.root.resizable(True, True)
        
        # Variables
        self.input_files = []  # List to store multiple files
        self.output_folder = tk.StringVar()
        self.output_format = tk.StringVar(value="mp3")
        self.quality = tk.StringVar(value="192")
        self.progress_var = tk.DoubleVar()
        self.is_converting = False
        self.conversion_mode = tk.StringVar(value="single")  # 'single' or 'batch'
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1) # Log frame will expand
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Conversion Mode", padding="5")
        mode_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(mode_frame, text="Single File", variable=self.conversion_mode, 
                        value="single", command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Batch Processing", variable=self.conversion_mode, 
                        value="batch", command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        
        # File selection frame
        self.file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        self.file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        self.file_frame.columnconfigure(0, weight=1)
        
        # Single file widgets (initially visible)
        self.single_frame = ttk.Frame(self.file_frame)
        self.single_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.single_frame.columnconfigure(1, weight=1)
        
        self.input_file = tk.StringVar()  # For single file mode
        self.output_file = tk.StringVar() # For single file mode
        
        ttk.Label(self.single_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.single_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(self.single_frame, text="Browse", command=self.browse_single_input).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(self.single_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.single_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(self.single_frame, text="Browse", command=self.browse_single_output).grid(row=1, column=2, padx=5, pady=2)
        
        # Batch widgets (initially hidden)
        self.batch_frame = ttk.Frame(self.file_frame)
        self.batch_frame.columnconfigure(0, weight=1)
        
        # Input files list
        files_label_frame = ttk.Frame(self.batch_frame)
        files_label_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        files_label_frame.columnconfigure(0, weight=1)
        
        ttk.Label(files_label_frame, text="Input Files:").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(files_label_frame, text="Add Files", command=self.add_batch_files).grid(row=0, column=1, padx=5)
        ttk.Button(files_label_frame, text="Clear All", command=self.clear_batch_files).grid(row=0, column=2, padx=5)
        
        # Listbox for files
        listbox_frame = ttk.Frame(self.batch_frame)
        listbox_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.files_listbox = tk.Listbox(listbox_frame, height=6)
        files_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Remove selected button
        ttk.Button(listbox_frame, text="Remove Selected", command=self.remove_selected_file).grid(row=1, column=0, pady=5)
        
        # Output folder
        ttk.Label(self.batch_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.batch_frame, textvariable=self.output_folder, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(self.batch_frame, text="Browse", command=self.browse_output_folder).grid(row=2, column=2, padx=5, pady=2)
        
        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Conversion Settings", padding="5")
        format_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(format_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, padx=5)
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format, 
                                    values=["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"], 
                                    state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        ttk.Label(format_frame, text="Quality (kbps):").grid(row=0, column=2, sticky=tk.W, padx=5)
        quality_combo = ttk.Combobox(format_frame, textvariable=self.quality,
                                     values=["64", "128", "192", "256", "320"],
                                     state="readonly", width=10)
        quality_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0/0")
        self.progress_label.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to convert")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.convert_button = ttk.Button(button_frame, text="Start Conversion", 
                                          command=self.start_conversion, style="Accent.TButton")
        self.convert_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Reset", command=self.reset_form).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=10)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # === ATTRIBUTION LABEL ===
        # Added a label to credit the creator and AI assistance.
        attribution_label = ttk.Label(main_frame, text="Created by Derza Andreas with AI assistance",
                                      font=("Segoe UI", 8), foreground="gray")
        attribution_label.grid(row=7, column=0, columnspan=3, sticky=tk.S, pady=(10, 0))

    def on_mode_change(self):
        """Event handler for when the conversion mode changes."""
        if self.conversion_mode.get() == "single":
            self.batch_frame.grid_remove()
            self.single_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
            self.file_frame.config(text="File Selection")
        else:
            self.single_frame.grid_remove()
            self.batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
            self.batch_frame.columnconfigure(1, weight=1)
            self.file_frame.config(text="Batch File Selection")
    
    def on_format_change(self, event=None):
        """Event handler for when the output format changes."""
        if self.conversion_mode.get() == "single":
            self.update_single_output_extension()
    
    def browse_single_input(self):
        """Browse for a single input file."""
        filetypes = [
            ("Audio/Video Files", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.mp4 *.avi *.mov"),
            ("All Files", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.input_file.set(filename)
            self.auto_set_single_output()
    
    def browse_single_output(self):
        """Browse for a single output file save location."""
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{self.output_format.get()}",
            filetypes=[(f"{self.output_format.get().upper()} files", f"*.{self.output_format.get()}")]
        )
        if filename:
            self.output_file.set(filename)
    
    def add_batch_files(self):
        """Add files for batch processing."""
        filetypes = [
            ("Audio/Video Files", "*.mp3 *.wav *.flac *.aac *.ogg *.m4a *.wma *.mp4 *.avi *.mov"),
            ("All Files", "*.*")
        ]
        filenames = filedialog.askopenfilenames(filetypes=filetypes)
        for filename in filenames:
            if filename not in self.input_files:
                self.input_files.append(filename)
                self.files_listbox.insert(tk.END, os.path.basename(filename))
    
    def remove_selected_file(self):
        """Remove the selected file from the batch list."""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            self.input_files.pop(index)
    
    def clear_batch_files(self):
        """Clear all files from the batch list."""
        self.input_files.clear()
        self.files_listbox.delete(0, tk.END)
    
    def browse_output_folder(self):
        """Browse for an output folder for batch processing."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
    
    def auto_set_single_output(self):
        """Automatically generate an output filename for single mode."""
        if self.input_file.get():
            input_path = Path(self.input_file.get())
            clean_name = self.sanitize_filename(input_path.stem)
            output_path = input_path.parent / f"{clean_name}_converted.{self.output_format.get()}"
            self.output_file.set(str(output_path))
    
    def update_single_output_extension(self):
        """Update the output file extension in single mode when format changes."""
        if self.output_file.get():
            output_path = Path(self.output_file.get())
            new_output_path = output_path.with_suffix(f".{self.output_format.get()}")
            self.output_file.set(str(new_output_path))
        elif self.input_file.get():
            self.auto_set_single_output()
    
    def sanitize_filename(self, filename):
        """Clean the filename of characters that might cause issues for FFmpeg."""
        import re
        sanitized = re.sub(r'[,\s]+', '_', filename)
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', sanitized)
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        sanitized = sanitized.strip('_')
        return sanitized
    
    def log_message(self, message):
        """Adds a message to the log text area."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def reset_form(self):
        """Resets the entire form to its initial state."""
        # Reset single mode
        self.input_file.set("")
        self.output_file.set("")
        
        # Reset batch mode
        self.input_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.output_folder.set("")
        
        # Reset common elements
        self.output_format.set("mp3")
        self.quality.set("192")
        self.conversion_mode.set("single")
        self.on_mode_change()
        self.log_text.delete(1.0, tk.END)
        self.status_label.config(text="Ready to convert")
        self.progress_bar.config(value=0)
        self.progress_label.config(text="0/0")
        
        if self.is_converting:
            self.is_converting = False # This can be used to signal cancellation to the thread
        self.convert_button.config(state="normal", text="Start Conversion")
    
    def validate_inputs(self):
        """Validate all necessary inputs before starting conversion."""
        if self.conversion_mode.get() == "single":
            if not self.input_file.get():
                messagebox.showerror("Error", "Please select an input file!")
                return False
            if not os.path.exists(self.input_file.get()):
                messagebox.showerror("Error", "Input file not found!")
                return False
            if not self.output_file.get():
                messagebox.showerror("Error", "Please specify an output file!")
                return False
        else: # Batch mode
            if not self.input_files:
                messagebox.showerror("Error", "Please add files for batch processing!")
                return False
            if not self.output_folder.get():
                messagebox.showerror("Error", "Please select an output folder for batch processing!")
                return False
            if not os.path.exists(self.output_folder.get()):
                messagebox.showerror("Error", "Output folder not found!")
                return False
        
        # Check for FFmpeg
        try:
            # Using a more specific path check, assuming ffmpeg is bundled
            ffmpeg_path = "./ffmpeg/bin/ffmpeg.exe"
            if not os.path.exists(ffmpeg_path):
                 # Fallback to PATH check
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Error", "FFmpeg not found! Please ensure FFmpeg is installed and in your system's PATH, or placed in './ffmpeg/bin/'.")
            return False
        
        return True
    
    def start_conversion(self):
        """Initiates the conversion process after validation."""
        if not self.validate_inputs():
            return
        
        if self.is_converting:
            messagebox.showwarning("Warning", "A conversion is already in progress!")
            return
        
        self.is_converting = True
        self.convert_button.config(state="disabled", text="Converting...")
        
        if self.conversion_mode.get() == "single":
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start()
            thread = threading.Thread(target=self.convert_single_audio)
        else:
            self.progress_bar.config(mode='determinate', maximum=len(self.input_files))
            self.progress_bar.config(value=0)
            self.progress_label.config(text=f"0/{len(self.input_files)}")
            thread = threading.Thread(target=self.convert_batch_audio)
        
        thread.daemon = True
        thread.start()
    
    def convert_single_audio(self):
        """Handles the conversion of a single audio file."""
        try:
            input_file = self.input_file.get()
            output_file = self.output_file.get()
            
            self.log_message(f"=== SINGLE CONVERSION ===")
            success = self.convert_file(input_file, output_file)
            
            if success:
                self.root.after(0, lambda: self.status_label.config(text="Conversion successful!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Audio conversion completed successfully!"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Conversion failed!"))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: self.status_label.config(text="Conversion failed!"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, self.conversion_finished)
    
    def convert_batch_audio(self):
        """Handles the conversion of multiple audio files."""
        try:
            total_files = len(self.input_files)
            successful_conversions = 0
            failed_conversions = 0
            
            self.log_message(f"=== BATCH CONVERSION - {total_files} files ===")
            
            for i, input_file in enumerate(self.input_files):
                if not self.is_converting:  # Check if conversion was cancelled by resetting
                    self.log_message("\nBatch conversion cancelled by user.")
                    break
                
                input_path = Path(input_file)
                clean_name = self.sanitize_filename(input_path.stem)
                output_file = os.path.join(self.output_folder.get(), 
                                           f"{clean_name}_converted.{self.output_format.get()}")
                
                self.log_message(f"\n[{i+1}/{total_files}] Processing: {input_path.name}")
                
                success = self.convert_file(input_file, output_file)
                
                if success:
                    successful_conversions += 1
                else:
                    failed_conversions += 1
                
                # Update progress
                progress_value = i + 1
                self.root.after(0, lambda pv=progress_value: self.progress_bar.config(value=pv))
                self.root.after(0, lambda pv=progress_value, t=total_files: 
                                self.progress_label.config(text=f"{pv}/{t}"))
            
            # Summary
            self.log_message(f"\n=== BATCH CONVERSION COMPLETED ===")
            self.log_message(f"Successful: {successful_conversions}")
            self.log_message(f"Failed: {failed_conversions}")
            self.log_message(f"Total: {total_files}")
            
            if failed_conversions == 0:
                self.root.after(0, lambda: self.status_label.config(text=f"All {total_files} files converted successfully!"))
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Batch conversion successful!\n{successful_conversions} files converted."))
            else:
                self.root.after(0, lambda: self.status_label.config(text=f"Batch complete: {successful_conversions} succeeded, {failed_conversions} failed"))
                self.root.after(0, lambda: messagebox.showwarning("Batch Complete", 
                                f"Batch conversion finished with the following results:\nSuccessful: {successful_conversions}\nFailed: {failed_conversions}"))
                
        except Exception as e:
            error_msg = f"Batch Error: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: self.status_label.config(text="Batch conversion failed!"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, self.conversion_finished)
    
    def convert_file(self, input_file, output_file):
        """Core conversion function using FFmpeg. Returns True if successful."""
        try:
            format_type = self.output_format.get()
            bitrate = self.quality.get()
            
            self.log_message(f"Input: {os.path.basename(input_file)}")
            self.log_message(f"Output: {os.path.basename(output_file)}")
            self.log_message(f"Format: {format_type.upper()}, Quality: {bitrate} kbps")
            
            # Build FFmpeg command
            # This assumes ffmpeg is in a subfolder. Change to just "ffmpeg" to use PATH.
            ffmpeg_path = "./ffmpeg/bin/ffmpeg.exe"
            if not os.path.exists(ffmpeg_path):
                ffmpeg_path = "ffmpeg" # Fallback to PATH

            # Use a creation flag to hide the console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            cmd = [ffmpeg_path, "-i", input_file, "-y"] # Base command
            
            # Add codec and bitrate options based on format
            if format_type in ["mp3", "aac", "ogg", "wma"]:
                cmd.extend(["-b:a", f"{bitrate}k"])
            if format_type == "m4a": # m4a is a container, typically with aac audio
                cmd.extend(["-c:a", "aac", "-b:a", f"{bitrate}k"])
            elif format_type == "flac":
                cmd.extend(["-c:a", "flac"]) # FLAC is lossless, bitrate is not applicable in the same way
            elif format_type == "wav":
                cmd.extend(["-c:a", "pcm_s16le"]) # Standard WAV format
            
            cmd.append(output_file)
            
            # Run FFmpeg
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                       universal_newlines=True, startupinfo=startupinfo)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.log_message("✅ Conversion successful!")
                return True
            else:
                self.log_message(f"❌ Conversion failed: {stderr.strip()}")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error converting {os.path.basename(input_file)}: {str(e)}")
            return False
    
    def conversion_finished(self):
        """Finalizes the UI state after a conversion process ends."""
        if self.conversion_mode.get() == "single":
            self.progress_bar.stop()
        self.is_converting = False
        self.convert_button.config(state="normal", text="Start Conversion")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set app style using a theme file (e.g., from rdbende's Azure-ttk-theme)
    # This makes the UI look more modern.
    try:
        # Assumes 'azure.tcl' is in the same directory
        root.tk.call('source', 'azure.tcl')
        root.tk.call("set_theme", "light")
    except tk.TclError:
        print("Azure theme not found. Using default TTK theme.") # Optional: log to console
    
    app = AudioConverter(root)
    root.mainloop()
