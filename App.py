import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import pywt
from scipy.fftpack import dct, idct
import os
import customtkinter

# --- Set default appearance mode and color theme ---
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class WatermarkApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("assets/icon.ico")
        self.title("WaveSecure-Digital Image Watermarking DWT-DCT")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        
        # Image paths and references
        self.original_img_path = None
        self.watermark_img_path = None
        self.watermarked_img_path = None
        self.extracted_img_path = None
        self.image_references = {}  # To prevent garbage collection

        self.setup_ui()
        self.status_var.set("Ready")

    def setup_ui(self):
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main frame
        main_frame = customtkinter.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Image display frames
        self.create_image_frame(main_frame, "Original Image", 0, 0, "original_img_label")
        self.create_image_frame(main_frame, "Watermark", 0, 1, "watermark_img_label")
        self.create_image_frame(main_frame, "Watermarked Image", 0, 2, "watermarked_img_label")

        # Control panel
        control_frame = customtkinter.CTkFrame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Buttons Frame 1 (Embedding)
        btn_frame1 = customtkinter.CTkFrame(control_frame)
        btn_frame1.pack(fill=tk.X, padx=10, pady=(10,0))

        buttons1 = [
            ("Select Original", self.select_original),
            ("Select Watermark", self.select_watermark),
            ("Embed Watermark", self.embed_watermark),
            ("Save Watermarked", self.save_watermarked)
        ]

        for col, (text, command) in enumerate(buttons1):
            customtkinter.CTkButton(btn_frame1, text=text, command=command).grid(row=0, column=col, padx=5, pady=5)

        # Buttons Frame 2 (Extraction)
        btn_frame2 = customtkinter.CTkFrame(control_frame)
        btn_frame2.pack(fill=tk.X, padx=10, pady=(0,10))

        buttons2 = [
            ("Extract From App", self.extract_from_app),
            ("Extract From File", self.extract_from_other),
            ("Save Extracted", self.save_extracted),
            ("Test Robustness", self.test_robustness),
            ("Calculate PSNR", self.calculate_imperceptibility)
        ]

        for col, (text, command) in enumerate(buttons2):
            customtkinter.CTkButton(btn_frame2, text=text, command=command).grid(row=0, column=col, padx=5, pady=5)

        # Parameters frame
        param_frame = customtkinter.CTkFrame(control_frame)
        param_frame.pack(fill=tk.X, padx=10, pady=10)

        # Wavelet selection
        customtkinter.CTkLabel(param_frame, text="Wavelet Model:").grid(row=0, column=0, padx=5, pady=5)
        self.wavelet_var = tk.StringVar(value="haar")
        wavelet_combo = customtkinter.CTkComboBox(
            param_frame, 
            variable=self.wavelet_var, 
            values=["haar", "db1", "db2", "iyus-svd"]
        )
        wavelet_combo.grid(row=0, column=1, padx=5, pady=5)

        # Decomposition level
        customtkinter.CTkLabel(param_frame, text="Decomposition Level:").grid(row=0, column=2, padx=5, pady=5)
        self.level_var = tk.StringVar(value="1")
        level_combo = customtkinter.CTkComboBox(
            param_frame, 
            variable=self.level_var, 
            values=["1", "2", "3"]
        )
        level_combo.grid(row=0, column=3, padx=5, pady=5)

        # Alpha strength
        customtkinter.CTkLabel(param_frame, text="Alpha (Strength):").grid(row=0, column=4, padx=5, pady=5)
        self.alpha_var = tk.DoubleVar(value=0.1)
        alpha_entry = customtkinter.CTkEntry(param_frame, textvariable=self.alpha_var, width=50)
        alpha_entry.grid(row=0, column=5, padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        status_bar = customtkinter.CTkLabel(self, textvariable=self.status_var, anchor=tk.W, corner_radius=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def create_image_frame(self, parent, title, row, col, attr_name):
        """Helper function to create image display frames"""
        container = customtkinter.CTkFrame(parent)
        container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        title_label = customtkinter.CTkLabel(container, text=title, font=customtkinter.CTkFont(weight="bold"))
        title_label.pack(pady=(10, 0))

        content_frame = customtkinter.CTkFrame(container)
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        label = customtkinter.CTkLabel(content_frame, text="", fg_color="#2B2B2B")
        label.pack(fill=tk.BOTH, expand=True)
        
        setattr(self, attr_name, label)

    def select_original(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            try:
                self.original_img_path = file_path
                img = Image.open(file_path)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                self.image_references["original"] = ImageTk.PhotoImage(img)
                self.original_img_label.configure(image=self.image_references["original"])
                self.status_var.set(f"Original image loaded: {os.path.basename(file_path)}")
                self.watermarked_img_path = None
                self.watermarked_img_label.configure(image='')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def select_watermark(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            try:
                self.watermark_img_path = file_path
                img = Image.open(file_path)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                self.image_references["watermark"] = ImageTk.PhotoImage(img)
                self.watermark_img_label.configure(image=self.image_references["watermark"])
                self.status_var.set(f"Watermark image loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load watermark:\n{str(e)}")

    def embed_watermark(self):
        if not self.original_img_path or not self.watermark_img_path:
            messagebox.showwarning("Warning", "Please select both original and watermark images.")
            return

        try:
            self.status_var.set("Embedding watermark...")
            self.update()

            # Read and process images
            original_img = convert_image(self.original_img_path, 512)
            watermark = convert_image(self.watermark_img_path, 128)  # Fixed size for watermark

            # Get parameters
            model = self.wavelet_var.get()
            level = int(self.level_var.get())
            alpha = self.alpha_var.get()

            # Embed watermark
            watermarked_img = embed_watermark_dwtdct(original_img, watermark, model, level, alpha)

            # Save and display result
            self.watermarked_img_path = "watermarked_image.jpg"
            cv2.imwrite(self.watermarked_img_path, watermarked_img)

            img = Image.open(self.watermarked_img_path).resize((250, 250), Image.Resampling.LANCZOS)
            self.image_references["watermarked"] = ImageTk.PhotoImage(img)
            self.watermarked_img_label.configure(image=self.image_references["watermarked"])

            self.status_var.set("Watermark embedded successfully.")
            messagebox.showinfo("Success", "Watermark embedded successfully and saved as 'watermarked_image.jpg'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to embed watermark:\n{str(e)}")
            self.status_var.set("Watermark embedding failed.")

    def save_watermarked(self):
        if not self.watermarked_img_path:
            messagebox.showwarning("Warning", "No watermarked image to save. Please embed watermark first.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
                initialfile="watermarked_image.jpg"
            )
            if file_path:
                img = Image.open(self.watermarked_img_path)
                img.save(file_path)
                self.status_var.set(f"Watermarked image saved as: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Watermarked image saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save watermarked image:\n{str(e)}")
            self.status_var.set("Save failed.")

    def extract_from_app(self):
        """Extract watermark from the image created by this app"""
        if not self.watermarked_img_path:
            messagebox.showwarning("Warning", "No watermarked image available. Please embed watermark first.")
            return

        try:
            self.status_var.set("Extracting watermark from app image...")
            self.update()

            # Get parameters
            model = self.wavelet_var.get()
            level = int(self.level_var.get())
            alpha = self.alpha_var.get()

            # Read watermarked image
            watermarked_img = convert_image(self.watermarked_img_path, 512)

            # Read original image if available
            original_img = None
            if self.original_img_path:
                try:
                    original_img = convert_image(self.original_img_path, 512)
                except Exception:
                    original_img = None

            # Extract watermark
            extracted_watermark = extract_watermark_dwtdct(watermarked_img, original_img, model, level, alpha)
            extracted_watermark_clipped = np.clip(extracted_watermark, 0, 255).astype(np.uint8)

            # Save extracted watermark
            self.extracted_img_path = "extracted_watermark.jpg"
            Image.fromarray(extracted_watermark_clipped).save(self.extracted_img_path)

            # Display result
            watermark_img_display = Image.fromarray(extracted_watermark_clipped).resize((250, 250), Image.Resampling.LANCZOS)
            self.image_references["extracted"] = ImageTk.PhotoImage(watermark_img_display)
            self.watermark_img_label.configure(image=self.image_references["extracted"])

            extraction_type = "Non-blind" if original_img is not None else "Blind"
            self.status_var.set(f"{extraction_type} watermark extracted from app image.")
            messagebox.showinfo("Success", f"{extraction_type} watermark extracted successfully from application image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract watermark:\n{str(e)}")
            self.status_var.set("Extraction failed.")

    def extract_from_other(self):
        """Extract watermark from any uploaded image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")],
            title="Select watermarked image for extraction"
        )
        
        if not file_path:
            return
            
        try:
            self.status_var.set("Extracting watermark from selected image...")
            self.update()

            # Get parameters
            model = self.wavelet_var.get()
            level = int(self.level_var.get())
            alpha = self.alpha_var.get()

            # Read watermarked image
            watermarked_img = convert_image(file_path, 512)

            # Read original image if available
            original_img = None
            if self.original_img_path:
                try:
                    original_img = convert_image(self.original_img_path, 512)
                except Exception:
                    original_img = None

            # Extract watermark
            extracted_watermark = extract_watermark_dwtdct(watermarked_img, original_img, model, level, alpha)
            extracted_watermark_clipped = np.clip(extracted_watermark, 0, 255).astype(np.uint8)

            # Save extracted watermark
            self.extracted_img_path = "extracted_watermark_from_upload.jpg"
            Image.fromarray(extracted_watermark_clipped).save(self.extracted_img_path)

            # Display result
            watermark_img_display = Image.fromarray(extracted_watermark_clipped).resize((250, 250), Image.Resampling.LANCZOS)
            self.image_references["extracted"] = ImageTk.PhotoImage(watermark_img_display)
            self.watermark_img_label.configure(image=self.image_references["extracted"])

            extraction_type = "Non-blind" if original_img is not None else "Blind"
            self.status_var.set(f"{extraction_type} watermark extracted from uploaded image.")
            messagebox.showinfo("Success", f"{extraction_type} watermark extracted successfully from:\n{os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract watermark:\n{str(e)}")
            self.status_var.set("Extraction failed.")

    def save_extracted(self):
        if not self.extracted_img_path:
            messagebox.showwarning("Warning", "No extracted watermark to save. Please extract watermark first.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
                initialfile="extracted_watermark.jpg"
            )
            if file_path:
                img = Image.open(self.extracted_img_path)
                img.save(file_path)
                self.status_var.set(f"Extracted watermark saved as: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Extracted watermark saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save extracted watermark:\n{str(e)}")
            self.status_var.set("Save failed.")

    def test_robustness(self):
        if not self.watermarked_img_path:
            messagebox.showwarning("Warning", "Please embed watermark first.")
            return

        try:
            self.status_var.set("Testing robustness with noise...")
            self.update()

            # Get parameters
            model = self.wavelet_var.get()
            level = int(self.level_var.get())
            alpha = self.alpha_var.get()

            # Read and add noise to watermarked image
            img = cv2.imread(self.watermarked_img_path, cv2.IMREAD_GRAYSCALE)
            noise = np.random.normal(0, 15, img.shape).astype(np.float32)
            noisy_img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            cv2.imwrite("image_noisy.jpg", noisy_img)

            # Read original image if available
            original_img = None
            if self.original_img_path:
                try:
                    original_img = convert_image(self.original_img_path, 512)
                except Exception:
                    original_img = None

            # Extract from noisy image
            extracted_watermark = extract_watermark_dwtdct(noisy_img, original_img, model, level, alpha)
            extracted_watermark_clipped = np.clip(extracted_watermark, 0, 255).astype(np.uint8)

            # Save and display result
            self.extracted_img_path = "watermark_after_noise.jpg"
            Image.fromarray(extracted_watermark_clipped).save(self.extracted_img_path)

            watermark_img_display = Image.fromarray(extracted_watermark_clipped).resize((250, 250), Image.Resampling.LANCZOS)
            self.image_references["extracted_robust"] = ImageTk.PhotoImage(watermark_img_display)
            self.watermark_img_label.configure(image=self.image_references["extracted_robust"])

            extraction_type = "Non-blind" if original_img is not None else "Blind"
            messagebox.showinfo("Robustness", f"{extraction_type} watermark extracted from noisy image.")
            self.status_var.set("Robustness test completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Robustness test failed:\n{str(e)}")
            self.status_var.set("Robustness test failed.")

    def calculate_imperceptibility(self):
        if not self.original_img_path or not self.watermarked_img_path:
            messagebox.showwarning("Warning", "Please select the Original Image and embed/select the Watermarked Image first.")
            return

        try:
            self.status_var.set("Calculating PSNR...")
            self.update()

            # Load images
            original_img = cv2.imread(self.original_img_path, cv2.IMREAD_GRAYSCALE)
            watermarked_img = cv2.imread(self.watermarked_img_path, cv2.IMREAD_GRAYSCALE)

            if original_img is None or watermarked_img is None:
                messagebox.showerror("Error", "Could not load one or both images.")
                self.status_var.set("Metric calculation failed.")
                return

            # Resize if necessary
            if original_img.shape != watermarked_img.shape:
                watermarked_img = cv2.resize(watermarked_img, (original_img.shape[1], original_img.shape[0]))

            # Calculate PSNR
            psnr = cv2.PSNR(original_img, watermarked_img)

            # Show results
            metrics_text = f"PSNR: {psnr:.2f} dB"
            explanation_text = (
                "\n\nPSNR (Peak Signal-to-Noise Ratio): Measures image quality.\n"
                "Higher PSNR indicates less distortion (better quality).\n"
                "Good quality: 30-50 dB\nPoor quality: <30 dB"
            )
            messagebox.showinfo("Imperceptibility Metrics", metrics_text + explanation_text)
            self.status_var.set(f"PSNR calculated: {psnr:.2f} dB")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate metrics:\n{str(e)}")
            self.status_var.set("Metric calculation failed.")

# Helper functions
def convert_image(image_path, size):
    """Convert image to grayscale and resize it"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found or cannot be read: {image_path}")
    return cv2.resize(img, (size, size))

def apply_dct(image_array):
    """Apply DCT to image"""
    return dct(dct(image_array.T, norm='ortho').T, norm='ortho')

def apply_idct(dct_array):
    """Apply inverse DCT to array"""
    return idct(idct(dct_array.T, norm='ortho').T, norm='ortho')

def process_coefficients(image_array, model, level):
    """Apply DWT to image and get coefficients"""
    return pywt.wavedec2(data=image_array.astype(np.float32), wavelet=model, level=level)

def embed_watermark_dwtdct(image_array, watermark, model, level, alpha=0.1):
    """Embed watermark using DWT-DCT method"""
    coeffs = process_coefficients(image_array, model, level)
    LL = coeffs[0].copy()
    LL_dct = apply_dct(LL)

    watermark_float = watermark.astype(np.float32)
    embed_row_start = LL_dct.shape[0] // 4
    embed_col_start = LL_dct.shape[1] // 4
    h_w, w_w = watermark_float.shape

    for i in range(h_w):
        for j in range(w_w):
            LL_dct[embed_row_start + i, embed_col_start + j] = LL_dct[embed_row_start + i, embed_col_start + j] * (1.0 + alpha * watermark_float[i, j] / 255.0)

    LL_watermarked = apply_idct(LL_dct)
    coeffs_watermarked = list(coeffs)
    coeffs_watermarked[0] = LL_watermarked

    watermarked_img = pywt.waverec2(coeffs=coeffs_watermarked, wavelet=model)
    return np.clip(watermarked_img, 0, 255).astype(np.uint8)

def extract_watermark_dwtdct(watermarked_img, original_img, model, level, alpha):
    """Extract watermark from watermarked image"""
    w_coeffs = process_coefficients(watermarked_img, model, level)
    w_LL_dct = apply_dct(w_coeffs[0])
    
    extracted_size = (w_LL_dct.shape[0] // 2, w_LL_dct.shape[1] // 2)
    watermark = np.zeros(extracted_size, dtype=np.float32)
    
    extract_row_start = w_LL_dct.shape[0] // 4
    extract_col_start = w_LL_dct.shape[1] // 4
    h_ext, w_ext = extracted_size

    if original_img is not None:
        o_coeffs = process_coefficients(original_img, model, level)
        o_LL_dct = apply_dct(o_coeffs[0])

        for i in range(h_ext):
            for j in range(w_ext):
                w_coeff = w_LL_dct[extract_row_start + i, extract_col_start + j]
                o_coeff = o_LL_dct[extract_row_start + i, extract_col_start + j]
                
                if abs(o_coeff) > 1e-6 and alpha != 0:
                    watermark[i, j] = ((w_coeff / o_coeff) - 1.0) / alpha * 255.0
                else:
                    watermark[i, j] = 128.0
    else:
        mean_coeff = np.mean(w_LL_dct[extract_row_start:extract_row_start+h_ext, extract_col_start:extract_col_start+w_ext])
        for i in range(h_ext):
            for j in range(w_ext):
                watermark[i, j] = (w_LL_dct[extract_row_start + i, extract_col_start + j] - mean_coeff) * 5.0 + 128.0

    return watermark

if __name__ == "__main__":
    app = WatermarkApp()
    app.mainloop()