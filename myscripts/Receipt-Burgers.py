import pygame
import random
from pygame import Color, Surface

#ingredients stored as such: Item name, price in can and us, calories in can and us, image for can and us, button location, and image dimensions
ingredients= [[["Bun","'Merica Burger Bun"],[0,0],[120,200],["canbun.png","ambun.png","bunbottom.png"],[550,0],[[271,187],[271,187]]],
              [["Cheese","Freedom Cheese"],[0.5,0.37],[113,500],["cancheese.png","amcheese.png"],[550,50],[[2400,2400],[800,800]]],
              [["Meat","All American Beef"],[1.0,0.73],[200,500],["canmeat.png","ammeat.png"],[550,100],[[2500,2500],[378,202]]],
              [["Tomato","Liberal-Faced Tomato"],[0.33,0.24],[3,5],["cantomato.png","amtomato.png"],[550,150],[[360,360],[303,166]]],
              [["Lettuce","Liberty Lettuce"],[0.33,0.24],[3,10],["canlettuce.png","notavailable.png"],[550,200],[[500,500],[500,500]]],
              [["Onion","Golden Rings"],[0.75,0.55],[50,200],["canonion.png","amonion.png"],[550,250],[[2500,2500],[500,500]]],
              [["Ketchup","Blood of the Soviets"],[0.0,0.0],[10,100],["canketchup.png","amketchup.png"],[550,300],[[1000,1655],[500,307]]],
              [["Mustard","Real Mustard"],[0.0,0.0],[30,100],["canmustard.png","ammustard.png"],[550,350],[[478,283],[607,103]]],
              [["Hot sauce","Almost as hot as me Sauce"],[-1.0,-0.73],[0,100],["canhotsauce.png","amhotsauce.png"],[550,400],[[360,360],[360,360]]],
              [["Pickles","Bick's"],[0.5,0.37],[10,50],["canpickles.png","ampickles.png"],[550,450],[[200,128],[566,606]]]]

#Settings specifying dimensions, fonts, and clock within pygame
window_width, window_height = 950, 500
pygame.init()
screen = pygame.display.set_mode((window_width, window_height), pygame.DOUBLEBUF, 32)
text_font = pygame.font.SysFont("Cooper Black", 15)
big_text_font = pygame.font.SysFont("Cooper Black", 30)
clock = pygame.time.Clock()

#Settings for the initialisation, where the user chooses what nation to order in
america = 0
canfont = pygame.font.SysFont("Goudy Stout", 30)
amfont = pygame.font.SysFont("Algerian", 30)
amcolour = "blue"
cancolour = "red"

#A couple variables being declared for global use
items = [ingredients[0][3][2]] #stores a list of each image's name to be loaded
receipt = "" #A string to contain the receipt that updates with each
finreceipt = "Ingredients: Bun" #Printes the ingredients at the end of the program
total = 0 #Total cost for the burger
buttons = [] #A list to contain the rects that need to be created for hitboxes
buttonindex = 0 #Tells the program which button is clicked

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col, None, 940) #renders the text
  screen.blit(img, (x, y))  #draws text onscreen

def final(): #Final screen of the program
    global runinit, receipt, text_font, big_text_font, finreceipt #variables from outside the function that will be used

    text = "Thank you for your order!" #Thanks the user
    draw_text(text, big_text_font, (255, 255, 255), 10, 10)

    draw_text(finreceipt, text_font, (255,255,255), 10, 50) #Lists every ingredient
    draw_text("Total: $"+str(total),big_text_font,(255,255,255), 10, 350) #Lists the final cost of the burger

    image("logo.png", False, 10, 380, None, None) #Displays the logo in the corner

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_RETURN:
                run = False
                pygame.quit()

def ordering():
    #Second screen of the program, displays your burger while you order, a live, updating receipt, and each ingredient that the user can choose from
    global ingredients, america, buttonindex, buttons, run, runinit, text_font, receipt, total, finreceipt #Imports variables to be used in the function
    buttons = [] #Empties the button list at the beginning of each loop, to avoid the list adding the same thing twice
    click = False #Tells the program the user has not clicked
    total = round(total,2) #Ensures there are no errors with addition (1+1=2.000001)

    text = "Press enter to submit your order" #Displays splash text, allowing the user to submit when they finish
    draw_text(text, text_font, (255, 255, 255), 10, 475)

    #Displays the total cost of the burger
    draw_text("Total: $"+ str(total), text_font, (255, 255, 255), 475 - (len(str(total))*10), 475)
    #Checks the amount of lines in the receipt, renders it, and moves it upwards depending on how many lines there are
    lineamount = len(receipt.splitlines())
    draw_text(receipt, text_font, (255, 255, 255), 350, 475- (lineamount * 18))

    for i in range(10):
        #Renders every button with a clickable hitbox
        button = pygame.Rect(ingredients[i][4][0],ingredients[i][4][1],200,50)
        buttons.append(button)
        image(ingredients[i][3][america], True, ingredients[i][4][0], ingredients[i][4][1],
              ingredients[i][5][america][0], ingredients[i][5][america][1])

        #Renders the lables for each ingredient, consisting of the name, price, and calorie count
        name = ingredients[i][0][america]
        price = ingredients[i][1][america]
        calories = ingredients[i][2][america]
        text = str(name)+"\n$"+str(price)+"\tCalories:"+str(calories)
        text = text.expandtabs(4) #Pygame cannot display tabs in text (\t), so this instead replaces them with spaces
        draw_text(text,text_font,(255,255,255), 750,ingredients[i][4][1])
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and buttons[0] != None: #checks if a user has pressed the leftmouse button, and if the buttons are properly rendered
            if event.button == 1:
                click = True
        if event.type == pygame.QUIT: #if user has pressed the X button, the program closes
            run = False
            pygame.quit()
        if event.type == pygame.KEYDOWN: #detect if user has pressed enter, to move on to the next screen
            if event.key==pygame.K_RETURN:
                runinit += 1
    if click:
        for num, button in enumerate(buttons): #assign each button a number, and repeat the loop for every button
            if button.collidepoint(event.pos): #if the user has clicked, which box they have clicked
                buttonindex = num #tells the rest of the program which button has been clicked
                items.append(ingredients[buttonindex][3][america]) #adds the inredient selected's image root to a list
                total += ingredients[buttonindex][1][america] #adds the price of the ingredient to the total
                receipt += "\n " + str(ingredients[buttonindex][0][america]) + "\n$" + str(round(ingredients[buttonindex][1][america],2)) + "    " + str(round(total,2)) #Adds each element of the receipt to the existing receipt
                finreceipt += ", " + str(ingredients[buttonindex][0][america]) #adds each ingredient to the final list at the end

def initiate():
    global buttons, cancolour, amcolour, runinit, america, run, canfont, amfont, window_width, big_text_font #variables from outside the function that will be used
    draw_text("Select your location:\n(Prices will be provided in that nations currency.)", big_text_font,(255,255,255),80,100) #Splash text instructions for the user

    #Renders the buttons and text for the country selection, and displays the logo
    canbutton = pygame.draw.rect(screen, cancolour, (100, 200, 200, 100), 100, 10)
    draw_text("Canada", canfont, "red",100, 300)
    ambutton = pygame.draw.rect(screen, amcolour, (window_width - 300, 200, 200, 100), 100, 10)
    draw_text("America", amfont, "blue", window_width - 300, 300)
    buttons = [canbutton, ambutton]
    image("logo.png", False, 10, 380, None, None)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for num, button in enumerate(buttons):
                    if button.collidepoint(event.pos): #checks which button has been pressed, moves onto the next screen, and tells the program which country the user selected
                        america = num
                        runinit += 1
        if event.type == pygame.MOUSEMOTION:
            cancolour = "red" #every frame, turn the button to the default colour
            amcolour = "blue"
            for num, button in enumerate(buttons):
                if button.collidepoint(event.pos): #if the mouse is hovering over the button, make the colour lighter
                    if button == ambutton:
                        amcolour = "cornflowerblue"
                    elif button == canbutton:
                        cancolour = "lightcoral"
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()

def image(source, button, dimx, dimy, cropx, cropy): #renders the image
    if button: #renders the image as a button
        image = pygame.image.load(source) #creates an image texture with the specified source
        if source == "notavailable.png":  #if the source of the image is the red x, instead render the lettuce image
            image = pygame.image.load("canlettuce.png")
            screen.blit(image, (dimx, dimy),(500/3,500/3,200,50))
        elif source == "ambun.png" or source == "canbun.png": #this just changes where the image focuses if the file is the bun
            screen.blit(image, (dimx, dimy), (cropx / 3, cropy*4 / 5, 200, 50))
        else:
            screen.blit(image, (dimx, dimy), (cropx / 3, cropy / 3, 200, 50)) #renders each image as a 200px*500px button, with a focus on one third of the total image
    else: #if the image is not supposed to be a button, render it normally
        if source == "logo.png":  #if the image is the logo, scale it by a factor of half instead of shrinking it to the specified dimensions to avoid stretching
            image = pygame.image.load(source)
            image = pygame.transform.scale_by(image,0.5)
        else:
            image = pygame.image.load(source)
            image = pygame.transform.scale(image,(300,100)) #stretch the image to be exactly 300x100 to make it fit onscreen, and because it looks funny
        screen.blit(image, (dimx, dimy)) #update the screen with the image

#the core loop that keeps the images open
run = True
runinit = 0 #a variable that tells the program what screen to display
while run:
    #refreshes the screen each frame
    screen.fill("black")

    #Checks what phase the program is on
    if runinit == 0:
        initiate()
    elif runinit == 1:
        ordering()
        for itemnum, item in enumerate(items): #for each image in the list of images to render
            image(items[itemnum], False,25,(390 - 10*itemnum), None, None) #Render each image in the list
    else:
        final()
    for event in pygame.event.get():  # if the pygame system detects the user interacting, check:
        if event.type == pygame.QUIT:  # if the user has quit the program. If they have, close the program
            run = False
            pygame.quit()

    clock.tick(30) #keep the program running at a consistent 30fps
    pygame.display.flip() #update the display

#Sources
#https://pyga.me/docs/
#https://www.youtube.com/watch?v=lTxaran0Cig
#https://www.youtube.com/watch?v=Ro82dac_J1Y
#https://www.youtube.com/watch?v=rHEnZfq_zEQ