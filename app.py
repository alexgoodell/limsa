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
		return '<Chain %r>' % self.name

class State(db.Model):
	__tablename__ = 'states'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	chain_id = db.Column(db.Integer,db.ForeignKey('chains.id'))

	def __repr__(self):
		return '<State %r>' % self.name





# type State struct {
# 	Id                        int
# 	Model_id                  int
# 	Name                      string
# 	Is_uninitialized_state    bool
# 	Is_uninitialized_2_state  bool
# 	Is_disease_specific_death bool
# 	Is_other_death            bool
# 	Is_natural_causes_death   bool
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

# type TransitionProbability struct {
# 	Id      int
# 	From_id int
# 	To_id   int
# 	Tp_base float64
# 	PSA_id  int
# }


class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	users = db.relationship('User', backref='role')

	def __repr__(self):
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username




### Migration manager

from flask.ext.migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__': 
	manager.run()





