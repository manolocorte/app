# (c) 2007-2022 NIHPO, Inc.
#
# This file is part of NIHPO's Synthetic Health Data Platform [https://github.com/nihpo/SynthHealthData]
#
# This platform is free software: you can redistribute it and/or modify it under the terms of the Affero GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU General Public License for more details.
# You should have received a copy of the Affero GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.txt
#
# Contact us (Jose.Lacal@NIHPO.com) for a commercial license to use the NIHPO Synthetic Health Data Platform, or if you're interested in licensing a customized version of this platform.
from flask_login import UserMixin
from CE_app import db, login
from sqlalchemy import Index
from sqlalchemy import event

class User(UserMixin, db.Model):
	__table_args__ = {"schema": "users"}
	__tablename__ = 'free_users'

	id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(64), index=True, unique=True)
	first_name = db.Column(db.String(64), index=True)
	last_name = db.Column(db.String(64), index=True)
	organization_name = db.Column(db.String(64), index=True)
	country = db.Column(db.String(64), index=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	folder_name = db.Column(db.String(120), index=True, unique=True)
	api_key = db.Column(db.String(20), index=True, unique=True)
	login_fails = db.Column(db.Integer(), index=True)
	files = db.relationship('Files', backref='file_user', lazy='dynamic')
	logs = db.relationship('Logs', backref='log_user', lazy='dynamic')
	role = db.Column(db.Integer, db.ForeignKey('users.roles.id'), index=True)
	podr_username = db.Column(db.String(64), unique=True)
	podr_password = db.Column(db.String(64))

	def __repr__(self):
		return '<User {}>'.format(self.username)

	
	def get_permissions(self):
		permissions = []
		user_role = Roles.query.filter_by(id=self.role).first()
		user_permissions = user_role.__dict__
		del user_permissions['id']
		del user_permissions['_sa_instance_state']
		for row in user_permissions:
			if user_permissions[row] == 1:
				permissions.append(row)
		return permissions


class Files(db.Model):
	__table_args__ = {"schema": "users"}

	id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String(64), index=True)
	file_type = db.Column(db.String(64), index=True)
	file_status = db.Column(db.String(64), index=True)
	module = db.Column(db.String(64), index=True)
	drugs_regulator = db.Column(db.String(64), index=True)
	drugs_randomization = db.Column(db.String(64), index=True)
	devices_regulator = db.Column(db.String(64), index=True)
	created_at = db.Column(db.DateTime, server_default=db.func.now())
	updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
	user_id = db.Column(db.Integer, db.ForeignKey('users.free_users.id'))

class Logs(db.Model):
	__table_args__ = {"schema": "users"}

	id = db.Column(db.Integer, primary_key=True)
	file_name = db.Column(db.String(), index=True)
	table = db.Column(db.String(), index=True)
	change = db.Column(db.String())
	created_at = db.Column(db.DateTime, server_default=db.func.now())
	updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
	user_id = db.Column(db.Integer, db.ForeignKey('users.free_users.id'), index=True)

class Roles(db.Model):
	__table_args__ = {"schema": "users"}

	id = db.Column(db.Integer, primary_key=True)
	role_name = db.Column(db.String(), index=True)
	read_records = db.Column(db.Integer)
	edit_records = db.Column(db.Integer)
	see_dashboards = db.Column(db.Integer)
	edit_dashboards = db.Column(db.Integer)
	create_global_dashboards = db.Column(db.Integer)
	create_submissions = db.Column(db.Integer)
	users = db.relationship('User', backref='user_role', lazy='dynamic')

# @event.listens_for(Roles.__table__, 'after_create')
# def create_roles(*args, **kwargs):
#     db.session.add(Roles(id=1, role_name='Customer Service', read_records=1))
#     db.session.commit()

@login.user_loader
def load_user(id):
	return User.query.get(int(id))
