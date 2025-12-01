import tkinter as tk
from tkinter import ttk, messagebox
from db import init_db, get_routes, search_schedules, book_ticket, get_booking, cancel_booking

def show_routes_window():
    routes = get_routes()
    win = tk.Toplevel(root)
    win.title("Available Routes")
    text = tk.Text(win, width=50, height=15)
    text.pack(padx=10, pady=10)
    if not routes:
        text.insert(tk.END, "No routes found.\n")
    else:
        text.insert(tk.END, "Available Routes:\n\n")
        for i, (src, dst) in enumerate(routes, start=1):
            text.insert(tk.END, f"{i}. {src} -> {dst}\n")
    text.config(state="disabled")

def search_and_book_window():
    win = tk.Toplevel(root)
    win.title("Search and Book Trains")

    search_frame = ttk.LabelFrame(win, text="Search Trains")
    search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    tk.Label(search_frame, text="Source").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Label(search_frame, text="Destination").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    tk.Label(search_frame, text="Travel Date (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=5, sticky="e")

    routes = get_routes()
    sources = sorted({src for (src, dst) in routes})
    destinations_map = {}
    for src, dst in routes:
        destinations_map.setdefault(src, set()).add(dst)

    src_var = tk.StringVar()
    dst_var = tk.StringVar()
    date_var = tk.StringVar()

    src_dropdown = ttk.Combobox(search_frame, textvariable=src_var, values=sources, state="readonly")
    src_dropdown.grid(row=0, column=1, padx=5, pady=5)

    dst_dropdown = ttk.Combobox(search_frame, textvariable=dst_var, values=[], state="readonly")
    dst_dropdown.grid(row=1, column=1, padx=5, pady=5)

    def update_destinations(event):
        selected_src = src_var.get()
        if selected_src in destinations_map:
            dst_dropdown["values"] = sorted(destinations_map[selected_src])
            dst_var.set("")
        else:
            dst_dropdown["values"] = []
            dst_var.set("")

    src_dropdown.bind("<<ComboboxSelected>>", update_destinations)

    tk.Entry(search_frame, textvariable=date_var).grid(row=2, column=1, padx=5, pady=5)

    result_frame = ttk.LabelFrame(win, text="Available Trains")
    result_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    columns = ("schedule_id", "train_number", "train_name", "date", "dep", "arr", "fare", "seats")
    tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
    for col in columns:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=100)
    tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky="ns")

    result_frame.rowconfigure(0, weight=1)
    result_frame.columnconfigure(0, weight=1)

    booking_frame = ttk.LabelFrame(win, text="Book Selected Train")
    booking_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    tk.Label(booking_frame, text="Selected Schedule ID").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Label(booking_frame, text="Seats").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    tk.Label(booking_frame, text="Name").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tk.Label(booking_frame, text="Phone").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    tk.Label(booking_frame, text="Email").grid(row=4, column=0, padx=5, pady=5, sticky="e")

    selected_schedule_var = tk.StringVar()
    seats_var = tk.StringVar()
    name_var = tk.StringVar()
    phone_var = tk.StringVar()
    email_var = tk.StringVar()

    tk.Entry(booking_frame, textvariable=selected_schedule_var, state="readonly").grid(row=0, column=1, padx=5, pady=5)
    tk.Entry(booking_frame, textvariable=seats_var).grid(row=1, column=1, padx=5, pady=5)
    tk.Entry(booking_frame, textvariable=name_var).grid(row=2, column=1, padx=5, pady=5)
    tk.Entry(booking_frame, textvariable=phone_var).grid(row=3, column=1, padx=5, pady=5)
    tk.Entry(booking_frame, textvariable=email_var).grid(row=4, column=1, padx=5, pady=5)

    def do_search():
        for row in tree.get_children():
            tree.delete(row)
        selected_schedule_var.set("")

        source = src_var.get().strip()
        destination = dst_var.get().strip()
        travel_date = date_var.get().strip()

        if not source or not destination or not travel_date:
            messagebox.showwarning("Input Error", "Please fill Source, Destination and Travel Date")
            return

        rows = search_schedules(source, destination, travel_date)
        if not rows:
            messagebox.showinfo("No Results", "No trains found for given details")
            return

        for r in rows:
            tree.insert("", tk.END, values=r)

    def on_tree_select(event):
        selected = tree.focus()
        if not selected:
            return
        values = tree.item(selected, "values")
        if values:
            selected_schedule_var.set(values[0])

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    def do_book():
        schedule_id_str = selected_schedule_var.get().strip()
        seats_str = seats_var.get().strip()

        if not schedule_id_str:
            messagebox.showwarning("Selection Error", "Please select a train from the list")
            return
        if not seats_str:
            messagebox.showwarning("Input Error", "Please enter number of seats")
            return

        try:
            schedule_id = int(schedule_id_str)
            seats = int(seats_str)
        except ValueError:
            messagebox.showerror("Input Error", "Schedule ID and Seats must be numbers")
            return

        name = name_var.get().strip()
        phone = phone_var.get().strip()
        email = email_var.get().strip()

        if not name or not phone:
            messagebox.showwarning("Input Error", "Name and Phone are required")
            return

        try:
            booking_id = book_ticket(schedule_id, name, phone, email, seats)
        except Exception as e:
            messagebox.showerror("Booking Failed", str(e))
            return

        messagebox.showinfo("Success", f"Booking successful.\nYour Booking ID is {booking_id}")
        seats_var.set("")
        name_var.set("")
        phone_var.set("")
        email_var.set("")

    tk.Button(search_frame, text="Search", command=do_search).grid(row=3, column=0, columnspan=2, pady=8)
    tk.Button(booking_frame, text="Book Ticket", command=do_book).grid(row=5, column=0, columnspan=2, pady=10)

def view_booking_window():
    win = tk.Toplevel(root)
    win.title("View Booking")

    tk.Label(win, text="Booking ID").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    booking_var = tk.StringVar()
    tk.Entry(win, textvariable=booking_var).grid(row=0, column=1, padx=5, pady=5)

    text = tk.Text(win, width=60, height=15)
    text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    text.config(state="disabled")

    def do_view():
        b_id_str = booking_var.get().strip()
        try:
            booking_id = int(b_id_str)
        except ValueError:
            messagebox.showerror("Input Error", "Booking ID must be a number")
            return

        row = get_booking(booking_id)
        text.config(state="normal")
        text.delete("1.0", tk.END)
        if not row:
            text.insert(tk.END, "Booking not found\n")
        else:
            (
                bid, status, seats, booked_at,
                name, phone, email,
                travel_date, dep, arr, fare,
                train_number, train_name, src, dst,
            ) = row
            text.insert(tk.END, f"Booking ID   : {bid}\n")
            text.insert(tk.END, f"Status       : {status}\n")
            text.insert(tk.END, f"Seats        : {seats}\n")
            text.insert(tk.END, f"Booked At    : {booked_at}\n\n")
            text.insert(tk.END, f"Passenger    : {name}\n")
            text.insert(tk.END, f"Phone        : {phone}\n")
            text.insert(tk.END, f"Email        : {email}\n\n")
            text.insert(tk.END, f"Route        : {src} -> {dst}\n")
            text.insert(tk.END, f"Train        : {train_number} - {train_name}\n")
            text.insert(tk.END, f"Travel Date  : {travel_date}\n")
            text.insert(tk.END, f"Departure    : {dep}\n")
            text.insert(tk.END, f"Arrival      : {arr}\n")
            text.insert(tk.END, f"Fare/Seat    : {float(fare)}\n")
            text.insert(tk.END, f"Total Fare   : {float(fare) * seats}\n")
        text.config(state="disabled")

    tk.Button(win, text="View", command=do_view).grid(row=1, column=0, columnspan=2, pady=5)

def cancel_booking_window():
    win = tk.Toplevel(root)
    win.title("Cancel Booking")

    tk.Label(win, text="Booking ID").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    booking_var = tk.StringVar()
    tk.Entry(win, textvariable=booking_var).grid(row=0, column=1, padx=5, pady=5)

    def do_cancel():
        b_id_str = booking_var.get().strip()
        try:
            booking_id = int(b_id_str)
        except ValueError:
            messagebox.showerror("Input Error", "Booking ID must be a number")
            return
        try:
            cancel_booking(booking_id)
        except Exception as e:
            messagebox.showerror("Cancel Failed", str(e))
            return
        messagebox.showinfo("Success", "Booking cancelled successfully")

    tk.Button(win, text="Cancel Booking", command=do_cancel).grid(row=1, column=0, columnspan=2, pady=10)

root = tk.Tk()
root.title("Online Train Ticket Reservation")

init_db()

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(main_frame, text="Online Train Ticket Reservation", font=("Segoe UI", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

ttk.Button(main_frame, text="View Routes", width=25, command=show_routes_window).grid(row=1, column=0, pady=5, padx=10)
ttk.Button(main_frame, text="Search & Book Trains", width=25, command=search_and_book_window).grid(row=1, column=1, pady=5, padx=10)
ttk.Button(main_frame, text="View Booking", width=25, command=view_booking_window).grid(row=2, column=0, pady=5, padx=10)
ttk.Button(main_frame, text="Cancel Booking", width=25, command=cancel_booking_window).grid(row=2, column=1, pady=5, padx=10)
ttk.Button(main_frame, text="Exit", width=25, command=root.destroy).grid(row=3, column=0, columnspan=2, pady=15)

root.mainloop()
