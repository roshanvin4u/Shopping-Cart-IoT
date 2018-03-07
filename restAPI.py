import pandas as pd
from flask import Flask, render_template, request
import json
import pymysql
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['SECRET_KEY'] = 'jsbcfsbfjefebw237u3gdbdc'
socketio = SocketIO(app)

global rules
rules = pd.read_csv("data/rules.csv")

def getItemName(barcodeString):
    conn = pymysql.connect(host='18.219.186.47', port=3306, user='root', passwd='password', db='products')
    cur = conn.cursor()
    no_of_rows = cur.execute("SELECT col from output WHERE barcode=%d"%int(barcodeString))
    itemName = ""
    if(no_of_rows > 0):
        queryResult = cur.fetchone()
        itemName = queryResult[0]
    cur.close()
    conn.close()
    return itemName
    
def getRecipes(barcodeString):
    #barcodeString = "5004593651"
    resultsToReturn = []
    conn = pymysql.connect(host='18.219.186.47', port=3306, user='root', passwd='password', db='products')
    cur = conn.cursor()
    no_of_rows = cur.execute("SELECT dish, ingredient_1, ingredient_2, ingredient_3 from Recipes WHERE ingredient_1=%d or ingredient_2=%d or ingredient_3=%d"% (int(barcodeString), int(barcodeString),int(barcodeString)))
    if (no_of_rows > 0):
        queryResult = cur.fetchone()
        resultsToReturn.append(queryResult[0])
        for i in range(1,4):
            itemName = getItemName(str(queryResult[i]))
            resultsToReturn.append(str(itemName))
    d = {"result":resultsToReturn}
    print(json.dumps(d))
    cur.close()
    conn.close()
    return json.dumps(d)
    
def getProductDetails(barcodeString):
    resultToReturn = []
    conn = pymysql.connect(host='18.219.186.47', port=3306, user='root', passwd='password', db='products')
    cur = conn.cursor()
    no_of_rows = cur.execute("SELECT col,price from output WHERE barcode=%d"%int(barcodeString))
    if(no_of_rows > 0):
        queryResult = cur.fetchone()
        for i in range(0,len(queryResult)):
            resultToReturn.append(str(queryResult[i]))
    d = {"result":resultToReturn}        
    cur.close()
    conn.close()
    return json.dumps(d)
    
def getAssociations(itemname):
    associatedItems = []
    lhsItem = ""
    #count = 0
    b = "(',)"
    for i in range(0,rules.shape[0]):
        if (itemname in rules['rhs'][i]):
            lhsItem = rules['lhs'][i]
            print(lhsItem)
            if(lhsItem != ""):
                for char in b:
                    lhsItem = lhsItem.replace(char,"")
        if (lhsItem not in associatedItems):
            #temp.append(lhsItem)
            #d = {str(count) : lhsItem}
            #count = count+ 1
            associatedItems.append(lhsItem)
    d = {"items":associatedItems}
    print(associatedItems)
    return json.dumps(d)
            

@app.route("/")
def index():
    #Render Home Page
    return render_template("index.html")

@app.route("/receiveBarcode/<itemName>", methods = ["POST"])
def receiveBarcode(itemName):
    print(itemName)
    #priceAndItem = ""
    #SearchDatabase for item for associations
    #itemname = getItemName(barcodeString)
    
    if(itemName == ""):
        associatedItems = []
        associatedItems.append("None")
        items = {"items":associatedItems}
    else :
        items = getAssociations(itemName)
        #priceAndItem = getProductDetails(itemName)
        #showRecipe = getRecipes(itemName)
        #socketio.emit('viewrecipe',showRecipe)
        #socketio.emit('viewproductdetails',priceAndItem)
    dataJson = json.dumps(items)
    #priceAndItem = getProductDetails(barcodeString)
    #print(priceAndItem)
    socketio.emit('viewassociations',dataJson)
    return dataJson

if __name__ == "__main__":
    socketio.run(app, host = "0.0.0.0", port= 5000)