import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import os
import json
from datetime import datetime

class ProductServiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PC HUB MAGALANG")
        self._set_icon()
        self.data = {}
        self.cart = {}
        self.load_data()  # Load saved data
        self._create_widgets()
        self._apply_styles()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window close event

    def _set_icon(self):
        icon_path = "logo.ico" if os.name == 'nt' else "logo.png"
        try:
            if os.name == 'nt':
                self.root.iconbitmap(icon_path)
            else:
                self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        except tk.TclError as e:
            print(f"Icon error: {e}. File not found or invalid.")

    def _create_widgets(self):
        # Search Frame
        search_frame = tk.Frame(self.root, bg="#f0f8ff")
        search_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        
        # Configure the search frame to expand horizontally
        self.root.columnconfigure(0, weight=1)  # Allow the first column to expand
        search_frame.columnconfigure(1, weight=1)  # Allow the search entry to expand

        tk.Label(search_frame, text="Search:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Search Entry - Make it expand to fill the available space
        self.search_entry = tk.Entry(search_frame, font=("Arial", 12))
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")  # Use sticky="we" to expand horizontally
        
        # Search and Clear Search Buttons
        ttk.Button(search_frame, text="Search", command=self.search_items, style="Rounded.TButton").grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search, style="Rounded.TButton").grid(row=0, column=3, padx=5, pady=5)

        # Result Treeview
        self.result_tree = ttk.Treeview(self.root, columns=("Item", "Price", "Quantity"), show="headings")
        for col, text in [("Item", "Item"), ("Price", "Price"), ("Quantity", "Quantity")]:
            self.result_tree.heading(col, text=text, anchor="center")
            self.result_tree.column(col, anchor="center", width=150)  # Set a fixed width for columns
        self.result_tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Buttons Frame
        button_frame = tk.Frame(self.root, bg="#f0f8ff")
        button_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        ttk.Button(button_frame, text="Add Item/Service", command=self.add_item, style="Rounded.TButton").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Edit Item/Service", command=self.edit_item, style="Rounded.TButton").grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Delete Item/Service", command=self.delete_item, style="Rounded.TButton").grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="Add to Cart", command=self.add_to_cart, style="Rounded.TButton").grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(button_frame, text="View Cart", command=self.view_cart, style="Rounded.TButton").grid(row=0, column=4, padx=5, pady=5)

        # Configure grid weights for the root window
        self.root.columnconfigure(0, weight=1)  # Allow the first column to expand
        self.root.rowconfigure(1, weight=1)  # Allow the result tree to expand vertically

    def _apply_styles(self):
        style = ttk.Style()
        style.configure("Rounded.TButton", padding=5, font=("Arial", 10), background="#b2ebf2", borderwidth=0, relief="flat")
        style.map("Rounded.TButton",
                  background=[("active", "#80deea"), ("pressed", "#4dd0e1")],
                  foreground=[("active", "black"), ("pressed", "black")])
        style.layout("Rounded.TButton", [
            ("Button.border", {"sticky": "nswe", "children": [
                ("Button.focus", {"sticky": "nswe", "children": [
                    ("Button.padding", {"sticky": "nswe", "children": [
                        ("Button.label", {"sticky": "nswe"})
                    ]})
                ]})
            ]})
        ])  # Added missing closing parenthesis and bracket
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#b2ebf2")
        style.configure("Treeview", font=("Arial", 11), rowheight=25)
        self.root.configure(bg="#f0f8ff")

    def format_price(self, price):
        return "₱{:,.2f}".format(price)

    def search_items(self, event=None):
        search_term = self.search_entry.get().strip().lower()
        self.result_tree.delete(*self.result_tree.get_children())
        if search_term:
            found_items = [(item, details["price"], details["quantity"]) for item, details in self.data.items() if search_term in item.lower()]
            for item, price, quantity in found_items:
                self.result_tree.insert("", "end", values=(item, self.format_price(price), quantity))

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.search_items()

    def add_item(self):
        item_name = simpledialog.askstring("Add Item", "Enter Item/Service Name:")
        if item_name:
            if item_name in self.data:
                messagebox.showerror("Error", "Item already exists.")
                return
            price = simpledialog.askfloat("Add Item", "Enter Price:")
            quantity = simpledialog.askinteger("Add Item", "Enter Quantity:")
            if price is not None and quantity is not None:
                if price < 0 or quantity < 0:
                    messagebox.showerror("Error", "Price and quantity must be positive.")
                    return
                self.data[item_name] = {"price": price, "quantity": quantity}
                messagebox.showinfo("Item Added", f"{item_name} added with price {self.format_price(price)} and quantity {quantity}")
            else:
                messagebox.showerror("Error", "Invalid input.")
        else:
            messagebox.showerror("Error", "Item name cannot be empty.")

    def edit_item(self):
        selected_item = self.result_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to edit.")
            return

        item_name = self.result_tree.item(selected_item, "values")[0]
        current_price = self.data[item_name]["price"]
        current_quantity = self.data[item_name]["quantity"]

        new_name = simpledialog.askstring("Edit Item", "Enter New Item/Service Name:", initialvalue=item_name)
        if new_name is not None:
            new_price = simpledialog.askfloat("Edit Item", "Enter New Price:", initialvalue=current_price)
            if new_price is not None:
                new_quantity = simpledialog.askinteger("Edit Item", "Enter New Quantity:", initialvalue=current_quantity)
                if new_quantity is not None:
                    if new_price < 0 or new_quantity < 0:
                        messagebox.showerror("Error", "Price and quantity must be positive.")
                        return
                    del self.data[item_name]
                    self.data[new_name] = {"price": new_price, "quantity": new_quantity}
                    messagebox.showinfo("Item Edited", f"{new_name} updated.")
                    self.search_items()
                else:
                    messagebox.showerror("Error", "Invalid quantity input.")
            else:
                messagebox.showerror("Error", "Invalid price input.")

    def delete_item(self):
        selected_item = self.result_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        item_name = self.result_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {item_name}?")
        if confirm:
            del self.data[item_name]
            messagebox.showinfo("Item Deleted", f"{item_name} deleted.")
            self.search_items()

    def add_to_cart(self):
        selected_item = self.result_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to add to cart.")
            return

        item_name = self.result_tree.item(selected_item, "values")[0]
        quantity = simpledialog.askinteger("Add to Cart", f"Enter quantity for {item_name}:", initialvalue=1)
        if quantity is not None and quantity > 0:
            if item_name in self.cart:
                self.cart[item_name] += quantity
            else:
                self.cart[item_name] = quantity
            messagebox.showinfo("Added to Cart", f"{quantity} {item_name}(s) added to cart.")
        elif quantity is not None:
            messagebox.showerror("Error", "Quantity must be greater than 0.")
        else:
            messagebox.showerror("Error", "Invalid quantity input.")

    def view_cart(self):
        if not self.cart:
            messagebox.showinfo("Cart", "Your cart is empty.")
            return

        cart_window = tk.Toplevel(self.root)
        cart_window.title("Cart")
        cart_window.geometry("800x500")  # Set a fixed size for the cart window
        cart_window.resizable(False, False)  # Disable resizing
        cart_window.configure(bg="#f0f8ff")

        # Create a frame to hold the cart content
        cart_frame = tk.Frame(cart_window, bg="#f0f8ff")
        cart_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame in the window

        cart_tree = ttk.Treeview(cart_frame, columns=("Item", "Quantity", "Total Price"), show="headings")
        cart_tree.heading("Item", text="Item", anchor="center")
        cart_tree.heading("Quantity", text="Quantity", anchor="center")
        cart_tree.heading("Total Price", text="Total Price", anchor="center")
        cart_tree.pack(fill="both", expand=True, padx=10, pady=10)

        total_cost = 0
        for item, quantity in self.cart.items():
            price = self.data[item]["price"]
            total_price = price * quantity
            total_cost += total_price
            cart_tree.insert("", "end", values=(item, quantity, self.format_price(total_price)))

        total_label = tk.Label(cart_frame, text=f"Total Cost: {self.format_price(total_cost)}", font=("Arial", 14, "bold"), bg="#f0f8ff")
        total_label.pack(pady=10)

        button_frame = tk.Frame(cart_frame, bg="#f0f8ff")
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Remove Selected Item", command=lambda: self.remove_from_cart(cart_tree), style="Rounded.TButton").pack(side="left", padx=5)
        ttk.Button(button_frame, text="Checkout", command=lambda: self.checkout(cart_window), style="Rounded.TButton").pack(side="left", padx=5)

    def remove_from_cart(self, cart_tree):
        selected_item = cart_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to remove.")
            return

        item_name = cart_tree.item(selected_item, "values")[0]
        del self.cart[item_name]
        messagebox.showinfo("Item Removed", f"{item_name} removed from cart.")
        self.view_cart()

    def checkout(self, cart_window):
        if not self.cart:
            messagebox.showinfo("Checkout", "Your cart is empty.")
            return

        # Decrease the quantity of items in the inventory
        for item, quantity in self.cart.items():
            if item in self.data:
                self.data[item]["quantity"] -= quantity
                if self.data[item]["quantity"] < 0:  # Prevent negative quantities
                    self.data[item]["quantity"] = 0
                    messagebox.showwarning("Inventory Update", f"Insufficient stock for {item}. Quantity set to 0.")

        # Generate receipt
        self.generate_receipt()
        messagebox.showinfo("Checkout", "Thank you for your purchase!")
        self.cart.clear()  # Clear the cart
        cart_window.destroy()  # Close the cart window

    def generate_receipt(self):
        if not self.cart:
            return

        # Create receipt content
        receipt_content = "PC HUB MAGALANG\n\n"
        receipt_content += "Receipt\n"
        receipt_content += "Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
        receipt_content += "Items Purchased:\n"
        total_cost = 0
        for item, quantity in self.cart.items():
            price = self.data[item]["price"]
            total_price = price * quantity
            total_cost += total_price
            receipt_content += f"{item} x {quantity} = {self.format_price(total_price)}\n"
        receipt_content += f"\nTotal Cost: {self.format_price(total_cost)}\n"
        receipt_content += "\nThank you for shopping with us!"

        # Display receipt in a new window
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Receipt")
        receipt_window.geometry("400x400")
        receipt_window.configure(bg="#f0f8ff")

        receipt_text = tk.Text(receipt_window, wrap="word", font=("Courier", 12), bg="white", fg="black")
        receipt_text.insert("end", receipt_content)
        receipt_text.config(state="disabled")  # Make it read-only
        receipt_text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_data(self):
        if os.path.exists("data.json"):
            try:
                with open("data.json", "r") as f:
                    saved_data = json.load(f)
                    self.data = saved_data.get("data", {})
                    self.cart = saved_data.get("cart", {})
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Corrupted data file. Starting with empty data.")
                self.data = {}
                self.cart = {}
        else:
            self.data = {}
            self.cart = {}

    def save_data(self):
        with open("data.json", "w") as f:
            json.dump({"data": self.data, "cart": self.cart}, f)

    def on_close(self):
        self.save_data()  # Save data when closing
        self.root.destroy()


if _name_ == "_main_":
    root = tk.Tk()
    app = ProductServiceApp(root)
    root.mainloop()
tk.tk