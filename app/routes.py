# coding: utf-8

from flask import render_template, flash, redirect, url_for, request, session
from app import app
from app.calc_namelist import OrdersParser
from app.forms import CalcForm

@app.route("/")
def index():
    form = CalcForm()
    return render_template("index.html", form=form)


@app.route("/orders", methods=['GET', 'POST'])
def orders():
    calcform = CalcForm()

    if calcform.validate_on_submit():
        price = float(calcform.price.data)
        classes = None

        with open('temp.txt','w', encoding='utf-8') as f:
            if calcform.mclass.data:
                classes_txt = calcform.classtxt.data
                classes = [x.split() for x in classes_txt.splitlines()]
            orderparser = OrdersParser(price=price, classes=classes, file=f)
            _, nok, descr, order_table, summary, headers = orderparser.parse_namelist(calcform.ordertxt.data)
        
        with open('temp.txt','r', encoding='utf-8') as f:
            outputs=f.read()
        
        session['nok'] = nok
        session['descr'] = descr
        session['order_table'] = order_table
        session['summary'] = summary
        session['headers'] = headers
        session['outputs'] = outputs

        return redirect(url_for('orders'))

    return render_template("orders.html", 
        descr=session['descr'], 
        errs=session['nok'], 
        order_table=session['order_table'], 
        outputs=session['outputs'], 
        summary=session['summary'], 
        headers=session['headers'])
