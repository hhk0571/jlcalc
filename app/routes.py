# coding: utf-8

from flask import render_template, flash, redirect, url_for, request
from app import app
import app.calc_namelist as calc


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/orders", methods=["POST"])
def orders():
    price = float(request.form.get('price', 88))
    classes = None

    with open('temp.txt','w') as f:
        if request.form.get('mclass') == "True":
            classes_txt = request.form.get('classes')
            classes = [x.split() for x in classes_txt.splitlines()]
        orderparser = calc.OrdersParser(price=price, classes=classes, file=f)
        _, nok, descr, order_table, summary, headers = orderparser.parse_namelist(request.form.get("order_txt"))
    
    with open('temp.txt','r') as f:
        outputs=f.read()

    return render_template("orders.html", descr=descr, errs=nok, order_table=order_table, outputs=outputs, summary=summary, headers=headers)
