# coding: utf-8

from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, TextAreaField
from wtforms.fields.html5 import DecimalField
from wtforms.validators import DataRequired


class CalcForm(FlaskForm):
    price = DecimalField ('物品价格', validators=[DataRequired()])
    mclass = BooleanField('多分类')
    classtxt = TextAreaField()
    ordertxt = TextAreaField('接龙文本', validators=[DataRequired()])
    submit = SubmitField('Submit')