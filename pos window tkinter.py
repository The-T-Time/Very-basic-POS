import tkinter as tk
import datetime
#import sys
import math

#screen settings, colors, and fonts
WIDTH, HEIGHT = 1280, 720
WHITE      = "#FFFFFF"
BLACK      = "#000000"
GRAY       = "#646464"
LIGHT_GRAY = "#A0A0A0"
font     = ("Arial", 15, "bold")
big_font = ("Arial", 25, "bold")
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50

#dictionary for menu
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

#navigation variables
finished_selected_index = 0
confirmation_selected_index = 0
current_page = "menu"
menu_mode = "grid"
menu_button_index = 1
selected_index = 0  

#order class
class Order:
    def __init__(self):
        self.items = []
        self.prices = []
        self.tip_pct = 0

    def add_item(self, item, price):
        self.items.append(item)
        self.prices.append(price)

    def calculate_totals(self):
        subtotal = sum(self.prices)
        tax = subtotal * 0.0735
        tip = subtotal * (self.tip_pct / 100)
        total = subtotal + tax + tip
        return subtotal, tax, tip, total

    def reset(self):
        self.items = []
        self.prices = []
        self.tip_pct = 0

order = Order()

#globals for mouse clicking rectangles
last_next_button_rect = None
last_menu_item_rects = []
last_remove_button_rect = None

'''functions to draw everything'''

#function to draw text
def draw_text(canvas, text, center, color=WHITE, font_obj=font):
    canvas.create_text(center[0], center[1], text=text, fill=color, font=font_obj)

#function to draw a button(that isnt in a grid)
def draw_button(canvas, text, rect, font_obj=font, text_color=WHITE, button_color=GRAY):
    x, y, w, h = rect
    canvas.create_rectangle(x, y, x+w, y+h, fill=button_color, outline=BLACK, width=2)
    draw_text(canvas, text, (x+w/2, y+h/2), color=text_color, font_obj=font_obj)

#function to draw the selected items box
def draw_selectedItems_and_removeButton(canvas, highlight_remove=False):
    area_rect = (10, HEIGHT - 140, WIDTH // 2 - 15, 130)
    x, y, w, h = area_rect
    canvas.create_rectangle(x, y, x+w, y+h, fill=BLACK, outline=GRAY, width=2)
    draw_text(canvas, "Selected Items:", (x+w/2, y+20), font_obj=big_font)
    header_offset = 45
    available_height = h - header_offset
    line_height = 20 + 4
    max_rows = max(1, available_height // line_height)
    num_items = len(order.items)
    num_columns = math.ceil(num_items / max_rows) if num_items > 0 else 1
    column_width = w // num_columns if num_columns > 0 else w
    for i, item in enumerate(order.items):
        col = i // max_rows
        row = i % max_rows
        item_x = x + col * column_width + column_width // 2
        item_y = y + header_offset + row * line_height
        draw_text(canvas, item, (item_x, item_y), font_obj=font)
    
    #remove button
    remove_button_rect = (WIDTH - BUTTON_WIDTH - 487, HEIGHT - BUTTON_HEIGHT - 92, BUTTON_WIDTH, BUTTON_HEIGHT)
    if highlight_remove:
        draw_button(canvas, "Remove", remove_button_rect, button_color=LIGHT_GRAY)
    else:
        draw_button(canvas, "Remove", remove_button_rect)
    return area_rect, remove_button_rect

#function to draw menu page
def draw_menu(canvas):
    global last_next_button_rect, last_menu_item_rects, last_remove_button_rect, selected_index, menu_mode, menu_button_index
    canvas.delete("all")
    menu_items = list(menu.keys())
    cols = 4
    rows = math.ceil(len(menu_items) / cols)
    padding = 10
    available_height = HEIGHT - 150
    box_width = (WIDTH - (cols + 1) * padding) // cols
    box_height = (available_height - (rows + 1) * padding) // rows

    last_menu_item_rects = []
    for i, item in enumerate(menu_items):
        col = i % cols
        row = i // cols
        rect_x = padding + col * (box_width + padding)
        rect_y = padding + row * (box_height + padding)
        rect = (rect_x, rect_y, box_width, box_height)
        last_menu_item_rects.append((rect, i))
        if menu_mode == "grid" and i == selected_index:
            canvas.create_rectangle(rect_x, rect_y, rect_x+box_width, rect_y+box_height, fill=GRAY)
        else:
            canvas.create_rectangle(rect_x, rect_y, rect_x+box_width, rect_y+box_height, outline=GRAY, width=2)
        text = f"{item} - ${menu[item]:.2f}"
        draw_text(canvas, text, (rect_x+box_width/2, rect_y+box_height/2))
    
    #draw the selected items area and remove button
    _, remove_button_rect = draw_selectedItems_and_removeButton(canvas, highlight_remove=(menu_mode=="buttons" and menu_button_index==0))
    last_remove_button_rect = remove_button_rect

    #draw the next button
    next_button_rect = (WIDTH - BUTTON_WIDTH - 10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    if menu_mode == "buttons" and menu_button_index == 1:
        draw_button(canvas, "Next", next_button_rect, button_color=LIGHT_GRAY)
    else:
        draw_button(canvas, "Next", next_button_rect)
    last_next_button_rect = next_button_rect

#function to draw confirmation page
def draw_confirmation(canvas):
    canvas.delete("all")
    draw_text(canvas, "Order Confirmation", (WIDTH // 2, 40), font_obj=big_font)
    subtotal, tax, tip, total = order.calculate_totals()
    summary_lines = [
        f"Subtotal: ${subtotal:.2f}",
        f"Tax (7.35%): ${tax:.2f}",
        f"Tip ({order.tip_pct}%): ${tip:.2f}",
        f"Total: ${total:.2f}"
    ]
    start_y = 120
    for line in summary_lines:
        draw_text(canvas, line, (WIDTH // 2, start_y))
        start_y += 40

    # Tip-change button
    tip_button_rect = (WIDTH//2 - 150, HEIGHT - 180, 300, 40)
    if confirmation_selected_index == 0:
        draw_button(canvas, "Change Tip", tip_button_rect, button_color=LIGHT_GRAY)
    else:
        draw_button(canvas, "Change Tip", tip_button_rect)
    
    #back and finish order buttons
    back_button_rect = (10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    finish_button_rect = (WIDTH - BUTTON_WIDTH - 10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    if confirmation_selected_index == 1:
        draw_button(canvas, "Back", back_button_rect, button_color=LIGHT_GRAY)
        draw_button(canvas, "Finish Order", finish_button_rect)
    elif confirmation_selected_index == 2:
        draw_button(canvas, "Back", back_button_rect)
        draw_button(canvas, "Finish Order", finish_button_rect, button_color=LIGHT_GRAY)
    else:
        draw_button(canvas, "Back", back_button_rect)
        draw_button(canvas, "Finish Order", finish_button_rect)
    return back_button_rect, finish_button_rect, tip_button_rect

#function to draw finished page
def draw_finished(canvas):
    canvas.delete("all")
    draw_text(canvas, "Order complete! Would you like another order?", (WIDTH // 2, HEIGHT // 2 - 40), font_obj=big_font)
    yes_rect = (WIDTH // 2 - BUTTON_WIDTH - 20, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    no_rect = (WIDTH // 2 + 20, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    if finished_selected_index == 0:
        draw_button(canvas, "Yes", yes_rect, button_color=LIGHT_GRAY)
        draw_button(canvas, "No", no_rect)
    else:
        draw_button(canvas, "Yes", yes_rect)
        draw_button(canvas, "No", no_rect, button_color=LIGHT_GRAY)
    return yes_rect, no_rect

#function to print receipt
def print_receipt():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("-" * 40)
    print(f"{'IN-N-OUT BURGER':^40}")
    print(f"{('Date: ' + now):^40}")
    print("-" * 40)
    for meal in order.items:
        price = menu[meal]
        print(f"{meal.capitalize():<32}{f'${price:.2f}':>8}")
    print("-" * 40)
    subtotal, tax, tip, total = order.calculate_totals()
    print(f"{'Subtotal':<32}{f'${subtotal:.2f}':>8}")
    print(f"{'Tax':<32}{f'${tax:.2f}':>8}")
    print(f"{'Tip':<32}{f'${tip:.2f}':>8}")
    print("-" * 40)
    print(f"{'Total':<32}{f'${total:.2f}':>8}")
    print("-" * 40)
    print("Thank you for dining with us!")
    print("We appreciate your visit.")
    print("-" * 40)

#function to reset everything
def reset_order():
    global finished_selected_index, confirmation_selected_index, menu_mode, menu_button_index, selected_index
    order.reset()
    finished_selected_index = 0
    confirmation_selected_index = 0
    menu_mode = "grid"
    menu_button_index = 1
    selected_index = 0

#check if point if point is in rectangle for mouse
def point_in_rect(x, y, rect):
    rx, ry, rw, rh = rect
    return rx <= x <= rx+rw and ry <= y <= ry+rh

#changes pages
def update_screen():
    if current_page == "menu":
        draw_menu(canvas)
    elif current_page == "confirmation":
        draw_confirmation(canvas)
    elif current_page == "finished":
        draw_finished(canvas)

#function for keyboard clicks
def on_key_press(event):
    global current_page, selected_index, menu_mode, menu_button_index
    global confirmation_selected_index, finished_selected_index

    if current_page == "menu":
        menu_items = list(menu.keys())
        cols = 4
        rows = math.ceil(len(menu_items) / cols)
        if menu_mode == "grid":
            row = selected_index // cols
            col = selected_index % cols
            if event.keysym == "Left":
                col = col - 1 if col > 0 else cols - 1
            elif event.keysym == "Right":
                col = col + 1 if col < cols - 1 else 0
            elif event.keysym == "Up":
                if row == 0:
                    menu_mode = "buttons"
                    menu_button_index = 0 if col < 2 else 1
                    update_screen()
                    return
                else:
                    row -= 1
            elif event.keysym == "Down":
                if row == rows - 1:
                    menu_mode = "buttons"
                    menu_button_index = 0 if col < 2 else 1
                    update_screen()
                    return
                else:
                    row += 1
            elif event.keysym in ("Return", "KP_Enter"):
                order.add_item(menu_items[selected_index], menu[menu_items[selected_index]])
            elif event.keysym == "BackSpace":
                for i in range(len(order.items) - 1, -1, -1):
                    if order.items[i] == menu_items[selected_index]:
                        order.items.pop(i)
                        order.prices.pop(i)
                        break
            new_index = row * cols + col
            if new_index >= len(menu_items):
                new_index = len(menu_items) - 1
            selected_index = new_index

        elif menu_mode == "buttons":
            if event.keysym in ("Left", "Right"):
                menu_button_index = 0 if menu_button_index == 1 else 1
            elif event.keysym == "Up":
                menu_mode = "grid"
                new_index = (rows - 1) * cols + (0 if menu_button_index == 0 else 2)
                if new_index >= len(menu_items):
                    new_index = len(menu_items) - 1
                selected_index = new_index
            elif event.keysym == "Down":
                menu_mode = "grid"
                selected_index = 0 if menu_button_index == 0 else (2 if len(menu_items) > 2 else 0)
            elif event.keysym in ("Return", "KP_Enter"):
                if menu_button_index == 0:
                    if order.items:
                        order.items.pop()
                        order.prices.pop()
                elif menu_button_index == 1:
                    if order.items:
                        current_page = "confirmation"
                        menu_mode = "grid"

    elif current_page == "confirmation":
        if event.keysym in ("Left", "Right"):
            if confirmation_selected_index == 0:
                confirmation_selected_index = 1 if event.keysym == "Left" else 2
            elif confirmation_selected_index == 1:
                if event.keysym == "Right":
                    confirmation_selected_index = 0
                else:
                    confirmation_selected_index = 1
            elif confirmation_selected_index == 2:
                if event.keysym == "Left":
                    confirmation_selected_index = 0
                else:
                    confirmation_selected_index = 2
        elif event.keysym in ("Return", "KP_Enter"):
            if confirmation_selected_index == 0:
                order.tip_pct = (order.tip_pct + 5) % 35
            elif confirmation_selected_index == 1:
                current_page = "menu"
            elif confirmation_selected_index == 2:
                print_receipt()
                current_page = "finished"
        elif event.keysym == "Escape":
            root.quit()

    elif current_page == "finished":
        if event.keysym in ("Left", "Right"):
            finished_selected_index = 1 - finished_selected_index
        elif event.keysym in ("Return", "KP_Enter"):
            if finished_selected_index == 0:
                reset_order()
                current_page = "menu"
            else:
                root.quit()
    update_screen()

#function for mouse clicks
def on_mouse_click(event):
    global current_page, selected_index, menu_mode, menu_button_index, finished_selected_index
    x, y = event.x, event.y

    if current_page == "menu":
        if point_in_rect(x, y, last_remove_button_rect):
            if order.items:
                order.items.pop()
                order.prices.pop()
        elif point_in_rect(x, y, last_next_button_rect):
            if order.items:
                current_page = "confirmation"
                menu_mode = "grid"
        else:
            for rect, index in last_menu_item_rects:
                if point_in_rect(x, y, rect):
                    selected_index = index
                    item = list(menu.keys())[index]
                    order.add_item(item, menu[item])
                    menu_mode = "grid"
                    break

    elif current_page == "confirmation":
        back_button_rect, finish_button_rect, tip_button_rect = draw_confirmation(canvas)
        if point_in_rect(x, y, tip_button_rect):
            order.tip_pct = (order.tip_pct + 5) % 35
        elif point_in_rect(x, y, back_button_rect):
            current_page = "menu"
        elif point_in_rect(x, y, finish_button_rect):
            print_receipt()
            current_page = "finished"

    elif current_page == "finished":
        yes_rect, no_rect = draw_finished(canvas)
        if point_in_rect(x, y, yes_rect):
            reset_order()
            current_page = "menu"
        elif point_in_rect(x, y, no_rect):
            root.quit()
    update_screen()

#main function
def main():
    global root, canvas
    root = tk.Tk()
    root.title("POS System")
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BLACK)
    canvas.pack()
    canvas.focus_set()
    canvas.bind("<Key>", on_key_press)
    canvas.bind("<Button-1>", on_mouse_click)
    update_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
