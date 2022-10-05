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
from flask import request, jsonify, render_template, redirect, url_for, session, flash
from flask_login import current_user, login_required
from flask.globals import current_app
from CE_app import db
from CE_app.models import Files
from CE_app.synth_person import bp
from CE_app.synth_person.forms import select_countries_form_generator, synthetic_person_form_generator
from CE_app.synth_phr.functions import Domains
from CE_app.synth_person.functions import func_nihpo_generate_json_file, func_nihpo_generate_SQLite3_file

@bp.route('/select_countries', methods=['GET', 'POST'])
@login_required
def select_countries():
    form = select_countries_form_generator(current_app)

    if form.add.data:
            form.country.append_entry()
    if form.remove.data:
            form.country.pop_entry()
    if form.validate_on_submit():
        if form.submit.data:
            countries = []
            people = []
            for idx, data in enumerate(form.country.data):
                if (data["country"] and data["number"]):
                    countries.append((data["country"], data["number"]))
            
            session['Data_' + current_user.username]['countries'] = countries
            return redirect(url_for('synth_person.create_synthperson'))
    return render_template('synth_person/select_countries.html', title='Create New SynthPerson', form=form, version=current_app.config['CT_NOTE_VERSION'])

@bp.route('/create_synthperson', methods=['GET', 'POST'])
@login_required
def create_synthperson():

    # Initialize variables
    data_countries = ''
    list_data_countries = []
    country_names = []
    country_names_subjects = []

    # Take countries from session
    try:
        countries = session['Data_' + current_user.username]['countries']
    except:
        flash('Please select correct countries')
        return redirect(url_for('synth_person.select_countries'))
    
    for item in countries:
        data_countries = data_countries + str(item[0]) + ',' + str(item[1]) + ';'
    data_countries = data_countries[:-1]

    for item in data_countries.split(';'):
        item_tupled = tuple(item.split(','))
        list_data_countries.append(item_tupled)
        country_name = Domains.geography(in_country_code_iso=item_tupled[0])["NIHPO_API"]["Results"][0]['Country_Name']
        country_names.append(country_name)
        country_names_subjects.append([country_name, item_tupled[1]])

    # Initialize form
    form = synthetic_person_form_generator(current_app)

    # Receive data once user submit it
    if form.validate_on_submit():

        file_name = form.output_file_name.data
        min_age = int(form.min_age.data)
        max_age = int(form.max_age.data)
        female = form.female.data
        male = form.male.data
        output_type = form.output_type.data

        # Initialize variables
        folder_name = current_user.folder_name
        first_name = current_user.first_name
        last_name = current_user.last_name
        email = current_user.email

        options_requested = {'Countries': country_names_subjects, 'Age range': [min_age, max_age], 'Gender distribution': [female, male], 'File name': file_name, 'Output type': output_type}
    
        flash_message = f"You requested: countries({countries}), age range({min_age}, {max_age}), gender distribution(Female:{female}%%, Male:{male}%%), file name({file_name}), output type({output_type})"

        # Show message
        flash(flash_message)

        if output_type == 'JSON':
            if current_app.config['PROFILE']:
                result = func_nihpo_generate_json_file(min_age, max_age, female, male, list_data_countries, folder_name, file_name, first_name, last_name, email, country_names)
            else:
                result = func_nihpo_generate_json_file.apply_async((min_age, max_age, female, male, list_data_countries, folder_name, file_name, first_name, last_name, email, country_names), countdown=1)
        elif output_type == 'SQLITE3':
            if current_app.config['PROFILE']:
                result = func_nihpo_generate_SQLite3_file(min_age, max_age, female, male, list_data_countries, folder_name, file_name, first_name, last_name, email, country_names, current_user.id)
            else:
                result = func_nihpo_generate_SQLite3_file.apply_async((min_age, max_age, female, male, list_data_countries, folder_name, file_name, first_name, last_name, email, country_names, current_user.id), countdown=1)

        # Add the task to the user tasks
        if not current_app.config['PROFILE']:
            try:
                if len(session[current_user.username + '_tasks_person_id']) >= 5:
                    session[current_user.username + '_tasks_person_id'] = session[current_user.username + '_tasks_person_id'][-4:]
                    session[current_user.username + '_tasks_person_parameters'] = session[current_user.username + '_tasks_person_parameters'][-4:]
                session[current_user.username + '_tasks_person_id'].append(result.id)
                session[current_user.username + '_tasks_person_parameters'].append(options_requested)
            except:
                session[current_user.username + '_tasks_person_id'] = [result.id]
                session[current_user.username + '_tasks_person_parameters'] = [options_requested]
            session[current_user.username + '_tasks_person_id'] = session[current_user.username + '_tasks_person_id']
            session[current_user.username + '_tasks_person_parameters'] = session[current_user.username + '_tasks_person_parameters']

        if current_app.env == 'development':
            files = Files.query.filter_by(user_id=current_user.id, module = "PERSON").all()
            for file in files:
                if file_name  == file.file_name:
                    db.session.delete(file)

        # Create file in the DB
        if current_app.config['PROFILE']:
            file = Files(file_name=file_name, file_type=output_type, file_status='Created', file_user=current_user, module='PERSON')
        else:
            file = Files(file_name=file_name, file_type=output_type, file_status='Pending', file_user=current_user, module='PERSON')
        db.session.add(file)
        db.session.commit()

        return redirect(url_for('main.synthperson'))

    return render_template('synth_person/create_synthperson.html', title='Create New SynthPerson', form=form, name='diego', version=current_app.config['CT_NOTE_VERSION'])

@bp.route('/check_tasks', methods=['GET', 'POST'])
def check_tasks():
    try:
        tasks = session[current_user.username + '_tasks_person_id']
    except:
        tasks = []
    return render_template('bars.html', tasks=tasks, file_type='person', version=current_app.config['CT_NOTE_VERSION'])