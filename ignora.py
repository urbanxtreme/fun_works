import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font
import os
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
from collections import deque
import numpy as np
import uuid
import copy

class Layer:
    def __init__(self, image, name="Layer", visible=True):
        self.image = image
        self.name = name
        self.visible = visible
        self.id = str(uuid.uuid4())

class ImageEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ignora Pro - Image Editor v2.1")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.layers = []
        self.current_layer = None
        self.original_image = None
        self.display_image = None
        self.image_path = None
        self.undo_stack = deque(maxlen=30)
        self.redo_stack = deque(maxlen=30)
        self.zoom_factor = 1.0
        self.drawing_mode = False
        self.text_mode = False
        self.draw_color = '#000000'
        self.brush_size = 5
        self.text_content = ""
        self.text_font = "Arial"
        self.text_size = 20
        self.last_x = None
        self.last_y = None
        
        # Create UI
        self.create_ui()
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_toolbar(main_frame)
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.create_left_panel(content_frame)
        self.create_canvas_area(content_frame)
        self.create_right_panel(content_frame)
        self.create_status_bar(main_frame)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_image())
        self.root.bind('<Control-s>', lambda e: self.save_image())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-t>', lambda e: self.toggle_text_mode())
        
    def create_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg='#34495e', height=60)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # File operations
        file_frame = tk.Frame(toolbar, bg='#34495e')
        file_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.create_button(file_frame, "📁 New", self.create_new_image, "#3498db")
        self.create_button(file_frame, "📂 Open", self.open_image, "#3498db")
        self.create_button(file_frame, "💾 Save", self.save_image, "#27ae60")
        self.create_button(file_frame, "📤 Export", self.export_image, "#27ae60")
        
        # Edit operations
        edit_frame = tk.Frame(toolbar, bg='#34495e')
        edit_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.create_button(edit_frame, "↶ Undo", self.undo, "#e67e22")
        self.create_button(edit_frame, "↷ Redo", self.redo, "#e67e22")
        
        # Tools
        tools_frame = tk.Frame(toolbar, bg='#34495e')
        tools_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.create_button(tools_frame, "✂️ Crop", self.crop_tool, "#9b59b6")
        self.create_button(tools_frame, "🔄 Rotate", self.rotate_tool, "#9b59b6")
        self.create_button(tools_frame, "🖌️ Draw", self.toggle_draw_mode, "#9b59b6")
        self.create_button(tools_frame, "🅰️ Text", self.toggle_text_mode, "#9b59b6")
        
        # Zoom controls
        zoom_frame = tk.Frame(toolbar, bg='#34495e')
        zoom_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.create_button(zoom_frame, "🔍+", self.zoom_in, "#9b59b6")
        self.create_button(zoom_frame, "🔍-", self.zoom_out, "#9b59b6")
        self.create_button(zoom_frame, "🔍 Fit", self.fit_to_window, "#9b59b6")
        
    def create_button(self, parent, text, command, color="#34495e"):
        btn = tk.Button(parent, text=text, command=command, 
                       bg=color, fg='white', font=('Arial', 10, 'bold'),
                       relief=tk.FLAT, padx=15, pady=5, cursor='hand2')
        btn.pack(side=tk.LEFT, padx=2)
        
        def on_enter(e): btn.configure(bg=self.lighten_color(color))
        def on_leave(e): btn.configure(bg=color)
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn
        
    def lighten_color(self, color):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
    def create_left_panel(self, parent):
        left_panel = tk.Frame(parent, bg='#34495e', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Tools section
        tools_frame = tk.LabelFrame(left_panel, text="🛠️ Tools", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_tool_button(tools_frame, "✂️ Crop", self.crop_tool)
        self.create_tool_button(tools_frame, "🔄 Rotate", self.rotate_tool)
        self.create_tool_button(tools_frame, "📏 Resize", self.resize_tool)
        self.create_tool_button(tools_frame, "🖌️ Draw", self.toggle_draw_mode)
        self.create_tool_button(tools_frame, "🅰️ Text", self.toggle_text_mode)
        self.create_tool_button(tools_frame, "🎨 Color Picker", self.choose_draw_color)
        
        # Filters section
        filters_frame = tk.LabelFrame(left_panel, text="🎭 Filters", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_tool_button(filters_frame, "⚫ Grayscale", self.apply_grayscale)
        self.create_tool_button(filters_frame, "📸 Sepia", self.apply_sepia)
        self.create_tool_button(filters_frame, "🔄 Invert", self.apply_invert)
        self.create_tool_button(filters_frame, "✨ Blur", self.apply_blur)
        self.create_tool_button(filters_frame, "🔍 Sharpen", self.apply_sharpen)
        self.create_tool_button(filters_frame, "🌟 Emboss", self.apply_emboss)
        self.create_tool_button(filters_frame, "🌙 Vignette", self.apply_vignette)
        self.create_tool_button(filters_frame, "📺 Noise", self.apply_noise)
        
        # Transform section
        transform_frame = tk.LabelFrame(left_panel, text="🔄 Transform", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        transform_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_tool_button(transform_frame, "↔️ Flip H", self.flip_horizontal)
        self.create_tool_button(transform_frame, "↕️ Flip V", self.flip_vertical)
        self.create_tool_button(transform_frame, "🔄 Rotate 90°", self.rotate_90)
        self.create_tool_button(transform_frame, "🔄 Rotate 180°", self.rotate_180)
        
    def create_tool_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                       bg='#3498db', fg='white', font=('Arial', 10),
                       relief=tk.FLAT, pady=8, cursor='hand2')
        btn.pack(fill=tk.X, padx=10, pady=2)
        
        def on_enter(e): btn.configure(bg='#2980b9')
        def on_leave(e): btn.configure(bg='#3498db')
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn
        
    def create_canvas_area(self, parent):
        canvas_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', cursor='crosshair')
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.handle_canvas_click)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.end_draw)
        
    def create_right_panel(self, parent):
        right_panel = tk.Frame(parent, bg='#34495e', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Layers section
        layers_frame = tk.LabelFrame(right_panel, text="📚 Layers", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        layers_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.layers_listbox = tk.Listbox(layers_frame, height=6, bg='#2c3e50', fg='white', selectbackground='#3498db')
        self.layers_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.layers_listbox.bind('<<ListboxSelect>>', self.select_layer)
        
        layer_buttons = tk.Frame(layers_frame, bg='#34495e')
        layer_buttons.pack(fill=tk.X, padx=5, pady=5)
        self.create_button(layer_buttons, "➕", self.add_layer, "#27ae60")
        self.create_button(layer_buttons, "➖", self.delete_layer, "#e74c3c")
        self.create_button(layer_buttons, "👁", self.toggle_layer_visibility, "#f39c12")
        
        # Properties section
        props_frame = tk.LabelFrame(right_panel, text="⚙️ Properties", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        props_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.size_label = tk.Label(props_frame, text="Size: No image", bg='#34495e', fg='white', font=('Arial', 9))
        self.size_label.pack(anchor=tk.W, padx=5)
        self.format_label = tk.Label(props_frame, text="Format: -", bg='#34495e', fg='white', font=('Arial', 9))
        self.format_label.pack(anchor=tk.W, padx=5)
        
        # Adjustments section
        adj_frame = tk.LabelFrame(right_panel, text="🎛️ Adjustments", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        adj_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_slider(adj_frame, "Brightness", -100, 100, 0, self.adjust_brightness)
        self.create_slider(adj_frame, "Contrast", -100, 100, 0, self.adjust_contrast)
        self.create_slider(adj_frame, "Saturation", -100, 100, 0, self.adjust_saturation)
        
        # Text tools
        text_frame = tk.LabelFrame(right_panel, text="🅰️ Text", fg='white', bg='#34495e', font=('Arial', 12, 'bold'))
        text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(text_frame, text="Text:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=5)
        self.text_entry = tk.Entry(text_frame)
        self.text_entry.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(text_frame, text="Font:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=5)
        self.font_combo = ttk.Combobox(text_frame, values=font.families(), state='readonly')
        self.font_combo.set('Arial')
        self.font_combo.pack(fill=tk.X, padx=5, pady=2)
        self.font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_text_font())
        
        tk.Label(text_frame, text="Size:", bg='#34495e', fg='white').pack(anchor=tk.W, padx=5)
        self.text_size_scale = tk.Scale(text_frame, from_=10, to=100, orient=tk.HORIZONTAL,
                                       bg='#34495e', fg='white', command=self.update_text_size)
        self.text_size_scale.set(20)
        self.text_size_scale.pack(fill=tk.X, padx=5, pady=2)
        
    def create_slider(self, parent, label, min_val, max_val, default, command):
        frame = tk.Frame(parent, bg='#34495e')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame, text=f"{label}:", bg='#34495e', fg='white').pack(anchor=tk.W)
        slider = tk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                         bg='#34495e', fg='white', highlightthickness=0,
                         command=lambda val: command(int(val)))
        slider.set(default)
        slider.pack(fill=tk.X)
        return slider
        
    def create_status_bar(self, parent):
        self.status_bar = tk.Label(parent, text="Ready", relief=tk.SUNKEN, 
                                  bg='#ecf0f1', fg='#2c3e50', anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))
        
    def add_layer(self):
        if self.current_layer:
            new_image = Image.new('RGBA', self.current_layer.image.size, (0, 0, 0, 0))
            new_layer = Layer(new_image, f"Layer {len(self.layers) + 1}")
            self.layers.append(new_layer)
            self.current_layer = new_layer
            self.update_layers_list()
            self.save_state()
            self.display_image_on_canvas()
        
    def delete_layer(self):
        if len(self.layers) > 1:
            self.layers.remove(self.current_layer)
            self.current_layer = self.layers[-1]
            self.update_layers_list()
            self.save_state()
            self.display_image_on_canvas()
            
    def toggle_layer_visibility(self):
        if self.current_layer:
            self.current_layer.visible = not self.current_layer.visible
            self.update_layers_list()
            self.display_image_on_canvas()
            
    def select_layer(self, event):
        selection = self.layers_listbox.curselection()
        if selection:
            self.current_layer = self.layers[selection[0]]
            self.update_status(f"Selected layer: {self.current_layer.name}")
            
    def update_layers_list(self):
        self.layers_listbox.delete(0, tk.END)
        for layer in self.layers:
            status = "👁" if layer.visible else "🚫"
            self.layers_listbox.insert(tk.END, f"{status} {layer.name}")
            
    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                image = Image.open(file_path).convert('RGBA')
                self.original_image = image.copy()
                self.layers = [Layer(image, "Background")]
                self.current_layer = self.layers[0]
                self.image_path = file_path
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.save_state()
                self.update_layers_list()
                self.display_image_on_canvas()
                self.update_image_info()
                self.update_status(f"Opened: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")
                
    def save_image(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image to save!")
            return
            
        if not self.image_path:
            self.save_as_image()
            return
            
        try:
            self.get_composite_image().save(self.image_path)
            self.update_status("Image saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image: {str(e)}")
            
    def save_as_image(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.get_composite_image().save(file_path)
                self.image_path = file_path
                self.update_status(f"Saved as: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {str(e)}")
                
    def export_image(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image to export!")
            return
            
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Image")
        export_window.geometry("400x300")
        export_window.configure(bg='#34495e')
        
        tk.Label(export_window, text="Export Settings", bg='#34495e', fg='white', 
                font=('Arial', 14, 'bold')).pack(pady=20)
                
        format_var = tk.StringVar(value="PNG")
        quality_var = tk.IntVar(value=95)
        
        format_frame = tk.Frame(export_window, bg='#34495e')
        format_frame.pack(pady=10)
        tk.Label(format_frame, text="Format:", bg='#34495e', fg='white').pack(side=tk.LEFT)
        ttk.Combobox(format_frame, values=["PNG", "JPEG", "BMP"], textvariable=format_var,
                    state='readonly').pack(side=tk.LEFT, padx=5)
        
        quality_frame = tk.Frame(export_window, bg='#34495e')
        quality_frame.pack(pady=10)
        tk.Label(quality_frame, text="Quality (JPEG):", bg='#34495e', fg='white').pack(anchor=tk.W)
        tk.Scale(quality_frame, from_=50, to=100, orient=tk.HORIZONTAL, variable=quality_var,
                bg='#34495e', fg='white').pack(fill=tk.X, padx=5)
        
        def do_export():
            file_path = filedialog.asksaveasfilename(
                title="Export Image",
                defaultextension=f".{format_var.get().lower()}",
                filetypes=[(f"{format_var.get()} files", f"*.{format_var.get().lower()}")]
            )
            if file_path:
                try:
                    img = self.get_composite_image()
                    if format_var.get() == "JPEG":
                        img = img.convert('RGB')
                        img.save(file_path, quality=quality_var.get())
                    else:
                        img.save(file_path)
                    self.update_status(f"Exported to: {os.path.basename(file_path)}")
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not export image: {str(e)}")
                    
        button_frame = tk.Frame(export_window, bg='#34495e')
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Export", command=do_export,
                 bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=export_window.destroy,
                 bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
    def get_composite_image(self):
        if not self.layers:
            return None
        composite = Image.new('RGBA', self.layers[0].image.size, (0, 0, 0, 0))
        for layer in self.layers:
            if layer.visible:
                composite = Image.alpha_composite(composite, layer.image)
        return composite.convert('RGB')
        
    def display_image_on_canvas(self):
        if not self.layers:
            return
            
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_image_on_canvas)
            return
            
        composite = self.get_composite_image()
        if not composite:
            return
            
        img_width, img_height = composite.size
        scale_x = (canvas_width - 20) / img_width
        scale_y = (canvas_height - 20) / img_height
        scale = min(scale_x, scale_y, 1.0) * self.zoom_factor
        
        new_width = max(1, int(img_width * scale))
        new_height = max(1, int(img_height * scale))
        
        try:
            self.display_image = composite.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.display_image)
            
            self.canvas.delete("all")
            x = canvas_width // 2
            y = canvas_height // 2
            
            self.canvas.create_image(x, y, image=self.photo, anchor=tk.CENTER)
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
        except Exception as e:
            self.update_status(f"Error displaying image: {e}")
        
    def update_image_info(self):
        if self.current_layer:
            width, height = self.current_layer.image.size
            self.size_label.config(text=f"Size: {width} × {height}")
            self.format_label.config(text=f"Format: {self.current_layer.image.format or 'RGBA'}")
        else:
            self.size_label.config(text="Size: No image")
            self.format_label.config(text="Format: -")
            
    def save_state(self):
        if self.layers:
            # Deep copy layers
            state = [Layer(copy.deepcopy(layer.image), layer.name, layer.visible) for layer in self.layers]
            self.undo_stack.append(state)
            self.redo_stack.clear()
            
    def undo(self):
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.layers)
            self.layers = self.undo_stack.pop()
            self.current_layer = self.layers[-1]
            self.update_layers_list()
            self.display_image_on_canvas()
            self.update_status("Undo successful")
            
    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.layers)
            self.layers = self.redo_stack.pop()
            self.current_layer = self.layers[-1]
            self.update_layers_list()
            self.display_image_on_canvas()
            self.update_status("Redo successful")
            
    def zoom_in(self):
        self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        self.display_image_on_canvas()
        
    def zoom_out(self):
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.1)
        self.display_image_on_canvas()
        
    def fit_to_window(self):
        self.zoom_factor = 1.0
        self.display_image_on_canvas()
        
    # Drawing functions
    def toggle_draw_mode(self):
        self.drawing_mode = not self.drawing_mode
        self.text_mode = False
        cursor = 'pencil' if self.drawing_mode else 'crosshair'
        self.canvas.configure(cursor=cursor)
        status = "Drawing mode ON" if self.drawing_mode else "Drawing mode OFF"
        self.update_status(status)
        
    def toggle_text_mode(self):
        self.text_mode = not self.text_mode
        self.drawing_mode = False
        cursor = 'ibeam' if self.text_mode else 'crosshair'
        self.canvas.configure(cursor=cursor)
        status = "Text mode ON" if self.text_mode else "Text mode OFF"
        self.update_status(status)
        
    def choose_draw_color(self):
        color = colorchooser.askcolor(color=self.draw_color)[1]
        if color:
            self.draw_color = color
            
    def update_brush_size(self, value):
        self.brush_size = int(value)
        
    def update_text_font(self):
        self.text_font = self.font_combo.get()
        
    def update_text_size(self, value):
        self.text_size = int(value)
        
    def handle_canvas_click(self, event):
        if self.text_mode and self.current_layer:
            self.add_text(event)
        elif self.drawing_mode and self.current_layer:
            self.start_draw(event)
            
    def start_draw(self, event):
        if self.drawing_mode and self.current_layer:
            self.last_x = event.x
            self.last_y = event.y
            
    def draw(self, event):
        if self.drawing_mode and self.current_layer and self.last_x and self.last_y:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.current_layer.image.size
            
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y) * self.zoom_factor
            
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            img_x = int((event.x - center_x) / scale + img_width // 2)
            img_y = int((event.y - center_y) / scale + img_height // 2)
            last_img_x = int((self.last_x - center_x) / scale + img_width // 2)
            last_img_y = int((self.last_y - center_y) / scale + img_height // 2)
            
            draw = ImageDraw.Draw(self.current_layer.image)
            draw.line([last_img_x, last_img_y, img_x, img_y], 
                     fill=self.draw_color, width=self.brush_size)
            
            self.display_image_on_canvas()
            self.last_x = event.x
            self.last_y = event.y
            
    def end_draw(self, event):
        if self.drawing_mode:
            self.save_state()
            self.last_x = None
            self.last_y = None
            
    def add_text(self, event):
        if self.text_mode and self.current_layer:
            text = self.text_entry.get()
            if not text:
                messagebox.showwarning("Warning", "Please enter text to add!")
                return
                
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.current_layer.image.size
            
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y) * self.zoom_factor
            
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            img_x = int((event.x - center_x) / scale + img_width // 2)
            img_y = int((event.y - center_y) / scale + img_height // 2)
            
            try:
                font = ImageFont.truetype(self.text_font, self.text_size)
                draw = ImageDraw.Draw(self.current_layer.image)
                draw.text((img_x, img_y), text, fill=self.draw_color, font=font)
                
                self.save_state()
                self.display_image_on_canvas()
                self.update_status("Text added successfully")
                self.text_mode = False
                self.canvas.configure(cursor='crosshair')
            except Exception as e:
                messagebox.showerror("Error", f"Could not add text: {str(e)}")
                
    # Filter functions
    def apply_grayscale(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.convert('L').convert('RGBA')
            self.display_image_on_canvas()
            self.update_status("Grayscale filter applied")
            
    def apply_sepia(self):
        if self.current_layer:
            self.save_state()
            img_array = np.array(self.current_layer.image.convert('RGB'))
            sepia_filter = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_img = img_array.dot(sepia_filter.T)
            sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
            self.current_layer.image = Image.fromarray(sepia_img).convert('RGBA')
            self.display_image_on_canvas()
            self.update_status("Sepia filter applied")
            
    def apply_invert(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = ImageOps.invert(self.current_layer.image.convert('RGB')).convert('RGBA')
            self.display_image_on_canvas()
            self.update_status("Invert filter applied")
            
    def apply_blur(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.filter(ImageFilter.GaussianBlur(2))
            self.display_image_on_canvas()
            self.update_status("Blur filter applied")
            
    def apply_sharpen(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.filter(ImageFilter.SHARPEN)
            self.display_image_on_canvas()
            self.update_status("Sharpen filter applied")
            
    def apply_emboss(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.filter(ImageFilter.EMBOSS).convert('RGBA')
            self.display_image_on_canvas()
            self.update_status("Emboss filter applied")
            
    def apply_vignette(self):
        if self.current_layer:
            self.save_state()
            img = self.current_layer.image.convert('RGBA')
            width, height = img.size
            
            # Create vignette mask
            mask = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask)
            for x in range(width):
                for y in range(height):
                    dx = x - width/2
                    dy = y - height/2
                    distance = np.sqrt(dx*dx + dy*dy)
                    intensity = 255 * (1 - distance/(max(width, height)/2))**2
                    draw.point((x, y), fill=int(intensity))
            
            mask = mask.filter(ImageFilter.GaussianBlur(50))
            img.putalpha(mask)
            self.current_layer.image = img
            self.display_image_on_canvas()
            self.update_status("Vignette effect applied")
            
    def apply_noise(self):
        if self.current_layer:
            self.save_state()
            img_array = np.array(self.current_layer.image.convert('RGB'))
            noise = np.random.normal(0, 20, img_array.shape).astype(np.uint8)
            noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            self.current_layer.image = Image.fromarray(noisy_img).convert('RGBA')
            self.display_image_on_canvas()
            self.update_status("Noise effect applied")
            
    # Transform functions
    def flip_horizontal(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            self.display_image_on_canvas()
            self.update_status("Flipped horizontally")
            
    def flip_vertical(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            self.display_image_on_canvas()
            self.update_status("Flipped vertically")
            
    def rotate_90(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.transpose(Image.Transpose.ROTATE_90)
            self.display_image_on_canvas()
            self.update_image_info()
            self.update_status("Rotated 90°")
            
    def rotate_180(self):
        if self.current_layer:
            self.save_state()
            self.current_layer.image = self.current_layer.image.transpose(Image.Transpose.ROTATE_180)
            self.display_image_on_canvas()
            self.update_image_info()
            self.update_status("Rotated 180°")
            
    # Tool functions
    def crop_tool(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        self.update_status("Crop tool: Click and drag to select area, then press SPACE to crop")
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_rect = None
        self.crop_active = True
        
        def start_crop(event):
            if not self.crop_active:
                return
            self.crop_start_x = self.canvas.canvasx(event.x)
            self.crop_start_y = self.canvas.canvasy(event.y)
            
        def draw_crop_rect(event):
            if not self.crop_active or self.crop_start_x is None:
                return
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
            
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            self.crop_rect = self.canvas.create_rectangle(
                self.crop_start_x, self.crop_start_y, current_x, current_y,
                outline='red', width=2, dash=(5, 5))
                
        def perform_crop(event):
            if not self.crop_active or not self.crop_rect:
                return
                
            try:
                coords = self.canvas.coords(self.crop_rect)
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                img_width, img_height = self.current_layer.image.size
                
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y) * self.zoom_factor
                
                scaled_width = int(img_width * scale)
                scaled_height = int(img_height * scale)
                img_x = (canvas_width - scaled_width) // 2
                img_y = (canvas_height - scaled_height) // 2
                
                x1 = max(0, int((coords[0] - img_x) / scale))
                y1 = max(0, int((coords[1] - img_y) / scale))
                x2 = min(img_width, int((coords[2] - img_x) / scale))
                y2 = min(img_height, int((coords[3] - img_y) / scale))
                
                if x2 > x1 and y2 > y1:
                    self.save_state()
                    self.current_layer.image = self.current_layer.image.crop((x1, y1, x2, y2))
                    self.display_image_on_canvas()
                    self.update_image_info()
                    self.update_status("Image cropped successfully")
                else:
                    self.update_status("Invalid crop area")
                
                if self.crop_rect:
                    self.canvas.delete(self.crop_rect)
                    self.crop_rect = None
                self.crop_active = False
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not crop image: {str(e)}")
                self.crop_active = False
                
        def cancel_crop(event):
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
                self.crop_rect = None
            self.crop_active = False
            self.update_status("Crop cancelled")
            
        self.canvas.bind('<Button-1>', start_crop)
        self.canvas.bind('<B1-Motion>', draw_crop_rect)
        self.root.bind('<space>', perform_crop)
        self.root.bind('<Escape>', cancel_crop)
        self.root.focus_set()
        
    def rotate_tool(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        rotate_window = tk.Toplevel(self.root)
        rotate_window.title("Rotate Image")
        rotate_window.geometry("350x250")
        rotate_window.configure(bg='#34495e')
        
        title_label = tk.Label(rotate_window, text="Rotate Image", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        angle_frame = tk.Frame(rotate_window, bg='#34495e')
        angle_frame.pack(pady=20)
        
        tk.Label(angle_frame, text="Angle (degrees):", 
                bg='#34495e', fg='white', font=('Arial', 11)).pack()
        
        angle_var = tk.IntVar()
        angle_scale = tk.Scale(angle_frame, from_=-180, to=180, orient=tk.HORIZONTAL,
                              variable=angle_var, bg='#34495e', fg='white',
                              highlightthickness=0, length=250)
        angle_scale.pack(pady=10)
        
        angle_display = tk.Label(angle_frame, text="0°", 
                                bg='#34495e', fg='#3498db', font=('Arial', 12, 'bold'))
        angle_display.pack()
        
        def update_angle_display(val):
            angle_display.config(text=f"{val}°")
            
        angle_scale.config(command=update_angle_display)
        
        quick_frame = tk.Frame(rotate_window, bg='#34495e')
        quick_frame.pack(pady=10)
        
        tk.Label(quick_frame, text="Quick Rotate:", 
                bg='#34495e', fg='white', font=('Arial', 10)).pack()
        
        quick_buttons_frame = tk.Frame(quick_frame, bg='#34495e')
        quick_buttons_frame.pack(pady=5)
        
        def set_angle(angle):
            angle_scale.set(angle)
            
        tk.Button(quick_buttons_frame, text="90°", command=lambda: set_angle(90),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="180°", command=lambda: set_angle(180),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_buttons_frame, text="270°", command=lambda: set_angle(270),
                 bg='#3498db', fg='white', font=('Arial', 9), width=6).pack(side=tk.LEFT, padx=2)
        
        button_frame = tk.Frame(rotate_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def apply_rotation():
            angle = angle_var.get()
            if angle != 0:
                try:
                    self.save_state()
                    self.current_layer.image = self.current_layer.image.rotate(-angle, expand=True)
                    self.display_image_on_canvas()
                    self.update_image_info()
                    self.update_status(f"Rotated by {angle}°")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not rotate image: {str(e)}")
            rotate_window.destroy()
            
        tk.Button(button_frame, text="Apply", command=apply_rotation,
                 bg='#27ae60', fg='white', font=('Arial', 10), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=rotate_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10), padx=15).pack(side=tk.LEFT, padx=5)
                 
    def resize_tool(self):
        if not self.current_layer:
            messagebox.showwarning("Warning", "No image loaded!")
            return
            
        resize_window = tk.Toplevel(self.root)
        resize_window.title("Resize Image")
        resize_window.geometry("400x300")
        resize_window.configure(bg='#34495e')
        
        tk.Label(resize_window, text="Resize Image", bg='#34495e', fg='white', 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        size_frame = tk.Frame(resize_window, bg='#34495e')
        size_frame.pack(pady=10)
        
        width_var = tk.IntVar(value=self.current_layer.image.size[0])
        height_var = tk.IntVar(value=self.current_layer.image.size[1])
        aspect_ratio_var = tk.BooleanVar(value=True)
        
        tk.Label(size_frame, text="Width:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5)
        width_entry = tk.Entry(size_frame, textvariable=width_var, width=10)
        width_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(size_frame, text="Height:", bg='#34495e', fg='white').grid(row=1, column=0, padx=5)
        height_entry = tk.Entry(size_frame, textvariable=height_var, width=10)
        height_entry.grid(row=1, column=1, padx=5)
        
        original_ratio = self.current_layer.image.size[0] / self.current_layer.image.size[1]
        
        def update_height(*args):
            if aspect_ratio_var.get():
                try:
                    width = int(width_var.get())
                    height_var.set(int(width / original_ratio))
                except ValueError:
                    pass
                    
        def update_width(*args):
            if aspect_ratio_var.get():
                try:
                    height = int(height_var.get())
                    width_var.set(int(height * original_ratio))
                except ValueError:
                    pass
                    
        width_var.trace('w', update_height)
        height_var.trace('w', update_width)
        
        tk.Checkbutton(size_frame, text="Maintain Aspect Ratio", variable=aspect_ratio_var,
                      bg='#34495e', fg='white', selectcolor='#34495e').grid(row=2, column=0, columnspan=2, pady=5)
        
        button_frame = tk.Frame(resize_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def apply_resize():
            try:
                width = int(width_var.get())
                height = int(height_var.get())
                if width <= 0 or height <= 0:
                    raise ValueError("Invalid dimensions")
                    
                self.save_state()
                self.current_layer.image = self.current_layer.image.resize(
                    (width, height), Image.Resampling.LANCZOS)
                self.display_image_on_canvas()
                self.update_image_info()
                self.update_status(f"Resized to {width}×{height}")
                resize_window.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid dimensions: {str(e)}")
                
        tk.Button(button_frame, text="Apply", command=apply_resize,
                 bg='#27ae60', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=resize_window.destroy,
                 bg='#e74c3c', fg='white', padx=20).pack(side=tk.LEFT, padx=5)
        
    def create_new_image(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Image")
        new_window.geometry("300x250")
        new_window.configure(bg='#34495e')
        
        title_label = tk.Label(new_window, text="Create New Image", 
                              bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title_label.pack(pady=20)
        
        size_frame = tk.Frame(new_window, bg='#34495e')
        size_frame.pack(pady=20)
        
        tk.Label(size_frame, text="Width:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(size_frame, width=10)
        width_entry.insert(0, "800")
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(size_frame, text="Height:", bg='#34495e', fg='white').grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(size_frame, width=10)
        height_entry.insert(0, "600")
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        color_frame = tk.Frame(new_window, bg='#34495e')
        color_frame.pack(pady=10)
        
        tk.Label(color_frame, text="Background:", bg='#34495e', fg='white').pack()
        color_var = tk.StringVar(value="white")
        color_options = [("White", "white"), ("Black", "black"), ("Transparent", "transparent")]
        
        for text, value in color_options:
            tk.Radiobutton(color_frame, text=text, variable=color_var, value=value,
                          bg='#34495e', fg='white', selectcolor='#34495e').pack(anchor=tk.W)
        
        button_frame = tk.Frame(new_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def create_image():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                color = color_var.get()
                
                if width <= 0 or height <= 0:
                    messagebox.showerror("Error", "Width and height must be positive numbers!")
                    return
                    
                image = Image.new('RGBA', (width, height), 
                                 (255, 255, 255, 0) if color == "transparent" else color)
                
                self.original_image = image.copy()
                self.layers = [Layer(image, "Background")]
                self.current_layer = self.layers[0]
                self.image_path = None
                
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.save_state()
                self.update_layers_list()
                self.display_image_on_canvas()
                self.update_image_info()
                self.update_status(f"Created new {width}×{height} image")
                new_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for width and height!")
                
        tk.Button(button_frame, text="Create", command=create_image,
                 bg='#27ae60', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=new_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=5)
        
    def adjust_brightness(self, value):
        """Adjust image brightness"""
        if self.current_layer and value != 0:
            self.save_state()
            enhancer = ImageEnhance.Brightness(self.current_layer.image)
            factor = 1.0 + (value / 100.0)
            self.current_layer.image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            self.update_status("Brightness adjusted")
            
    def adjust_contrast(self, value):
        """Adjust image contrast"""
        if self.current_layer and value != 0:
            self.save_state()
            enhancer = ImageEnhance.Contrast(self.current_layer.image)
            factor = 1.0 + (value / 100.0)
            self.current_layer.image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            self.update_status("Contrast adjusted")
            
    def adjust_saturation(self, value):
        """Adjust image saturation"""
        if self.current_layer and value != 0:
            self.save_state()
            enhancer = ImageEnhance.Color(self.current_layer.image)
            factor = 1.0 + (value / 100.0)
            self.current_layer.image = enhancer.enhance(factor)
            self.display_image_on_canvas()
            self.update_status("Saturation adjusted")
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New...", command=self.create_new_image, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_image)
        file_menu.add_command(label="Export...", command=self.export_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window, accelerator="Ctrl+0")
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Crop", command=self.crop_tool)
        tools_menu.add_command(label="Rotate", command=self.rotate_tool)
        tools_menu.add_command(label="Resize", command=self.resize_tool)
        tools_menu.add_command(label="Drawing Mode", command=self.toggle_draw_mode)
        tools_menu.add_command(label="Text Mode", command=self.toggle_text_mode, accelerator="Ctrl+T")
        
        filters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filters", menu=filters_menu)
        filters_menu.add_command(label="Grayscale", command=self.apply_grayscale)
        filters_menu.add_command(label="Sepia", command=self.apply_sepia)
        filters_menu.add_command(label="Invert", command=self.apply_invert)
        filters_menu.add_command(label="Blur", command=self.apply_blur)
        filters_menu.add_command(label="Sharpen", command=self.apply_sharpen)
        filters_menu.add_command(label="Emboss", command=self.apply_emboss)
        filters_menu.add_command(label="Vignette", command=self.apply_vignette)
        filters_menu.add_command(label="Noise", command=self.apply_noise)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        self.root.bind('<Control-n>', lambda e: self.create_new_image())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About Ignora Pro")
        about_window.geometry("350x350")
        about_window.configure(bg='#34495e')
        
        tk.Label(about_window, text="Ignora Pro", 
                bg='#34495e', fg='white', font=('Arial', 18, 'bold')).pack(pady=20)
        tk.Label(about_window, text="Version 2.1", 
                bg='#34495e', fg='#bdc3c7', font=('Arial', 12)).pack(pady=5)
        tk.Label(about_window, 
                text="Advanced image editor with layers support\nBuilt with Python and Tkinter",
                bg='#34495e', fg='white', font=('Arial', 11), justify=tk.CENTER).pack(pady=20)
        tk.Label(about_window, 
                text="Features:\n• Layers & non-destructive editing\n• Text overlay\n• Advanced filters\n• Resize & transform\n• Multiple export formats",
                bg='#34495e', fg='#bdc3c7', font=('Arial', 10), justify=tk.LEFT).pack(pady=20)
        tk.Button(about_window, text="Close", command=about_window.destroy,
                 bg='#3498db', fg='white', font=('Arial', 10), padx=20).pack(pady=20)
        
    def run(self):
        self.create_menu_bar()
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ImageEditor()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()