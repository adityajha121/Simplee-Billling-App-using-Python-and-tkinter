import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import sys
import subprocess
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class RetailBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AR Enterprises Billing System")
        self.root.geometry("1200x800")  # Increased width to accommodate new column
        
        self.setup_ui()
        
    def setup_ui(self):
        self.create_header()
        self.create_customer_info()
        self.create_item_table()
        self.create_total_section()
        self.create_buttons()
        
    def create_header(self):
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="AR ENTERPRISES", font=("Arial", 20, "bold")).pack()
        ttk.Label(header_frame, text="AR MINIMART, BHIWANDI", font=("Arial", 14)).pack()
        ttk.Label(header_frame, text="Contact:+9188303-74199", font=("Arial", 12)).pack()
        
    def create_customer_info(self):
        customer_frame = ttk.Frame(self.root, padding="10")
        customer_frame.pack(fill=tk.X)
        
        ttk.Label(customer_frame, text="Customer Name:").grid(row=0, column=0, sticky="e")
        self.customer_name = ttk.Entry(customer_frame)
        self.customer_name.grid(row=0, column=1)
        
        ttk.Label(customer_frame, text="Customer ID:").grid(row=0, column=2, sticky="e")
        self.customer_id = ttk.Entry(customer_frame)
        self.customer_id.grid(row=0, column=3)
        
        ttk.Label(customer_frame, text="Phone:").grid(row=1, column=0, sticky="e")
        self.customer_phone = ttk.Entry(customer_frame)
        self.customer_phone.grid(row=1, column=1)
        
        self.invoice_number = tk.StringVar(value=f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
        ttk.Label(customer_frame, text="Invoice #:").grid(row=1, column=2, sticky="e")
        ttk.Entry(customer_frame, textvariable=self.invoice_number, state="readonly").grid(row=1, column=3)
        
    def create_item_table(self):
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        headers = ["Description", "Quantity", "Unit Price", "Warranty", "Amount"]
        for col, header in enumerate(headers):
            ttk.Label(table_frame, text=header, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=5, pady=5)
        
        self.item_rows = []
        for row in range(1, 11):  # 10 rows for items
            description = ttk.Entry(table_frame, width=30)
            quantity = ttk.Entry(table_frame, width=10)
            unit_price = ttk.Entry(table_frame, width=10)
            warranty = ttk.Entry(table_frame, width=15)
            amount = ttk.Label(table_frame, text="0.00", width=10)
            
            description.grid(row=row, column=0, padx=5, pady=2)
            quantity.grid(row=row, column=1, padx=5, pady=2)
            unit_price.grid(row=row, column=2, padx=5, pady=2)
            warranty.grid(row=row, column=3, padx=5, pady=2)
            amount.grid(row=row, column=4, padx=5, pady=2)
            
            self.item_rows.append((description, quantity, unit_price, warranty, amount))
        
    def create_total_section(self):
        total_frame = ttk.Frame(self.root, padding="10")
        total_frame.pack(fill=tk.X)
        
        ttk.Label(total_frame, text="Subtotal:").grid(row=0, column=0, sticky="e")
        self.subtotal_label = ttk.Label(total_frame, text="0.00")
        self.subtotal_label.grid(row=0, column=1, sticky="w")
        
        ttk.Label(total_frame, text="Discount:").grid(row=1, column=0, sticky="e")
        self.discount_entry = ttk.Entry(total_frame, width=10)
        self.discount_entry.grid(row=1, column=1, sticky="w")
        self.discount_entry.insert(0, "0")
        
        ttk.Label(total_frame, text="Total:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="e")
        self.total_label = ttk.Label(total_frame, text="0.00", font=("Arial", 12, "bold"))
        self.total_label.grid(row=2, column=1, sticky="w")
        
    def create_buttons(self):
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Calculate Total", command=self.calculate_total).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Bill", command=self.generate_bill).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Print Bill", command=self.print_bill).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
    def calculate_total(self):
        subtotal = 0.0
        for description, quantity, unit_price, warranty, amount in self.item_rows:
            if quantity.get() and unit_price.get():
                try:
                    line_total = float(quantity.get()) * float(unit_price.get())
                    subtotal += line_total
                    amount.config(text=f"{line_total:.2f}")
                except ValueError:
                    amount.config(text="Error")
        
        self.subtotal_label.config(text=f"{subtotal:.2f}")
        
        try:
            discount = float(self.discount_entry.get())
            total = subtotal - discount
            self.total_label.config(text=f"{total:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Invalid discount amount")
        
    def generate_bill(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.create_pdf_bill(file_path)
            
    def create_pdf_bill(self, file_path):
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            
            # Add logo
            logo_path = self.get_logo_path()
            if logo_path:
                c.drawImage(logo_path, 430, 680, width=2*inch, height=2*inch, preserveAspectRatio=True, mask='auto')
            
            c.setFont("Helvetica-Bold", 20)
            c.drawString(100, 750, "AR ENTERPRISES")
            c.setFont("Helvetica", 14)
            c.drawString(100, 730, "AR MINIMART, BHIWANDI")
            c.drawString(100, 710, "Contact: +9188303-74199")
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 670, f"Invoice #{self.invoice_number.get()}")
            c.setFont("Helvetica", 12)
            c.drawString(100, 650, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            
            c.drawString(100, 620, f"Customer: {self.customer_name.get()}")
            c.drawString(100, 600, f"Customer ID: {self.customer_id.get()}")
            c.drawString(100, 580, f"Phone: {self.customer_phone.get()}")
            
            # Item table
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 540, "Description")
            c.drawString(250, 540, "Qty")
            c.drawString(300, 540, "Unit Price")
            c.drawString(380, 540, "Warranty")
            c.drawString(480, 540, "Amount")
            
            c.setFont("Helvetica", 12)
            y = 520
            for description, quantity, unit_price, warranty, amount in self.item_rows:
                if description.get():
                    c.drawString(100, y, description.get())
                    c.drawString(250, y, quantity.get())
                    c.drawString(300, y, unit_price.get())
                    c.drawString(380, y, warranty.get())
                    c.drawString(480, y, amount.cget("text"))
                    y -= 20
            
            # Totals
            c.drawString(400, y-20, "Subtotal:")
            c.drawString(480, y-20, self.subtotal_label.cget("text"))
            c.drawString(400, y-40, "Discount:")
            c.drawString(480, y-40, self.discount_entry.get())
            c.setFont("Helvetica-Bold", 12)
            c.drawString(400, y-60, "Total:")
            c.drawString(480, y-60, self.total_label.cget("text"))
            
            # Signature box
            c.setFont("Helvetica", 12)
            c.drawString(100, 100, "Signature:")
            c.rect(100, 50, 200, 40, stroke=1, fill=0)
            
            c.setFont("Helvetica", 10)
            c.drawString(100, 30, "Terms: NO RETURN OF STOCK")
            c.drawString(100, 15, "Thank you for your business!")
            
            c.save()
            messagebox.showinfo("Success", f"Bill saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")

    def print_bill(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file_path = temp_file.name
        temp_file.close()

        self.create_pdf_bill(temp_file_path)

        try:
            if os.name == 'nt':  # For Windows
                os.startfile(temp_file_path)
            elif os.name == 'posix':  # For macOS and Linux
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, temp_file_path])
            else:
                messagebox.showerror("Error", "Unsupported operating system for opening PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")

        # Don't delete the file immediately, let the user close it
        self.root.after(300000, lambda: os.unlink(temp_file_path))  # Delete after 5 minutes

    def get_logo_path(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")
        return logo_path if os.path.exists(logo_path) else None
        
    def clear_form(self):
        self.customer_name.delete(0, tk.END)
        self.customer_id.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")
        
        for description, quantity, unit_price, warranty, amount in self.item_rows:
            description.delete(0, tk.END)
            quantity.delete(0, tk.END)
            unit_price.delete(0, tk.END)
            warranty.delete(0, tk.END)
            amount.config(text="0.00")
        
        self.subtotal_label.config(text="0.00")
        self.total_label.config(text="0.00")
        
        self.invoice_number.set(f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RetailBillingApp(root)
    root.mainloop()