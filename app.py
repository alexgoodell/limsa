
import os
from flask import Flask, render_template, session, redirect, url_for, flash
app = Flask(__name__)

app.config['SECRET_KEY'] = 'x3432d3232432lkjew3242'
# allows for debuging mode in runserver
app.config['DEBUG'] = True 

from flask.ext.script import Manager, Shell
manager = Manager(app)

from flask.ext.bootstrap import Bootstrap
bootstrap = Bootstrap(app)

# Flask-WTF
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField 
from wtforms.validators import Required

class NameForm(Form):
	name = StringField('What is your name?', validators=[Required()]) 
	submit = SubmitField('Submit')


#### ---------------- Routes -------------------------

@app.route('/', methods=['GET', 'POST']) 
def index():
	form = NameForm()
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('Looks like you have changed your name!')
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('index'))
	return render_template('index.html', form=form, name=session.get('name'))


@app.route('/user/<name>') 
def user(name):
	return render_template('user.html', name=name)


@app.route('/chains') 
def chains_view():
	chains = Chain.query.all()
	return render_template('chains.html', chains=chains)

# if __name__ == '__main__':
# 	app.run(debug=True)





#### ---------------- Models -------------------------

from flask.ext.sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database/limsa.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


class Chain(db.Model):
	__tablename__ = 'chains'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	states = db.relationship('State', backref='chain')

	def __repr__(self):
		return self.name

class State(db.Model):
	__tablename__ = 'states'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	Chain = db.relationship("Chain", foreign_keys=[chain_id])


	# TODO: Add chain name to representation
	def __repr__(self):
		return self.name

class Transition_probability(db.Model):
	__tablename__ = 'transition_probabilities'
	id = db.Column(db.Integer, primary_key=True)

	From_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	To_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	From_state = db.relationship("State", foreign_keys=[From_state_id])
	To_state = db.relationship("State", foreign_keys=[To_state_id])

	Tp_base = db.Column(db.Float)

	Is_dynamic = db.Column(db.Boolean)

	Chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))
	Chain = db.relationship("Chain", foreign_keys=[Chain_id])

	def __repr__(self):
		return self.From_state.name + " => " + self.To_state.name

class Interaction(db.Model):
	__tablename__ = 'interactions'
	id = db.Column(db.Integer, primary_key=True)

	In_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	From_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))
	To_state_id = db.Column(db.Integer,db.ForeignKey('states.id'))

	In_state = db.relationship("State", foreign_keys=[In_state_id])
	From_state = db.relationship("State", foreign_keys=[From_state_id])
	To_state = db.relationship("State", foreign_keys=[To_state_id])

	Adjustment = db.Column(db.Float)

	Effected_chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))

	def __repr__(self):
		return self.In_state.name + " affects " + self.From_state.name + " => " + self.To_state.name

# type TransitionProbability struct {
# 	Id      int
# 	From_id int
# 	To_id   int
# 	Tp_base float64
# 	PSA_id  int
# }

# type Interaction struct {
# 	Id                int
# 	In_state_id       int
# 	From_state_id     int
# 	To_state_id       int
# 	Adjustment        float64
# 	Effected_model_id int
# 	PSA_id            int
# }



class Raw_input(db.Model):
	__tablename__ = 'raw_inputs'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	slug = db.Column(db.String(64), unique=True)
	value = db.Column(db.Float)
	low = db.Column(db.Float)
	high = db.Column(db.Float)
	reference_id = db.Column(db.Integer,db.ForeignKey('references.id'))

	def __repr__(self):
		return self.name

class Reference(db.Model):
	__tablename__ = 'references'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(4000))
	bibtex = db.Column(db.String(2000))
	raw_data = db.relationship('Raw_input', backref='reference')

	def __repr__(self):
		return self.name


#### ---------------- Admin -------------------------


from flask.ext.superadmin import Admin, model


 # Create admin
admin = Admin(app, 'Simple Models')

# Add views
admin.register(Chain, session=db.session)
admin.register(State, session=db.session)
admin.register(Raw_input, session=db.session)
admin.register(Reference, session=db.session)
admin.register(Transition_probability, session=db.session)
admin.register(Interaction, session=db.session)


# admin.add_view(sqlamodel.ModelView(Post, session=db.session))

# Create DB
db.create_all()


# Start app
### Migration manager

from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# if __name__ == '__main__': 
# 	manager.run()

if __name__ == '__main__':
	app.run(host='0.0.0.0')


