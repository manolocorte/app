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
from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField, TextAreaField, SelectField, IntegerField, FieldList, FormField,\
BooleanField
from wtforms.fields.html5 import DateField
from wtforms.widgets import TextArea
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
from flask_babel import _, lazy_gettext as _l

class CreateSyntheticSubForm(FlaskForm):
    submit = SubmitField('Submit Submission')


