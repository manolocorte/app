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
from flask import (
    render_template,
    redirect,
    url_for,
    session,
    current_app,
    send_file,
    request,
    flash,
    jsonify,
)
from CE_app.synth_trial import bp
from CE_app.synth_trial.trial_design_creation import (
    func_nihpo_generate_trial_design_from_sqlite,
)
from CE_app.synth_trial.forms import (
    synthetic_creates_trial_form_generator,
    SyntheticTrialArmsElementsVisits,
    SyntheticTrialVariablesNotControlled,
    synthetic_trial_output,
)
import json
from flask_login import login_required, current_user
from CE_app import db
from CE_app.models import Files, Logs
import sqlite3
import sqlalchemy
from CE_app.nihpo_functions import required_permissions
import os


@bp.route("/try_permission", methods=["GET", "POST"])
@login_required
@required_permissions("edit_records", "read_record")
def try_permission():
    return redirect(url_for("main.synthphr"))


@bp.route("/trial_summary_parameters", methods=["GET", "POST"])
@login_required
def trial_summary_parameters():
    form = synthetic_creates_trial_form_generator(current_user)
    data = {}
    data_i = {}
    data_v = {}
    session.pop(
        "Data_" + current_user.username + "_" + "controlled_terminology_file", None
    )
    session.pop(
        "Data_" + current_user.username + "_" + "arms_elements_visits_file", None
    )
    if form.validate_on_submit():
        data["PHR File"] = form.phr_files.data
        data["Study ID"] = form.study_id.data
        data["Trial Name"] = form.trial_name.data
        data["Sponsor"] = form.sponsor.data
        data["Start Date"] = str(form.start_date.data)
        data["End Date"] = str(form.end_date.data)
        data["Number Sites Per Country"] = str(form.number_sites_per_country.data)
        data["Planned Number of Subjects"] = form.planned_num_subjects.data
        data["Planned Number of Arms"] = form.planned_number_arms.data
        data["Number of Groups"] = form.num_groups.data
        data["Trial Length"] = form.trial_length.data
        data["Trial Primary Objective"] = form.trial_primary_obj.data
        data["Trial Secondary Objective"] = form.trial_secondary_obj.data
        data["Trial Type"] = form.trial_type.data
        data["Study Type"] = form.study_type.data
        data["Therapeutic Area"] = form.ther_area.data
        data["Study Stop Rules"] = form.stop_rules.data
        data["Trial Blinding Schema"] = form.trial_blinding_schema.data
        data["Control Type"] = form.control_type.data
        data["Trial Phase Classification"] = form.trial_phase_classification.data
        data["Primary Outcome Measure"] = form.primary_outcome_measure.data
        data["Adaptive Design"] = form.adaptative_design.data
        data["Data Cutoff Date"] = str(form.data_cutoff_date.data)
        data["Data Cutoff Description"] = form.data_cutoff_desc.data
        data["Registry Identifier"] = form.registry_id.data
        data_i["Added on to Existing Treatments"] = form.test_product_added.data
        data_i["Randomized"] = form.randomized.data
        data_i["Extension Trial Indicator"] = form.ex_trial_id.data
        data_i["Pediatric Study Indicator"] = form.ped_study_id.data
        data_i["Pediatric Investigation Plan Indicator"] = form.ped_inv_plan_id.data
        data_i["Pediatric Postmarket Study Indicator"] = form.ped_postmark_study_id.data
        data_i["Rare Disease Indicator"] = form.rare_disease_id.data
        data_i["Healthy Subject Indicator"] = form.healthy_subj_id.data
        data_v["SDTM IG"] = form.sdtm_ig_version.data
        data_v["SDTM"] = form.sdtm_version.data
        session[
            "Data_" + current_user.username + "_" + "trial_summary_parameters"
        ] = data
        session["Data_" + current_user.username + "_" + "indicators"] = data_i
        session["Data_" + current_user.username + "_" + "versions"] = data_v
        return redirect(url_for("synth_trial.controlled_terminology"))
    return render_template(
        "synth_trial/trial_summary_parameters.html",
        title="Create New SynthTrial",
        form=form,
        version=current_app.config["CT_NOTE_VERSION"],
    )


@bp.route("/controlled_terminology", methods=["GET", "POST"])
@login_required
def controlled_terminology():

    # Initialize variables
    data = {}
    form = SyntheticTrialVariablesNotControlled()

    # Check if the file inserted in the dropzone is correct
    if request.method == "POST" and not form.validate_on_submit():
        file = request.files.get("file")
        try:
            data = json.loads(file.getvalue().decode())
            session[
                "Data_" + current_user.username + "_" + "controlled_terminology_file"
            ] = data
        except:
            flash(
                "Use a correct file, you can download a sample file pressing the button at the bottom"
            )
            session.pop(
                "Data_" + current_user.username + "_" + "controlled_terminology", None
            )

    # Handle different buttons
    if form.validate_on_submit():

        # Download SAMPLE CONTROLLED TERMINOLOGY
        if form.download.data:
            return send_file(
                current_app.config["CT_JSON_SAMPLE_CONTROLLED_TERMINOLOGY"],
                as_attachment=True,
            )

        # Use the Sponsor-specific CT defined by default
        if request.form["submit_button"] == "Use default Sponsor-specific CT":
            with open(
                current_app.config["CT_JSON_SAMPLE_CONTROLLED_TERMINOLOGY_DECOMPRESSED"]
            ) as outfile:
                data = json.load(outfile)
                session[
                    "Data_" + current_user.username + "_" + "controlled_terminology"
                ] = data
            return redirect(url_for("synth_trial.arms_definition"))

        # Use CDISC SDTM CT only
        elif request.form["submit_button"] == "Use CDISC SDTM CT only":
            session[
                "Data_" + current_user.username + "_" + "controlled_terminology"
            ] = None
            return redirect(url_for("synth_trial.arms_definition"))

        # Use file inserted in the dropzone
        else:
            try:
                file_data = session[
                    "Data_"
                    + current_user.username
                    + "_"
                    + "controlled_terminology_file"
                ]
                if file_data:
                    session[
                        "Data_" + current_user.username + "_" + "controlled_terminology"
                    ] = file_data
                if not file_data:
                    flash(
                        "Use a correct file, you can download a sample file by pressing the button at the bottom or continue with a default file (press on 'Continue without file')"
                    )
                else:
                    return redirect(url_for("synth_trial.arms_definition"))
            except KeyError:
                flash(
                    "Use a correct file, you can download a sample file by pressing the button at the bottom or continue with a default file (press on 'Continue without file')"
                )
    return render_template(
        "synth_trial/controlled_terminology.html",
        title="Create New SynthTrial",
        form=form,
        version=current_app.config["CT_NOTE_VERSION"],
    )


@bp.route("/arms_definition", methods=["GET", "POST"])
@login_required
def arms_definition():

    # Initialize variables
    form = SyntheticTrialArmsElementsVisits()
    data = {}

    # Check if the file inserted in the dropzone is correct
    if request.method == "POST" and not form.validate_on_submit():
        file = request.files.get("file")
        try:
            data = json.loads(file.getvalue().decode())
            session[
                "Data_" + current_user.username + "_" + "arms_elements_visits_file"
            ] = data
        except:
            flash(
                "Use a correct file, you can download a sample file pressing the button at the bottom"
            )
            session.pop(
                "Data_" + current_user.username + "_" + "arms_elements_visits", None
            )

    # Handle different buttons
    if form.validate_on_submit():

        # Download SAMPLE ARMS ELEMENTS VISITS
        if form.download.data:
            return send_file(
                current_app.config["CT_JSON_SAMPLE_ARMS_ELEMENTS_VISITS"],
                as_attachment=True,
            )

        # Use default file
        elif request.form["submit_button"] == "Use default":
            with open(
                current_app.config["CT_JSON_SAMPLE_ARMS_ELEMENTS_VISITS_DECOMPRESSED"]
            ) as outfile:
                data = json.load(outfile)
                session[
                    "Data_" + current_user.username + "_" + "arms_elements_visits"
                ] = data
            return redirect(url_for("synth_trial.trial_output"))

        # Use file inserted in the dropzone
        elif request.form["submit_button"] == "Continue":
            try:
                file_data = session[
                    "Data_" + current_user.username + "_" + "arms_elements_visits_file"
                ]
                if file_data:
                    session[
                        "Data_" + current_user.username + "_" + "arms_elements_visits"
                    ] = file_data
                if not file_data:
                    flash(
                        "Use a correct file, you can download a sample file by pressing the button at the bottom or continue with a default file (press on 'Continue without file')"
                    )
                else:
                    return redirect(url_for("synth_trial.trial_output"))
            except KeyError:
                flash(
                    "Use a correct file, you can download a sample file by pressing the button at the bottom or continue with a default file (press on 'Continue without file')"
                )
    return render_template(
        "synth_trial/trial_arms.html",
        title="Create New SynthTrial",
        form=form,
        version=current_app.config["CT_NOTE_VERSION"],
    )


@bp.route("/trial_output", methods=["GET", "POST"])
@login_required
def trial_output():
    form = synthetic_trial_output(current_user, current_app)
    if form.validate_on_submit():
        data = {}
        data["Output"] = {}
        data["Demography"] = {}
        data["Trial Summary Parameters"] = session.get(
            "Data_" + current_user.username + "_" + "trial_summary_parameters", None
        )
        data["Indicators"] = session.get(
            "Data_" + current_user.username + "_" + "indicators", None
        )
        data["Standard Versions"] = session.get(
            "Data_" + current_user.username + "_" + "versions", None
        )
        data["Controlled Terminology"] = session.get(
            "Data_" + current_user.username + "_" + "controlled_terminology", None
        )
        data["Arms, Elements & Visits"] = session.get(
            "Data_" + current_user.username + "_" + "arms_elements_visits", None
        )
        data["Output"]["File Name"] = form.output_file_name.data
        data["Output"]["Types"] = []
        if form.sqlite.data:
            data["Output"]["Types"].append("sqlite")
        if form.csv.data:
            data["Output"]["Types"].append("csv")
        if form.sas.data:
            data["Output"]["Types"].append("sas")
        # data['Arms, Elements & Visits'] = session['Data_' + current_user.username + '_' + 'arms_elements_visits']
        first_name = current_user.first_name
        last_name = current_user.last_name
        email = current_user.email

        try:
            con = sqlite3.connect(
                current_app.config["CT_DOWNLOADS_PATH"]
                + data["Trial Summary Parameters"]["PHR File"],
                uri=True,
            )
            cur = con.cursor()
            cur.execute("SELECT COUNT() from Synth_PHR_Demographics;")
            number_subjects = cur.fetchone()[0]
            con.close()
        except:
            con.close()
            try:
                con = sqlite3.connect(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + data["Trial Summary Parameters"]["PHR File"],
                    uri=True,
                )
                cur = con.cursor()
                cur.execute("SELECT COUNT() from Synth_PHR_Demographics;")
                number_subjects = cur.fetchone()[0]
                con.close()
            except:
                flash(
                    "The PHR file you tried to use seems to be wrong, please choose another one"
                )
                return redirect(url_for("synth_trial.trial_summary_parameters"))

        options_requested = {
            "PHR file": data["Trial Summary Parameters"]["PHR File"],
            "Number subjects": number_subjects,
            "Output type": ", ".join(data["Output"]["Types"]),
        }

        flash_message_1 = f"""You requested: PHR file ({options_requested['PHR file']}) with {options_requested['Number subjects']} subjects, output file name ({data['Output']['File Name']}), output file type/s ({options_requested['Output type']})"""
        flash(flash_message_1)

        if current_app.config["PROFILE"]:
            func_nihpo_generate_trial_design_from_sqlite(
                data, first_name, last_name, email, in_user_id=current_user.id
            )
        else:
            result = func_nihpo_generate_trial_design_from_sqlite.delay(
                data, first_name, last_name, email, in_user_id=current_user.id
            )

            # Add the task to the user tasks:
            try:
                if len(session[current_user.username + "_tasks_trial_id"]) >= 5:
                    session[current_user.username + "_tasks_trial_id"] = session[
                        current_user.username + "_tasks_trial_id"
                    ][-4:]
                    session[
                        current_user.username + "_tasks_trial_parameters"
                    ] = session[current_user.username + "_tasks_trial_parameters"][-4:]
                session[current_user.username + "_tasks_trial_id"].append(result.id)
                session[current_user.username + "_tasks_trial_parameters"].append(
                    options_requested
                )
            except:
                session[current_user.username + "_tasks_trial_id"] = [result.id]
                session[current_user.username + "_tasks_trial_parameters"] = [
                    options_requested
                ]
            session[current_user.username + "_tasks_trial_id"] = session[
                current_user.username + "_tasks_trial_id"
            ]
            session[current_user.username + "_tasks_trial_parameters"] = session[
                current_user.username + "_tasks_trial_parameters"
            ]

        if current_app.env == "development":
            files = Files.query.filter_by(user_id=current_user.id, module="TRIAL").all()
            for file in files:
                if data["Output"]["File Name"] == file.file_name:
                    db.session.delete(file)
        if current_app.config["PROFILE"]:
            trial_file = Files(
                file_name=data["Output"]["File Name"],
                file_type="ZIP",
                file_status="Created",
                file_user=current_user,
                module="TRIAL",
            )
        else:
            trial_file = Files(
                file_name=data["Output"]["File Name"],
                file_type="ZIP",
                file_status="Pending",
                file_user=current_user,
                module="TRIAL",
            )
        db.session.add(trial_file)
        db.session.commit()

        return redirect(url_for("main.synthtrial"))
    return render_template(
        "synth_trial/trial_output.html",
        title="Create New SynthTrial",
        form=form,
        version=current_app.config["CT_NOTE_VERSION"],
    )


@bp.route("/check_tasks", methods=["GET", "POST"])
@login_required
def check_tasks():
    try:
        tasks = session[current_user.username + "_tasks_trial_id"]
    except:
        tasks = []
    return render_template(
        "bars.html",
        tasks=tasks,
        file_type="trial",
        version=current_app.config["CT_NOTE_VERSION"],
    )


@bp.route("/dashboards", methods=["GET", "POST"])
@required_permissions(
    "edit_records",
    "read_records",
    "see_dashboards",
    "edit_dashboards",
    "create_global_dashboards",
)
@login_required
def dashboards():

    # Get table name from user selection
    file_name = request.args["file_name"]
    user_id = request.args["user_id"]

    query = "SELECT * FROM Synth_PHR_Demographics;"
    query_sqlite = current_app.config["CT_DOWNLOADS_PATH"] + "%s.sqlite3" % file_name

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    con = sqlite3.connect(query_sqlite)

    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)

    # Get data from table
    list_data = cur.fetchall()

    con.close()

    # Get field names
    list_fields = list(list_data[0].keys())

    con = sqlite3.connect(query_sqlite)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    list_tables = cur.fetchall()

    # Get table names that are not table definitions as a list
    list_tables = [
        x[0]
        for x in list_tables
        if "Definition" not in x[0] and "NIHPO" not in x[0] and "sqlite" not in x[0]
    ]

    con.close()

    session["trial_file_" + current_user.username] = file_name
    return render_template(
        "synth_trial/dashboards.html",
        title="Dashboards",
        list_data=list_data,
        list_fields=list_fields,
        list_tables=list_tables,
        dashboard_url=current_app.config["CT_SUPERSET_HREF"],
        file_name=file_name,
        user_id=user_id,
        user_permissions=current_user.get_permissions(),
    )


@bp.route("/update-db", methods=["POST"])
@login_required
def update_db():

    # Get data
    file_name = session["trial_file_" + current_user.username]
    last_value = request.form["pk"]
    field_name = request.form["name"]
    new_value = request.form["value"]
    table_name = request.form["table_name"]

    query_sqlite = current_app.config["CT_DOWNLOADS_PATH"] + "%s.sqlite3" % file_name

    if "edit_records" not in current_user.get_permissions():
        return jsonify(message="You don't have write permissions"), 500

    # Connect to the current trial file
    engine = sqlalchemy.create_engine("sqlite:///" + query_sqlite)
    conn = engine.connect()

    query = "UPDATE %s SET '%s' = '%s' WHERE id = %s" % (
        table_name,
        field_name,
        new_value,
        last_value,
    )

    # Change data
    conn.execute(query)

    # Close connection
    conn.close()

    # Log change
    log = Logs(
        file_name=file_name, table=table_name, change=query, user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()

    return json.dumps({"status": "OK"})


@bp.route("/get_data", methods=["POST", "GET"])
@login_required
def get_data():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    # Get table name from Ajax request
    table_name = request.get_json()

    # Get file name from session
    file_name = session["trial_file_" + current_user.username]

    # Define query for the table requested
    query = "SELECT * FROM %s;" % table_name
    query_sqlite = current_app.config["CT_DOWNLOADS_PATH"] + "%s.sqlite3" % file_name

    # Connect to the selected trial file
    con = sqlite3.connect(query_sqlite)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)

    # Get data from table
    list_data = cur.fetchall()

    # Get field names
    if list_data:
        list_fields = list(list_data[0].keys())
    else:
        list_fields = [description[0] for description in cur.description]

    # Close connection
    con.close()

    return jsonify(list_fields, list_data)


@bp.route("/create_submission", methods=["POST", "GET"])
@required_permissions("create_submissions")
@login_required
def create_submission():

    # Get file name from Ajax request
    data_sent = request.get_json()
    old_file_name = data_sent["trial_file"]
    user_id = data_sent["user_id"]

    # Initialize variables
    number_file = 1
    downloads_path = current_app.config["CT_DOWNLOADS_PATH"]
    sub_file_name = old_file_name + "-submission_0"

    # Create new Submission file inside DB
    file = Files.query.filter_by(file_name=sub_file_name).first()
    while file:
        sub_file_name = sub_file_name[:-1] + str(number_file)
        file = Files.query.filter_by(file_name=sub_file_name).first()
        number_file += 1

    try:
        trial_file = Files(
            file_name=sub_file_name,
            file_type="SUB",
            file_status="Pending",
            user_id=user_id,
            module="SUBMISSION",
        )
        db.session.add(trial_file)
        db.session.commit()

        os.system(
            f"cp {downloads_path}{old_file_name}.sqlite3 {downloads_path}{sub_file_name}.sqlite3"
        )

        # Insert Superset medatadata inside the new Submission file
        con_superset = sqlite3.connect(current_app.config["CT_SUPERSET_DB_PATH"])
        cur_superset = con_superset.cursor()
        cur_superset.execute(
            "ATTACH DATABASE '%s%s.sqlite3' AS new_db;"
            % (current_app.config["CT_DOWNLOADS_PATH"], sub_file_name)
        )

        cur_superset.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';"
        )
        list_tables_superset = cur_superset.fetchall()
        for table in list_tables_superset:
            cur_superset.execute(
                "CREATE TABLE new_db.%s as select * from %s;" % (table[0], table[0])
            )

        # Update file status to Created
        file = Files.query.filter_by(file_name=sub_file_name).first()
        if file:
            file.file_status = "Created"
            db.session.commit()
    except Exception as e:
        message = "Error creating submission:", e
        if current_app.config["CT_LOGS"]:
            current_app.logger.info(message)
        else:
            print(message)

        # Rollback db
        db.session.delete(trial_file)
        db.session.commit()

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}
