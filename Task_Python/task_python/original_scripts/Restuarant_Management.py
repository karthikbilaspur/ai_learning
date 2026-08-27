from tkinter import *
import random

class RestaurantManagementSystem:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("1600x800+0+0")

        self.fries = StringVar()
        self.burger = StringVar()
        self.filet = StringVar()
        self.chicken_burger = StringVar()
        self.cheese_burger = StringVar()
        self.drinks = StringVar()
        self.cost = StringVar()
        self.service_charge = StringVar()
        self.tax = StringVar()
        self.sub_total = StringVar()
        self.total = StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Create frames
        self.top_frame = Frame(self.root, width=1600, height=600, bg="white", relief=GROOVE)
        self.top_frame.pack(side=TOP)

        self.left_frame = Frame(self.root, width=900, height=700, bg="white", relief=GROOVE)
        self.left_frame.pack(side=LEFT)

        self.right_frame = Frame(self.root, width=300, height=700, bg="sky blue", relief=GROOVE)
        self.right_frame.pack(side=RIGHT)

        # Create labels and entries
        self.create_labels_and_entries()

        # Create buttons
        self.create_buttons()

    def create_labels_and_entries(self):
        # Create labels and entries for left frame
        Label(self.left_frame, font=('arial', 16, 'bold'), text="Fries").grid(row=0, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.fries).grid(row=0, column=1)

        Label(self.left_frame, font=('arial', 16, 'bold'), text="Burger").grid(row=1, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.burger).grid(row=1, column=1)

        Label(self.left_frame, font=('arial', 16, 'bold'), text="Filet").grid(row=2, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.filet).grid(row=2, column=1)

        Label(self.left_frame, font=('arial', 16, 'bold'), text="Chicken Burger").grid(row=3, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.chicken_burger).grid(row=3, column=1)

        Label(self.left_frame, font=('arial', 16, 'bold'), text="Cheese Burger").grid(row=4, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.cheese_burger).grid(row=4, column=1)

        Label(self.left_frame, font=('arial', 16, 'bold'), text="Drinks").grid(row=5, column=0)
        Entry(self.left_frame, font=('arial', 16, 'bold'), textvariable=self.drinks).grid(row=5, column=1)

        # Create labels and entries for right frame
        Label(self.right_frame, font=('arial', 16, 'bold'), text="Cost").grid(row=0, column=0)
        Entry(self.right_frame, font=('arial', 16, 'bold'), textvariable=self.cost).grid(row=0, column=1)

        Label(self.right_frame, font=('arial', 16, 'bold'), text="Service Charge").grid(row=1, column=0)
        Entry(self.right_frame, font=('arial', 16, 'bold'), textvariable=self.service_charge).grid(row=1, column=1)

        Label(self.right_frame, font=('arial', 16, 'bold'), text="Tax").grid(row=2, column=0)
        Entry(self.right_frame, font=('arial', 16, 'bold'), textvariable=self.tax).grid(row=2, column=1)

        Label(self.right_frame, font=('arial', 16, 'bold'), text="Sub Total").grid(row=3, column=0)
        Entry(self.right_frame, font=('arial', 16, 'bold'), textvariable=self.sub_total).grid(row=3, column=1)

        Label(self.right_frame, font=('arial', 16, 'bold'), text="Total").grid(row=4, column=0)
        Entry(self.right_frame, font=('arial', 16, 'bold'), textvariable=self.total).grid(row=4, column=1)

    def create_buttons(self):
        Button(self.right_frame, text="Total", command=self.calculate_total).grid(row=5, column=0)
        Button(self.right_frame, text="Reset", command=self.reset).grid(row=5, column=1)
        Button(self.right_frame, text="Exit", command=self.root.destroy).grid(row=6, column=0, columnspan=2)

    def calculate_total(self):
        try:
            fries = float(self.fries.get())
            burger = float(self.burger.get())
            filet = float(self.filet.get())
            chicken_burger = float(self.chicken_burger.get())
            cheese_burger = float(self.cheese_burger.get())
            drinks = float(self.drinks.get())

            total_cost = fries + burger + filet + chicken_burger + cheese_burger + drinks
            service_charge = total_cost * 0.1
            tax = total_cost * 0.08
            sub_total = total_cost + service_charge + tax

            self.cost.set(total_cost)
            self.service_charge.set(service_charge)
            self.tax.set(tax)
            self.sub_total.set(sub_total)
            self.total.set(sub_total)
        except ValueError:
            print("Error: Invalid input values")

    def reset(self):
        self.fries.set("")
        self.burger.set("")
        self.filet.set("")
        self.chicken_burger.set("")
        self.cheese_burger.set("")
        self.drinks.set("")
        self.cost.set("")
        self.service_charge.set("")
        self.tax.set("")
        self.sub_total.set("")
        self.total.set("")

if __name__ == "__main__":
    root = Tk()
    app = RestaurantManagementSystem(root)
    root.mainloop()