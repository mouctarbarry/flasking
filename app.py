"""Flask Application for Paws Rescue Center."""
from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm, EditPetForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paws.db'
db = SQLAlchemy(app)

"""Model for Pets."""


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    age = db.Column(db.String)
    bio = db.Column(db.String)
    posted_by = db.Column(db.String, db.ForeignKey('user.id'))


"""Model for Users."""


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    pets = db.relationship('Pet', backref='user')


with app.app_context():
    db.create_all()

    # Define a list of users to add
    users_to_add = [
        User(full_name="Pet Rescue Team", email="team@petrescue.co", password="adminPass")
    ]

    # Define a list of pets to add
    pets_to_add = [
        Pet(name="Nelly", age="5 weeks",
            bio="I am a tiny kitten rescued by the good people at Paws Rescue Center. "
                "I love squeaky toys and cuddles."),
        Pet(name="Yuki", age="8 months", bio="I am a handsome gentle-cat. I like to dress up in bow ties."),
        Pet(name="Basker", age="1 year", bio="I love barking. But, I love my friends more."),
        Pet(name="Mr. Furrkins", age="5 years", bio="Probably napping.")
    ]

    # Add users to the session if they don't already exist
    for user in users_to_add:
        existing_user = User.query.filter_by(email=user.email).first()
        if existing_user is None:
            db.session.add(user)

    # Add pets to the session if they don't already exist
    for pet in pets_to_add:
        existing_pet = Pet.query.filter_by(name=pet.name).first()
        if existing_pet is None:
            db.session.add(pet)

    # Commit changes in the session
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()


@app.route("/")
def homepage():
    """View function for Home Page."""
    pets = Pet.query.all()
    return render_template("home.html", pets=pets)


@app.route("/about")
def about():
    """View function for About Page."""
    return render_template("about.html")


@app.route("/details/<int:pet_id>", methods=["POST", "GET"])
def pet_details(pet_id):
    """View function for Showing Details of Each Pet."""
    form = EditPetForm()
    a_pet = Pet.query.get(pet_id)
    if a_pet is None:
        abort(404, description="No Pet was Found with the given ID")
    if form.validate_on_submit():
        a_pet.name = form.name.data
        a_pet.age = form.age.data
        a_pet.bio = form.bio.data
        try:
            db.session.commit()
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return render_template("details.html", pet=a_pet, form=form, message="A Pet with this name already exists!")
    return render_template("details.html", pet=a_pet, form=form)


@app.route("/delete/<int:pet_id>")
def delete_pet(pet_id):
    a_pet = Pet.query.get(pet_id)
    if a_pet is None:
        abort(404, description="No Pet was Found with the given ID")
    db.session.delete(a_pet)
    try:
        db.session.commit()
    except Exception as ex:
        print(ex)
        db.session.rollback()
    return redirect(url_for('homepage', _scheme='http', _external=True))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    """View function for Showing Details of Each Pet."""
    form = SignUpForm()
    if form.validate_on_submit():
        new_user = User(full_name=form.full_name.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as ex:
            print(ex)
            db.session.rollback()
            return render_template("signup.html", form=form,
                                   message="This Email already exists in the system! Please Login instead.")
        finally:
            db.session.close()
        return render_template("signup.html", message="Successfully signed up")
    return render_template("signup.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        a_user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if a_user is None:
            return render_template("login.html", form=form, message="Wrong Credentials. Please Try Again.")
        else:
            session['user'] = a_user.id
            return render_template("login.html", message="Successfully Logged In!")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('homepage', _scheme='http', _external=True))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
