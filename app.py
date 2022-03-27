from flask import Flask, redirect, render_template,request,session
from flask_pymongo import PyMongo
import os
app=Flask(__name__)

if os.environ.get('ENVIRONMENT')==None:  #checks if running code on our comp
    file=open('connectionstring.txt','r')
    connectionstring=file.read().strip()
    file.close()
else: #running on heroku
    connectionstring=os.environ.get('MONGO_URI')
app.config['MONGO_URI']=connectionstring

if os.environ.get('ENVIRONMENT')==None:
    file=open('secretkey.txt','r')
    secretkey=file.read().strip()
    file.close()
else:
    secretkey=os.environ.get('SECRET_KEY')
app.config['SECRET_KEY']=secretkey

mongo=PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addproduct',methods=['GET','POST'])
def addproduct():
    if request.method=='GET':
        return render_template('addproduct.html')
    else:
        image=request.form['image']
        limit=request.form['limit']
        price=request.form['price']
        title=request.form['title']
        unit=request.form['unit']
        desc=request.form['desc']
        record={'image':image,'limit':limit,'price':price,'title':title,'unit':unit,'desc':desc}
        mongo.db.products.insert_one(record)
        print(image, limit, price, title, unit)
        return redirect('/buyproduct')

@app.route('/buyproduct',methods=['GET','POST'])
def buyproduct():
    if request.method=='GET':
        all_products=[]
        products=mongo.db.products.find()
        for product in products:
            all_products.append(product)
        # print(products)
        return render_template('buyproduct.html', all_products=all_products, session=session)

@app.route('/add_to_cart')
def add_cart():
    itemname=request.args.get('itemname')
    if itemname in session:
        session[itemname]=session[itemname]+1
    else:
        session[itemname]=1
    
    return redirect('/buyproduct')

@app.route('/delete_from_cart')
def delfromcart():
    itemname=request.args.get('itemname')
    if itemname in session:
        session[itemname]=session[itemname]-1
        if session[itemname]<=0:
            del(session[itemname])
    return redirect('/buyproduct')

@app.route('/checkout')
def checkout():
    items=[]
    quantity=[]
    prices=[]
    prices_total=[]
    totalprice=0
    for stuff in session:
        quantity.append(session[stuff])
        items.append(stuff)
        product_details=mongo.db.products.find_one({'title':stuff})
        prices.append(product_details['price'])
        final_price_of_each_item=int(product_details['price'])*int(session[stuff])
        prices_total.append(final_price_of_each_item)
        totalprice=final_price_of_each_item+totalprice
    return render_template('checkout.html',items=items,quantity=quantity,prices=prices,prices_total=prices_total, totalprice=totalprice)

if __name__ == "__main__":
    app.run()
