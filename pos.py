import datetime

#dictionary for menu and prices
menu = {
    "double-double": 5.90,
    "cheeseburger": 4.10,
    "hamburger": 3.60,
    "fries": 2.30,
    "shake": 3.00,
    "small drink": 2.10,
    "medium drink": 2.25,
    "large drink": 2.45,
    "x-large drink": 2.65,
    "milk": 0.99,
    "hot cocoa": 2.25,
    "coffee": 1.35
}

#function for yes or no
def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ('yes', 'no'):
            return answer == 'yes'
        print("Please enter 'yes' or 'no'.")

#function for meal selection
def get_meals():
    selected_items = []
    while True:
        meal = input(f"\nWhat would you like to order? {', '.join(menu.keys())}: ").strip().lower()
        if meal in menu:
            selected_items.append(meal)
        else:
            print("Sorry, we don't have that item. Please choose from the menu.")
        
        if not ask_yes_no("\nWould you like to add another item? (yes/no): "):
            if not selected_items:
                print("You haven't selected any items. Please add at least one item.")
                continue
            break
    return selected_items

#function for tip
def get_tip(subtotal):
    while True:
        try:
            tip_percentage = float(input("\nEnter tip percentage (e.g., 10 for 10% or 0 for none): "))
            if tip_percentage >= 0:
                return subtotal * tip_percentage / 100
            print("Tip percentage cannot be negative.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

#function for receipt
def print_receipt(selected_items, subtotal, tax, tip, total):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("-" * 40)
    print(f"{'IN-N-OUT BURGER':^40}")
    print(f"{('Date: ' + now):^40}")
    print("-" * 40)
    for meal in selected_items:
        price = menu[meal]
        print(f"{meal.capitalize():<32}{f'${price:.2f}':>8}")
    print("-" * 40)
    print(f"{'Subtotal':<32}{f'${subtotal:.2f}':>8}")
    print(f"{'Tax':<32}{f'${tax:.2f}':>8}")
    print(f"{'Tip':<32}{f'${tip:.2f}':>8}")
    print("-" * 40)
    print(f"{'Total':<32}{f'${total:.2f}':>8}")
    print("-" * 40)
    print("Thank you for dining with us!")
    print("We appreciate your visit.")
    print("-" * 40)

#main function
def main():
    while True:
        print("\nStarting a new order...")
        selected_items = get_meals()
        subtotal = sum(menu[item] for item in selected_items)
        tax = subtotal * 0.0735
        tip = get_tip(subtotal)
        total = subtotal + tax + tip
        print_receipt(selected_items, subtotal, tax, tip, total)
        
        if not ask_yes_no("Another order? (yes/no): "):
            print("Goodbye! Have a great day!")
            break

if __name__ == "__main__":
    main()