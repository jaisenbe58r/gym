import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, colorchooser
import cv2
import json
import numpy as np
from PIL import Image, ImageTk
import random


class VideoCalibrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Calibration App")

        self.video_file = None
        self.capture = None
        self.frame = None
        self.objects = []
        self.current_object = []
        self.max_points = 4  # Máximo número de puntos por objeto

        self.create_widgets()

    def create_widgets(self):
        self.load_video_button = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_video_button.pack(side=tk.TOP)

        self.save_coordinates_button = tk.Button(self.root, text="Save Coordinates", command=self.save_coordinates, state=tk.DISABLED)
        self.save_coordinates_button.pack(side=tk.TOP)

        self.load_coordinates_button = tk.Button(self.root, text="Load Coordinates", command=self.load_coordinates)
        self.load_coordinates_button.pack(side=tk.TOP)

        self.add_object_button = tk.Button(self.root, text="Add Object", command=self.add_object)
        self.add_object_button.pack(side=tk.TOP)

        self.delete_object_button = tk.Button(self.root, text="Delete Object", command=self.delete_object)
        self.delete_object_button.pack(side=tk.TOP)

        self.object_list = Listbox(self.root, height=10, width=40)
        self.object_list.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.object_scroll = Scrollbar(self.root, orient=tk.VERTICAL)
        self.object_scroll.config(command=self.object_list.yview)
        self.object_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.object_list.config(yscrollcommand=self.object_scroll.set)

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.draw_point)


    def load_video(self):
        self.video_file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        if not self.video_file:
            return
        self.capture = cv2.VideoCapture(self.video_file)
        success, self.frame = self.capture.read()
        if success:
            self.display_frame()
            self.save_coordinates_button.config(state=tk.NORMAL)

    def display_frame(self):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.original_frame = self.frame.copy()
        self.frame = Image.fromarray(self.frame)
        self.frame = self.frame.resize((self.frame.width // 2, self.frame.height // 2))  # Escalar a la mitad
        self.frame = ImageTk.PhotoImage(self.frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame)
        self.canvas.image = self.frame  # Evitar recolección de basura

    def draw_point(self, event):
        if len(self.current_object) < self.max_points:
            x, y = event.x, event.y
            self.current_object.append((x, y))
            color = self.get_random_color()  # Obtener color aleatorio
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color)
            if len(self.current_object) == self.max_points:
                self.objects.append(self.current_object)
                self.current_object = []  # Reiniciar para el siguiente objeto
                self.update_object_list()
                self.render_objects()

    def render_objects(self):
        self.canvas.delete("rendered_object")
        for idx, obj in enumerate(self.objects):
            color = self.get_object_color(obj)  # Obtener color del primer punto
            for i in range(self.max_points - 1):
                x1, y1 = obj[i]
                x2, y2 = obj[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2, tags="rendered_object")
            x1, y1 = obj[-1]  # Conectar el último punto al primer punto
            x2, y2 = obj[0]
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2, tags="rendered_object")
            # Calcular el centro del área del objeto
            center_x = sum(point[0] for point in obj) / self.max_points
            center_y = sum(point[1] for point in obj) / self.max_points
            # Dibujar el número del objeto en el centro del área
            self.canvas.create_text(center_x, center_y, text=str(idx + 1), fill=color, font=("Arial", 12), tags="rendered_object")

    def get_object_color(self, obj):
        try:
            # Obtener las coordenadas del primer punto del objeto
            x, y = obj[0]
            # Encontrar el objeto más cercano al primer punto del objeto
            closest_item = self.canvas.find_closest(x, y)[0]
            # Verificar el tipo de elemento y obtener el color apropiado
            item_type = self.canvas.type(closest_item)
            if item_type == "rectangle" or item_type == "polygon":
                # Si el elemento es un rectángulo o un polígono, obtener el color de relleno
                color = self.canvas.itemcget(closest_item, "fill")
            elif item_type == "line":
                # Si el elemento es una línea, obtener el color de la línea
                color = self.canvas.itemcget(closest_item, "fill")
            else:
                # Si el elemento es otro tipo, devolver un color predeterminado
                color = "black"
            return color
        except IndexError:
            # Manejar el caso en que no se pueda encontrar ningún objeto cerca del punto especificado
            return "black"  # Devolver un color predeterminado, por ejemplo, negro

    def get_random_color(self):
        r = lambda: random.randint(0, 255)
        return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

    def save_coordinates(self):
        if not self.video_file or not self.objects:
            messagebox.showinfo("Error", "Please load a video and mark objects before saving.")
            return
        json_filename = f"{self.video_file}.json"
        json_data = []
        for idx, obj in enumerate(self.objects):
            # Escalar las coordenadas de cada punto del objeto a la escala original
            scaled_obj = [(x * 2, y * 2) for x, y in obj]
            item_json = {"item": idx + 1, "positions": {"object_" + str(idx + 1): scaled_obj}}
            json_data.append(item_json)
        with open(json_filename, "w") as json_file:
            json.dump(json_data, json_file)
        messagebox.showinfo("Save Successful", "Coordinates saved successfully.")

    def load_coordinates(self):
        if not self.video_file:
            messagebox.showinfo("Error", "Please load a video first.")
            return
        json_filename = f"{self.video_file}.json"
        try:
            with open(json_filename, "r") as json_file:
                json_data = json.load(json_file)
            # Aplicar la escala de reducción a la mitad en las coordenadas cargadas
            self.objects = [[(int(x / 2), int(y / 2)) for x, y in item["positions"]["object_" + str(idx + 1)]]
                            for idx, item in enumerate(json_data)]
            # Cambiar el orden de las operaciones
            success, self.frame = self.capture.read()
            if success:
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.original_frame = self.frame.copy()
                self.frame = Image.fromarray(self.frame)
                self.frame = self.frame.resize((self.frame.width // 2, self.frame.height // 2))  # Escalar a la mitad
                self.frame = ImageTk.PhotoImage(self.frame)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.frame)
                self.canvas.image = self.frame  # Evitar recolección de basura
                self.update_object_list()
                self.render_objects()
        except FileNotFoundError:
            messagebox.showinfo("Error", "Coordinate file not found.")
            
        
    def add_object(self):
        messagebox.showinfo("Add Object", "Click on the canvas to add a new object.")

    def delete_object(self):
        selected_indices = self.object_list.curselection()
        if selected_indices:
            for index in selected_indices:
                del self.objects[index]
            self.update_object_list()
            self.render_objects()

    def update_object_list(self):
        self.object_list.delete(0, tk.END)
        for i, obj in enumerate(self.objects):
            color = self.get_object_color(obj)
            self.object_list.insert(tk.END, f"Item {i+1}")  # Colorear con el color del objeto
            self.object_list.itemconfig(0, foreground=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCalibrationApp(root)
    root.mainloop()
