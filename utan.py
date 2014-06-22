import datetime
import os
import stripe

from flask import Flask, request, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy

# STRIPE ACCOUNT: durianpy.stripe@yopmail.com / tester101

TEST_SECRET_KEY = 'sk_test_uDRQbDeQMHk1mc4WhkvD2z5K'
TEST_PUBLIC_KEY = 'pk_test_a8OgVzFR6WRG0vcdLIseTi2U'

app = Flask(__name__)
DB_NAME = 'utan_db'
DB_USER = 'ralphleyga'
DB = 'postgresql://postgres:%s@localhost/%s' % (DB_USER, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = DB
app.config['autocommit'] = True
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret key'
db = SQLAlchemy(app)

GULAY = {
    'pechay': 5,
    'kangkong': 10,
    'malunggay': 15
}


class PaidItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(80))
    email = db.Column(db.String(120))
    amount = db.Column(db.Integer())
    date_added = db.Column(db.DateTime())

    def __init__(self, item, amount, email):
        self.item = item
        self.amount = amount
        self.email = email
        self.date_added = datetime.datetime.today()

    def __repr__(self):
        return '<Customer %r>' % self.email


@app.route('/', methods=['GET', 'POST'])
def home():
    context = {
        'TEST_PUBLIC_KEY': TEST_PUBLIC_KEY,
        'paid_items': PaidItem.query.order_by(PaidItem.date_added.desc())
    }
    stripe.api_key = TEST_SECRET_KEY
    total = 0
    description = 'Paid Item\n'
    if request.method == 'POST':
        card = request.form['stripeToken']
        email = request.form['email']
        for item in request.form.getlist('item'):
            total += GULAY[item] * 100
            description += '%s : %s \n' % (item, GULAY[item])
            paid_item = PaidItem(item, GULAY[item], email)
            db.session.add(paid_item)
            db.session.commit()
        description += 'customer email: %s' % (email)

        if total > 0:
            # Charge card
            stripe.Charge.create(
                amount=total,
                currency="usd",
                card=card,
                description=str(description)
            )
            flash('Utan Paid!')
        else:
            flash('Select Utan!')
    return render_template('main.html', data=context)


if __name__ == '__main__':
    app.run()
