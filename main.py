from flask import Flask, render_template, redirect, url_for,flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_databases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'mysecretkeyishere'
Bootstrap(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    author = db.Column(db.String(50), nullable=False) 
    rating = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()

class Form(FlaskForm):
    title = StringField('Book Name', validators=[DataRequired()])
    author = StringField('Book Author', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Add Book')

@app.route('/')
def home_page():
    books = Book.query.order_by(Book.rating.desc()).all()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = Form()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            rating=form.rating.data
        )
        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect(url_for('home_page'))
        except IntegrityError:
            db.session.rollback()  # Rollback on error
            flash('This author already has a book in the database.', 'error')  # Use flash to show error message
    return render_template('add.html', form=form)


@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit(book_id):
    book = Book.query.get(book_id)
    if book is None:
        return redirect(url_for('home_page'))  # Redirect if book not found

    form = Form(
        title=book.title,
        author=book.author,
        rating=book.rating
    )

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.rating = form.rating.data
        db.session.commit()
        return redirect(url_for('home_page'))

    return render_template('edit.html', form=form, book=book)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=False)
