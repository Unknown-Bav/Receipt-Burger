import pygame
import os
from enum import Enum
from typing import List, Tuple, Optional

# ============================================================================
# CURRENCY AND INGREDIENT CLASSES
# ============================================================================

class Currency(Enum):
    """Enum for supported currencies."""
    CANADA = 0
    AMERICA = 1
    EURO = 2
    BRITISH = 3
    JAPAN = 4
    AUSTRALIA = 5
    
    def get_symbol(self) -> str:
        """Get currency symbol."""
        symbols = {
            Currency.CANADA: "$",
            Currency.AMERICA: "$",
            Currency.EURO: "€",
            Currency.BRITISH: "£",
            Currency.JAPAN: "¥",
            Currency.AUSTRALIA: "A$",
        }
        return symbols.get(self, "$")
    
    def get_name(self) -> str:
        """Get currency name."""
        names = {
            Currency.CANADA: "Canada",
            Currency.AMERICA: "America",
            Currency.EURO: "Euro",
            Currency.BRITISH: "British",
            Currency.JAPAN: "Japan",
            Currency.AUSTRALIA: "Australia",
        }
        return names.get(self, "Unknown")


class Ingredient:
    """Represents a burger ingredient with multi-currency pricing."""
    
    def __init__(self, name: str, prices: dict, calories: dict, 
                 images: Tuple[str, str], button_pos: Tuple[int, int],
                 dimensions: dict, logo_image: Optional[str] = None):
        """
        Initialize an ingredient.
        
        Args:
            name: Ingredient name
            prices: Dict mapping Currency to price
            calories: Dict mapping Currency to calorie count
            images: Tuple of (can_image, am_image) for backwards compatibility
            button_pos: (x, y) position of button
            dimensions: Dict mapping Currency to (width, height) tuple
            logo_image: Optional special image for display
        """
        self.name = name
        self.prices = prices
        self.calories = calories
        self.images = images  # (can_image, am_image)
        self.button_pos = button_pos
        self.dimensions = dimensions
        self.logo_image = logo_image or images[0]
    
    def get_price(self, currency: Currency) -> float:
        """Get price for specified currency."""
        return self.prices.get(currency, 0.0)
    
    def get_calories(self, currency: Currency) -> int:
        """Get calories for specified currency."""
        return self.calories.get(currency, 0)
    
    def get_image(self, currency: Currency) -> str:
        """Get image filename for specified currency (Canada=0, America=1)."""
        if currency == Currency.CANADA:
            return self.images[0]
        elif currency == Currency.AMERICA:
            return self.images[1]
        else:
            # For other currencies, use America image as fallback
            return self.images[1]
    
    def get_dimensions(self, currency: Currency) -> Tuple[int, int]:
        """Get image dimensions for specified currency."""
        if currency == Currency.CANADA:
            key = 0
        elif currency == Currency.AMERICA:
            key = 1
        else:
            key = 1  # Fallback to America
        
        # Return dimensions using the Canada/America index
        for i, (curr, dims) in enumerate(self.dimensions.items()):
            if (i == 0 and key == 0) or (i == 1 and key == 1):
                return dims
        return self.dimensions[Currency.CANADA]


# ============================================================================
# DROPDOWN WIDGET
# ============================================================================

class DropdownMenu:
    """Simple dropdown menu widget using pygame."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 options: List[str], default_index: int = 0):
        """
        Initialize dropdown menu.
        
        Args:
            x, y: Position of dropdown
            width, height: Dimensions
            options: List of option strings
            default_index: Index of default selected option
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        self.rect = pygame.Rect(x, y, width, height)
        self.option_rects = []
        self.font = pygame.font.SysFont("Arial", 14)
        self.color_closed = (100, 100, 100)
        self.color_open = (150, 150, 150)
        self.color_text = (255, 255, 255)
        self.color_border = (255, 255, 255)
        self.color_hover = (200, 200, 200)
        self.hovered_index = -1
    
    def handle_event(self, event: pygame.event.EventType) -> Optional[int]:
        """
        Handle pygame events.
        
        Args:
            event: pygame event
            
        Returns:
            Selected option index if changed, None otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check if clicked on closed dropdown
                if not self.is_open and self.rect.collidepoint(event.pos):
                    self.is_open = True
                    return None
                
                # Check if clicked on option in open dropdown
                if self.is_open:
                    for i, opt_rect in enumerate(self.option_rects):
                        if opt_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.is_open = False
                            return i
                    
                    # Clicked outside dropdown, close it
                    self.is_open = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.is_open:
                self.hovered_index = -1
                for i, opt_rect in enumerate(self.option_rects):
                    if opt_rect.collidepoint(event.pos):
                        self.hovered_index = i
                        break
        
        return None
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the dropdown menu."""
        # Draw closed dropdown button
        pygame.draw.rect(screen, self.color_closed, self.rect)
        pygame.draw.rect(screen, self.color_border, self.rect, 2)
        
        # Draw selected option text
        text = self.font.render(self.options[self.selected_index], True, self.color_text)
        screen.blit(text, (self.x + 5, self.y + self.height // 2 - text.get_height() // 2))
        
        # Draw dropdown arrow
        arrow_x = self.x + self.width - 15
        arrow_y = self.y + self.height // 2
        pygame.draw.polygon(screen, self.color_text, 
                          [(arrow_x, arrow_y - 4), (arrow_x + 8, arrow_y - 4), (arrow_x + 4, arrow_y)])
        
        # Draw open dropdown options
        if self.is_open:
            self.option_rects = []
            for i, option in enumerate(self.options):
                opt_y = self.y + self.height + (i * self.height)
                opt_rect = pygame.Rect(self.x, opt_y, self.width, self.height)
                self.option_rects.append(opt_rect)
                
                # Use hover color if hovered
                color = self.color_hover if i == self.hovered_index else self.color_open
                pygame.draw.rect(screen, color, opt_rect)
                pygame.draw.rect(screen, self.color_border, opt_rect, 1)
                
                # Draw option text
                text = self.font.render(option, True, self.color_text)
                screen.blit(text, (self.x + 5, opt_y + self.height // 2 - text.get_height() // 2))
    
    def get_selected(self) -> int:
        """Get index of selected option."""
        return self.selected_index


# ============================================================================
# IMAGE CACHE MANAGER
# ============================================================================

class ImageManager:
    """Manages image loading and caching."""
    
    def __init__(self, image_dir: Optional[str] = None):
        """Initialize the image manager."""
        self.image_cache = {}
        self.image_dir = image_dir or os.path.dirname(os.path.abspath(__file__))
    
    def load_image(self, filename: str) -> Optional[pygame.Surface]:
        """Load an image, using cache if available."""
        if filename in self.image_cache:
            return self.image_cache[filename]
        
        filepath = os.path.join(self.image_dir, filename)
        try:
            image = pygame.image.load(filepath)
            self.image_cache[filename] = image
            return image
        except pygame.error as e:
            print(f"Error loading image '{filename}': {e}")
            return None


# ============================================================================
# SETTINGS AND INITIALIZATION
# ============================================================================

window_width, window_height = 950, 500
pygame.init()
screen = pygame.display.set_mode((window_width, window_height), pygame.DOUBLEBUF, 32)
pygame.display.set_caption("Receipt Burger")
text_font = pygame.font.SysFont("Cooper Black", 15)
big_text_font = pygame.font.SysFont("Cooper Black", 30)
clock = pygame.time.Clock()

# Initialize managers
image_manager = ImageManager()

# A couple variables being declared for global use
items = []  # stores a list of each image's name to be loaded
receipt = ""  # A string to contain the receipt that updates with each ingredient added
finreceipt = "Ingredients: Bun"  # Prints the ingredients at the end of the program
total = 0  # Total cost for the burger
buttons = []  # A list to contain the rects that need to be created for hitboxes
buttonindex = 0  # Tells the program which button is clicked
current_currency = None  # Will hold the selected Currency enum
dropdown = None  # Will hold the dropdown menu widget

# ============================================================================
# INGREDIENTS WITH MULTI-CURRENCY SUPPORT
# ============================================================================

ingredients = [
    Ingredient(
        name="Bun",
        prices={Currency.CANADA: 0, Currency.AMERICA: 0, Currency.EURO: 0, 
                Currency.BRITISH: 0, Currency.JAPAN: 0, Currency.AUSTRALIA: 0},
        calories={Currency.CANADA: 120, Currency.AMERICA: 200, Currency.EURO: 200,
                 Currency.BRITISH: 200, Currency.JAPAN: 200, Currency.AUSTRALIA: 200},
        images=("canbun.png", "ambun.png"),
        button_pos=(550, 0),
        dimensions={Currency.CANADA: (271, 187), Currency.AMERICA: (271, 187), 
                   Currency.EURO: (271, 187), Currency.BRITISH: (271, 187),
                   Currency.JAPAN: (271, 187), Currency.AUSTRALIA: (271, 187)},
        logo_image="bunbottom.png"
    ),
    Ingredient(
        name="Cheese",
        prices={Currency.CANADA: 0.5, Currency.AMERICA: 0.37, Currency.EURO: 0.45,
                Currency.BRITISH: 0.35, Currency.JAPAN: 45, Currency.AUSTRALIA: 0.55},
        calories={Currency.CANADA: 113, Currency.AMERICA: 500, Currency.EURO: 500,
                 Currency.BRITISH: 500, Currency.JAPAN: 500, Currency.AUSTRALIA: 500},
        images=("cancheese.png", "amcheese.png"),
        button_pos=(550, 50),
        dimensions={Currency.CANADA: (2400, 2400), Currency.AMERICA: (800, 800),
                   Currency.EURO: (800, 800), Currency.BRITISH: (800, 800),
                   Currency.JAPAN: (800, 800), Currency.AUSTRALIA: (800, 800)}
    ),
    Ingredient(
        name="Meat",
        prices={Currency.CANADA: 1.0, Currency.AMERICA: 0.73, Currency.EURO: 0.90,
                Currency.BRITISH: 0.70, Currency.JAPAN: 100, Currency.AUSTRALIA: 1.10},
        calories={Currency.CANADA: 200, Currency.AMERICA: 500, Currency.EURO: 500,
                 Currency.BRITISH: 500, Currency.JAPAN: 500, Currency.AUSTRALIA: 500},
        images=("canmeat.png", "ammeat.png"),
        button_pos=(550, 100),
        dimensions={Currency.CANADA: (2500, 2500), Currency.AMERICA: (378, 202),
                   Currency.EURO: (378, 202), Currency.BRITISH: (378, 202),
                   Currency.JAPAN: (378, 202), Currency.AUSTRALIA: (378, 202)}
    ),
    Ingredient(
        name="Tomato",
        prices={Currency.CANADA: 0.33, Currency.AMERICA: 0.24, Currency.EURO: 0.30,
                Currency.BRITISH: 0.23, Currency.JAPAN: 30, Currency.AUSTRALIA: 0.38},
        calories={Currency.CANADA: 3, Currency.AMERICA: 5, Currency.EURO: 5,
                 Currency.BRITISH: 5, Currency.JAPAN: 5, Currency.AUSTRALIA: 5},
        images=("cantomato.png", "amtomato.png"),
        button_pos=(550, 150),
        dimensions={Currency.CANADA: (360, 360), Currency.AMERICA: (303, 166),
                   Currency.EURO: (303, 166), Currency.BRITISH: (303, 166),
                   Currency.JAPAN: (303, 166), Currency.AUSTRALIA: (303, 166)}
    ),
    Ingredient(
        name="Lettuce",
        prices={Currency.CANADA: 0.33, Currency.AMERICA: 0.24, Currency.EURO: 0.30,
                Currency.BRITISH: 0.23, Currency.JAPAN: 30, Currency.AUSTRALIA: 0.38},
        calories={Currency.CANADA: 3, Currency.AMERICA: 10, Currency.EURO: 10,
                 Currency.BRITISH: 10, Currency.JAPAN: 10, Currency.AUSTRALIA: 10},
        images=("canlettuce.png", "notavailable.png"),
        button_pos=(550, 200),
        dimensions={Currency.CANADA: (500, 500), Currency.AMERICA: (500, 500),
                   Currency.EURO: (500, 500), Currency.BRITISH: (500, 500),
                   Currency.JAPAN: (500, 500), Currency.AUSTRALIA: (500, 500)}
    ),
    Ingredient(
        name="Onion",
        prices={Currency.CANADA: 0.75, Currency.AMERICA: 0.55, Currency.EURO: 0.68,
                Currency.BRITISH: 0.52, Currency.JAPAN: 70, Currency.AUSTRALIA: 0.85},
        calories={Currency.CANADA: 50, Currency.AMERICA: 200, Currency.EURO: 200,
                 Currency.BRITISH: 200, Currency.JAPAN: 200, Currency.AUSTRALIA: 200},
        images=("canonion.png", "amonion.png"),
        button_pos=(550, 250),
        dimensions={Currency.CANADA: (2500, 2500), Currency.AMERICA: (500, 500),
                   Currency.EURO: (500, 500), Currency.BRITISH: (500, 500),
                   Currency.JAPAN: (500, 500), Currency.AUSTRALIA: (500, 500)}
    ),
    Ingredient(
        name="Ketchup",
        prices={Currency.CANADA: 0.0, Currency.AMERICA: 0.0, Currency.EURO: 0.0,
                Currency.BRITISH: 0.0, Currency.JAPAN: 0, Currency.AUSTRALIA: 0.0},
        calories={Currency.CANADA: 10, Currency.AMERICA: 100, Currency.EURO: 100,
                 Currency.BRITISH: 100, Currency.JAPAN: 100, Currency.AUSTRALIA: 100},
        images=("canketchup.png", "amketchup.png"),
        button_pos=(550, 300),
        dimensions={Currency.CANADA: (1000, 1655), Currency.AMERICA: (500, 307),
                   Currency.EURO: (500, 307), Currency.BRITISH: (500, 307),
                   Currency.JAPAN: (500, 307), Currency.AUSTRALIA: (500, 307)}
    ),
    Ingredient(
        name="Mustard",
        prices={Currency.CANADA: 0.0, Currency.AMERICA: 0.0, Currency.EURO: 0.0,
                Currency.BRITISH: 0.0, Currency.JAPAN: 0, Currency.AUSTRALIA: 0.0},
        calories={Currency.CANADA: 30, Currency.AMERICA: 100, Currency.EURO: 100,
                 Currency.BRITISH: 100, Currency.JAPAN: 100, Currency.AUSTRALIA: 100},
        images=("canmustard.png", "ammustard.png"),
        button_pos=(550, 350),
        dimensions={Currency.CANADA: (478, 283), Currency.AMERICA: (607, 103),
                   Currency.EURO: (607, 103), Currency.BRITISH: (607, 103),
                   Currency.JAPAN: (607, 103), Currency.AUSTRALIA: (607, 103)}
    ),
    Ingredient(
        name="Hot sauce",
        prices={Currency.CANADA: -1.0, Currency.AMERICA: -0.73, Currency.EURO: -0.85,
                Currency.BRITISH: -0.65, Currency.JAPAN: -100, Currency.AUSTRALIA: -1.0},
        calories={Currency.CANADA: 0, Currency.AMERICA: 100, Currency.EURO: 100,
                 Currency.BRITISH: 100, Currency.JAPAN: 100, Currency.AUSTRALIA: 100},
        images=("canhotsauce.png", "amhotsauce.png"),
        button_pos=(550, 400),
        dimensions={Currency.CANADA: (360, 360), Currency.AMERICA: (360, 360),
                   Currency.EURO: (360, 360), Currency.BRITISH: (360, 360),
                   Currency.JAPAN: (360, 360), Currency.AUSTRALIA: (360, 360)}
    ),
    Ingredient(
        name="Pickles",
        prices={Currency.CANADA: 0.5, Currency.AMERICA: 0.37, Currency.EURO: 0.45,
                Currency.BRITISH: 0.35, Currency.JAPAN: 45, Currency.AUSTRALIA: 0.55},
        calories={Currency.CANADA: 10, Currency.AMERICA: 50, Currency.EURO: 50,
                 Currency.BRITISH: 50, Currency.JAPAN: 50, Currency.AUSTRALIA: 50},
        images=("canpickles.png", "ampickles.png"),
        button_pos=(550, 450),
        dimensions={Currency.CANADA: (200, 128), Currency.AMERICA: (566, 606),
                   Currency.EURO: (566, 606), Currency.BRITISH: (566, 606),
                   Currency.JAPAN: (566, 606), Currency.AUSTRALIA: (566, 606)}
    ),
]


# ============================================================================
# FUNCTIONS (ORIGINAL WITH MINIMAL CHANGES)
# ============================================================================

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    """Renders and draws text on the screen."""
    img = font.render(text, True, text_col, None, 940)  # renders the text
    screen.blit(img, (x, y))  # draws text onscreen


def final():
    """Final screen of the program"""
    global receipt, finreceipt  # variables from outside the function that will be used

    text = "Thank you for your order!"  # Thanks the user
    draw_text(text, big_text_font, (255, 255, 255), 10, 10)

    draw_text(finreceipt, text_font, (255, 255, 255), 10, 50)  # Lists every ingredient
    # Lists the final cost of the burger
    draw_text("Total: " + current_currency.get_symbol() + str(round(total, 2)), big_text_font, (255, 255, 255), 10, 350)

    image("logo.png", False, 10, 380, None, None)  # Displays the logo in the corner

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                run = False
                pygame.quit()


def ordering():
    """Second screen of the program, displays your burger while you order, a live, updating receipt, and each ingredient that the user can choose from"""
    global ingredients, buttonindex, buttons, run, text_font, receipt, total, finreceipt  # Imports variables to be used in the function
    buttons = []  # Empties the button list at the beginning of each loop, to avoid the list adding the same thing twice
    click = False  # Tells the program the user has not clicked
    total = round(total, 2)  # Ensures there are no errors with addition (1+1=2.000001)

    text = "Press enter to submit your order"  # Displays splash text, allowing the user to submit when they finish
    draw_text(text, text_font, (255, 255, 255), 10, 475)

    # Displays the total cost of the burger
    draw_text("Total: " + current_currency.get_symbol() + str(total), text_font, (255, 255, 255), 475 - (len(str(total)) * 10), 475)
    # Checks the amount of lines in the receipt, renders it, and moves it upwards depending on how many lines there are
    lineamount = len(receipt.splitlines())
    draw_text(receipt, text_font, (255, 255, 255), 350, 475 - (lineamount * 18))

    for i in range(10):
        # Renders every button with a clickable hitbox
        button = pygame.Rect(ingredients[i].button_pos[0], ingredients[i].button_pos[1], 200, 50)
        buttons.append(button)
        image(ingredients[i].get_image(current_currency), True, ingredients[i].button_pos[0], ingredients[i].button_pos[1],
              ingredients[i].get_dimensions(current_currency)[0], ingredients[i].get_dimensions(current_currency)[1])

        # Renders the labels for each ingredient, consisting of the name, price, and calorie count
        name = ingredients[i].name
        price = ingredients[i].get_price(current_currency)
        calories = ingredients[i].get_calories(current_currency)
        text = str(name) + "\n" + current_currency.get_symbol() + str(price) + "\tCalories:" + str(calories)
        text = text.expandtabs(4)  # Pygame cannot display tabs in text (\t), so this instead replaces them with spaces
        draw_text(text, text_font, (255, 255, 255), 750, ingredients[i].button_pos[1])
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and buttons[0] != None:  # checks if a user has pressed the left mouse button, and if the buttons are properly rendered
            if event.button == 1:
                click = True
        if event.type == pygame.QUIT:  # if user has pressed the X button, the program closes
            run = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:  # detect if user has pressed enter, to move on to the next screen
            if event.key == pygame.K_RETURN:
                runinit += 1
    if click:
        for num, button in enumerate(buttons):  # assign each button a number, and repeat the loop for every button
            if button.collidepoint(event.pos):  # if the user has clicked, determine which box they have clicked
                buttonindex = num  # tells the rest of the program which button has been clicked
                items.append(ingredients[buttonindex].get_image(current_currency))  # adds the ingredient selected's image root to a list
                total += ingredients[buttonindex].get_price(current_currency)  # adds the price of the ingredient to the total
                # Adds each element to the receipt string with updated formatting
                receipt += "\n " + str(ingredients[buttonindex].name) + "\n" + current_currency.get_symbol() + str(round(ingredients[buttonindex].get_price(current_currency), 2)) + "    " + str(round(total, 2))
                finreceipt += ", " + str(ingredients[buttonindex].name)  # adds each ingredient to the final list at the end


def initiate():
    """Initialization screen where the user chooses which currency to order in"""
    global buttons, runinit, current_currency, dropdown, run  # variables from outside the function that will be used
    
    draw_text("Select your location:\n(Prices will be provided in that nation's currency.)", big_text_font, (255, 255, 255), 50, 50)  # Splash text instructions for the user

    # Initialize dropdown on first run
    if dropdown is None:
        currency_names = [c.get_name() for c in Currency]
        dropdown = DropdownMenu(375, 200, 200, 40, currency_names)
    
    # Draw dropdown
    dropdown.draw(screen)
    
    # Display logo
    image("logo.png", False, 10, 380, None, None)

    for event in pygame.event.get():
        # Handle dropdown events
        selected = dropdown.handle_event(event)
        if selected is not None:
            # Currency selected
            current_currency = Currency(selected)
            items.append(ingredients[0].get_image(current_currency))  # Add bun as first item
            runinit += 1
        
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()


def image(source, button, dimx, dimy, cropx, cropy):
    """Renders the image"""
    if button:  # renders the image as a button
        loaded_image = image_manager.load_image(source)  # creates an image texture with the specified source
        if loaded_image is None:
            return
        
        if source == "notavailable.png":  # if the source of the image is the red x, instead render the lettuce image
            loaded_image = image_manager.load_image("canlettuce.png")
            if loaded_image:
                screen.blit(loaded_image, (dimx, dimy), (500 / 3, 500 / 3, 200, 50))
        elif source == "ambun.png" or source == "canbun.png":  # this just changes where the image focuses if the file is the bun
            screen.blit(loaded_image, (dimx, dimy), (cropx / 3, cropy * 4 / 5, 200, 50))
        else:
            # renders each image as a 200px*50px button, with a focus on one third of the total image
            screen.blit(loaded_image, (dimx, dimy), (cropx / 3, cropy / 3, 200, 50))
    else:  # if the image is not supposed to be a button, render it normally
        if source == "logo.png":  # if the image is the logo, scale it by a factor of half instead of shrinking it to the specified dimensions to avoid stretching
            loaded_image = image_manager.load_image(source)
            if loaded_image:
                loaded_image = pygame.transform.scale_by(loaded_image, 0.5)
                screen.blit(loaded_image, (dimx, dimy))
        else:
            loaded_image = image_manager.load_image(source)
            if loaded_image:
                # stretch the image to be exactly 300x100 to make it fit onscreen, and because it looks funny
                loaded_image = pygame.transform.scale(loaded_image, (300, 100))
                screen.blit(loaded_image, (dimx, dimy))  # update the screen with the image


# ============================================================================
# MAIN LOOP
# ============================================================================

# The core loop that keeps the program open
run = True
runinit = 0  # a variable that tells the program what screen to display
while run:
    # Refreshes the screen each frame
    screen.fill("black")

    # Checks what phase the program is on
    if runinit == 0:
        initiate()
    elif runinit == 1:
        ordering()
        # for each image in the list of images to render
        for itemnum, item in enumerate(items):
            image(items[itemnum], False, 25, (390 - 10 * itemnum), None, None)  # Render each image in the list
    else:
        final()
    
    for event in pygame.event.get():  # if the pygame system detects the user interacting, check:
        if event.type == pygame.QUIT:  # if the user has quit the program. If they have, close the program
            run = False
            pygame.quit()

    clock.tick(30)  # keep the program running at a consistent 30fps
    pygame.display.flip()  # update the display

# Sources
# https://pyga.me/docs/
# https://www.youtube.com/watch?v=lTxaran0Cig
# https://www.youtube.com/watch?v=Ro82dac_J1Y
# https://www.youtube.com/watch?v=rHEnZfq_zEQ
