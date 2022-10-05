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
from datetime import datetime
from flask import redirect, render_template, flash, url_for, current_app, session, send_file, jsonify
from flask_babel import _
from CE_app.main import bp
from flask_login import current_user, login_required
from CE_app import celery
from CE_app.main.forms import synthetic_person_form_generator, synthetic_phr_form_generator, synthetic_trial_form_generator, LicenseForUseForm, DisclaimerForm
from CE_app.synth_trial.functions import func_nihpo_update_sqlite3_in_superset
from CE_app.main.forms import synthetic_sub_form_generator
from CE_app.models import Files

c = 'Choose a correct file.'



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title=_('Home'), version = current_app.config['CT_NOTE_VERSION'])

@bp.route('/synthperson', methods=['GET', 'POST'])
@login_required
def synthperson():
    form = synthetic_person_form_generator(current_user)
    if form.validate_on_submit():
        if form.create.data:
            data = {}
            data['type'] = 'person'
            session['Data_' + current_user.username] = data
            return redirect(url_for('synth_person.select_countries'))
        elif form.download.data:
            file_name = form.person_files.data
            if file_name != 'NONE':
                return send_file(current_app.config["CT_DOWNLOADS_PATH"] + file_name, as_attachment=True)
            else:
                flash(c)
    return render_template('synth_person/synthperson.html', title='SynthPerson', form=form, version = current_app.config['CT_NOTE_VERSION'])

@bp.route('/synthphr', methods=['GET', 'POST'])
@login_required
def synthphr():
    form = synthetic_phr_form_generator(current_user)
    if form.validate_on_submit():
        if form.create.data:
            data = {}
            data['type'] = 'phr'
            session['Data_' + current_user.username] = data
            return redirect(url_for('synth_phr.select_countries'))
        elif form.download.data:
            file_name = form.phr_files.data
            if file_name != 'NONE':
                return send_file(current_app.config["CT_DOWNLOADS_PATH"] + file_name, as_attachment=True)
            else:
                flash(c)
    return render_template('synth_phr/synthphr.html', title='SynthPHR', form=form, version = current_app.config['CT_NOTE_VERSION'])


@bp.route('/synthtrial', methods=['GET', 'POST'])
@login_required
def synthtrial():
    form = synthetic_trial_form_generator(current_user)
    file_name_with_zip = form.trial_files.data
    file_name = 'Not chosen'
    if form.validate_on_submit():
        if form.create.data:
            data = {}
            data['type'] = 'trial'
            session['Data_' + current_user.username] = data
            return redirect(url_for('synth_trial.trial_summary_parameters'))
              
        elif form.dashboards.data:
            if file_name_with_zip != 'NONE':
                file_name = file_name_with_zip[:-4]

                func_nihpo_update_sqlite3_in_superset(current_app.config["CT_DOWNLOADS_PATH"], file_name, current_app.config['CT_SUPERSET_DB_PATH'])
                return redirect(url_for('synth_trial.dashboards', file_name=file_name, user_id=current_user.id, user_folder=current_user.folder_name))
            else:
                flash(c)

        elif form.download.data:
            if file_name_with_zip != 'NONE':
                return send_file(current_app.config["CT_DOWNLOADS_PATH"] + file_name_with_zip, as_attachment=True)
            else:
                flash(c)
    return render_template('synth_trial/synthtrial.html', title='SynthTrial', form=form,
        version = current_app.config['CT_NOTE_VERSION'], file_name=file_name, href=current_app.config['CT_SUPERSET_HREF'])


@bp.route('/synthsub', methods=['GET', 'POST'])
@login_required
def synthsub():
    form = synthetic_sub_form_generator(current_user)
    if form.validate_on_submit():
        file_name = form.sub_files.data
        if file_name != 'NONE':
            return send_file(current_app.config["CT_DOWNLOADS_PATH"] + file_name, as_attachment=True)
            
        else:
            flash(c)
    return render_template('synth_sub/synthsub.html', title='SynthSubmission', form=form, version = current_app.config['CT_NOTE_VERSION'])

# Routes for everybody
@bp.route('/help')
def help():
    return render_template('help.html', title='Help', version = current_app.config['CT_NOTE_VERSION'])
@bp.route('/aboutus')
def aboutus():
    return render_template('about.html', title='About Us', version = current_app.config['CT_NOTE_VERSION'])
@bp.route('/contactus')
def contactus():
    return render_template('contact.html', title='Contact Us', version = current_app.config['CT_NOTE_VERSION'])

@bp.route('/license', methods=['GET', 'POST'])
@login_required
def license_for_use():
    form = LicenseForUseForm()
    if form.validate_on_submit():
        return redirect(url_for('main.disclaimer'))
    return render_template('licenseforuse.html', title='License For Use', form=form, version = current_app.config['CT_NOTE_VERSION'])

@bp.route('/disclaimer', methods=['GET', 'POST'])
@login_required
def disclaimer():
    form = DisclaimerForm()
    data = session.get('Data_' + current_user.username, None)
    if form.validate_on_submit():
        if data['type'] == 'phr':
            return redirect(url_for('synth_phr.create_synthphr'))
        return redirect(url_for('main.thank_you'))
    return render_template('disclaimer.html', title='Disclaimer', form=form, version = current_app.config['CT_NOTE_VERSION'])

@bp.route('/thankyou')
@login_required
def thank_you():
    return render_template('thankyou.html', title='Thank you', version = current_app.config['CT_NOTE_VERSION'])

@celery.task(bind=True)
def long_task(self):
    """
    Background task that runs a long function with progress reports.
    """
    return True

@bp.route('/status/<task_id>/<task_parameters>')
def taskstatus(task_id, task_parameters=None):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...',
            'parameters': task_parameters
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            'parameters': task_parameters
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        if current_app.env == 'development':
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': str(task.info),  # this is the exception raised
                'parameters': task_parameters
            }
        elif current_app.env == 'production':
            response = {
                'state': task.state,
                'current': 1,
                'total': 1,
                'status': "There was some error during the file creation, try again please",  # this is the exception raised
                'parameters': task_parameters
            }
    return jsonify(response)

@bp.route('/pass_task_trial/<number_task>', methods=['POST'])
def pass_task_trial(number_task=None):
    try:
        task_id = session.get(current_user.username + '_tasks_trial_id', None)[int(number_task)]
        task_parameters = session.get(current_user.username + '_tasks_trial_parameters', None)[int(number_task)]
    except:
        session[current_user.username + '_tasks_trial_id'] = session.get(current_user.username + '_tasks_trial_id', None)[-1:]
        session[current_user.username + '_tasks_trial_parameters'] = session.get(current_user.username + '_tasks_trial_parameters', None)[-1:]
        task_id = session[current_user.username + '_tasks_trial_id']
        task_parameters = session[current_user.username + '_tasks_trial_parameters']
    return jsonify({}), 202, {'Location': url_for('main.taskstatus', task_id=task_id, task_parameters=task_parameters)}

@bp.route('/pass_task_phr/<number_task>', methods=['POST'])
def pass_task_phr(number_task=None):
    try:
        task_id = session.get(current_user.username + '_tasks_phr_id', None)[int(number_task)]
        task_parameters = session.get(current_user.username + '_tasks_phr_parameters', None)[int(number_task)]
    except:
        session[current_user.username + '_tasks_phr_id'] = session.get(current_user.username + '_tasks_phr_id', None)[-1:]
        session[current_user.username + '_tasks_phr_parameters'] = session.get(current_user.username + '_tasks_phr_parameters', None)[-1:]
        task_id = session[current_user.username + '_tasks_phr_id']
        task_parameters = session[current_user.username + '_tasks_phr_parameters']
    return jsonify({}), 202, {'Location': url_for('main.taskstatus', task_id=task_id, task_parameters=task_parameters)}

@bp.route('/pass_task_person/<number_task>', methods=['POST'])
def pass_task_person(number_task=None):
    try:
        task_id = session.get(current_user.username + '_tasks_person_id', None)[int(number_task)]
        task_parameters = session.get(current_user.username + '_tasks_person_parameters', None)[int(number_task)]
    except:
        session[current_user.username + '_tasks_person_id'] = session.get(current_user.username + '_tasks_person_id', None)[-1:]
        session[current_user.username + '_tasks_person_parameters'] = session.get(current_user.username + '_tasks_person_parameters', None)[-1:]
        task_id = session[current_user.username + '_tasks_person_id']
        task_parameters = session[current_user.username + '_tasks_person_parameters']
    return jsonify({}), 202, {'Location': url_for('main.taskstatus', task_id=task_id, task_parameters=task_parameters)}

