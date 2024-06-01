import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def hilbert_curve(n):
    def hilbert(x, y, xi, xj, yi, yj, n):
        if n <= 0:
            return [(x + (xi + yi) // 2, y + (xj + yj) // 2)]
        else:
            points = []
            points += hilbert(x, y, yi // 2, yj // 2, xi // 2, xj // 2, n - 1)
            points += hilbert(x + xi // 2, y + xj // 2, xi // 2, xj // 2, yi // 2, yj // 2, n - 1)
            points += hilbert(x + xi // 2 + yi // 2, y + xj // 2 + yj // 2, xi // 2, xj // 2, yi // 2, yj // 2, n - 1)
            points += hilbert(x + xi // 2 + yi, y + xj // 2 + yj, -yi // 2, -yj // 2, -xi // 2, -xj // 2, n - 1)
            return points

    return hilbert(0, 0, n, 0, 0, n, int(np.log2(n)))

def embed_data(image_path, data, output_path):
    img = Image.open(image_path)
    pixels = np.array(img)
    flat_pixels = pixels.flatten()
    
    data_bits = ''.join(format(ord(char), '08b') for char in data)
    data_len = len(data_bits)
    
    hilbert_points = hilbert_curve(min(img.size))
    
    for i in range(data_len):
        x, y = hilbert_points[i]
        index = y * img.width + x
        pixel = flat_pixels[index]
        flat_pixels[index] = (pixel & ~1) | int(data_bits[i])
    
    new_pixels = flat_pixels.reshape(pixels.shape)
    new_img = Image.fromarray(new_pixels)
    new_img.save(output_path)

def extract_data(image_path, data_len):
    img = Image.open(image_path)
    pixels = np.array(img)
    flat_pixels = pixels.flatten()
    
    hilbert_points = hilbert_curve(min(img.size))
    data_bits = []
    
    for i in range(data_len * 8):
        x, y = hilbert_points[i]
        index = y * img.width + x
        pixel = flat_pixels[index]
        data_bits.append(pixel & 1)
    
    data = ''.join(chr(int(''.join(map(str, data_bits[i:i + 8])), 2)) for i in range(0, len(data_bits), 8))
    return data

def browse_file():
    filename = filedialog.askopenfilename()
    return filename

def embed_gui():
    image_path = browse_file()
    if not image_path:
        return

    data = text_input.get("1.0", tk.END).strip()
    if not data:
        messagebox.showerror("Error", "Data to hide is required.")
        return

    output_path = filedialog.asksaveasfilename(defaultextension=".png")
    if not output_path:
        return

    embed_data(image_path, data, output_path)
    messagebox.showinfo("Success", f"Data embedded into {output_path}")

def extract_gui():
    image_path = browse_file()
    if not image_path:
        return

    data_len = int(length_input.get().strip())
    if not data_len:
        messagebox.showerror("Error", "Length of data to extract is required.")
        return

    extracted_data = extract_data(image_path, data_len)
    output_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if not output_path:
        return

    with open(output_path, "w") as f:
        f.write(extracted_data)
    messagebox.showinfo("Success", f"Data extracted and saved to {output_path}")

def create_gui():
    root = tk.Tk()
    root.title("Steganography using Hilbert Curve")

    embed_frame = tk.Frame(root)
    embed_frame.pack(padx=10, pady=10)

    embed_label = tk.Label(embed_frame, text="Embed Data")
    embed_label.pack()

    text_label = tk.Label(embed_frame, text="Tulis Text Untuk Disusupi:")
    text_label.pack()
    global text_input
    text_input = tk.Text(embed_frame, height=5, width=40)
    text_input.pack()

    embed_button = tk.Button(embed_frame, text="Pilih Gambar Murni", command=embed_gui)
    embed_button.pack(pady=5)

    extract_frame = tk.Frame(root)
    extract_frame.pack(padx=10, pady=10)

    extract_label = tk.Label(extract_frame, text="Extract Data")
    extract_label.pack()

    length_label = tk.Label(extract_frame, text="Jumlah karakter yang disembunyikan (Pake Angka!):")
    length_label.pack()
    global length_input
    length_input = tk.Entry(extract_frame)
    length_input.pack()

    extract_button = tk.Button(extract_frame, text="Pilih Gambar Yang Telah disusupi", command=extract_gui)
    extract_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()