import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, simpledialog, messagebox, Button, Label, Toplevel, Frame, BOTH, LEFT, RIGHT, TOP
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Definicja zakresów kolorów HSV
color_ranges = {
    "DarkBlue":  [(100, 50, 20), (130, 255, 100)],
    "Blue":      [(100, 50, 100), (130, 255, 200)],
    "Cyan":      [(85, 50, 100), (99, 255, 255)],
    "Green":     [(60, 50, 50), (84, 255, 255)],
    "Yellow":    [(25, 50, 50), (35, 255, 255)],
    "OrangeRed": [(10, 50, 50), (24, 255, 255)],
    "Red":       [(0, 50, 50), (9, 255, 255)]
}

# Kolory dla wykresów matplotlib
color_map = {
    "DarkBlue":  "#00008B",
    "Blue":      "#0000FF",
    "Cyan":      "#00FFFF",
    "Green":     "#00FF00",
    "Yellow":    "#FFFF00",
    "OrangeRed": "#FF4500",
    "Red":       "#FF0000"
}

def analyze_image(image_path):
    # Wczytaj obraz
    image = cv2.imread(image_path)
    if image is None:
        messagebox.showerror("Błąd", "Nie można wczytać obrazu.")
        return

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Pobierz wartości mikrometrów dla każdego koloru
    color_values = {}
    for color in color_ranges.keys():
        value = simpledialog.askfloat("Wartość w µm", f"Podaj wartość w µm dla koloru {color}:", minvalue=0)
        if value is None:
            messagebox.showinfo("Anulowano", "Anulowano działanie.")
            return
        color_values[color] = value

    # Maski pikseli nie-czarnych
    non_black_mask = cv2.inRange(hsv_image, (0, 0, 20), (180, 255, 255))
    non_black_pixels = cv2.countNonZero(non_black_mask)

    if non_black_pixels == 0:
        messagebox.showerror("Błąd", "Obraz zawiera za mało kolorów do analizy.")
        return

    # Liczenie pikseli dla każdego koloru
    color_counts = {}
    for color, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv_image, lower_np, upper_np)
        count = cv2.countNonZero(mask)
        color_counts[color] = count

    # Procenty pikseli
    color_percentages = {color: (count / non_black_pixels) * 100 for color, count in color_counts.items()}

    # Średnia i odchylenie
    values = np.array([color_values[color] for color in color_ranges.keys()])
    percentages = np.array([color_percentages[color] for color in color_ranges.keys()]) / 100
    mean_thickness = np.sum(percentages * values)
    variance = np.sum(percentages * (values - mean_thickness) ** 2)
    std_dev = np.sqrt(variance)

    # Okno wyników
    result_win = Toplevel(root)
    result_win.title("Wyniki analizy biofilmu")

    # Nagłówek z wynikiem
    text_result = f"📏 Estimated mean thickness: {mean_thickness:.2f} µm    📊 Standard deviation: {std_dev:.2f} µm"
    Label(result_win, text=text_result, font=("Arial", 12)).pack(pady=8)

    # Główna ramka pozioma
    main_frame = Frame(result_win)
    main_frame.pack(fill=BOTH, expand=True)

    # Wykres kołowy po lewej
    pie_frame = Frame(main_frame)
    pie_frame.pack(side=LEFT, padx=5, pady=5)

    fig1, ax1 = plt.subplots(figsize=(3, 3), dpi=100)
    labels = list(color_percentages.keys())
    sizes = [color_percentages[color] for color in labels]
    colors = [color_map[color] for color in labels]

    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    ax1.set_title("Procentowy udział kolorów")

    canvas1 = FigureCanvasTkAgg(fig1, master=pie_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack()

    # Obraz na środku
    image_frame = Frame(main_frame)
    image_frame.pack(side=LEFT, padx=5, pady=5)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    pil_image = pil_image.resize((400, int(400 * image_rgb.shape[0] / image_rgb.shape[1])), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(pil_image)

    label_img = Label(image_frame, image=photo)
    label_img.image = photo
    label_img.pack()

    # Wykres krzywej po prawej
    curve_frame = Frame(main_frame)
    curve_frame.pack(side=LEFT, padx=5, pady=5)

    fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
    ax2.plot(values, percentages * 100, marker='o', linestyle='-', color='blue')
    ax2.set_title("Rozkład grubości biofilmu")
    ax2.set_xlabel("Grubość [µm]")
    ax2.set_ylabel("Procent pikseli [%]")
    ax2.grid(True)

    canvas2 = FigureCanvasTkAgg(fig2, master=curve_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack()

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
    if file_path:
        analyze_image(file_path)

# Główne okno GUI
root = Tk()
root.title("Biofilm Thickness Analyzer")

Label(root, text="Program do pomiaru grubości biofilmu na zdjęciach 3D z mikroskopu cyfrowego Keyence VHX-S770E", font=("Arial", 12)).pack(pady=5)
Label(root, text="Kliknij przycisk, aby wybrać zdjęcie i podać wartości mikrometrów.", font=("Arial", 10)).pack(pady=10)
Button(root, text="Wybierz zdjęcie", command=select_image, width=25, height=2).pack(pady=20)
Label(root, text="Autor: Tomasz M. Karpiński", font=("Arial", 9)).pack(side="bottom", pady=5)
Label(root, text="Licencja: Uznanie autorstwa-Użycie niekomercyjne-Na tych samych warunkach 4.0", font=("Arial", 9)).pack(side="bottom")

root.mainloop()
