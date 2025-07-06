import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import os
import sys
import threading
from PIL import Image, ImageDraw, ImageFont

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def is_point_on_segment(p, a, b, eps=1e-9):
    cross_val = cross(a, b, p)
    if abs(cross_val) > eps:
        return False
    min_x, max_x = sorted([a[0], b[0]])
    min_y, max_y = sorted([a[1], b[1]])
    return min_x - eps <= p[0] <= max_x + eps and min_y - eps <= p[1] <= max_y + eps

def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]

def get_output_directory(folder_name="wykresy"):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    output_dir = os.path.join(base_dir, folder_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_unique_filename(base_name="convex_hull", ext="png"):
    output_dir = get_output_directory()
    i = 1
    while True:
        filename = os.path.join(output_dir, f"{base_name}_{i}.{ext}")
        if not os.path.exists(filename):
            return filename
        i += 1

def save_points_as_image(points):
    output_dir = get_output_directory()
    filename = get_unique_filename(base_name="lista_punktow", ext="png")

    width = 400
    line_height = 30
    height = line_height * (len(points) + 2)

    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    draw.text((10, 10), "Lista punktów:", font=font, fill="black")
    for i, (x, y) in enumerate(points):
        draw.text((10, 10 + (i + 1) * line_height), f"P{i+1}: ({x}, {y})", font=font, fill="black")

    image.save(filename)
    print(f"Lista punktów zapisana do pliku: {filename}")

def plot_points_and_hull(points, hull):
    def plotting():
        plt.figure(figsize=(6, 6.8))

        hull_set = set(hull)
        on_edge = []
        inner = []

        for pt in points:
            if pt in hull_set:
                continue
            for i in range(len(hull)):
                a = hull[i]
                b = hull[(i + 1) % len(hull)]
                if is_point_on_segment(pt, a, b):
                    on_edge.append(pt)
                    break
            else:
                inner.append(pt)

        if len(hull) > 1:
            hx, hy = zip(*(hull + [hull[0]]))
            plt.plot(hx, hy, 'r-', linewidth=2, label='Otoczka wypukła')

        if hull:
            hx, hy = zip(*hull)
            plt.scatter(hx, hy, color='red', s=140, edgecolor='black', label='Wierzchołki')

        if inner:
            ix, iy = zip(*inner)
            plt.scatter(ix, iy, color='lightgreen', s=100, edgecolor='black', label='Wewnętrzne')

        if on_edge:
            ex, ey = zip(*on_edge)
            plt.scatter(ex, ey, color='yellow', s=100, edgecolor='black', label='Na krawędzi')

        for i, (x, y) in enumerate(points):
            plt.text(x + 0.05, y + 0.05, f'P{i+1}', fontsize=9)

        typy_otoczki = {1: "Punkt", 2: "Odcinek", 3: "Trójkąt", 4: "Czworokąt", 5: "Pięciokąt"}
        n = len(hull)
        typ = typy_otoczki.get(n, f"{n}-kąt")
        plt.title(f"Otoczka wypukła: {typ}", fontsize=14)

        plt.subplots_adjust(bottom=0.15)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.axis('equal')
        plt.legend()
        plt.grid(True)

        filename = get_unique_filename()
        plt.savefig(filename, bbox_inches='tight')
        print(f"Wizualizacja została zapisana do pliku: {filename}")
        plt.show()

    threading.Thread(target=plotting).start()

def show_points_in_window(points):
    save_points_as_image(points)

    top = tk.Toplevel()
    top.title("Lista punktów")

    frame = tk.Frame(top, padx=10, pady=10)
    frame.pack()

    label = tk.Label(frame, text="Lista punktów (Px: (x, y)):", font=('Arial', 12, 'bold'))
    label.pack()

    text_box = tk.Text(frame, width=30, height=min(25, len(points)+2), font=("Courier New", 10))
    text_box.pack()

    for i, (x, y) in enumerate(points):
        text_box.insert(tk.END, f"P{i+1}: ({x}, {y})\n")

    text_box.config(state=tk.DISABLED)

def parse_input_points(text):
    lines = text.strip().splitlines()
    points = []
    for line in lines:
        parts = line.replace(',', ' ').split()
        if len(parts) != 2:
            raise ValueError(f"Nieprawidłowy format: '{line}'")
        x, y = float(parts[0]), float(parts[1])
        points.append((x, y))
    return points

def compute_and_plot():
    try:
        points = parse_input_points(text_input.get("1.0", tk.END))
        if len(points) < 3:
            messagebox.showwarning("Za mało punktów", "Wprowadź co najmniej 3 punkty.")
            return
        hull = convex_hull(points)
        show_points_in_window(points)
        plot_points_and_hull(points, hull)
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

# GUI
root = tk.Tk()
root.title("Otoczka wypukła")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

label = tk.Label(frame, text="Wprowadź punkty (każdy w nowej linii, np. '1 2' lub '3,4'):")
label.pack()

text_input = tk.Text(frame, width=40, height=10)
text_input.pack()

button = tk.Button(frame, text="Oblicz otoczkę wypukłą", command=compute_and_plot)
button.pack(pady=10)

root.mainloop()