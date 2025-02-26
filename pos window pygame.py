import pygame
import datetime
import sys
import math

pygame.init()

#screen settings, colors, and fonts
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("POS System")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (160, 160, 160)
font = pygame.font.SysFont("Arial", 20, bold=True)
big_font = pygame.font.SysFont("Arial", 30, bold=True)
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
finished_index = 0
confirmation_index = 0
current_page = "menu"
menu_mode = "grid"
menu_button_index = 1

#order class
class Order:
    def __init__(self):
        self.items = []
        self.prices = []
        self.tip_pct = 0

    def add(self, item, price):
        self.items.append(item)
        self.prices.append(price)

    def totals(self):
        subtotal = sum(self.prices)
        tax = subtotal * 0.0735
        tip = subtotal * (self.tip_pct / 100)
        return subtotal, tax, tip, subtotal + tax + tip

    def reset(self):
        self.items.clear()
        self.prices.clear()
        self.tip_pct = 0

order = Order()

'''functions to draw everything'''

#function to draw text
def draw_text(text, center, color=WHITE, font_obj=font):
    surface = font_obj.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))

#function to draw a button(that isnt in a grid)
def draw_button(text, rect, font_obj=font, text_color=WHITE, button_color=GRAY):
    pygame.draw.rect(screen, button_color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    surface = font_obj.render(text, True, text_color)
    screen.blit(surface, surface.get_rect(center=rect.center))

#function to draw the selected items box
def draw_selected_items(highlight_remove=False):
    area_rect = pygame.Rect(10, HEIGHT - 140, WIDTH // 2 - 15, 130)
    pygame.draw.rect(screen, BLACK, area_rect)
    pygame.draw.rect(screen, GRAY, area_rect, 2)
    draw_text("Selected Items:", (area_rect.centerx, area_rect.y + 20), font_obj=big_font)
    header = 40
    line_height = font.get_height() + 4
    max_rows = max(1, (area_rect.height - header) // line_height)
    num_cols = math.ceil(len(order.items) / max_rows) if order.items else 1
    col_width = area_rect.width // num_cols
    for i, item in enumerate(order.items):
        col, row = i // max_rows, i % max_rows
        x = area_rect.x + col * col_width + col_width // 2
        y = area_rect.y + header + row * line_height
        draw_text(item, (x, y), font_obj=font)
    return area_rect

#function to draw menu page
def draw_menu(selected_index):
    screen.fill(BLACK)
    items = list(menu.keys())
    cols = 4
    rows = (len(items) + cols - 1) // cols
    pad = 10
    avail_h = HEIGHT - 150
    box_w = (WIDTH - (cols + 1) * pad) // cols
    box_h = (avail_h - (rows + 1) * pad) // rows
    menu_item_rects = []
    
    for i, item in enumerate(items):
        col, row = i % cols, i // cols
        rect = pygame.Rect(pad + col * (box_w + pad), pad + row * (box_h + pad), box_w, box_h)
        menu_item_rects.append((rect, i))
        if menu_mode == "grid" and i == selected_index:
            pygame.draw.rect(screen, GRAY, rect)
        else:
            pygame.draw.rect(screen, GRAY, rect, 2)
        draw_text(f"{item} - ${menu[item]:.2f}", rect.center)
    
    #draw the selected items box
    draw_selected_items(highlight_remove=(menu_mode == "buttons" and menu_button_index == 0))
    
    #remove button
    remove_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 487, HEIGHT - BUTTON_HEIGHT - 92, BUTTON_WIDTH, BUTTON_HEIGHT)
    draw_button("Remove", remove_rect, button_color=LIGHT_GRAY if (menu_mode == "buttons" and menu_button_index == 0) else GRAY)

    #next button
    next_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    draw_button("Next", next_rect, button_color=LIGHT_GRAY if (menu_mode == "buttons" and menu_button_index == 1) else GRAY)
    
    return next_rect, menu_item_rects, remove_rect

#function to draw confirmation page
def draw_confirmation():
    screen.fill(BLACK)
    draw_text("Order Confirmation", (WIDTH // 2, 40), font_obj=big_font)
    subtotal, tax, tip, total = order.totals()
    for i, line in enumerate([f"Subtotal: ${subtotal:.2f}",
                              f"Tax (7.35%): ${tax:.2f}",
                              f"Tip ({order.tip_pct}%): ${tip:.2f}",
                              f"Total: ${total:.2f}"]):
        draw_text(line, (WIDTH // 2, 120 + 40 * i))
    tip_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 180, 300, 40)
    draw_button("Change Tip", tip_rect, button_color=LIGHT_GRAY if confirmation_index == 0 else GRAY)
    back_rect = pygame.Rect(10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    finish_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)
    if confirmation_index == 1:
        draw_button("Back", back_rect, button_color=LIGHT_GRAY)
        draw_button("Finish Order", finish_rect, font_obj=font)
    elif confirmation_index == 2:
        draw_button("Back", back_rect)
        draw_button("Finish Order", finish_rect, font_obj=font, button_color=LIGHT_GRAY)
    else:
        draw_button("Back", back_rect)
        draw_button("Finish Order", finish_rect, font_obj=font)
    return back_rect, finish_rect, tip_rect

#function to draw finished page
def draw_finished(sel_index):
    screen.fill(BLACK)
    draw_text("Order complete! Would you like another order?", (WIDTH // 2, HEIGHT // 2 - 40), font_obj=big_font)
    yes_rect = pygame.Rect(WIDTH // 2 - BUTTON_WIDTH - 20, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    no_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    draw_button("Yes", yes_rect, button_color=LIGHT_GRAY if sel_index == 0 else GRAY)
    draw_button("No", no_rect, button_color=LIGHT_GRAY if sel_index == 1 else GRAY)
    return yes_rect, no_rect

#function to print receipt
def print_receipt():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("-" * 40)
    print(f"{'IN-N-OUT BURGER':^40}")
    print(f"{('Date: ' + now):^40}")
    print("-" * 40)
    for meal in order.items:
        print(f"{meal.capitalize():<32}{f'${menu[meal]:.2f}':>8}")
    print("-" * 40)
    subtotal, tax, tip, total = order.totals()
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
    global finished_index, confirmation_index, menu_mode, menu_button_index
    order.reset()
    finished_index, confirmation_index, menu_mode, menu_button_index = 0, 0, "grid", 1

#main function
def main():
    global finished_index, confirmation_index, menu_mode, menu_button_index, current_page
    clock = pygame.time.Clock()
    items = list(menu.keys())
    cols = 4
    rows = (len(items) + cols - 1) // cols
    selected_index = 0

    running = True
    while running:
        if current_page == "menu":
            next_rect, menu_item_rects, remove_rect = draw_menu(selected_index)
        elif current_page == "confirmation":
            back_rect, finish_rect, tip_rect = draw_confirmation()
        elif current_page == "finished":
            yes_rect, no_rect = draw_finished(finished_index)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #menu page events
            if current_page == "menu":
                if event.type == pygame.KEYDOWN:
                    if menu_mode == "grid":
                        row, col = selected_index // cols, selected_index % cols
                        if event.key == pygame.K_LEFT:
                            col = col - 1 if col > 0 else cols - 1
                        elif event.key == pygame.K_RIGHT:
                            col = col + 1 if col < cols - 1 else 0
                        elif event.key == pygame.K_UP:
                            if row == 0:
                                menu_mode = "buttons"
                                menu_button_index = 0 if col < 2 else 1
                            else:
                                row -= 1
                        elif event.key == pygame.K_DOWN:
                            if row == rows - 1:
                                menu_mode = "buttons"
                                menu_button_index = 0 if col < 2 else 1
                            else:
                                row += 1
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            order.add(items[selected_index], menu[items[selected_index]])
                        elif event.key == pygame.K_BACKSPACE:
                            for i in range(len(order.items) - 1, -1, -1):
                                if order.items[i] == items[selected_index]:
                                    order.items.pop(i)
                                    order.prices.pop(i)
                                    break
                        new_index = row * cols + col
                        selected_index = new_index if new_index < len(items) else len(items) - 1
                    else:
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            menu_button_index = 0 if menu_button_index == 1 else 1
                        elif event.key == pygame.K_UP:
                            menu_mode = "grid"
                            new_index = (rows - 1) * cols + (0 if menu_button_index == 0 else 2)
                            selected_index = new_index if new_index < len(items) else len(items) - 1
                        elif event.key == pygame.K_DOWN:
                            menu_mode = "grid"
                            selected_index = 0 if menu_button_index == 0 else (2 if len(items) > 2 else 0)
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            if menu_button_index == 0 and order.items:
                                order.items.pop()
                                order.prices.pop()
                            elif menu_button_index == 1 and order.items:
                                current_page = "confirmation"
                                menu_mode = "grid"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if remove_rect.collidepoint(event.pos):
                        if order.items:
                            order.items.pop()
                            order.prices.pop()
                    elif next_rect.collidepoint(event.pos):
                        if order.items:
                            current_page = "confirmation"
                            menu_mode = "grid"
                    else:
                        for rect, index in menu_item_rects:
                            if rect.collidepoint(event.pos):
                                selected_index = index
                                order.add(items[index], menu[items[index]])
                                menu_mode = "grid"
                                break

            #confirmation page events
            elif current_page == "confirmation":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if tip_rect.collidepoint(event.pos):
                        order.tip_pct = (order.tip_pct + 5) % 35
                    elif back_rect.collidepoint(event.pos):
                        current_page = "menu"
                    elif finish_rect.collidepoint(event.pos):
                        print_receipt()
                        current_page = "finished"
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        if confirmation_index == 0:
                            confirmation_index = 1 if event.key == pygame.K_LEFT else 2
                        elif confirmation_index == 1:
                            confirmation_index = 0 if event.key == pygame.K_RIGHT else 1
                        elif confirmation_index == 2:
                            confirmation_index = 0 if event.key == pygame.K_LEFT else 2
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if confirmation_index == 0:
                            order.tip_pct = (order.tip_pct + 5) % 35
                        elif confirmation_index == 1:
                            current_page = "menu"
                        elif confirmation_index == 2:
                            print_receipt()
                            current_page = "finished"
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            #finished page events
            elif current_page == "finished":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        finished_index = 1 - finished_index
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if finished_index == 0:
                            reset_order()
                            selected_index = 0
                            current_page = "menu"
                        else:
                            running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if yes_rect.collidepoint(event.pos):
                        reset_order()
                        selected_index = 0
                        current_page = "menu"
                    elif no_rect.collidepoint(event.pos):
                        running = False

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
