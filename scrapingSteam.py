from bs4 import BeautifulSoup
from bs4.element import AttributeValueWithCharsetSubstitution
import requests
import lxml
import openpyxl

todoslosImpuestos = 1.66 #taxes summed up

def scrapingSteam(argument):
    if (argument.startswith("https://store.steampowered.com/app") == -1):
       print("Error, ese link no se puede procesar, solo los de https://store.steampowered.com/app son utilizables")
    else:
        r = requests.get(argument)
        soup = BeautifulSoup(r.content, "lxml")
        name = soup.find("div", class_="apphub_AppName").text
        prices = ""

        #First of all: we get all the prices
        for x in soup.find_all("div", class_="game_purchase_action_bg"):
            prices = f"{prices} ~ {x.get_text()}"

        #We do this in order to be sure it is the price we want because prices contains all the prices in the page
        prices = prices.strip()
        prices = prices.split("~")
        firstPrice = prices[1].strip()

        #This line adds compatibility with packages
        if (firstPrice.find("Package info") > -1):
            firstPrice = prices[2].strip()
        
        #If it can find free: its free
        if (firstPrice.find("Free") > -1):
            price = 0
            priceWithTaxes = 0
            #print(f"`{name} es gratuito!`")


        #If it can find download: then it is a demo
        elif (firstPrice.find("Download") > -1):
            price = 0
            priceWithTaxes = 0
            #print(f"`{name} tiene/es una demo!`")

        #if you can put it in your cart, then it is a paid game 
        elif (firstPrice.find("Add to Cart") > -1):

            #Getting the last price in the first element of the list, works with games on a discount
            firstPrice = firstPrice.split("$")
            firstPrice = firstPrice[-1]

            #Now, to avoid a million methods() we'll check if its a character we want and add it to a string
            price = ""
            for x in firstPrice:
                if x.isdigit() == True: 
                    price += x
                elif x == ",":
                    price += "."
                    
            #Finally, we get a float and then the taxes are calculated
            price = float(price)
            priceWithTaxes = price * todoslosImpuestos
        else: 
            print("Error")
            price = 0
            priceWithTaxes = 0
            #last resort error

        return([(f"{name}: {round(priceWithTaxes, 2)} \n"), round(priceWithTaxes, 2), round(price, 2), name])

#Long explanation: we get the webpage, then the class we want; if we can buy either second or third element, it will turn the string into only the value of the game.
#If it we can't buy it, to avoid errors, its worth 0.
#At the end it returns a list, the first element is a string with the name and value, the second the price w/taxes, the third the game untaxed and fourth the name


def cart():

    #Now, input is used to get the steam link and the return from scrapingsteam is defined as a variable
    #And several variables are defined to store each value
    originalInput = input("Ingresá el link!: ")
    listFromInput = scrapingSteam(originalInput)
    nameWithPrice = listFromInput[0]
    priceTaxed = listFromInput[1]

    #Now, the input asks us to either enter a new link or to end
    ifStatement = input("Deseas añadir algo más al carrito? Y o N: ")
    while (ifStatement == "Y" or ifStatement == "y"):
        listFromInput = (scrapingSteam((input("Ingresá el link!: "))))
        nameWithPrice += listFromInput[0]
        priceTaxed += float(listFromInput[1])
        #Redefining the list as new values from the link and also adding them to variables
        ifStatement = input("Deseas añadir algo más al carrito? Y o N: ")
    print(nameWithPrice + "Total: " + round(priceTaxed, 2))


def cartExel():
    originalInput = input("Ingresá el link!: ")
    listFromInput = scrapingSteam(originalInput)
    nameWithPrice = listFromInput[0]
    priceTaxed = listFromInput[1]
    priceWithoutTaxes = listFromInput[2]
    #It starts same as before but we have an extra variable, the original untaxed price

    my_wb = openpyxl.Workbook()
    my_sheet = my_wb.active
    my_sheet.title = "CarritoDeSteam"
    my_row = 3
    #Now, a spreadsheet is created and named, also my_row is initialized 

    my_sheet.cell(row=1, column=1).value = "Juego"
    my_sheet.cell(row=1, column=2).value = "Costo sin impuestos"
    my_sheet.cell(row=1, column=3).value = "Costo con impuestos"
    my_sheet.cell(row=2, column=1).value = listFromInput[3] #nombre
    my_sheet.cell(row=2, column=2).value = listFromInput[2] #costo sin impuestos
    my_sheet.cell(row=2, column=3).value = listFromInput[1] #costo con impuestos
    #my_row is initialized on 3 asuming the "titles" row and the first input

    ifStatement = input("Deseas añadir algo más al carrito? Y o N: ")
    while (ifStatement == "Y" or ifStatement == "y"):
        listFromInput = (scrapingSteam((input("Ingresá el link!: "))))
        nameWithPrice += listFromInput[0]
        priceTaxed += float(listFromInput[1])
        priceWithoutTaxes += listFromInput[2]
        #this is the same as before, only that one more variable is stored

        my_sheet.cell(row=my_row, column=1).value = listFromInput[3] #nombre
        my_sheet.cell(row=my_row, column=2).value = listFromInput[2] #costo sin impuestos
        my_sheet.cell(row=my_row, column=3).value = listFromInput[1] #costo con impuestos
        my_row += 1
        #Now we write the values from the list into the xlsx file, also adding +1 to the row so it does not overwrite on the next link

        ifStatement = input("Deseas añadir algo más al carrito? Y o N: ")

    my_sheet.cell(row=my_row, column=1).value = "Total" #nombre
    my_sheet.cell(row=my_row, column=2).value = priceWithoutTaxes #costo SIN impuestos
    my_sheet.cell(row=my_row, column=3).value = priceTaxed #costo CON impuestos
    my_wb.save("CarritoDeSteam.xlsx")
    #Finally, a sum of all the game's prices is written and saved

    print(nameWithPrice + "Total: " , round(priceTaxed, 2))

def start():
    ifStatement = input("Deseas escribirlo en un documento de exel con más detalles? Y o N: ")
    if (ifStatement == "N" or ifStatement == "n"):   cart()
    elif (ifStatement == "Y" or ifStatement == "y"):   cartExel()
    #Yeah, once again running input to make a choice.

start()
