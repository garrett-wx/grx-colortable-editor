import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.colorchooser import askcolor
import re
import pyautogui
from PIL import ImageGrab
import threading
import time
from pynput import mouse

class ColorTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Table Creator")
        self.color_entries = []
        self.setup_ui()

    def setup_ui(self):
        # File menu
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Color Table", command=self.open_color_table)
        file_menu.add_command(label="Save Color Table", command=self.save_color_table)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Product, Units, Scale, Offset, Step, and RF settings
        frame_settings = ttk.LabelFrame(self.root, text="Settings")
        frame_settings.pack(fill="x", padx=10, pady=5)

        # Row 0: Product and Units
        ttk.Label(frame_settings, text="Product:").grid(row=0, column=0, sticky='e')
        self.product_entry = ttk.Entry(frame_settings, width=15)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_settings, text="Units:").grid(row=0, column=2, sticky='e')
        self.units_entry = ttk.Entry(frame_settings, width=15)
        self.units_entry.grid(row=0, column=3, padx=5, pady=5)

        # Row 1: Scale and Offset
        ttk.Label(frame_settings, text="Scale:").grid(row=1, column=0, sticky='e')
        self.scale_entry = ttk.Entry(frame_settings, width=15)
        self.scale_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_settings, text="Offset:").grid(row=1, column=2, sticky='e')
        self.offset_entry = ttk.Entry(frame_settings, width=15)
        self.offset_entry.grid(row=1, column=3, padx=5, pady=5)

        # Row 2: Step
        ttk.Label(frame_settings, text="Step:").grid(row=2, column=0, sticky='e')
        self.step_entry = ttk.Entry(frame_settings, width=15)
        self.step_entry.grid(row=2, column=1, padx=5, pady=5)

        # Row 3: RF Color Selector
        ttk.Label(frame_settings, text="RF:").grid(row=3, column=0, sticky='e')
        self.rf_color_preview = tk.Label(
            frame_settings, width=3, background="#FFFFFF",
            relief="solid", borderwidth=1
        )
        self.rf_color_preview.grid(row=3, column=1, padx=5, pady=5)

        self.rf_color_button = ttk.Button(
            frame_settings, text="Select RF Color", command=self.select_rf_color
        )
        self.rf_color_button.grid(row=3, column=2, padx=5, pady=5)

        # Scrollable frame for color entries with both vertical and horizontal scrollbars
        frame_colors = ttk.LabelFrame(self.root, text="Color Entries")
        frame_colors.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(frame_colors)
        self.scroll_frame = ttk.Frame(canvas)
        scroll_y = ttk.Scrollbar(frame_colors, orient="vertical", command=canvas.yview)
        scroll_x = ttk.Scrollbar(frame_colors, orient="horizontal", command=canvas.xview)

        canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Add color button
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(fill="x", padx=10, pady=5)

        self.add_color_button = ttk.Button(frame_buttons, text="Add Color", command=self.add_color_entry)
        self.add_color_button.pack(side="left")

        self.preview_button = ttk.Button(frame_buttons, text="Preview Color Table", command=self.preview_color_table)
        self.preview_button.pack(side="right")

        # Preview canvas (increase height to accommodate labels)
        self.preview_canvas = tk.Canvas(self.root, height=70)  # Increased height
        self.preview_canvas.pack(fill="x", padx=10, pady=5)

    def refresh_color_entries(self):
        """
        Sort the color_entries list based on the numeric value in 'value_entry'
        and re-pack them into the GUI in sorted order.
        """
        # Define a helper function to extract the numeric value
        def get_entry_value(entry):
            try:
                return float(entry['value_entry'].get())
            except ValueError:
                # Assign a large number to push invalid entries to the end
                return float('inf')
        
        # Sort the color_entries list
        self.color_entries.sort(key=get_entry_value)
        
        # Re-pack the entries in sorted order
        for entry in self.color_entries:
            entry['frame'].pack_forget()  # Remove from current position
        for entry in self.color_entries:
            entry['frame'].pack(fill="x", pady=2)  # Re-pack in sorted order

    def create_color_entry(self, value='', color_band=None):
        """
        Create a color entry in the GUI.

        Parameters:
        - value: The starting data value for the color band.
        - color_band: A dictionary containing color band information:
          - 'type': 'single', 'solid', 'gradient'
          - 'format': 'rgb', 'rgba'
          - 'start_color': Hex color string
          - 'end_color': Hex color string (only for gradients)
        """
        color_row = ttk.Frame(self.scroll_frame)
        color_row.pack(fill="x", pady=2)

        value_entry = ttk.Entry(color_row, width=10)
        value_entry.pack(side="left", padx=5)
        value_entry.insert(0, value)
        
        # Bind the value_entry to refresh entries on value change
        value_entry.bind("<FocusOut>", lambda e: self.refresh_color_entries())
        value_entry.bind("<Return>", lambda e: self.refresh_color_entries())

        # Store the color band info
        color_info = {
            'type': 'single',
            'format': 'rgb',
            'start_color': '#FFFFFF',
            'end_color': None,
            'start_alpha': 255,
            'end_alpha': 255
        }
        if color_band:
            color_info.update(color_band)

        # Get band type from color_info if available
        initial_band_type = color_info.get('type', 'single').capitalize()
        band_type_var = tk.StringVar(value=initial_band_type)
        band_type_menu = ttk.OptionMenu(color_row, band_type_var, initial_band_type, 'Single', 'Solid', 'Gradient')
        band_type_menu.pack(side="left", padx=5)

        # Color format selector
        initial_color_format = color_info.get('format', 'rgb').upper()
        color_format_var = tk.StringVar(value=initial_color_format)
        color_format_menu = ttk.OptionMenu(color_row, color_format_var, initial_color_format, 'RGB', 'RGBA')
        color_format_menu.pack(side="left", padx=5)

        # Color previews
        start_color_preview = tk.Label(
            color_row, width=3, background=color_info['start_color'],
            relief="solid", borderwidth=1
        )
        start_color_preview.pack(side="left", padx=5)
        start_color_preview.color_value = color_info['start_color']
        start_color_preview.alpha_value = color_info.get('start_alpha', 255)

        start_color_button = ttk.Button(
            color_row, text="Start Color",
            command=lambda cp=start_color_preview: self.select_color(cp, color_format_var)
        )
        start_color_button.pack(side="left", padx=5)

        # Added: Pick Screen Color Button
        pick_screen_color_button = ttk.Button(
            color_row, text="Pick Screen Color",
            command=lambda cp=start_color_preview: self.pick_screen_color(cp, color_format_var)
        )
        pick_screen_color_button.pack(side="left", padx=5)

        # Initialize 'end_color_preview' and 'end_color_button' as None
        entry = {
            'frame': color_row,
            'value_entry': value_entry,
            'band_type_var': band_type_var,
            'color_format_var': color_format_var,
            'start_color_preview': start_color_preview,
            'end_color_preview': None,
            'end_color_button': None,
            'end_pick_screen_color_button': None,  # To handle end color picking
            'color_info': color_info
        }

        # Append to color_entries
        self.color_entries.append(entry)
        
        # Refresh the entries to sort them
        self.refresh_color_entries()

        def update_band_type(*args):
            band_type = band_type_var.get().lower()
            # Show/hide end color widgets based on band type
            if band_type == 'gradient':
                if entry['end_color_preview'] is None:
                    # Create end color widgets
                    end_color_preview = tk.Label(
                        color_row, width=3,
                        background=color_info.get('end_color', '#FFFFFF'),
                        relief="solid", borderwidth=1
                    )
                    end_color_preview.pack(side="left", padx=5)
                    end_color_preview.color_value = color_info.get('end_color', '#FFFFFF')
                    end_color_preview.alpha_value = color_info.get('end_alpha', 255)

                    end_color_button = ttk.Button(
                        color_row, text="End Color",
                        command=lambda cp=end_color_preview: self.select_color(cp, color_format_var)
                    )
                    end_color_button.pack(side="left", padx=5)

                    # Add Pick Screen Color Button for End Color
                    end_pick_screen_color_button = ttk.Button(
                        color_row, text="Pick Screen Color",
                        command=lambda cp=end_color_preview: self.pick_screen_color(cp, color_format_var)
                    )
                    end_pick_screen_color_button.pack(side="left", padx=5)

                    # Store in entry
                    entry['end_color_preview'] = end_color_preview
                    entry['end_color_button'] = end_color_button
                    entry['end_pick_screen_color_button'] = end_pick_screen_color_button
                else:
                    # Widgets already exist; make sure they're visible
                    entry['end_color_preview'].pack(side="left", padx=5)
                    entry['end_color_button'].pack(side="left", padx=5)
                    entry['end_pick_screen_color_button'].pack(side="left", padx=5)
            else:
                # Hide end color widgets
                if entry['end_color_preview'] is not None:
                    entry['end_color_preview'].pack_forget()
                    entry['end_color_button'].pack_forget()
                    entry['end_pick_screen_color_button'].pack_forget()

            # Update color_info
            color_info['type'] = band_type

        # Bind the band type selector to update widgets
        band_type_var.trace_add('write', update_band_type)
        update_band_type()  # Initialize UI correctly

        # Bind the color format selector to update color selection
        def update_color_format(*args):
            # Update color_info
            color_info['format'] = color_format_var.get().lower()

        color_format_var.trace_add('write', update_color_format)
        update_color_format()  # Initialize UI correctly

        remove_button = ttk.Button(
            color_row, text="Remove",
            command=lambda cr=color_row: self.remove_color_entry(cr)
        )
        remove_button.pack(side="right", padx=5)

    def add_color_entry(self):
        self.create_color_entry()

    def remove_color_entry(self, color_row):
        # Remove the entry from color_entries and destroy the frame
        for entry in self.color_entries:
            if entry['frame'] == color_row:
                color_row.destroy()
                self.color_entries.remove(entry)
                break
        
        # Refresh the entries to sort them
        self.refresh_color_entries()


    def select_color(self, color_preview, color_format_var):
        # Get the current color value of the color preview label
        current_color = color_preview.color_value if hasattr(
            color_preview, 'color_value') else "#FFFFFF"
        # Open the color chooser
        if color_format_var.get().lower() == 'rgba':
            # Ask for color and alpha separately
            color = askcolor(color=current_color)[1]
            if color:
                alpha = simpledialog.askinteger(
                    "Alpha", "Enter alpha value (0-255):",
                    minvalue=0, maxvalue=255, initialvalue=color_preview.alpha_value
                )
                if alpha is not None:
                    color_preview.config(background=color)
                    color_preview.color_value = color
                    color_preview.alpha_value = alpha
        else:
            color = askcolor(color=current_color)[1]
            if color:
                color_preview.config(background=color)
                color_preview.color_value = color
                color_preview.alpha_value = 255  # Default alpha

    def pick_screen_color(self, color_preview, color_format_var):
        """
        Allows the user to pick a color from anywhere on the screen via a mouse click.
        """
        # Minimize the main window to allow the user to see the screen
        self.root.withdraw()
        time.sleep(0.2)  # Wait for the window to minimize

        # Inform the user
        messagebox.showinfo("Pick Color", "After clicking OK, click anywhere on the primary screen to select a color.")

        # Function to handle the mouse click
        def on_click(x, y, button, pressed):
            if pressed:
                try:
                    # Get the primary screen size
                    screen_width, screen_height = pyautogui.size()
                    
                    # Check if the click is within the primary screen
                    if x < 0 or y < 0 or x > screen_width or y > screen_height:
                        messagebox.showerror("Invalid Selection", "Selected position is outside the primary monitor.")
                        self.root.deiconify()  # Restore the main window
                        return False  # Stop listener

                    # Get the color of the pixel at the clicked position
                    screenshot = ImageGrab.grab()
                    selected_color = screenshot.getpixel((x, y))
                    
                    # Update the color preview
                    if selected_color:
                        hex_color = "#{:02x}{:02x}{:02x}".format(*selected_color[:3])
                        self.root.deiconify()  # Restore the main window
                        self.root.lift()        # Bring it to the front
                        color_preview.config(background=hex_color)
                        color_preview.color_value = hex_color
                        if color_format_var.get().lower() == 'rgba':
                            # Handle alpha if available
                            alpha = selected_color[3] if len(selected_color) > 3 else 255
                            color_preview.alpha_value = alpha
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to capture color: {e}")
                finally:
                    self.root.deiconify()  # Ensure the window is restored
                # Stop the listener after one click
                return False

        # Start the mouse listener in a separate thread
        listener = mouse.Listener(on_click=on_click)
        listener.start()

    def select_rf_color(self):
        # Get the current RF color
        current_color = self.rf_color_preview['background']
        # Open the color chooser
        color = askcolor(color=current_color)[1]
        if color:
            self.rf_color_preview.config(background=color)

    def preview_color_table(self):
        self.preview_canvas.delete("all")
        # Update the canvas to get the correct width
        self.preview_canvas.update_idletasks()
        total_width = self.preview_canvas.winfo_width()
        height = self.preview_canvas.winfo_height()

        margin = 10  # Define a margin on both sides
        width = total_width - 2 * margin  # Adjusted width for drawing

        # Collect entries that have both value and color set
        entries = []
        for entry in self.color_entries:
            value_entry = entry['value_entry']
            color_info = entry['color_info']
            band_type = entry['band_type_var'].get().lower()
            color_format = entry['color_format_var'].get().lower()
            start_color_preview = entry['start_color_preview']
            end_color_preview = entry.get('end_color_preview')  # Use .get() in case it's None
            if value_entry.get().lstrip('-').replace('.', '', 1).isdigit():
                value = float(value_entry.get())
                start_color = start_color_preview.color_value
                start_alpha = getattr(start_color_preview, 'alpha_value', 255)
                end_color = None
                end_alpha = 255
                if band_type == 'gradient' and end_color_preview:
                    end_color = end_color_preview.color_value
                    end_alpha = getattr(end_color_preview, 'alpha_value', 255)
                entries.append({
                    'value': value,
                    'color_info': {
                        'type': band_type,
                        'format': color_format,
                        'start_color': start_color,
                        'start_alpha': start_alpha,
                        'end_color': end_color,
                        'end_alpha': end_alpha
                    }
                })

        if len(entries) > 1:
            # Sort entries by value
            entries.sort(key=lambda x: x['value'])
            values = [e['value'] for e in entries]
            min_val, max_val = min(values), max(values)
            if max_val - min_val == 0:
                color_width = width
            else:
                color_width = width / (max_val - min_val)

            # Draw the color bar
            for i in range(len(entries)):
                x0 = margin + (entries[i]['value'] - min_val) * color_width
                x1 = margin + (entries[i + 1]['value'] - min_val) * color_width if i + 1 < len(entries) else margin + width
                color_info = entries[i]['color_info']

                if color_info['type'] == 'gradient' and color_info['end_color']:
                    # Draw gradient between start_color and end_color
                    steps = int(x1 - x0) if x1 - x0 > 0 else 1
                    for j in range(int(steps)):
                        ratio = j / steps
                        start_rgb = self.hex_to_rgb(color_info['start_color'])
                        end_rgb = self.hex_to_rgb(color_info['end_color'])
                        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
                        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
                        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
                        color = f'#{r:02x}{g:02x}{b:02x}'
                        self.preview_canvas.create_line(x0 + j, 0, x0 + j, 40, fill=color)
                else:
                    # Draw solid color
                    fill_color = color_info['start_color']
                    self.preview_canvas.create_rectangle(x0, 0, x1, 40, fill=fill_color, outline="")

            # Draw tick marks and labels
            step_value = self.step_entry.get()
            try:
                step = float(step_value)
            except ValueError:
                step = (max_val - min_val) / 5  # Default to dividing into 5 steps if Step is invalid

            units = self.units_entry.get().strip()
            if not units:
                units = ''  # Default to empty string if units are not provided

            # Determine the range and tick positions
            tick_values = []
            current_tick = min_val
            while current_tick <= max_val:
                tick_values.append(current_tick)
                current_tick += step
            if tick_values[-1] < max_val:
                tick_values.append(max_val)

            for tick_value in tick_values:
                x = margin + (tick_value - min_val) / (max_val - min_val) * width
                self.preview_canvas.create_line(x, 40, x, 45, fill='black')
                label = f"{tick_value} {units}"
                self.preview_canvas.create_text(x, 55, text=label, anchor='n', font=('Arial', 8))

        # Optional: Display RF Color in Preview Canvas (e.g., as a separate indicator)
            rf_color = self.rf_color_preview['background']
            self.preview_canvas.create_rectangle(margin, 50, margin + 20, 60, fill=rf_color, outline="black")
            self.preview_canvas.create_text(margin + 30, 55, text="RF Color", anchor='w', font=('Arial', 8))

    def open_color_table(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Color Table Files", "*.txt *.pal *.pal3 *.pal3.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()

                # Clear existing color entries
                for entry in self.color_entries:
                    entry['frame'].destroy()
                self.color_entries.clear()

                # Reset RF color to default
                self.rf_color_preview.config(background="#FFFFFF")

                # Remove comments and empty lines
                lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith((';', '#', '//'))]

                # Check for ColorTable block
                if lines and 'colortable' in lines[0].lower():
                    self.parse_colortable_block(lines)
                else:
                    # Legacy parsing for older formats
                    self.parse_legacy_format(lines)

                messagebox.showinfo("Color Table Loaded", "Color table loaded successfully.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load color table: {e}")

    def parse_colortable_block(self, lines):
        # Join lines to handle multi-line definitions
        content = '\n'.join(lines)
        # Extract the content inside the ColorTable { ... }
        match = re.search(r'colortable\s*\{(.*)\}', content, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid ColorTable block.")
        block_content = match.group(1)

        # Parse block content line by line
        for line in block_content.split('\n'):
            line = line.strip()
            if not line or line.startswith((';', '#', '//')):
                continue  # Skip comments and empty lines

            if '=' in line:
                key, rest = line.split('=', 1)
                key = key.strip().lower()
                rest = rest.strip().strip('"').strip("'")
                if key == 'category':
                    self.product_entry.delete(0, tk.END)
                    self.product_entry.insert(0, rest)
                elif key == 'units':
                    self.units_entry.delete(0, tk.END)
                    self.units_entry.insert(0, rest)
                elif key == 'scale':
                    self.scale_entry.delete(0, tk.END)
                    self.scale_entry.insert(0, rest)
                elif key == 'offset':
                    self.offset_entry.delete(0, tk.END)
                    self.offset_entry.insert(0, rest)
                elif key == 'step':
                    self.step_entry.delete(0, tk.END)
                    self.step_entry.insert(0, rest)
                elif key.startswith('color['):
                    # Extract the value inside the brackets
                    value_match = re.match(r'color\[(.*?)\]', key, re.IGNORECASE)
                    if value_match:
                        value = value_match.group(1)
                        color_band = self.parse_color_band(rest)
                        self.create_color_entry(value=value, color_band=color_band)
                elif key == 'rf':
                    # Handle RF Field
                    rgb = rest.split()
                    if len(rgb) == 3:
                        try:
                            r, g, b = map(int, rgb)
                            # Validate RGB values
                            if all(0 <= val <= 255 for val in (r, g, b)):
                                hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                                self.rf_color_preview.config(background=hex_color)
                            else:
                                raise ValueError("RGB values must be between 0 and 255.")
                        except ValueError as ve:
                            print(f"Error parsing RF line: {ve}")
                # Additional keys like Decimals, ND, RF, Label can be added here if needed

    def parse_color_band(self, rest):
        rest = rest.strip()
        # Handle different color band definitions
        if rest.lower().startswith('rgb('):
            # SingleColor
            color = self.parse_single_color(rest)
            return {'type': 'single', 'start_color': color}
        elif rest.lower().startswith('solid('):
            # Solid color band
            match = re.match(r'solid\(\s*(.*?)\s*\)', rest, re.IGNORECASE)
            if match:
                color_str = match.group(1)
                color = self.parse_single_color(color_str)
                return {'type': 'solid', 'start_color': color}
        elif rest.lower().startswith('gradient('):
            # Gradient color band
            match = re.match(r'gradient\(\s*(.*?),\s*(.*?)\s*\)', rest, re.IGNORECASE)
            if match:
                color1_str = match.group(1)
                color2_str = match.group(2)
                color1 = self.parse_single_color(color1_str)
                color2 = self.parse_single_color(color2_str)
                return {'type': 'gradient', 'start_color': color1, 'end_color': color2}
        else:
            raise ValueError(f"Unknown color band definition: {rest}")

    def parse_single_color(self, color_str):
        color_str = color_str.strip()
        if color_str.lower().startswith('rgb('):
            match = re.match(r'rgb\(\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\s*\)', color_str, re.IGNORECASE)
            if match:
                r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
                # Optionally handle alpha channel
                return "#{:02x}{:02x}{:02x}".format(r, g, b)
        elif color_str.lower().startswith('hsluv('):
            # Parse HSLuv colors if needed
            pass  # For simplicity, we skip HSLuv in this example
        raise ValueError(f"Unknown color format: {color_str}")

    def parse_legacy_format(self, lines):
        for line in lines:
            if ':' in line:
                key, rest = line.split(':', 1)
                key = key.strip().lower()
                rest = rest.strip()

                if key == 'product':
                    # Set product
                    self.product_entry.delete(0, tk.END)
                    self.product_entry.insert(0, rest)
                elif key == 'units':
                    # Set units
                    self.units_entry.delete(0, tk.END)
                    self.units_entry.insert(0, rest)
                elif key == 'scale':
                    # Set scale
                    self.scale_entry.delete(0, tk.END)
                    self.scale_entry.insert(0, rest)
                elif key == 'offset':
                    # Set offset
                    self.offset_entry.delete(0, tk.END)
                    self.offset_entry.insert(0, rest)
                elif key == 'step':
                    # Set step
                    self.step_entry.delete(0, tk.END)
                    self.step_entry.insert(0, rest)
                elif key in ('solidcolor', 'solidcolor4'):
                    # Handle SolidColor and SolidColor4
                    parts = rest.split()
                    value_num = parts[0]

                    try:
                        if key == 'solidcolor':
                            # SolidColor: value R G B
                            if len(parts) != 4:
                                raise ValueError(f"Invalid SolidColor format: {rest}")
                            r, g, b = map(int, parts[1:4])
                            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                            color_band = {
                                'type': 'solid',
                                'start_color': hex_color,
                                'format': 'rgb'
                            }
                        elif key == 'solidcolor4':
                            # SolidColor4: value R G B A
                            if len(parts) != 5:
                                raise ValueError(f"Invalid SolidColor4 format: {rest}")
                            r, g, b, a = map(int, parts[1:5])
                            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                            color_band = {
                                'type': 'solid',
                                'start_color': hex_color,
                                'start_alpha': a,
                                'format': 'rgba'
                            }
                        else:
                            continue  # Skip unknown keys

                        self.create_color_entry(value=value_num, color_band=color_band)
                    except ValueError as e:
                        print(f"Error parsing line '{line}': {e}")
                        continue
                elif key in ('color', 'color4'):
                    parts = rest.split()
                    value_num = parts[0]

                    # Initialize default alpha values
                    alpha1 = 255
                    alpha2 = 255

                    if len(parts) == 7:
                        # Gradient without alpha values
                        rgb1 = parts[1:4]
                        rgb2 = parts[4:7]
                    elif len(parts) == 9 and key == 'color4':
                        # Gradient with alpha values
                        rgb1 = parts[1:4]
                        rgb2 = parts[4:7]
                        alpha1 = int(parts[7])
                        alpha2 = int(parts[8])
                    elif len(parts) == 4:
                        # Single color without alpha
                        rgb1 = parts[1:4]
                        rgb2 = None
                    elif len(parts) == 5 and key == 'color4':
                        # Single color with alpha
                        rgb1 = parts[1:4]
                        rgb2 = None
                        alpha1 = int(parts[4])
                    else:
                        continue  # Skip invalid entries

                    try:
                        rgb1_ints = list(map(int, rgb1))
                        hex_color1 = "#{:02x}{:02x}{:02x}".format(*rgb1_ints)
                        if rgb2:
                            rgb2_ints = list(map(int, rgb2))
                            hex_color2 = "#{:02x}{:02x}{:02x}".format(*rgb2_ints)
                            # Create color_band for gradient
                            color_band = {
                                'type': 'gradient',
                                'start_color': hex_color1,
                                'end_color': hex_color2,
                                'start_alpha': alpha1,
                                'end_alpha': alpha2,
                                'format': 'rgba' if alpha1 != 255 or alpha2 != 255 else 'rgb'
                            }
                        else:
                            # Create color_band for single color
                            color_band = {
                                'type': 'single',
                                'start_color': hex_color1,
                                'start_alpha': alpha1,
                                'format': 'rgba' if alpha1 != 255 else 'rgb'
                            }
                        self.create_color_entry(value=value_num, color_band=color_band)
                    except ValueError as e:
                        print(f"Error parsing line '{line}': {e}")
                        continue
                elif key == 'rf':
                    # Handle RF Field in Legacy Format
                    rgb = rest.split()
                    if len(rgb) == 3:
                        try:
                            r, g, b = map(int, rgb)
                            # Validate RGB values
                            if all(0 <= val <= 255 for val in (r, g, b)):
                                hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
                                self.rf_color_preview.config(background=hex_color)
                            else:
                                raise ValueError("RGB values must be between 0 and 255.")
                        except ValueError as ve:
                            print(f"Error parsing RF line: {ve}")
                else:
                    continue
            else:
                continue

    def save_color_table(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("PAL Files", "*.pal"), ("PAL3 Files", "*.pal3"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(f"Product: {self.product_entry.get()}\n")
                    file.write(f"Units: {self.units_entry.get()}\n")
                    
                    # Check if Scale field is not empty before writing
                    scale_value = self.scale_entry.get()
                    if scale_value.strip():
                        file.write(f"Scale: {scale_value}\n")
                    
                    # Check if Offset field is not empty before writing
                    offset_value = self.offset_entry.get()
                    if offset_value.strip():
                        file.write(f"Offset: {offset_value}\n")
                    
                    # Check if Step field is not empty before writing
                    step_value = self.step_entry.get()
                    if step_value.strip():
                        file.write(f"Step: {step_value}\n")
                    
                    file.write("\n")

                    entries = []
                    for entry in self.color_entries:
                        value_entry = entry['value_entry']
                        color_info = entry['color_info']
                        band_type = entry['band_type_var'].get().lower()
                        color_format = entry['color_format_var'].get().lower()
                        if (value_entry.get().lstrip('-').replace('.', '', 1).isdigit()):
                            value = float(value_entry.get())
                            entries.append({
                                'value': value,
                                'color_info': color_info,
                                'band_type': band_type,
                                'color_format': color_format
                            })

                    # Sort entries by value in descending order
                    entries.sort(key=lambda x: x['value'], reverse=True)

                    for i, entry in enumerate(entries):
                        value = entry['value']
                        color_info = entry['color_info']
                        band_type = entry['band_type']
                        color_format = entry['color_format']

                        # Prepare RGB(A) strings
                        start_rgb = self.rgb_list_from_hex(
                            color_info['start_color'], color_info.get('start_alpha', 255)
                        )
                        end_rgb = None
                        if color_info['type'] == 'gradient' and color_info['end_color']:
                            end_rgb = self.rgb_list_from_hex(
                                color_info['end_color'], color_info.get('end_alpha', 255)
                            )

                        # Determine the statement type
                        if band_type == 'solid':
                            if color_format == 'rgba':
                                # SolidColor4
                                rgb_str = ' '.join(map(str, start_rgb))
                                file.write(f"SolidColor4: {value} {rgb_str}\n")
                            else:
                                # SolidColor
                                rgb_str = ' '.join(map(str, start_rgb[:3]))
                                file.write(f"SolidColor: {value} {rgb_str}\n")
                        elif band_type == 'gradient':
                            if color_format == 'rgba':
                                # Color4 with RGBA2
                                start_rgb_str = ' '.join(map(str, start_rgb))
                                end_rgb_str = ' '.join(map(str, end_rgb))
                                file.write(f"Color4: {value} {start_rgb_str} {end_rgb_str}\n")
                            else:
                                # Color with RGB2
                                start_rgb_str = ' '.join(map(str, start_rgb[:3]))
                                end_rgb_str = ' '.join(map(str, end_rgb[:3]))
                                file.write(f"Color: {value} {start_rgb_str} {end_rgb_str}\n")
                        else:
                            if color_format == 'rgba':
                                # Color4 without RGBA2
                                rgb_str = ' '.join(map(str, start_rgb))
                                file.write(f"Color4: {value} {rgb_str}\n")
                            else:
                                # Color without RGB2
                                rgb_str = ' '.join(map(str, start_rgb[:3]))
                                file.write(f"Color: {value} {rgb_str}\n")

                    # Write RF Line at the End
                    rf_hex = self.rf_color_preview['background']
                    rf_rgb = self.hex_to_rgb(rf_hex)
                    file.write(f"\nRF: {rf_rgb[0]} {rf_rgb[1]} {rf_rgb[2]}\n")

                messagebox.showinfo("Save Successful", "Color table saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save color table: {e}")

    def hex_to_rgb(self, hex_color, alpha=255):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return rgb + (alpha,)

    def rgb_list_from_hex(self, hex_color, alpha=255):
        rgb = self.hex_to_rgb(hex_color, alpha)
        return list(rgb)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorTableApp(root)
    root.mainloop()
