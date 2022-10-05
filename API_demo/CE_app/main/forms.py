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
from wtforms import SubmitField, SelectField
from flask_babel import _, lazy_gettext as _l
from sqlalchemy import desc
from CE_app.models import Files
from datetime import date, datetime


d = 'Download File'

def synthetic_person_form_generator(current_user):
    class SyntheticPHRForm(FlaskForm):
        file_choices = [('NONE', 'NONE')]
        files = Files.query.filter_by(user_id=current_user.id, module = "PERSON").order_by(desc(Files.updated_at)).all()
        for file in files:
            if (file.file_type == 'JSON' or file.file_type == 'SQLITE3') and file.file_status == 'Created':
                file_choices.append((file.file_name + '.' + file.file_type.lower(), f'{file.file_name} ({file.file_type})'))
        person_files = SelectField('Person Files:', choices=file_choices)
        download = SubmitField(d)
        create = SubmitField('Create New Synthetic Person')
        check_tasks = SubmitField('Check Files Creation Status')
    return SyntheticPHRForm()

def synthetic_phr_form_generator(current_user):
    class SyntheticPHRForm(FlaskForm):
        file_choices = [('NONE', 'NONE')]
        files = Files.query.filter_by(user_id=current_user.id, module = "PHR").order_by(desc(Files.updated_at)).all()
        for file in files:
            if (file.file_type == 'JSON' or file.file_type == 'SQLITE3') and file.file_status == 'Created':
                file_choices.append((file.file_name + '.' + file.file_type.lower(), f'{file.file_name} ({file.file_type})'))
        phr_files = SelectField('PHR Files:', choices=file_choices)
        download = SubmitField(d)
        create = SubmitField('Create New Synthetic PHR')
        check_tasks = SubmitField('Check Files Creation Status')
    return SyntheticPHRForm()

def synthetic_trial_form_generator(current_user):
    class SyntheticTrialForm(FlaskForm):
        file_choices = [('NONE', 'NONE')]
        files = Files.query.filter_by(user_id=current_user.id, module = "TRIAL").order_by(desc(Files.updated_at)).all()
        for file in files:
            if file.file_type == 'ZIP' and file.file_status == 'Created':
                file_choices.append((file.file_name + '.' + file.file_type.lower(), f'{file.file_name} ({file.file_type})'))
        trial_files = SelectField('Trial Files:', choices=file_choices)
        download = SubmitField(d)
        dashboards = SubmitField('Create dashboards')
        create = SubmitField('Create New Synthetic Trial')
        check_tasks = SubmitField('Check Files Creation Status')
    return SyntheticTrialForm()

def synthetic_sub_form_generator(current_user):
    class SyntheticSubForm(FlaskForm):
        file_choices = [('NONE', 'NONE')]
        files = Files.query.filter_by(user_id=current_user.id, module = "SUBMISSION").order_by(desc(Files.updated_at)).all()

        for file in files:

            # Update time to correct syntax
            file_date_update = file.updated_at.strftime("%m/%d/%Y, %H:%M:%S")

            # Assign sub files to droplist
            file_choices.append((file.file_name + '.sqlite3', f'file.file_name  ({file_date_update})'))
        
        # Define form fields
        sub_files = SelectField('Trial Files:', choices=file_choices)
        download = SubmitField(d)
        create = SubmitField('Create New Synthetic Submission')
        
    return SyntheticSubForm()

class LicenseForUseForm(FlaskForm):
    submit = SubmitField('I Accept')

class DisclaimerForm(FlaskForm):
    submit = SubmitField('I Accept')   
