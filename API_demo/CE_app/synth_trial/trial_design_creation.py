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
from flask import current_app
from CE_app.synth_trial.constants import Constants
from CE_app.synth_trial.functions import (
    func_nihpo_create_trial_random_domain_row,
    func_nihpo_create_trial_design_domain_row,
    func_nihpo_create_TS_domain,
)
from CE_app.nihpo_functions import *
from CE_app.synth_phr.functions import Domains
from CE_app import celery, db
from CE_app.models import Files
import sqlite3, datetime, os, random, time
import pandas as pd
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from io import BytesIO
from time import perf_counter as time_1
from sqlite3 import OperationalError
import psycopg2
import psycopg2.extras
import sqlalchemy
from CE_app.synth_phr.synth_phr_func import func_nihpo_random_date_birth

DEBUG = []  # 'times', 'times_report'

csv_files = "csv_files/"
sas_files = "sas_files/"


@celery.task(bind=True)
def func_nihpo_generate_trial_design_from_sqlite(
    self,
    in_data,
    in_first_name,
    in_last_name,
    in_email,
    in_user_id=None,
):
    """
    Generates all the trial domains and a ZIP file where the asked files by the user are put in.

    :param in_data: All data passed by the user
    :type in_data: Dictionary
    :returns: ZIP file with all the data files
    :rtype: ZIP file
    """

    if "times" in DEBUG:
        time_total_I = time_1()
    if "times_report" in DEBUG:
        times_to_report = {}

    # Initialize variables
    times = []
    date_format = "%Y-%m-%d"
    CT_SQLITE = 0
    CT_CSV = 0
    CT_SAS = 0
    sites = {}
    in_data["Countries"] = {}
    in_data["Real World Data"] = {}

    # try:
    time_get_data_I = time_1()

    # Take data from imputs
    trial_summary_parameters = in_data["Trial Summary Parameters"]
    controlled_terminology = in_data["Controlled Terminology"]
    arms_elements_visits = in_data["Arms, Elements & Visits"]
    number_sites_per_country = int(trial_summary_parameters["Number Sites Per Country"])

    # Parse dates
    trial_summary_parameters["Start Date"] = datetime.datetime.strptime(
        str(trial_summary_parameters["Start Date"]), date_format
    ).date()
    trial_summary_parameters["End Date"] = datetime.datetime.strptime(
        str(trial_summary_parameters["End Date"]), date_format
    ).date()
    trial_summary_parameters["Data Cutoff Date"] = datetime.datetime.strptime(
        str(trial_summary_parameters["Data Cutoff Date"]), date_format
    ).date()

    # Check chosen outputs
    if "sqlite" in in_data["Output"]["Types"]:
        CT_SQLITE = 1
    if "csv" in in_data["Output"]["Types"]:
        CT_CSV = 1
    if "sas" in in_data["Output"]["Types"]:
        CT_SAS = 1
        percentage_subjects_parameter_time = 41
    elif CT_CSV == 1:
        percentage_subjects_parameter_time = 98
    else:
        percentage_subjects_parameter_time = 99

    if "times" in DEBUG:
        time_get_data = time_1() - time_get_data_I
        print("Get data time:", time_get_data)
    if "times_report" in DEBUG:
        times_to_report["Get data time"] = time_get_data

    time_get_CDISC_I = time_1()
    # Connect to CDISC_SDTM DB
    cdisc_sdtm_conn = psycopg2.connect(
        database=current_app.config["CT_DATABASE"],
        user=current_app.config["CT_DATABASE_USER"],
        password=current_app.config["CT_DATABASE_PASSWORD"],
        host=current_app.config["CT_DATABASE_HOST"],
        port=current_app.config["CT_DATABASE_PORT"],
    )
    cdisc_sdtm_cur = cdisc_sdtm_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Read domain, rules, dates rules and sas formats from CDISC_SDTM DB
    domains_df = pd.read_sql_query(
        "SELECT * FROM cdisc_sdtm_domains ORDER BY domain_name, variable_name ASC;",
        cdisc_sdtm_conn,
    )
    rules_df = pd.read_sql_query(
        "SELECT * FROM cdisc_sdtm_domain_rules ORDER BY domain_code ASC;",
        cdisc_sdtm_conn,
    )
    dates_rules_df = pd.read_sql_query(
        "SELECT * FROM cdisc_sdtm_dates_rules ORDER BY date_before ASC;",
        cdisc_sdtm_conn,
    )
    sas_format_df = pd.read_sql_query(
        "SELECT domain_name, variable_name, variable_label, variable_type FROM cdisc_sdtm_domains ORDER BY domain_name ASC;",
        cdisc_sdtm_conn,
    )

    # Parse dates
    dates_rules_after = dates_rules_df["date_after"].tolist()
    dates_rules_before = dates_rules_df["date_before"].tolist()
    dates_rules_same_date = dates_rules_df["same_date"].tolist()

    if "times_report" in DEBUG:
        times_to_report["Get CDISC time"] = time_1() - time_get_CDISC_I

    time_get_phr_I = time_1()
    # Create a ZIP file in memory
    in_memory = BytesIO()
    zip_Obj = ZipFile(in_memory, mode="w", compression=ZIP_DEFLATED, allowZip64=True)

    # Connect to the chosen SQLite3 file
    nihpo_conn_1 = sqlite3.connect(
        current_app.config["CT_DOWNLOADS_PATH"] + trial_summary_parameters["PHR File"],
        uri=True,
    )
    nihpo_cur_1 = nihpo_conn_1.cursor()

    # Create a SQLite3 file in memory (using SQLAlchemy improves to_sql method to insert multiple rows at once)
    engine = sqlalchemy.create_engine("sqlite://")

    # Copy PHR tables inside trial file
    with engine.connect() as conn:
        for line in nihpo_conn_1.iterdump():
            try:
                conn.execute(line)
            except sqlalchemy.exc.OperationalError:
                pass

    # Get subjects data from the chosen SQLite3 file
    people_df = pd.read_sql_query(
        """SELECT * FROM Synth_PHR_Demographics;""", nihpo_conn_1
    )
    number_subjects = people_df.shape[0]

    # Take important data from the subjects introduced in the trial
    in_data["Demography"]["Number of Subjects"] = number_subjects
    in_data["Demography"]["Maximum Age"] = people_df["Age"].max()
    in_data["Demography"]["Minimum Age"] = people_df["Age"].min()

    for country, people in people_df["Country_Of_Birth"].value_counts().items():
        in_data["Countries"][country] = people

    # Check genders of all the subjects
    if (
        people_df["Gender"].str.contains("F").any()
        and people_df["Gender"].str.contains("M").any()
    ):
        in_data["Demography"]["Gender"] = "BOTH"
    elif people_df["Gender"].str.contains("F").any():
        in_data["Demography"]["Gender"] = "F"
    elif people_df["Gender"].str.contains("M").any():
        in_data["Demography"]["Gender"] = "M"

    # Get drugs & devices information from subjects
    phr_file = Files.query.filter_by(
        user_id=in_user_id, file_name=trial_summary_parameters["PHR File"][:-8]
    ).first()
    in_data["Real World Data"]["Drugs Regulator"] = phr_file.drugs_regulator
    in_data["Real World Data"]["Drugs Randomization"] = (
        phr_file.drugs_randomization if phr_file.drugs_randomization else "Random"
    )
    in_data["Real World Data"]["Devices Regulator"] = phr_file.devices_regulator

    # Modify subjects date of birth to match age with trial start date
    for i, row in enumerate(people_df.itertuples()):
        subject_age = int(row[19])
        trial_start = trial_summary_parameters["Start Date"]
        people_df.at[i, "Date_Of_Birth"] = func_nihpo_random_date_birth(
            trial_start, subject_age, subject_age
        )

    with engine.connect() as conn:
        people_df.to_sql(
            "Synth_PHR_Demographics", conn, if_exists="replace", index=False
        )

    if "times_report" in DEBUG:
        time_get_phr = time_1() - time_get_phr_I
        times_to_report["Get PHR time"] = time_get_phr

    time_create_sites_I = time_1()
    # Get different countries in the chosen SQLite3 file
    nihpo_cur_1.execute(
        "SELECT DISTINCT Country_Of_Residence FROM Synth_PHR_Demographics;"
    )
    countries = [item[0] for item in nihpo_cur_1.fetchall()]

    # Get sites for every country
    for country in countries:
        # Initialize list of sites
        sites[country] = []

        # Get country code
        for tuple_country in current_app.config["CT_COUNTRIES"]:
            if country in tuple_country:
                country_code = tuple_country[0]

        # Insert a location into sites list per site
        for i in range(number_sites_per_country):
            sites[country].append(
                Domains.geography(in_country_code_iso=country_code)["NIHPO_API"][
                    "Results"
                ][0]["Place_Name"]
            )

    if "times_report" in DEBUG:
        times_to_report["Create sites time"] = time_1() - time_create_sites_I

    # Get total number of elements in the task to set progress bar
    task_total = round(100 * number_subjects / percentage_subjects_parameter_time)

    # Put dates rules in a dictionary and trial end_date in a variable
    dates_rules_dict = {
        "Dates_Before": dates_rules_before,
        "Dates_After": dates_rules_after,
        "Same_date": dates_rules_same_date,
    }
    end_date = trial_summary_parameters["End Date"]

    time_subjects_I = time_1()
    if "times_report" in DEBUG:
        times_to_report["Subject dates time"] = 0
        times_to_report["Subject death time"] = 0
        times_to_report["Subject arm time"] = 0
        times_to_report["Subject domains time"] = 0
        times_to_report["Subject domains create table time"] = 0
        times_to_report["Subject domains visit measurements time"] = 0
        times_to_report["Subject domains visit findings time"] = 0
        times_to_report["Subject domains visits time"] = 0
        times_to_report["Subject domains adverse events time"] = 0
        times_to_report["Subject domains deaths time"] = 0
        times_to_report["Subject domains SE time"] = 0
        times_to_report["Subject domains others time"] = 0
        times_to_report["Subject domains load DB time"] = 0
        times_to_report["Domains CSV time"] = 0
        times_to_report["Domains SAS time"] = 0
    # Loop over subjects
    for subject in range(0, number_subjects):

        # Initialize variables
        time_parameters_subject_I = time_1()
        dict_date_fields = {}
        subject_status = "RANDOMIZED"

        if current_app.config["CT_LOGS"]:
            print("Processing subject:", subject + 1)

        # Take single subject
        person = people_df.iloc[[subject]]

        time_subject_dates_I = time_1()
        # Set start and end participation dates
        start_participation = func_nihpo_random_date_between_dates(
            trial_summary_parameters["Start Date"], end_date
        )
        while (end_date - start_participation).days < int(
            trial_summary_parameters["Trial Length"]
        ):
            start_participation = func_nihpo_random_date_between_dates(
                trial_summary_parameters["Start Date"], end_date
            )
        end_participation = start_participation + datetime.timedelta(
            int(trial_summary_parameters["Trial Length"]) - 1
        )

        if "times_report" in DEBUG:
            times_to_report["Subject dates time"] += time_1() - time_subject_dates_I

        # Set start and end dates of exposure to any treatment
        start_date_exposure = start_participation
        end_date_exposure = end_participation

        time_subject_death_I = time_1()
        # Set if the subject dies during the trial
        prob_death = random.random()
        if prob_death <= current_app.config["CT_PROBABILITY_DEAD_DURING_TRIAL"]:
            dead = True
        else:
            dead = False
        last_AE = False

        if "times_report" in DEBUG:
            times_to_report["Subject death time"] += time_1() - time_subject_death_I

        time_subject_arm_I = time_1()
        # Assign an arm to the subject
        name_arm = random.choice(list(arms_elements_visits["ARMS"].keys()))
        arm = arms_elements_visits["ARMS"][name_arm]

        if "times_report" in DEBUG:
            times_to_report["Subject arm time"] += time_1() - time_subject_arm_I

        time_subject_domains_I = time_1()
        # Loop over domains
        for domain in current_app.config["CT_MAIN_DOMAINS"]:

            time_subject_domains_create_table_I = time_1()
            # Create table if doesn not exist yet
            try:
                with engine.connect() as conn:
                    conn.execute(
                        """CREATE TABLE 'CDISC_SDTM_%s'
                        (
                        id INTEGER PRIMARY KEY AUTOINCREMENT);"""
                        % domain
                    )
            except sqlalchemy.exc.OperationalError:
                pass

            if "times_report" in DEBUG:
                times_to_report["Subject domains create table time"] += (
                    time_1() - time_subject_domains_create_table_I
                )

            # Initialize variables
            list_date_fields = []
            df = pd.DataFrame()

            # Use only domains with lenght = 2:
            if len(domain) != 2:
                continue

            # Continue if the domain is created per subject
            if (
                int(rules_df[rules_df["domain_code"] == domain]["per_subject"].iloc[0])
                == 1
            ):

                # Continue if the domain is created per visit
                if (
                    int(
                        rules_df[rules_df["domain_code"] == domain]["per_visit"].iloc[0]
                    )
                    == 1
                ):
                    visit_number = 0

                    # Loop over visits
                    for visit in arm["VISITS"]:
                        visit_number += 1

                        # Continue if the visit is created per visit measurement
                        if (
                            int(
                                rules_df[rules_df["domain_code"] == domain][
                                    "per_visit_measurement"
                                ].iloc[0]
                            )
                            == 1
                        ):
                            time_subject_domains_visit_measurements_I = time_1()
                            # Loop over visit measurements
                            for visit_measurement in range(
                                1,
                                current_app.config["CT_NUMBER_VISIT_MEASUREMENTS"] + 1,
                            ):
                                seq_number = (
                                    visit_measurement
                                    + (visit_number - 1)
                                    * current_app.config["CT_NUMBER_VISIT_MEASUREMENTS"]
                                )
                                (
                                    df,
                                    list_date_fields,
                                ) = func_nihpo_create_trial_random_domain_row(
                                    cdisc_sdtm_cur,
                                    rules_df,
                                    domains_df,
                                    domain,
                                    df,
                                    dates_rules_dict,
                                    seq_number,
                                    person,
                                    trial_summary_parameters["Study ID"],
                                    start_participation,
                                    end_participation,
                                    start_date_exposure,
                                    end_date_exposure,
                                    end_date,
                                    dead,
                                    controlled_terminology,
                                    arms_elements_visits,
                                    arm,
                                    list_date_fields,
                                    in_visit_number=visit_number,
                                    in_visit=visit,
                                )

                            if "times_report" in DEBUG:
                                times_to_report[
                                    "Subject domains visit measurements time"
                                ] += (
                                    time_1() - time_subject_domains_visit_measurements_I
                                )

                        # Continue if the visit is created per finding
                        elif (
                            int(
                                rules_df[rules_df["domain_code"] == domain][
                                    "per_finding"
                                ].iloc[0]
                            )
                            == 1
                        ):
                            time_subject_domains_visit_finding_I = time_1()
                            # Loop over finding measurements
                            for finding in range(
                                1, current_app.config["CT_NUMBER_FINDINGS"] + 1
                            ):
                                seq_number = (
                                    finding
                                    + (visit_number - 1)
                                    * current_app.config["CT_NUMBER_VISIT_MEASUREMENTS"]
                                )
                                (
                                    df,
                                    list_date_fields,
                                ) = func_nihpo_create_trial_random_domain_row(
                                    cdisc_sdtm_cur,
                                    rules_df,
                                    domains_df,
                                    domain,
                                    df,
                                    dates_rules_dict,
                                    seq_number,
                                    person,
                                    trial_summary_parameters["Study ID"],
                                    start_participation,
                                    end_participation,
                                    start_date_exposure,
                                    end_date_exposure,
                                    end_date,
                                    dead,
                                    controlled_terminology,
                                    arms_elements_visits,
                                    arm,
                                    list_date_fields,
                                    in_visit_number=visit_number,
                                    in_visit=visit,
                                )

                            if "times_report" in DEBUG:
                                times_to_report[
                                    "Subject domains visit findings time"
                                ] += (time_1() - time_subject_domains_visit_finding_I)

                        # Continue if the visit is not created per finding or visit measurement
                        else:
                            time_subject_domains_visit_I = time_1()
                            # Create one row per visit
                            seq_number = visit_number
                            (
                                df,
                                list_date_fields,
                            ) = func_nihpo_create_trial_random_domain_row(
                                cdisc_sdtm_cur,
                                rules_df,
                                domains_df,
                                domain,
                                df,
                                dates_rules_dict,
                                seq_number,
                                person,
                                trial_summary_parameters["Study ID"],
                                start_participation,
                                end_participation,
                                start_date_exposure,
                                end_date_exposure,
                                end_date,
                                dead,
                                controlled_terminology,
                                arms_elements_visits,
                                arm,
                                list_date_fields,
                                in_visit_number=visit_number,
                                in_visit=visit,
                            )

                            if "times_report" in DEBUG:
                                times_to_report["Subject domains visits time"] += (
                                    time_1() - time_subject_domains_visit_I
                                )

                # Continue if the domain is created per adverse event
                elif (
                    int(
                        rules_df[rules_df["domain_code"] == domain][
                            "per_adverse_event"
                        ].iloc[0]
                    )
                    == 1
                ):
                    time_subject_domains_adverse_event_I = time_1()
                    # Loop over adverse events
                    for adverse_event in range(
                        1, current_app.config["CT_NUMBER_AES"] + 1
                    ):
                        seq_number = adverse_event
                        (
                            df,
                            last_AE,
                            list_date_fields,
                        ) = func_nihpo_create_trial_random_domain_row(
                            cdisc_sdtm_cur,
                            rules_df,
                            domains_df,
                            domain,
                            df,
                            dates_rules_dict,
                            seq_number,
                            person,
                            trial_summary_parameters["Study ID"],
                            start_participation,
                            end_participation,
                            start_date_exposure,
                            end_date_exposure,
                            end_date,
                            dead,
                            controlled_terminology,
                            arms_elements_visits,
                            arm,
                            list_date_fields,
                            in_last_AE=last_AE,
                        )

                        if last_AE and domain == "AE":
                            break

                    if "times_report" in DEBUG:
                        times_to_report["Subject domains adverse events time"] += (
                            time_1() - time_subject_domains_adverse_event_I
                        )

                    # Create a new adverse event of there is no related with a death and subject is dead
                    if dead and not last_AE:
                        time_subject_domains_death_I = time_1()
                        seq_number = adverse_event + 1
                        (
                            df,
                            last_AE,
                            list_date_fields,
                        ) = func_nihpo_create_trial_random_domain_row(
                            cdisc_sdtm_cur,
                            rules_df,
                            domains_df,
                            domain,
                            df,
                            dates_rules_dict,
                            seq_number,
                            person,
                            trial_summary_parameters["Study ID"],
                            start_participation,
                            end_participation,
                            start_date_exposure,
                            end_date_exposure,
                            end_date,
                            dead,
                            controlled_terminology,
                            arms_elements_visits,
                            arm,
                            list_date_fields,
                            in_last_AE="Forced",
                        )

                        if "times_report" in DEBUG:
                            times_to_report["Subject domains deaths time"] += (
                                time_1() - time_subject_domains_death_I
                            )

                # Continue if the domain is SE
                elif domain == "SE":
                    time_subject_domains_SE_I = time_1()
                    elements = arm["ELEMENTS"]
                    seq_number = 1
                    for element in elements:
                        (
                            df,
                            list_date_fields,
                        ) = func_nihpo_create_trial_random_domain_row(
                            cdisc_sdtm_cur,
                            rules_df,
                            domains_df,
                            domain,
                            df,
                            dates_rules_dict,
                            seq_number,
                            person,
                            trial_summary_parameters["Study ID"],
                            start_participation,
                            end_participation,
                            start_date_exposure,
                            end_date_exposure,
                            end_date,
                            dead,
                            controlled_terminology,
                            arms_elements_visits,
                            arm,
                            list_date_fields,
                        )
                        seq_number = seq_number + 1

                    if "times_report" in DEBUG:
                        times_to_report["Subject domains SE time"] += (
                            time_1() - time_subject_domains_SE_I
                        )

                # Continue if no previous conditions have been met
                else:
                    time_subject_domains_other_I = time_1()
                    # Do not create the death domain if subject did not die during the trial
                    if domain == "DD" and not dead:
                        continue

                    seq_number = 1
                    (df, list_date_fields,) = func_nihpo_create_trial_random_domain_row(
                        cdisc_sdtm_cur,
                        rules_df,
                        domains_df,
                        domain,
                        df,
                        dates_rules_dict,
                        seq_number,
                        person,
                        trial_summary_parameters["Study ID"],
                        start_participation,
                        end_participation,
                        start_date_exposure,
                        end_date_exposure,
                        end_date,
                        dead,
                        controlled_terminology,
                        arms_elements_visits,
                        arm,
                        list_date_fields,
                        in_sites=sites,
                    )

                    if "times_report" in DEBUG:
                        times_to_report["Subject domains others time"] += (
                            time_1() - time_subject_domains_other_I
                        )

            time_subject_domains_load_db_I = time_1()
            df = df.applymap(str)

            # Load df into the DB
            try:
                with engine.connect() as conn:
                    df.to_sql(
                        "CDISC_SDTM_" + domain,
                        conn,
                        if_exists="append",
                        index=False,
                        method="multi",
                    )
            except sqlalchemy.exc.OperationalError:
                for field in df.columns:
                    try:
                        with engine.connect() as conn:
                            conn.execute(
                                """ALTER TABLE 'CDISC_SDTM_%s'
                                ADD %s VARCHAR;"""
                                % (domain, field)
                            )
                    except OperationalError:
                        pass
                with engine.connect() as conn:
                    df.to_sql(
                        "CDISC_SDTM_" + domain,
                        conn,
                        if_exists="append",
                        index=False,
                        method="multi",
                    )

            dict_date_fields[domain] = list_date_fields

            if "times_report" in DEBUG:
                times_to_report["Subject domains load DB time"] += (
                    time_1() - time_subject_domains_load_db_I
                )

        if "times_report" in DEBUG:
            times_to_report["Subject domains time"] += time_1() - time_subject_domains_I

        # Check times
        time_parameters_subject_F = time_1()
        time_parameters_subject = time_parameters_subject_F - time_parameters_subject_I
        times.append(time_parameters_subject)
        average_time_per_subject = sum(times) / len(times)
        estimated_time_subjects = average_time_per_subject * number_subjects
        estimated_time_in_seconds = (
            estimated_time_subjects * 100 / percentage_subjects_parameter_time
            - average_time_per_subject * subject
        )

        # Estimate total time
        if estimated_time_in_seconds > 600:
            estimated_time = (
                time.strftime("%M", time.gmtime(estimated_time_in_seconds)) + " (min)"
            )
        elif estimated_time_in_seconds <= 600:
            estimated_time = (
                time.strftime("%M:%S", time.gmtime(estimated_time_in_seconds))
                + " (min, s)"
            )
        else:
            estimated_time = (
                time.strftime("%H:%M", time.gmtime(estimated_time_in_seconds))
                + " (h, min)"
            )

        if not current_app.config["PROFILE"]:
            # Update progress bar when not testing
            if current_app.env != "testing":
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": subject,
                        "total": task_total,
                        "status": "Creating "
                        + '"'
                        + in_data["Output"]["File Name"]
                        + '" '
                        + "file in "
                        + str(estimated_time),
                    },
                )

    if "times_report" in DEBUG:
        times_to_report["Subjects time"] = time_1() - time_subjects_I

    time_domains_I = time_1()
    # Loop over main domains
    for number_domain, domain in enumerate(current_app.config["CT_MAIN_DOMAINS"]):

        with engine.connect() as conn:
            df = pd.read_sql_query("SELECT * FROM CDISC_SDTM_%s;" % (domain), conn)

            # Delete empty columns if domain different of DM
            if domain != "DM" and not df.empty:
                df.replace("", float("NaN"), inplace=True)
                df.dropna(how="all", axis=1, inplace=True)
                df.replace(float("NAN"), "", inplace=True)

            df.to_sql("CDISC_SDTM_" + domain, conn, if_exists="replace", index=False)

        # Create columns required in DM domain
        # (To do): Select correctly when ARMNRS must be populated (when ARM/ARMCD are empty)
        if domain == "DM":
            for field in ["ARMNRS", "DTHDTC", "DTHFL"]:
                if not field in df.columns:
                    df[field] = ""

        # ID field is not included in SDTM format
        del df["id"]

        # Create CSV file and export them into the zip file
        try:
            if CT_CSV == 1:
                time_main_domains_csv_I = time_1()
                df.to_csv(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + csv_files
                    + domain
                    + ".csv",
                    index=False,
                    header=True,
                    sep=Constants.CT_CSV_SEPARATOR,
                )
                zip_Obj.write(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + csv_files
                    + domain
                    + ".csv",
                    arcname="csv_files/" + domain + ".csv",
                )

                if "times_report" in DEBUG:
                    times_to_report["Domains CSV time"] += (
                        time_1() - time_main_domains_csv_I
                    )
        except:
            pass

        # Create SAS files and export them into the zip file
        try:
            if CT_SAS == 1:
                time_main_domains_sas_I = time_1()
                func_nihpo_convert_to_sas(
                    in_df=df,
                    in_name=domain,
                    in_url=current_app.config["CT_DOWNLOADS_PATH"] + sas_files + domain,
                    in_sas_format_df=sas_format_df,
                )
                zip_Obj.write(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + sas_files
                    + domain
                    + ".xpt",
                    arcname="sas_files/" + domain + ".xpt",
                )

                if "times_report" in DEBUG:
                    times_to_report["Domains SAS time"] += (
                        time_1() - time_main_domains_sas_I
                    )
        except:
            pass
        # except:
        #     pass
        # df = pd.DataFrame()
        # Create domain DD if there are not dead subjects:
        # if domain == 'DD' and df.empty:
        #     df = func_nihpo_create_trial_random_domain_row(cdisc_sdtm_cur, rules_df, domains_df,
        #             'DD', df, dates_rules_dict, 0, person, in_data['Trial Summary Paramters']['Study ID'], start_participation,
        #             end_participation, start_date_exposure, end_date_exposure, end_date,
        #             dead)
        #     df = df.drop([0])
        #     df = df.applymap(str)
        #     with engine.connect() as conn:
        #         df.to_sql('CDISC_SDTM_' + domain, conn, if_exists = 'replace',  index = False)
        # Create CSV files and export them into the zip file:

        # Estimate time
        number_total_domains = len(current_app.config["CT_MAIN_DOMAINS"]) + len(
            Constants.CT_DOMAINS_TRIAL_DESIGN
        )
        estimated_time_in_seconds = (
            (estimated_time_subjects * 100 / percentage_subjects_parameter_time)
            - average_time_per_subject * number_subjects
        ) * (1 - (number_domain + 1) / number_total_domains)
        if estimated_time_in_seconds > 600:
            estimated_time = (
                time.strftime("%M", time.gmtime(estimated_time_in_seconds)) + " (min)"
            )
        elif estimated_time_in_seconds <= 600:
            estimated_time = (
                time.strftime("%M:%S", time.gmtime(estimated_time_in_seconds))
                + " (min, s)"
            )
        else:
            estimated_time = (
                time.strftime("%H:%M", time.gmtime(estimated_time_in_seconds))
                + " (h, min)"
            )

        percentage_per_domain = (
            task_total
            * (100 - percentage_subjects_parameter_time)
            / (100 * number_total_domains)
        )

        if not current_app.config["PROFILE"]:
            # Update progress bar when not testing
            if current_app.env != "testing":
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": number_subjects
                        + round(percentage_per_domain * (number_domain + 1)),
                        "total": task_total,
                        "status": "Creating "
                        + '"'
                        + in_data["Output"]["File Name"]
                        + '" '
                        + "file "
                        + str(estimated_time),
                    },
                )

    if "times_report" in DEBUG:
        times_to_report["Domains time"] = time_1() - time_domains_I

    time_indices_I = time_1()
    # Create indices
    for domain in current_app.config["CT_MAIN_DOMAINS"]:
        for field in Constants.CT_FIELDS_INDEX:
            try:
                if field == "SEQ":
                    with engine.connect() as conn:
                        conn.execute(
                            "CREATE INDEX CDISC_SDTM_%s_%s ON CDISC_SDTM_%s (%s);"
                            % (domain, domain + field, domain, domain + field)
                        )
                else:
                    with engine.connect() as conn:
                        conn.execute(
                            "CREATE INDEX CDISC_SDTM_%s_%s ON CDISC_SDTM_%s (%s);"
                            % (domain, field, domain, field)
                        )
            except:
                pass

    with engine.connect() as conn:
        conn.execute(
            "CREATE INDEX Synth_PHR_Demographics_Date_Of_Birth ON Synth_PHR_Demographics (Date_Of_Birth);"
        )
        conn.execute(
            "CREATE INDEX Synth_PHR_Lab_Results_Date_Of_Birth ON Synth_PHR_Lab_Results (Event_date);"
        )
        conn.execute(
            "CREATE INDEX Synth_PHR_Procedures_Date_Of_Birth ON Synth_PHR_Procedures (Event_date);"
        )

    if "times_report" in DEBUG:
        times_to_report["SQL Indices time"] = time_1() - time_indices_I

    # Delete Data Frames
    del df
    del rules_df

    time_trial_domains_I = time_1()
    # Loop over trial design domains:
    for number_trial_domain, domain in enumerate(Constants.CT_DOMAINS_TRIAL_DESIGN):

        # Create table
        with engine.connect() as conn:
            conn.execute(
                """CREATE TABLE 'CDISC_SDTM_%s'
                (
                id INTEGER PRIMARY KEY AUTOINCREMENT);"""
                % domain
            )

        number_trial_domain += 1

        if current_app.config["CT_LOGS"]:
            print("Processing %s domain" % domain)

        df = pd.DataFrame()

        # Loop over each arm of the trial design
        number_arm = 1
        for arm in arms_elements_visits["ARMS"]:
            arm_code = arms_elements_visits["ARMS"][arm]["ARM_CODE"]
            arm_condition = arms_elements_visits["ARMS"][arm]["ARM_CONDITION"]
            elements = arms_elements_visits["ARMS"][arm]["ELEMENTS"]
            rest_counter = 1
            treatment_counter = 1
            if domain == "TA":
                # Loop over each element of the arm
                taetord = 1
                for element in elements:
                    element_code = arms_elements_visits["ELEMENTS"][element][
                        "ELEMENT_CODE"
                    ]
                    transition_condition = arms_elements_visits["ELEMENTS"][element][
                        "TRANSITION_CONDITION"
                    ]
                    start_condition = arms_elements_visits["ELEMENTS"][element][
                        "START_CONDITION"
                    ]
                    finish_condition = arms_elements_visits["ELEMENTS"][element][
                        "FINISH_CONDITION"
                    ]
                    element_duration = arms_elements_visits["ELEMENTS"][element][
                        "DURATION"
                    ]
                    epoch = arms_elements_visits["ELEMENTS"][element]["EPOCH"]
                    df = func_nihpo_create_trial_design_domain_row(
                        cdisc_sdtm_cur,
                        domains_df,
                        domain,
                        df,
                        controlled_terminology,
                    )

                    # Fields in TA domain
                    df.at[len(df) - 1, "ARM"] = arm
                    df.at[len(df) - 1, "ARMCD"] = arm_code
                    df.at[len(df) - 1, "TAETORD"] = taetord
                    df.at[len(df) - 1, "ELEMENT"] = element
                    df.at[len(df) - 1, "ETCD"] = element_code
                    df.at[len(df) - 1, "TATRANS"] = transition_condition
                    df.at[len(df) - 1, "EPOCH"] = epoch
                    df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]
                    treatment_counter = treatment_counter + 1
                    if taetord == 1:
                        df.at[len(df) - 1, "TABRANCH"] = arm_condition
                    taetord = taetord + 1
                    df.at[len(df) - 1, "PURPOSE"] = "TESTING"

            elif domain in Constants.CT_DOMAINS_VISITS:
                number_visit = 1

                # Loop over each visit into the arm
                for visit in arms_elements_visits["ARMS"][arm]["VISITS"]:

                    # Fields in TV domain
                    if domain == "TV":
                        df = func_nihpo_create_trial_design_domain_row(
                            cdisc_sdtm_cur,
                            domains_df,
                            domain,
                            df,
                            controlled_terminology,
                        )
                        df.at[len(df) - 1, "ARM"] = arm
                        df.at[len(df) - 1, "ARMCD"] = arm_code
                        df.at[len(df) - 1, "VISITNUM"] = number_visit
                        df.at[len(df) - 1, "VISIT"] = "Visit_" + str(number_visit)
                        df.at[len(df) - 1, "VISITDY"] = arms_elements_visits["ARMS"][
                            arm
                        ]["VISITS"][visit]["PLANNED_DAY_VISIT"]
                        df.at[len(df) - 1, "TVSTRL"] = arms_elements_visits["ARMS"][
                            arm
                        ]["VISITS"][visit]["START_RULE"]
                        df.at[len(df) - 1, "TVENRL"] = arms_elements_visits["ARMS"][
                            arm
                        ]["VISITS"][visit]["END_RULE"]
                        number_visit += 1
                    df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]
            number_arm = number_arm + 1

        # Fields in TE domain
        if domain == "TE":
            for element in arms_elements_visits["ELEMENTS"]:
                element_code = arms_elements_visits["ELEMENTS"][element]["ELEMENT_CODE"]
                transition_condition = arms_elements_visits["ELEMENTS"][element][
                    "TRANSITION_CONDITION"
                ]
                start_condition = arms_elements_visits["ELEMENTS"][element][
                    "START_CONDITION"
                ]
                finish_condition = arms_elements_visits["ELEMENTS"][element][
                    "FINISH_CONDITION"
                ]
                element_duration = arms_elements_visits["ELEMENTS"][element]["DURATION"]
                epoch = arms_elements_visits["ELEMENTS"][element]["EPOCH"]
                df = func_nihpo_create_trial_design_domain_row(
                    cdisc_sdtm_cur, domains_df, domain, df, controlled_terminology
                )
                # TEDUR or TEENRL: At lest 1 of them
                df.at[len(df) - 1, "ELEMENT"] = element
                df.at[len(df) - 1, "ETCD"] = element_code
                df.at[len(df) - 1, "TESTRL"] = start_condition
                df.at[len(df) - 1, "TEENRL"] = finish_condition
                df.at[len(df) - 1, "TEDUR"] = element_duration
                df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]

        if domain in Constants.CT_DOMAINS_SCHEDULE_FOR_ASSESSMENTS:

            # Fields in TD domain
            if domain == "TD":
                for number_assessment in range(
                    0, current_app.config["CT_NUMBER_PLANNED_ASSESSMENT_SCHEDULE"]
                ):
                    df = func_nihpo_create_trial_design_domain_row(
                        cdisc_sdtm_cur,
                        domains_df,
                        domain,
                        df,
                        controlled_terminology,
                    )
                    df.at[len(df) - 1, "TDORDER"] = number_assessment + 1
                    df.at[len(df) - 1, "TDNUMRPT"] = current_app.config[
                        "CT_MAX_NUMBER_ACTUAL_ASSESSMENTS"
                    ][number_assessment]
                    df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]
                    # (To do): Set correct reference
                    df.at[
                        len(df) - 1, "TDANCVAR"
                    ] = "A reference to the date variable name..."
                    # (To do): Set correct durations
                    df.at[len(df) - 1, "TDMINPAI"] = "P1Y2M10DT2H30M"
                    df.at[len(df) - 1, "TDMAXPAI"] = "P1Y2M10DT2H30M"
                    df.at[len(df) - 1, "TDTGTPAI"] = "P1Y2M10DT2H30M"
                    df.at[len(df) - 1, "TDSTOFF"] = "P1Y2M10DT2H30M"

            # Fields in TM domain
            if domain == "TM":
                for number_disease_milestone in range(
                    0, current_app.config["CT_NUMBER_DISEASE_MILESTONES"]
                ):
                    df = func_nihpo_create_trial_design_domain_row(
                        cdisc_sdtm_cur,
                        domains_df,
                        domain,
                        df,
                        controlled_terminology,
                    )
                    df.at[len(df) - 1, "MIDSTYPE"] = current_app.config[
                        "CT_DISEASE_MILESTONES_TYPE"
                    ][number_disease_milestone]
                    df.at[len(df) - 1, "TMDEF"] = current_app.config[
                        "CT_DISEASE_MILESTONES_DEFINITION"
                    ][number_disease_milestone]
                    df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]

        if domain in Constants.CT_DOMAINS_INCLUSION_EXCLUSION_SUMMARY:

            # Fields in TI domain
            if domain == "TI":
                for number_inclusion_exclusion in range(
                    0, len(current_app.config["CT_INCLUSION_EXCLUSION"])
                ):
                    df = func_nihpo_create_trial_design_domain_row(
                        cdisc_sdtm_cur,
                        domains_df,
                        domain,
                        df,
                        controlled_terminology,
                    )
                    df.at[len(df) - 1, "IECAT"] = current_app.config[
                        "CT_INCLUSION_EXCLUSION"
                    ][number_inclusion_exclusion][0]
                    df.at[len(df) - 1, "IETESTCD"] = current_app.config[
                        "CT_INCLUSION_EXCLUSION"
                    ][number_inclusion_exclusion][1]
                    # df.at[len(df)-1, 'IESCAT'] = 'INCLUSION'
                    df.at[len(df) - 1, "IETEST"] = current_app.config[
                        "CT_INCLUSION_EXCLUSION"
                    ][number_inclusion_exclusion][2]
                    df.at[len(df) - 1, "STUDYID"] = trial_summary_parameters["Study ID"]

            # Fields in TS domain
            # (To do): TSPARMCD and TSPARM are related, maybe fix them to really be related
            # (To do): TSVALCD is the code of the term in TSVAL. That codes are standarized.
            if domain == "TS":
                seq_counter = 1
                df = func_nihpo_create_TS_domain(
                    cdisc_sdtm_cur, df, domains_df, in_data, countries
                )

        # Load df into the DB
        df.replace("", float("NaN"), inplace=True)
        # df.dropna(how='all', axis=1, inplace=True)
        df.replace(float("NAN"), "", inplace=True)
        df = df.applymap(str)

        # Load df into the DB
        with engine.connect() as conn:
            try:
                df.to_sql("CDISC_SDTM_" + domain, conn, if_exists="append", index=False)
            except sqlalchemy.exc.OperationalError:
                for field in df.columns:
                    try:
                        conn.execute(
                            """ALTER TABLE 'CDISC_SDTM_%s'
                            ADD %s VARCHAR;"""
                            % (domain, field)
                        )
                    except OperationalError:
                        pass
                df.to_sql("CDISC_SDTM_" + domain, conn, if_exists="append", index=False)

        # Create sas and csv folders if they don not exist:
        dir_name_csv = current_app.config["CT_DOWNLOADS_PATH"] + csv_files
        dir_name_sas = current_app.config["CT_DOWNLOADS_PATH"] + sas_files
        try:
            test_csv = os.listdir(dir_name_csv)
        except FileNotFoundError:
            os.mkdir(dir_name_csv)
            test_csv = os.listdir(dir_name_csv)
        try:
            test_sas = os.listdir(dir_name_sas)
        except FileNotFoundError:
            os.mkdir(dir_name_sas)
            test_sas = os.listdir(dir_name_sas)

        try:
            if CT_CSV == 1:
                time_design_domains_csv_I = time_1()
                df.to_csv(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + csv_files
                    + domain
                    + ".csv",
                    index=False,
                    header=True,
                    sep=Constants.CT_CSV_SEPARATOR,
                )
                zip_Obj.write(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + csv_files
                    + domain
                    + ".csv",
                    arcname="csv_files/" + domain + ".csv",
                )
                if "times" in DEBUG:
                    time_design_domains_csv = time_1() - time_design_domains_csv_I
                    print("Domains CSV time:", time_design_domains_csv)
                if "times_report" in DEBUG:
                    times_to_report["Domains CSV time"] += time_design_domains_csv
        except:
            pass
        try:
            if CT_SAS == 1:
                time_design_domains_sas_I = time_1()
                func_nihpo_convert_to_sas(
                    in_df=df,
                    in_name=domain,
                    in_url=current_app.config["CT_DOWNLOADS_PATH"] + sas_files + domain,
                    in_sas_format_df=sas_format_df,
                )
                zip_Obj.write(
                    current_app.config["CT_DOWNLOADS_PATH"]
                    + sas_files
                    + domain
                    + ".xpt",
                    arcname="sas_files/" + domain + ".xpt",
                )
                if "times_report" in DEBUG:
                    times_to_report["Domains SAS time"] += (
                        time_1() - time_design_domains_sas_I
                    )
        except:
            pass
        estimated_time_in_seconds = (
            (estimated_time_subjects * 100 / percentage_subjects_parameter_time)
            - average_time_per_subject * number_subjects
        ) * (
            1
            - (len(current_app.config["CT_MAIN_DOMAINS"]) + number_trial_domain)
            / number_total_domains
        )
        if estimated_time_in_seconds > 600:
            estimated_time = (
                time.strftime("%M", time.gmtime(estimated_time_in_seconds)) + " (min)"
            )
        elif estimated_time_in_seconds <= 600:
            estimated_time = (
                time.strftime("%M:%S", time.gmtime(estimated_time_in_seconds))
                + " (min, s)"
            )
        else:
            estimated_time = (
                time.strftime("%H:%M", time.gmtime(estimated_time_in_seconds))
                + " (h, min)"
            )

        if not current_app.config["PROFILE"]:
            # Update progress bar:
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": number_subjects
                    + round(
                        percentage_per_domain
                        * (
                            number_trial_domain
                            + len(current_app.config["CT_MAIN_DOMAINS"])
                        )
                    ),
                    "total": task_total,
                    "status": "Creating "
                    + '"'
                    + in_data["Output"]["File Name"]
                    + '" '
                    + "file "
                    + str(estimated_time),
                },
            )

    if "times_report" in DEBUG:
        times_to_report["Trial domains time"] = time_1() - time_trial_domains_I

    cdisc_sdtm_conn.close()

    time_trial_domains_sqlite3_I = time_1()
    if CT_SQLITE == 1:
        # Include domain definitions into SQLite file
        domains = domains_df["domain_name"].unique()
        for domain in domains:
            if current_app.config["CT_LOGS"]:
                print("Processing %s domain definition" % domain)
            var_sql_drop_table = "DROP TABLE IF EXISTS CDISC_SDTM_Definition_%s;" % (
                domain
            )
            with engine.connect() as conn:
                conn.execute(var_sql_drop_table)
                CT_SQL_TABLE_DOMAINS = """CREATE TABLE CDISC_SDTM_Definition_%s (
                    Variable_Name TEXT,
                    Variable_Label TEXT,
                    Type TEXT,
                    Controlled_Terms TEXT,
                    Role TEXT,
                    CDISC_Notes TEXT,
                    Core TEXT);""" % (
                    domain
                )
                conn.execute(CT_SQL_TABLE_DOMAINS)
                df_new = domains_df[domains_df["domain_name"] == domain]
                sql_row = (
                    "INSERT INTO CDISC_SDTM_Definition_%s (Variable_Name, Variable_Label, Type, Controlled_Terms, Role, CDISC_Notes, Core) VALUES (?, ?, ?, ?, ?, ?, ?);"
                    % (domain)
                )
                for field in df_new.itertuples():
                    data_row = (
                        field[2],
                        field[3],
                        field[4],
                        field[5],
                        field[6],
                        field[7],
                        field[8],
                    )
                    conn.execute(sql_row, data_row)

            # Create indices for date fields
            try:
                for field in dict_date_fields[domain]:
                    try:
                        with engine.connect() as conn:
                            conn.execute(
                                "CREATE INDEX CDISC_SDTM_%s_%s ON CDISC_SDTM_%s (%s);"
                                % (domain, field, domain, field)
                            )
                    except:
                        pass
            except KeyError:
                pass

        # Make a back up of the DB created in the user folder
        backck_up_path = f'{current_app.config["CT_DOWNLOADS_PATH"]}{in_data["Output"]["File Name"]}.sqlite3'

        engine_file = sqlalchemy.create_engine(f"sqlite:////{backck_up_path}")
        raw_connection_memory = engine_file.raw_connection()
        raw_connection_file = engine.raw_connection()
        raw_connection_file.backup(raw_connection_memory.connection)

        zip_Obj.write(
            current_app.config["CT_DOWNLOADS_PATH"]
            + in_data["Output"]["File Name"]
            + ".sqlite3",
            arcname=in_data["Output"]["File Name"] + ".sqlite3",
        )
        os.remove(
            current_app.config["CT_DOWNLOADS_PATH"]
            + in_data["Output"]["File Name"]
            + ".sqlite3"
        )

    if "times_report" in DEBUG:
        times_to_report["Trial domains SQLite3 time"] = (
            time_1() - time_trial_domains_sqlite3_I
        )

    cdisc_sdtm_conn.close()

    # Create Sphinx report of selected parameters
    pdf_file_path = func_nihpo_create_trial_doc(in_data)
    zip_Obj.write(pdf_file_path, arcname="trial_parameters.pdf")
    os.system(
        f"rm -R {current_app.config['CT_DOWNLOADS_PATH']}{in_data['Output']['File Name']}"
    )

    # Insert common files inside the ZIP file
    time_write_zip_I = time_1()
    zip_Obj.write(current_app.config["APP_NAME"] + "/README.txt", arcname="README.txt")
    zip_Obj.write(
        current_app.config["APP_NAME"] + "/LICENSE.txt", arcname="LICENSE.txt"
    )
    zip_Obj.write(current_app.config["APP_NAME"] + "/README.md", arcname="README.md")
    zip_Obj.close()

    # Delete csv and sas files:
    for item in test_csv:
        if item.endswith(".csv"):
            os.remove(os.path.join(dir_name_csv, item))
    for item in test_sas:
        if item.endswith(".xpt"):
            os.remove(os.path.join(dir_name_sas, item))

    # Write zip file locally:
    in_memory.seek(0)
    data_zip = in_memory.read()
    with open(
        current_app.config["CT_DOWNLOADS_PATH"]
        + in_data["Output"]["File Name"]
        + ".zip",
        "wb",
    ) as out:
        out.write(data_zip)

    # Change file status to 'Created'
    if in_user_id != None:
        file = Files.query.filter_by(
            file_name=in_data["Output"]["File Name"], user_id=in_user_id
        ).first()
        if file:
            file.file_status = "Created"
            db.session.commit()

    if "times_report" in DEBUG:
        times_to_report["Write ZIP time"] = time_1() - time_write_zip_I
        total_time = time_1() - time_total_I
        print("Total trial time:", total_time)
        report_trial_time = "Report of trial creation times:"
        for i in times_to_report:
            report_trial_time += f"\n{i}: {round(times_to_report[i], 2)} ({round(times_to_report[i]*100/total_time, 2)}%)"
        print(report_trial_time)

    # except Exception as error:
    #     current_app.logger.info(error)

    #     # Remove file from DB if there is some failure
    #     file = Files.query.filter_by(
    #         user_id=in_user_id, file_name=in_data["Output"]["File Name"]
    #     ).first()
    #     if in_user_id != None:
    #         file = Files.query.filter_by(
    #             file_name=in_data["Output"]["File Name"]
    #         ).first()
    #         if file:
    #             db.session.delete(file)
    #             db.session.commit()

    return {
        "current": 100,
        "total": 100,
        "status": "File "
        + '"'
        + in_data["Output"]["File Name"]
        + '" '
        + "ready to download!!",
        "result": "File created successfully",
    }
