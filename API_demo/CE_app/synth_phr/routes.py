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
from CE_app.synth_phr import bp
from CE_app.synth_phr.functions import Domains
from CE_app.synth_phr.json_subject_creation import func_nihpo_json_file
from CE_app.synth_phr.sqlite_subject_creation import func_nihpo_generate_SQLite3_file
from CE_app.synth_phr.forms import select_countries_form_generator, synthetic_phr_form_generator
from CE_app.synth_phr.sqlite_subject_creation import func_nihpo_subjects_creation
from CE_app import db
from CE_app.models import Files

error_path = 'errors/error.html'

@bp.route('/api/v01/home', methods=['GET'])
@login_required
def api_home():

    return render_template('synth_phr/home.html')

@bp.route('/api/v01/condition', methods=['GET'])
@login_required
def api_condition():
    query_parameters = request.args

    hierarchy_list = query_parameters.get('record_type')
    source = query_parameters.get('source')
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/condition.html')
        except:
            return render_template(error_path)

    result = Domains.condition.apply_async(args=[hierarchy_list, source, number])
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    api/v01/condition
    api/v01/condition?record_type=disorder,finding
    api/v01/condition?source=snomed_ct_core
    api/v01/condition?help

    """

@bp.route('/api/v01/device', methods=['GET'])
@login_required
def api_device():
    query_parameters = request.args

    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/device.html')
        except:
            return render_template(error_path)

    result = Domains.device(in_number=number)
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    api/v01/device
    api/v01/device?help
    
    """
    
@bp.route('/api/v01/drug', methods=['GET'])
@login_required
def api_drug():

    query_parameters = request.args

    active_ingredient = query_parameters.get('active_ingredient')
    applno = query_parameters.get('applno')
    form = query_parameters.get('form')
    regulator_code_list = query_parameters.get('regulator')
    inn= query_parameters.get('inn')
    source = query_parameters.get('source')
    submission_type = query_parameters.get('submission_type')
    name = query_parameters.get('name')
    sponsor = query_parameters.get('sponsor')
    marketing_status = query_parameters.get('marketing_status')
    help_active_ingredients = query_parameters.get('help_active_ingredients')
    help_names = query_parameters.get('help_names') 
    help_sponsors = query_parameters.get('help_sponsors')
    list_active_ingredients = query_parameters.get('list_active_ingredients')   
    list_drugs = query_parameters.get('list_drugs')
    list_sponsors = query_parameters.get('list_sponsors')   
    indication = query_parameters.get('indication')
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/drug.html')
        except:
            return render_template(error_path)

    result = Domains.drug(in_active_ingredient=active_ingredient, in_applno=applno, in_form=form, in_regulator_code_list=regulator_code_list, in_inn=inn,\
        in_source=source, in_submission_type=submission_type, in_name=name, in_sponsor=sponsor, in_marketing_status=marketing_status, \
        in_help_active_ingredients=help_active_ingredients, in_help_names=help_names, in_help_sponsors=help_sponsors, in_list_active_ingredients=list_active_ingredients,\
        in_list_drugs=list_drugs, in_list_sponsors=list_sponsors, in_indication= indication, in_number=number)
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    FDA:

    api/v01/drug?regulator=us_fda
    api/v01/drug?regulator=us_fda&active_ingredient=sulfapyridine
    api/v01/drug?regulator=us_fda&applno=000552
    api/v01/drug?regulator=us_fda&form=vial
    api/v01/drug?regulator=us_fda&marketing_status=disc
    api/v01/drug?regulator=us_fda&name=paredrine
    api/v01/drug?regulator=us_fda&sponsor=pharmics
    api/v01/drug?regulator=us_fda&submission_type=orig
    api/v01/drug?regulator=us_fda&help_active_ingredients=a
    api/v01/drug?regulator=us_fda&help_names=c
    api/v01/drug?regulator=us_fda&help_sponsors=h
    api/v01/drug?help

    EMA:

    api/v01/drug?regulator=eu_ema
    api/v01/drug?regulator=eu_ema&active_ingredient=peramivir
    api/v01/drug?regulator=eu_ema&applno=000482
    api/v01/drug?regulator=eu_ema&marketing_status=authorised
    api/v01/drug?regulator=eu_ema&name=zalmoxis
    api/v01/drug?regulator=eu_ema&sponsor=bayer ag
    api/v01/drug?regulator=eu_ema&help_active_ingredients=a
    api/v01/drug?regulator=eu_ema&help_names=c
    api/v01/drug?regulator=eu_ema&help_sponsors=h

    """
#
#
@bp.route('/api/v01/geography', methods=['GET'])
@login_required
def api_geography():
    #(To do): Better handling of errors.
    #(To do): There are loading errors in the Geography dataset. (Unicode characters that did not get loaded properly)
    query_parameters = request.args

    country_code_iso = query_parameters.get('country')
    location_state = query_parameters.get('state')
    location = query_parameters.get('location')
    help_country = query_parameters.get('help_country')
    randomize = query_parameters.get('randomize')
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/geography.html')
        except:
            return render_template(error_path)
    if 'help_countries' in request.args:
        help_countries = True
    else:
        help_countries = False
    if 'states' in request.args:
        states = True
    else:
        states = False
    if 'locations' in request.args:
        locations = True
    else:
        locations = False

    result = Domains.geography(in_country_code_iso=country_code_iso, in_location_state=location_state, in_location=location, in_help_country=help_country,\
        in_help_countries=help_countries, in_states=states, in_locations=locations, in_randomize=randomize, in_number=number)
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    api/v01/geography
    api/v01/geography?country=us
    api/v01/geography?country=us&state=fl
    api/v01/geography?help_countries
    api/v01/geography?help_country=de&states
    api/v01/geography?help_country=us&state=fl&locations
    api/v01/geography?help

    """

@bp.route('/api/v01/lab_result', methods=['GET'])
@login_required
def api_lab_result():
    query_parameters = request.args

    cdisc_common_tests = query_parameters.get('cdisc_common_tests') 
    class_type = query_parameters.get('class_type')
    loinc_num = query_parameters.get('loinc_num')
    panel_type = query_parameters.get('panel_type')
    rank = query_parameters.get('rank')
    record_type = query_parameters.get('record_type')
    source = query_parameters.get('source')
    status = query_parameters.get('status')
    atc_code_filter = query_parameters.get('atc_code_filter')
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/lab_result.html')
        except:
            return render_template(error_path)

    result = Domains.lab_result(in_cdisc_common_tests=cdisc_common_tests, in_class_type=class_type, in_loinc_num=loinc_num, in_panel_type=panel_type,\
         in_rank=rank, in_record_type=record_type, in_source=source, in_status=status, in_atc_code_filter=atc_code_filter, in_number=number)
    return jsonify(result)

    """
    Test URLs:

    api/v01/lab_result
    api/v01/lab_result?cdisc_common_tests=y
    api/v01/lab_result?class_type=1,2
    api/v01/lab_result?loinc_num="6896-5"
    api/v01/lab_result?panel_type=organizer,convenience
    api/v01/lab_result?rank=order
    api/v01/lab_result?status=deprecated
    api/v01/lab_result?source=loinc
    api/v01/lab_result?help

    """

@bp.route('/api/v01/procedure', methods=['GET'])
@login_required
def api_procedure():
    query_parameters = request.args

    hierarchy_list = query_parameters.get('record_type')
    number = query_parameters.get('number')
    source = query_parameters.get('source')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/procedure.html')
        except:
            return render_template(error_path)

    result = Domains.procedure(in_hierarchy_list=hierarchy_list, in_source=source, in_number=number)
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    api/v01/procedure
    api/v01/procedure?record_type=procedure,regime/therapy
    api/v01/procedure?help
    
    """

@bp.route('/api/v01/provider', methods=['GET'])
@login_required
def api_provider():
    query_parameters = request.args

    state = query_parameters.get('state')   
    city = query_parameters.get('city')
    npi = query_parameters.get('npi')
    entity_type_code = query_parameters.get('entity_type')
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/provider.html')
        except:
            return render_template(error_path)

    '''
    if 'help_states' in request.args:
        query = "SELECT state_code, state_name FROM nihpo_states WHERE country_code_iso= 'US' ORDER BY state_code ASC;"
        results = cur.execute(query)
        choose_all = cur.fetchall()
        for row in choose_all:
            final_result.append(dict(row))
        return jsonify(final_result)
    if 'help_cities' in request.args:
        query = """SELECT DISTINCT "Provider Business Mailing Address City Name" FROM hhs_cms_npi_npidata_pfile WHERE "Provider Business Mailing Address State Name" = '%(state)s';"""
        to_filter['state'] = state
        results = cur.execute(query, to_filter)
        choose_all = cur.fetchall()
        for row in choose_all:
            final_result.append(dict(row))
        for data in final_result:
                data['Cities'] = data.pop('Provider Business Mailing Address City Name')
        res = defaultdict(list) 
        for sub in final_result: 
            for key in sub: 
                res[key].append(sub[key])
        try:
            res['Cities'] = sorted(dict(res)['Cities'])
        except:
            return render_template(error_path)
        final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
        final_result_1['NIHPO_API']['Results'] = res
        final_result_1['NIHPO_API']["Note_Source"] = Config.CT_PROVIDER_NOTE_SOURCE
        return jsonify(final_result_1)'''
    
    # if npi:
    #   query += """
    #   FROM hhs_cms_npi_npidata_pfile
    #   WHERE "Entity Type Code" = 1 AND"""
    # else:
    #   query += """ 
    #   FROM hhs_cms_npi_npidata_pfile
    #   TABLESAMPLE SYSTEM_ROWS(%s*1000)
    #   WHERE "Entity Type Code" = 1 AND"""
    #   to_filter.append(number)
    #
    result = Domains.provider(in_state=state, in_city=city, in_npi=npi, in_entity_type_code=entity_type_code, in_number=number)
    return jsonify(result)

    """
    Test URLs:

    Locally: http://0.0.0.0:5000/ 
    Online: http://3.18.111.161:5000/

    FDA:
    api/v01/provider?entity_type=1
    api/v01/provider?entity_type=1&state=ca
    api/v01/provider?entity_type=2&city=las vegas
    api/v01/provider?npi=1598918971
    api/v01/provider?help_states
    api/v01/provider?state=ca&help_cities
    api/v01/provider?help
   
    """

@bp.route('/api/v01/vital', methods=['GET'])
@login_required
def api_vital():
    query_parameters = request.args

    age = int(query_parameters.get('age'))
    number = query_parameters.get('number')

    if 'help' in request.args:
        try:
            return render_template('synth_phr/vital.html')
        except:
            return render_template(error_path)

    if not age:
        return render_template(error_path)
    random_vital = Domains.vital(in_age=age, in_number=number)
    return random_vital 

    """
    Test URLs:

    api/v01/vital?age=3
    api/v01/vital?help

    """

@bp.route('/api/v01/person', methods=['GET'])
@login_required
def api_person():
    query_parameters = request.args

    min_age = query_parameters.get('min_age')
    max_age = query_parameters.get('max_age')
    female = query_parameters.get('female')
    male = query_parameters.get('male')
    country = query_parameters.get('country')
    number = query_parameters.get('number')

    if not number:
        number = 1

    countries = [(country, number)]

    if 'help' in request.args:
        try:
            return render_template('synth_phr/person.html')
        except:
            return render_template(error_path)

    if min_age:
        if max_age:
            if female:
                if male:
                    result = func_nihpo_subjects_creation(in_min_age=min_age, in_max_age=max_age, in_female=female, in_male=male, in_countries=countries)
                else:
                    male = 100 - int(female)
                    result = func_nihpo_subjects_creation(in_min_age=min_age, in_max_age=max_age, in_female=female, in_male=male, in_countries=countries)
            else:
                result = func_nihpo_subjects_creation(in_min_age=min_age, in_max_age=max_age, in_countries=countries)
        else:
            result = func_nihpo_subjects_creation(in_min_age=min_age, in_countries=countries)
    else:
        result = func_nihpo_subjects_creation(in_countries=countries)
    return jsonify(result)
    #
    """
    Test URLs:
    
    api/v01/person
    api/v01/person?age=33
    api/v01/person?number=3
    api/v01/person?help

    """
#
@bp.route('/select_countries', methods=['GET', 'POST'])
@login_required
def select_countries():
    session['Data_' + current_user.username] = {}
    form = select_countries_form_generator(current_app)
    if form.add.data:
            form.country.append_entry()
    if form.remove.data:
            form.country.pop_entry()
    if form.validate_on_submit():
        if form.submit.data:
            countries = []
            for idx, data in enumerate(form.country.data):
                if (data["country"] and data["number"]):
                    countries.append((data["country"], data["number"]))
            session['Data_' + current_user.username]['countries'] = countries
            return redirect(url_for('synth_phr.create_synthphr'))
    return render_template('synth_phr/select_countries.html', title='Create New SynthPHR', form=form, version=current_app.config['CT_NOTE_VERSION'])


@bp.route('/create_synthphr', methods=['GET', 'POST'])
@login_required
def create_synthphr():

    # Initialize variables
    data_countries = ''
    drugs_filter = None

    # Take countries from session
    try:
        countries = session['Data_' + current_user.username]['countries']
    except:
        flash('Please select correct countries')
        return redirect(url_for('synth_phr.select_countries'))
    
    for item in countries:
        data_countries = data_countries + str(item[0]) + ',' + str(item[1]) + ';'
    data_countries = data_countries[:-1]

    # Initialize form
    form = synthetic_phr_form_generator(current_app)

    # Receive data once user submit it
    if form.validate_on_submit():
        file_name = form.output_file_name.data
        min_age = int(form.min_age.data)
        max_age = int(form.max_age.data)
        female = form.female.data
        male = form.male.data
        drug_regulator = form.drug_regulator.data
        drug_randomization = form.drug_random.data
        if drug_randomization=='ATC-Specific':
            atc_top_lvl = form.drug_1st_level.data
            if atc_top_lvl:
                atc_lvl_2 = form.drug_2nd_level.data
                if atc_lvl_2!='None':
                    drugs_filter = atc_lvl_2
                else:
                    drugs_filter = atc_top_lvl

        output_type = form.output_type.data
        if output_type == 'JSON':
            # response = requests.get(url="http://0.0.0.0:5055/synth_phr/create_subject_json?min_age=5&max_age=10&female=50&male=50&countries=es,1;us,2&name=2")
            return redirect(url_for('synth_phr.create_subject_json', min_age=min_age, max_age=max_age, female=female, male=male,\
                drug_regulator=drug_regulator, countries=data_countries, name=file_name, drugs_filter=drugs_filter))
        elif output_type == 'SQLite3':
            return redirect(url_for('synth_phr.create_subject_sqlite', min_age=min_age, max_age=max_age, female=female, male=male,\
                drug_regulator=drug_regulator, countries=data_countries, name=file_name, drugs_filter=drugs_filter))
    return render_template('synth_phr/create_synthphr.html', title='Create New SynthPHR', form=form, version=current_app.config['CT_NOTE_VERSION'])

@bp.route('/drug_atc_levels', methods=['GET'])
def drug_atc_levels():
    query_parameters = request.args
    array_drug = []

    level_1 = query_parameters.get('level_1')   
    # level_2 = query_parameters.get('level_2')

    # Filter drugs by given paramters
    if level_1:
        drugs = Domains.drugs_atc_second_levels(level_1)

        for drug in drugs:
            dict_drug = {}
            dict_drug['second_level_code'] = drug[0]
            dict_drug['second_level_name'] = drug[1]
            array_drug.append(dict_drug)
    
    return jsonify({'drug_levels': array_drug})

@bp.route('/create_subject_json', methods=['GET', 'POST'])
@login_required
def create_subject_json():
    query_parameters = request.args

    data_countries = []
    country_names = []
    country_names_subjects = []

    min_age = int(query_parameters.get('min_age'))
    max_age = int(query_parameters.get('max_age'))
    female = int(query_parameters.get('female'))
    male = int(query_parameters.get('male'))
    drug_regulator = query_parameters.get('drug_regulator')
    countries = query_parameters.get('countries')
    file_name = query_parameters.get('name')
    drugs_filter = query_parameters.get('drugs_filter')

    folder_name = current_user.folder_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    for item in countries.split(';'):
        item_tupled = tuple(item.split(','))
        data_countries.append(item_tupled)
        country_name = Domains.geography(in_country_code_iso=item_tupled[0])["NIHPO_API"]["Results"][0]['Country_Name']
        country_names.append(country_name)
        country_names_subjects.append([country_name, item_tupled[1]])
        
    options_requested = {'Countries': country_names_subjects, 'Age range': [min_age, max_age],\
        'Gender distribution': [female, male], 'Drug regulator': drug_regulator,\
        'Device regulator': 'FDA', 'Drug level': drugs_filter, 'File name': file_name, 'Output type': 'JSON'}
    
    flash_message_1 = """You requested: countries(%s), age range(%s, %s), gender distribution(Female:%s%%, Male:%s%%),
            drug regulator(%s), drug level(%s), device regulator(FDA), file name(%s), output type(JSON)"""\
    % (countries, min_age, max_age, female, male, drug_regulator, drugs_filter, file_name)

    # Show message
    flash(flash_message_1)

    # Create file
    if current_app.config['PROFILE']:
        func_nihpo_json_file(min_age, max_age, female, male, drug_regulator, drugs_filter, data_countries, folder_name,\
            file_name, first_name, last_name, email, country_names)
    else:
        result = func_nihpo_json_file.apply_async((min_age, max_age, female, male, drug_regulator, drugs_filter, data_countries,\
            folder_name, file_name, first_name, last_name, email, country_names), countdown=1)

        # Add the task to the user tasks:
        try:
            if len(session[current_user.username + '_tasks_phr_id']) >= 5:
                session[current_user.username + '_tasks_phr_id'] = session[current_user.username + '_tasks_phr_id'][-4:]
                session[current_user.username + '_tasks_phr_parameters'] = session[current_user.username + '_tasks_phr_parameters'][-4:]
            session[current_user.username + '_tasks_phr_id'].append(result.id)
            session[current_user.username + '_tasks_phr_parameters'].append(options_requested)
        except:
            session[current_user.username + '_tasks_phr_id'] = [result.id]
            session[current_user.username + '_tasks_phr_parameters'] = [options_requested]
        session[current_user.username + '_tasks_phr_id'] = session[current_user.username + '_tasks_phr_id']
        session[current_user.username + '_tasks_phr_parameters'] = session[current_user.username + '_tasks_phr_parameters']

    if current_app.env == 'development':
        files = current_user.files.all()
        for file in files:
            if file_name  == file.file_name:
                db.session.delete(file)
    json_file = Files(file_name=file_name, file_type='JSON', file_status='Pending', file_user=current_user, module='PHR')
    db.session.add(json_file)
    db.session.commit()

    return redirect(url_for('main.synthphr'))

@bp.route('/create_subject_sqlite', methods=['GET', 'POST'])
@login_required
def create_subject_sqlite():
    query_parameters = request.args

    data_countries = []
    country_names = []
    country_names_subjects = []

    min_age = int(query_parameters.get('min_age'))
    max_age = int(query_parameters.get('max_age'))
    female = int(query_parameters.get('female'))
    male = int(query_parameters.get('male'))
    drug_regulator = query_parameters.get('drug_regulator')
    countries = query_parameters.get('countries')
    file_name = query_parameters.get('name')
    drugs_filter = query_parameters.get('drugs_filter')

    folder_name = current_user.folder_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    for item in countries.split(';'):
        item_tupled = tuple(item.split(','))
        data_countries.append(item_tupled)
        country_name = Domains.geography(in_country_code_iso=item_tupled[0])["NIHPO_API"]["Results"][0]['Country_Name']
        country_names.append(country_name)
        country_names_subjects.append([country_name, item_tupled[1]])

    options_requested = {'Countries': country_names_subjects, 'Age range': [min_age, max_age], 'Gender distribution': [female, male],\
        'Drug regulator': drug_regulator, 'Device regulator': 'FDA', 'File name': file_name, 'Output type': 'SQLITE3'}
    
    flash_message_1 = """You requested: countries(%s), age range(%s, %s), gender distribution(Female:%s%%, Male:%s%%),
            drug regulator(%s), drug level(%s), device regulator(FDA), file name(%s), output type(SQLITE3)"""\
    % (countries, min_age, max_age, female, male, drug_regulator, drugs_filter, file_name)
    flash(flash_message_1)

    if current_app.config['PROFILE']:
        result = func_nihpo_generate_SQLite3_file(min_age, max_age, female, male, drug_regulator, drugs_filter, data_countries,\
            folder_name, file_name, first_name, last_name, email, country_names, in_user_id=current_user.id)
    else:
        result = func_nihpo_generate_SQLite3_file.apply_async((min_age, max_age, female, male, drug_regulator, drugs_filter,\
            data_countries, folder_name, file_name, first_name, last_name, email, country_names, current_user.id), countdown=1)

        # Add the task to the user tasks
        try:
            if len(session[current_user.username + '_tasks_phr_id']) >= 5:
                session[current_user.username + '_tasks_phr_id'] = session[current_user.username + '_tasks_phr_id'][-4:]
                session[current_user.username + '_tasks_phr_parameters'] = session[current_user.username + '_tasks_phr_parameters'][-4:]
            session[current_user.username + '_tasks_phr_id'].append(result.id)
            session[current_user.username + '_tasks_phr_parameters'].append(options_requested)
        except:
            session[current_user.username + '_tasks_phr_id'] = [result.id]
            session[current_user.username + '_tasks_phr_parameters'] = [options_requested]
        session[current_user.username + '_tasks_phr_id'] = session[current_user.username + '_tasks_phr_id']
        session[current_user.username + '_tasks_phr_parameters'] = session[current_user.username + '_tasks_phr_parameters']
    
    # Add file to database
    if current_app.env == 'development':
        files = Files.query.filter_by(user_id=current_user.id, module = "PHR").all()
        for file in files:
            if file_name  == file.file_name:
                db.session.delete(file)
    if current_app.config['PROFILE']:
        sqlite_file = Files(file_name=file_name, file_type='SQLITE3', file_status='Created', file_user=current_user, module='PHR', drugs_regulator=drug_regulator,
                            drugs_randomization=drugs_filter, devices_regulator='FDA')
    else:
        sqlite_file = Files(file_name=file_name, file_type='SQLITE3', file_status='Pending', file_user=current_user, module='PHR', drugs_regulator=drug_regulator,
                            drugs_randomization=drugs_filter, devices_regulator='FDA')
    db.session.add(sqlite_file)
    db.session.commit()

    return redirect(url_for('main.synthphr'))


@bp.route('/check_tasks', methods=['GET', 'POST'])
def check_tasks():
    try:
        tasks = session[current_user.username + '_tasks_phr_id']
    except:
        tasks = []
    return render_template('bars.html', tasks=tasks, file_type='phr', version=current_app.config['CT_NOTE_VERSION'])