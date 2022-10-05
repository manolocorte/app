# (c) 2007-2022 NIHPO, Inc.
#
# This file is part of NIHPO's Synthetic Health Data Platform [https://github.com/nihpo/SynthHealthData]
#
# This platform is free software: you can redistribute it and/or modify it under the terms of the Affero GNU General Public License as published by the Free Software Foundation, version 3.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the Affero GNU General Public License for more details.
# You should have received a copy of the Affero GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.txt
#
# Contact us (Jose.Lacal@NIHPO.com) for a commercial license to use the NIHPO Synthetic Health Data Platform, or if you're interested in licensing a customized version of this platform.
#
from flask import render_template
from CE_app import db
from CE_app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(in_error):
	"""
	Throws an error page when 404 error is found (the url is incorrect)

	:param error: Error 404 message
	:type error: Error Object
	:returns: Error 404 page
	:rtype: HTML page
	"""
	return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(in_error):
	"""
	Throws an error page when 500 error is found (some problem with the users DB). And rollback the DB to avoid wrong changes

	:param error: Error 500 message
	:type error: Error Object
	:returns: Error 500 page
	:rtype: HTML page
	"""
	db.session.rollback()
	return render_template('errors/500.html'), 500

@bp.app_errorhandler(502)
def internal_error(in_error):
	"""
	Throws an error page when 502 error is found (some problem with the server connection). And rollback the DB to avoid wrong changes

	:param error: Error 502 message
	:type error: Error Object
	:returns: Error 502 page
	:rtype: HTML page
	"""
	db.session.rollback()
	return render_template('errors/502.html'), 502
