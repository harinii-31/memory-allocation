import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Text, Scrollbar

class Train:
    def __init__(self, train_number, total_seats):
        self.train_number = train_number
        self.total_seats = total_seats
        self.booked_seats = 0
        self.waiting_list = []
        self.waiting_assigned_seats = []  # To track seats assigned from the waiting list

    def available_seats(self):
        return self.total_seats - self.booked_seats

    def book_ticket(self, passenger_id, num_tickets):
        if self.booked_seats + num_tickets <= self.total_seats:
            for _ in range(num_tickets):
                if len(self.waiting_list) > 0:
                    # Assign seat from the waiting list
                    self.waiting_assigned_seats.append(self.booked_seats)
                self.booked_seats += 1
            return True
        else:
            self.waiting_list.append((passenger_id, num_tickets))
            return False

    def cancel_ticket(self, passenger_id, num_tickets):
        if self.booked_seats >= num_tickets:
            self.booked_seats -= num_tickets
            self.discharge_from_waiting_list()
            return True
        return False

    def discharge_from_waiting_list(self):
        while self.waiting_list and self.available_seats() > 0:
            passenger_id, num_tickets = self.waiting_list[0]
            if self.book_ticket(passenger_id, num_tickets):
                messagebox.showinfo("Waiting List Update", f"Passenger {passenger_id} has been assigned a seat.")
                self.waiting_list.pop(0)
            else:
                break

    def view_seats(self):
        return f"Train {self.train_number}: Booked Seats: {self.booked_seats}, Available Seats: {self.available_seats()}"


class RailwayReservationSystem:
    def __init__(self):
        self.trains = []
        self.add_train(Train("Train1", 5))
        self.add_train(Train("Train2", 3))
        self.add_train(Train("Train3", 10))

    def add_train(self, train):
        self.trains.append(train)

    def first_fit(self, passenger_id, num_tickets):
        for train in self.trains:
            if train.book_ticket(passenger_id, num_tickets):
                return True
        return False

    def best_fit(self, passenger_id, num_tickets):
        best_train = None
        min_available = float('inf')
        for train in self.trains:
            if train.available_seats() >= num_tickets and train.available_seats() < min_available:
                best_train = train
                min_available = train.available_seats()
        if best_train:
            return best_train.book_ticket(passenger_id, num_tickets)
        return False

    def worst_fit(self, passenger_id, num_tickets):
        worst_train = None
        max_available = -1
        for train in self.trains:
            if train.available_seats() >= num_tickets and train.available_seats() > max_available:
                worst_train = train
                max_available = train.available_seats()
        if worst_train:
            return worst_train.book_ticket(passenger_id, num_tickets)
        return False

    def cancel_ticket(self, passenger_id, num_tickets):
        for train in self.trains:
            if train.cancel_ticket(passenger_id, num_tickets):
                return True
        return False

    def view_waiting_list(self):
        waiting_info = ""
        for train in self.trains:
            waiting_info += f"Train {train.train_number} Waiting List: {train.waiting_list}\n"
        return waiting_info if waiting_info else "No waiting list."

    def view_selected_seats(self):
        seat_info = ""
        for train in self.trains:
            seat_info += train.view_seats() + "\n"
        return seat_info if seat_info else "No trains available."


class RailwayReservationApp(tk.Tk):
    def __init__(self, railway_system):
        super().__init__()
        self.railway_system = railway_system
        self.title("Railway Reservation System")
        self.geometry("600x700")
        self.configure(bg="#f0f0f0")

        tk.Label(self, text="Railway Reservation System", font=("Arial", 20), bg="#f0f0f0").pack(pady=10)

        input_frame = Frame(self, bg="#f0f0f0")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Passenger Name:", bg="#f0f0f0").grid(row=0, column=0, sticky=tk.W)
        self.passenger_name_entry = tk.Entry(input_frame)
        self.passenger_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Number of Tickets:", bg="#f0f0f0").grid(row=1, column=0, sticky=tk.W)
        self.num_tickets_entry = tk.Entry(input_frame)
        self.num_tickets_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Booking Strategy:", bg="#f0f0f0").grid(row=2, column=0, sticky=tk.W)
        self.booking_strategy_var = tk.StringVar(value="First Fit")
        tk.Radiobutton(input_frame, text="First Fit", variable=self.booking_strategy_var, value="First Fit", bg="#f0f0f0").grid(row=2, column=1, sticky=tk.W)
        tk.Radiobutton(input_frame, text="Best Fit", variable=self.booking_strategy_var, value="Best Fit", bg="#f0f0f0").grid(row=2, column=2, sticky=tk.W)
        tk.Radiobutton(input_frame, text="Worst Fit", variable=self.booking_strategy_var, value="Worst Fit", bg="#f0f0f0").grid(row=2, column=3, sticky=tk.W)

        tk.Button(self, text="Book Ticket", command=self.book_ticket, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self, text="View Selected Seats", command=self.view_selected_seats, bg="#2196F3", fg="white").pack(pady=5)
        tk.Button(self, text="Cancel Ticket", command=self.cancel_ticket, bg="#f44336", fg="white").pack(pady=5)
        tk.Button(self, text="View Waiting List", command=self.view_waiting_list, bg="#FFC107").pack(pady=5)

        self.canvas = Canvas(self, width=500, height=350, bg="white")
        self.canvas.pack(pady=20)
        self.draw_seat_map()

        self.output_frame = Frame(self)
        self.output_frame.pack(pady=10)

        self.output_text = Text(self.output_frame, width=50, height=10, bg="#f0f0f0", wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT)

        self.scrollbar = Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def draw_seat_map(self):
        self.canvas.delete("all")
        x_start = 10
        y_start = 10
        seat_size = 30
        gap = 20

        for index, train in enumerate(self.railway_system.trains):
            y_offset = y_start + (seat_size + gap) * index * 2  # Adjusting vertical distance for train rows

            # Draw train number label above each train's seat map
            self.canvas.create_text(
                x_start, 
                y_offset, 
                text=f"{train.train_number}", 
                font=("Arial", 14, "bold"), 
                anchor=tk.W  # Align left
            )

            # Determine the number of rows needed for each train's seats
            rows = (train.total_seats // 5) + (train.total_seats % 5 > 0)

            for row in range(rows):
                for i in range(5):
                    seat_index = row * 5 + i
                    if seat_index >= train.total_seats:
                        break

                    # Check if the seat was assigned from the waiting list
                    if seat_index in train.waiting_assigned_seats:
                        color = "yellow"  # Waiting list assigned seat
                    elif seat_index < train.booked_seats:
                        color = "green"  # Normally booked seat
                    else:
                        color = "red"  # Available seat

                    # Draw seat rectangles
                    self.canvas.create_rectangle(
                        x_start + (seat_size + gap) * i,
                        y_offset + (seat_size + gap) * (row + 1),  # Align seat rows
                        x_start + (seat_size + gap) * i + seat_size,
                        y_offset + (seat_size + gap) * (row + 1) + seat_size,
                        fill=color
                    )

            # Draw the "Available Seats" text after the seats
            self.canvas.create_text(
                x_start + (seat_size + gap) * 6,  # Position to the right of seats
                y_offset + (seat_size + gap) * (rows + 1),  # Below the seat map
                text=f"Available: {train.available_seats()}",
                font=("Arial", 10, "italic")
            )

    def book_ticket(self):
        passenger_id = self.passenger_name_entry.get()
        try:
            num_tickets = int(self.num_tickets_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of tickets.")
            return

        strategy = self.booking_strategy_var.get()

        if strategy == "First Fit":
            booked = self.railway_system.first_fit(passenger_id, num_tickets)
        elif strategy == "Best Fit":
            booked = self.railway_system.best_fit(passenger_id, num_tickets)
        else:
            booked = self.railway_system.worst_fit(passenger_id, num_tickets)

        if booked:
            messagebox.showinfo("Success", "Tickets booked successfully!")
        else:
            messagebox.showinfo("Waiting List", "Added to the waiting list.")

        self.draw_seat_map()

    def cancel_ticket(self):
        passenger_id = self.passenger_name_entry.get()
        try:
            num_tickets = int(self.num_tickets_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of tickets.")
            return

        if self.railway_system.cancel_ticket(passenger_id, num_tickets):
            messagebox.showinfo("Success", "Tickets canceled successfully!")
        else:
            messagebox.showerror("Error", "Cancellation failed. Not enough booked seats or invalid operation.")
        self.draw_seat_map()

    def view_waiting_list(self):
        waiting_info = self.railway_system.view_waiting_list()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, waiting_info)

    def view_selected_seats(self):
        seat_info = self.railway_system.view_selected_seats()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, seat_info)


if __name__ == "__main__":
    railway_system = RailwayReservationSystem()
    app = RailwayReservationApp(railway_system)
    app.mainloop()
