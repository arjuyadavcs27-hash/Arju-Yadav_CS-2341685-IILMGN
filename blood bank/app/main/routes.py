from flask import render_template, current_app
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title='Home')

@bp.route('/about')
def about():
    return render_template('main/about.html', title='About Us')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact Us')

@bp.route('/blood-banks')
def blood_banks():
    return render_template('main/blood_banks.html', title='Blood Banks')

@bp.route('/faq')
def faq():
    return render_template('main/faq.html', title='FAQ') 