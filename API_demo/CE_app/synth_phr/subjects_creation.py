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
from CE_app.synth_phr.synth_phr_func import (
    func_nihpo_random_date_birth,
    func_nihpo_calculate_age,
)
from CE_app.nihpo_functions import func_nihpo_random_date
from CE_app.synth_phr.functions import Domains
import psycopg2
import psycopg2.extras
from datetime import date
from time import perf_counter as time_1
import time, uuid, copy, random, datetime, math, unicodedata

DEBUG = []  # 'times', 'times_report'


def func_nihpo_subjects_creation(
    in_min_age,
    in_max_age,
    in_female,
    in_male,
    in_drug_regulator,
    in_drugs_filter,
    in_countries,
    in_file_name,
    in_task=None,
):
    """
    Generates all the information for a number of subjects, in a range of ages, with a specific distribution by gender and country, in JSON format.

    :param in_min_age: Minimum age of the subects
    :type in_min_age: Integer
    :param in_max_age: Maximum age of the subects
    :type in_max_age: Integer
    :param in_female: Percentage of women
    :type in_female: Integer (0-100)
    :param in_male: Percentage of men
    :type in_male: Integer (0-100)
    :param in_drug_regulator: Drug regulator (EMA or FDA)
    :type in_drug_regulator: String
    :param in_drugs_filter: Drugs filter level
    :type in_drugs_filter: String
    :param in_countries: Number of subjects per country
    :type in_countries: List of tuples: (Integer, String) Example: ('es, 100)
    :param in_file_name: Name of the output file
    :type in_file_name: String
    :param in_task: Name of the celery task
    :type in_task: String
    :returns: Subjects created in JSON format
    :rtype: JSON dictionary
    """

    # Initialize variables
    number_person = 0
    total_subjects = 0
    times = []
    time_total_I = time_1()
    cur = current_app.config["CT_POSTGRESQL_CUR"]
    result = copy.deepcopy(current_app.config["CT_JSON_FORMAT"])

    # try:
    # Get total number of subjects
    for item in in_countries:
        total_subjects += int(item[1])

    # Iterate over countries
    for data in in_countries:
        country = data[0]
        number = int(data[1])

        # Iterate over each subject of the country
        for person_number in range(1, number + 1):
            # Initialize variables
            list_drugs = []
            list_providers = []
            list_lab_results = []
            list_vitals = []
            list_procedures = []
            list_devices = []
            time_person_creation_I = time_1()
            number_person = number_person + 1
            title = "Person_" + str(number_person)

            # Get random gender
            gender_choose = random.random() * 100
            if gender_choose <= int(in_female):
                gender = "F"
            else:
                gender = "M"

            time_age_I = time_1()
            # Create date of birth and age
            if in_min_age != None and in_max_age != None:
                in_min_age = int(in_min_age)
                in_max_age = int(in_max_age)
                date_birth = func_nihpo_random_date_birth(
                    date.today(), in_min_age, in_max_age
                )
                age = func_nihpo_calculate_age(
                    datetime.datetime.strptime(date_birth, "%Y-%m-%d").date()
                )
            else:
                date_birth = func_nihpo_random_date_birth(date.today(), 15, 80)
                age = func_nihpo_calculate_age(
                    datetime.datetime.strptime(date_birth, "%Y-%m-%d").date()
                )

            if "times" in DEBUG:
                age_time = time_1() - time_age_I
                print("Age time:", age_time)

            # Create locations
            time_locat_I = time_1()

            random_location_1 = Domains.geography(in_country_code_iso=country)[
                "NIHPO_API"
            ]["Results"][0]
            try:
                random_location_1_state_name = (
                    unicodedata.normalize("NFKD", random_location_1["State_Name"])
                    .encode("ASCII", "ignore")
                    .decode()
                )
            except:
                random_location_1_state_name = random_location_1["State_Name"]
                pass
            try:
                random_location_1_place_name = (
                    unicodedata.normalize("NFKD", random_location_1["Place_Name"])
                    .encode("ASCII", "ignore")
                    .decode()
                )
            except:
                random_location_1_place_name = random_location_1["Place_Name"]
                pass
            random_location_2 = Domains.geography(in_country_code_iso=country)[
                "NIHPO_API"
            ]["Results"][0]
            try:
                random_location_2_state_name = (
                    unicodedata.normalize("NFKD", random_location_2["State_Name"])
                    .encode("ASCII", "ignore")
                    .decode()
                )
            except:
                random_location_2_state_name = random_location_2["State_Name"]
                pass
            try:
                random_location_2_place_name = (
                    unicodedata.normalize("NFKD", random_location_2["Place_Name"])
                    .encode("ASCII", "ignore")
                    .decode()
                )
            except:
                random_location_2_place_name = random_location_2["Place_Name"]
                pass
            if "times" in DEBUG:
                locat_time = time_1() - time_locat_I
                print("Locations time:", locat_time)

            time_cond_I = time_1()
            # Create conditions
            random_conditions = Domains.condition(
                in_number=current_app.config["CT_NUMBER_CONDITIONS_PER_PERSON"]
            )
            if "times" in DEBUG:
                cond_time = time_1() - time_cond_I
                print("Conditions time:", cond_time)

            # Create drugs
            time_drug_I = time_1()

            if in_drug_regulator == "FDA":
                list_drugs.append(
                    Domains.drug(
                        in_regulator_code_list="us_fda",
                        in_marketing_status="pre",
                        in_drugs_filter=in_drugs_filter,
                        in_number=current_app.config["CT_NUMBER_DRUGS_PRE_PER_PERSON"],
                    )["NIHPO_API"]["Results"]
                )

                list_drugs.append(
                    Domains.drug(
                        in_regulator_code_list="us_fda",
                        in_marketing_status="otc",
                        in_drugs_filter=in_drugs_filter,
                        in_number=current_app.config["CT_NUMBER_DRUGS_OTC_PER_PERSON"],
                    )["NIHPO_API"]["Results"]
                )

                for i in range(
                    0, current_app.config["CT_NUMBER_DRUGS_OTHER_PER_PERSON"]
                ):
                    status = random.choice(
                        current_app.config["CT_RANDOMIZE_OTHER_DRUG"]
                    )
                    list_drugs.append(
                        Domains.drug(
                            in_regulator_code_list="us_fda",
                            in_marketing_status=status,
                            in_drugs_filter=in_drugs_filter,
                        )["NIHPO_API"]["Results"]
                    )

            elif in_drug_regulator == "EMA":
                list_drugs.append(
                    Domains.drug(
                        in_regulator_code_list="eu_ema",
                        in_drugs_filter=in_drugs_filter,
                        in_number=current_app.config["CT_NUMBER_DRUGS_EMA_PER_PERSON"],
                    )["NIHPO_API"]["Results"]
                )
            elif in_drug_regulator == "AEMPS":
                list_drugs.append(
                    Domains.drug(
                        in_regulator_code_list="spain",
                        in_drugs_filter=in_drugs_filter,
                        in_number=current_app.config["CT_NUMBER_DRUGS_EMA_PER_PERSON"],
                    )["NIHPO_API"]["Results"]
                )
            if "times" in DEBUG:
                drug_time = time_1() - time_drug_I
                print("Drugs time:", drug_time)

            # Create providers (only for US subjects)
            time_prov_I = time_1()
            if country == "us":
                for i in range(0, current_app.config["CT_NUMBER_PROVIDERS_PER_PERSON"]):
                    status = str(
                        random.choice(current_app.config["CT_RANDOMIZE_PROVIDER"])
                    )
                    state_code = random_location_2["State_Code"]
                    list_providers.append(
                        Domains.provider(
                            in_state=state_code, in_entity_type_code=status
                        )["NIHPO_API"]["Results"]
                    )
            if "times" in DEBUG:
                prov_time = time_1() - time_prov_I
                print("Providers time:", prov_time)

            time_lab_res_I = time_1()
            # Create lab results
            list_lab_results.append(
                Domains.lab_result(
                    in_atc_code_filter=in_drugs_filter,
                    in_number=current_app.config["CT_NUMBER_LAB_RESULTS_PER_PERSON"],
                )["NIHPO_API"]["Results"]
            )
            if "times" in DEBUG:
                lab_time = time_1() - time_lab_res_I
                print("Lab results time:", lab_time)

            time_proc_I = time_1()
            # Create procedures
            list_procedures.append(
                Domains.procedure(
                    in_number=current_app.config["CT_NUMBER_PROCEDURES_PER_PERSON"]
                )["NIHPO_API"]["Results"]
            )

            if "times" in DEBUG:
                proc_time = time_1() - time_proc_I
                print("Procedures time:", proc_time)

            time_dev_I = time_1()
            # Create devices
            list_devices.append(
                Domains.device(
                    in_number=current_app.config["CT_NUMBER_DEVICES_PER_PERSON"]
                )["NIHPO_API"]["Results"]
            )
            if "times" in DEBUG:
                dev_time = time_1() - time_dev_I
                print("Devices time:", dev_time)

            # Create vitals
            time_vit_I = time_1()
            for i in range(0, current_app.config["CT_NUMBER_VITALS_PRE_PER_PERSON"]):
                random_date = func_nihpo_random_date_birth(date.today(), 0, age)
                year_vital = age - func_nihpo_calculate_age(
                    datetime.datetime.strptime(random_date, "%Y-%m-%d").date()
                )
                random_vital = Domains.vital(in_age=year_vital)["NIHPO_API"]["Results"]
                list_vitals.append(random_vital)
                list_vitals[i][0]["Event_Date[YYYY-MM-DD]"] = random_date
            if "times" in DEBUG:
                vit_time = time_1() - time_vit_I
                print("Vitals time:", vit_time)

            time_first_names_I = time_1()
            # Create subjects name
            first_name = Domains.first_name(in_gender=gender)["NIHPO_API"]["Results"][
                0
            ]["first_name"]
            middle_name = Domains.middle_name(in_gender=gender)["NIHPO_API"]["Results"][
                0
            ]["middle_name"]

            if "times" in DEBUG:
                names_time = time_1() - time_first_names_I
                print("Names time:", names_time)

            time_last_name_I = time_1()
            last_name = Domains.last_name()["NIHPO_API"]["Results"][0]["last_name"]

            if "times" in DEBUG:
                last_time = time_1() - time_last_name_I
                print("Last name time:", last_time)

            time_person_inj_I = time_1()
            # Create JSON variable with all the data:
            person = {
                title: {
                    "Demographics": {
                        "Patient_ID": str(uuid.uuid4()),
                        "First_Name": first_name,
                        "Middle_Name": middle_name,
                        "Last_Name": last_name,
                        "Gender": gender,
                        "Race": random.choice(current_app.config["CT_RACES"]),
                        "Date_Of_Birth[YYYY-MM-DD]": date_birth,
                        "Country_Of_Birth": random_location_1["Country_Name"],
                        "State_Province_Of_Birth": random_location_1_state_name,
                        "Location_Of_Birth": random_location_1_place_name,
                        "Location_Of_Birth_Lat": random_location_1["Latitude"],
                        "Location_Of_Birth_Long": random_location_1["Longitude"],
                        "Country_Of_Residence": random_location_2["Country_Name"],
                        "State_Province_Of_Residence": random_location_2_state_name,
                        "Location_Of_Residence": random_location_2_place_name,
                        "Location_Of_Residence_Lat": random_location_2["Latitude"],
                        "Location_Of_Residence_Long": random_location_2["Longitude"],
                        "Age": age,
                        "Age_Units": "Years",
                        "Civil_Status": random.choice(
                            current_app.config["CT_CIVIL_STATUS"]
                        ),
                    },
                    "Conditions": {
                        "Note_Source": current_app.config["CT_CONDITION_NOTE_SOURCE"],
                        "Note_Copyright": current_app.config[
                            "CT_CONDITION_NOTE_COPYRIGHT"
                        ],
                        "Note_Description": current_app.config[
                            "CT_CONDITION_NOTE_DESCRIPTION"
                        ],
                    },
                    "Devices": {
                        "Note_Source": current_app.config["CT_DEVICE_NOTE_SOURCE"],
                    },
                    "Drugs": {
                        "Drugs_Prescription": {},
                        "Drugs_Over_The_Counter": {},
                        "Drugs_Other": {},
                        "Note_Source": current_app.config["CT_DRUG_NOTE_SOURCE_FDA"],
                    },
                    "Lab_Results": {
                        "Note_Source": current_app.config["CT_LAB_RESULT_NOTE_SOURCE"],
                        "Note_Copyright": current_app.config[
                            "CT_LAB_RESULT_NOTE_COPYRIGHT"
                        ],
                    },
                    "Procedures": {
                        "Note_Source": current_app.config["CT_PROCEDURE_NOTE_SOURCE"],
                        "Note_Copyright": current_app.config[
                            "CT_PROCEDURE_NOTE_COPYRIGHT"
                        ],
                        "Note_Description": current_app.config[
                            "CT_PROCEDURE_NOTE_DESCRIPTION"
                        ],
                    },
                    "Providers": {
                        "Note_Source": current_app.config["CT_PROVIDER_NOTE_SOURCE"],
                    },
                    "Vitals": {
                        "Note_Source": current_app.config["CT_VITAL_NOTE_SOURCE"],
                    },
                }
            }
            cond_counter = 1
            pre_counter = 1
            otc_counter = 1
            other_counter = 1
            pro_counter = 1
            lab_counter = 1
            vit_counter = 1
            proce_counter = 1
            dev_counter = 1
            for condition in random_conditions["NIHPO_API"]["Results"]:
                condition["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                    date.today(), 0, age
                )
                person[title]["Conditions"]["Condition" + str(cond_counter)] = condition
                cond_counter = cond_counter + 1
            for list_1 in list_drugs:
                for drug in list_1:
                    drug_date = func_nihpo_random_date_birth(date.today(), 0, age)
                    drug["drug_start_date[YYYY-MM-DD]"] = drug_date
                    drug["drug_end_date[YYYY-MM-DD]"] = func_nihpo_random_date(
                        drug_date, 0, 500
                    )
                    if drug["marketing_status"] == "Prescription":
                        person[title]["Drugs"]["Drugs_Prescription"][
                            "Drug" + str(pre_counter)
                        ] = drug
                        pre_counter = pre_counter + 1
                    elif drug["marketing_status"] == "Over-the-counter":
                        person[title]["Drugs"]["Drugs_Over_The_Counter"][
                            "OTC" + str(otc_counter)
                        ] = drug
                        otc_counter = otc_counter + 1
                    else:
                        person[title]["Drugs"]["Drugs_Other"][
                            "Other" + str(other_counter)
                        ] = drug
                        other_counter = other_counter + 1
            for list_2 in list_providers:
                for provider in list_2:
                    provider_date = func_nihpo_random_date_birth(date.today(), 0, age)
                    provider["Provider_Visit_Start_Date[YYYY-MM-DD]"] = provider_date
                    provider[
                        "Provider_Visit_End_Date[YYYY-MM-DD]"
                    ] = func_nihpo_random_date(provider_date, 0, 500)
                    person[title]["Providers"]["Provider" + str(pro_counter)] = provider
                    pro_counter = pro_counter + 1
            for list_3 in list_lab_results:
                for lab_result in list_3:
                    lab_result["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                        date.today(), 0, age
                    )
                    person[title]["Lab_Results"][
                        "Lab_Result" + str(lab_counter)
                    ] = lab_result
                    lab_counter = lab_counter + 1
            for vital in list_vitals:
                person[title]["Vitals"]["Vital" + str(vit_counter)] = vital[0]
                vit_counter = vit_counter + 1
            for list_4 in list_devices:
                for device in list_4:
                    device["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                        date.today(), 0, age
                    )
                    person[title]["Devices"]["Device" + str(dev_counter)] = device
                    dev_counter = dev_counter + 1
            for list_5 in list_procedures:
                for procedure in list_5:
                    procedure["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                        date.today(), 0, age
                    )
                    person[title]["Procedures"][
                        "Procedure" + str(proce_counter)
                    ] = procedure
                    proce_counter = proce_counter + 1
            result["NIHPO_API"]["Results"][title] = person[title]

            if "times" in DEBUG:
                person_inj_time = time_1() - time_person_inj_I
                print("Persons injection time:", person_inj_time)

            if current_app.config["CT_LOGS"]:
                message = (
                    "Person "
                    + str(number_person)
                    + " created in: "
                    + str(time_1() - time_total_I)
                )
                current_app.logger.info(message)

            time_estimation_I = time_1()
            time_person_creation_F = time_1()
            time_person_creation = time_person_creation_F - time_person_creation_I
            times.append(time_person_creation)
            estimated_time_in_seconds = (
                sum(times) * (total_subjects - number_person) / len(times)
            )
            if estimated_time_in_seconds > 600:
                estimated_time = (
                    time.strftime("%M", time.gmtime(estimated_time_in_seconds))
                    + " (min)"
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

            if "times" in DEBUG:
                estimation_time = time_1() - time_estimation_I
                print("Times estimation time:", estimation_time)

            time_task_I = time_1()
            if not current_app.config["PROFILE"]:
                # Update task state:
                if in_task and current_app.env != "testing":
                    in_task.update_state(
                        state="PROGRESS",
                        meta={
                            "current": number_person,
                            "total": total_subjects,
                            "status": "Creating "
                            + '"'
                            + in_file_name
                            + '" '
                            + "file in "
                            + str(estimated_time),
                        },
                    )

            if "times" in DEBUG:
                task_time = time_1() - time_task_I
                print("Task update time:", task_time)

    if "times_report" in DEBUG:
        total_time = time_1() - time_age_I
        print("Total domains time:", total_time)
        print(
            f"Report of creation times:\nAge: {round(age_time, 2)} ({round(age_time*100/total_time, 2)}%)\nLocations: {round(locat_time, 2)} ({round(locat_time*100/total_time, 2)}%)\
            \nConditions: {round(cond_time, 2)} ({round(cond_time*100/total_time, 2)}%)\nDevices: {round(dev_time, 2)} ({round(dev_time*100/total_time, 2)}%)\nDrugs: {round(drug_time, 2)} ({round(drug_time*100/total_time, 2)}%)\
            \nProviders: {round(prov_time, 2)} ({round(prov_time*100/total_time, 2)}%)\nLaboratory Results: {round(lab_time, 2)} ({round(lab_time*100/total_time, 2)}%)\nProcedures: {round(proc_time, 2)} ({round(proc_time*100/total_time, 2)}%)\
            \nVitals: {round(vit_time, 2)} ({round(vit_time*100/total_time, 2)}%)\nNames: {round(names_time, 2)} ({round(names_time*100/total_time, 2)}%)\nLast names: {round(last_time, 2)} ({round(last_time*100/total_time, 2)}%)\
            \nPersons injection: {round(person_inj_time, 2)} ({round(person_inj_time*100/total_time, 2)}%)\nTimes estimation: {round(estimation_time, 2)}, 2) ({round(estimation_time*100/total_time, 2)}%)\
            \nUpdate task: {round(task_time, 2)} ({round(task_time*100/total_time, 2)}%)"
        )

    if current_app.config["CT_LOGS"]:
        message = (
            str(number_person) + " subjects created in: " + str(time_1() - time_total_I)
        )
        current_app.logger.info(message)

    # except Exception as e:
    #     current_app.logger.info(e)

    return result


def func_nihpo_subjects_creation_in_provinces(
    in_min_age,
    in_max_age,
    in_female,
    in_male,
    in_drug_regulator,
    in_drugs_filter,
    in_countries,
    in_file_name,
    in_provinces,
    in_task=None,
):
    """
    Generates all the information for a number of subjects, in a range of ages, with a specific distribution by gender and country, in JSON format.

    :param in_min_age: Minimum age of the subects
    :type in_min_age: Integer
    :param in_max_age: Maximum age of the subects
    :type in_max_age: Integer
    :param in_female: Percentage of women
    :type in_female: Integer (0-100)
    :param in_male: Percentage of men
    :type in_male: Integer (0-100)
    :param in_drug_regulator: Drug regulator (EMA or FDA)
    :type in_drug_regulator: String
    :param in_drugs_filter: Drugs filter level
    :type in_drugs_filter: String
    :param in_countries: Number of subjects per country
    :type in_countries: List of tuples: (Integer, String) Example: ('es, 100)
    :param in_file_name: Name of the output file
    :type in_file_name: String
    :param in_provinces: Provinces into the country
    :type in_provinces: List
    :param in_task: Name of the celery task
    :type in_task: String
    :returns: Subjects created in JSON format
    :rtype: JSON dictionary
    """

    # Initialize variables
    number_person = 0
    total_subjects = 0
    times = []
    time_total_I = time_1()
    cur = current_app.config["CT_POSTGRESQL_CUR"]
    result = copy.deepcopy(current_app.config["CT_JSON_FORMAT"])

    # try:
    # Get total number of subjects
    for item in in_countries:
        total_subjects += int(item[1])

    # Iterate over countries
    for data in in_countries:
        country = data[0]
        number = int(data[1])
        number_for_province = math.ceil(number / len(in_provinces))

        for province in in_provinces:
            # Iterate over each subject of the country
            for person_number in range(1, number_for_province + 1):
                # Initialize variables
                list_drugs = []
                list_providers = []
                list_lab_results = []
                list_vitals = []
                list_procedures = []
                list_devices = []
                time_person_creation_I = time_1()
                number_person = number_person + 1
                title = "Person_" + str(number_person)

                # Get random gender
                gender_choose = random.random() * 100
                if gender_choose <= int(in_female):
                    gender = "F"
                else:
                    gender = "M"

                time_age_I = time_1()
                # Create date of birth and age:
                if in_min_age != None and in_max_age != None:
                    in_min_age = int(in_min_age)
                    in_max_age = int(in_max_age)
                    date_birth = func_nihpo_random_date_birth(
                        date.today(), in_min_age, in_max_age
                    )
                    age = func_nihpo_calculate_age(
                        datetime.datetime.strptime(date_birth, "%Y-%m-%d").date()
                    )
                else:
                    date_birth = func_nihpo_random_date_birth(date.today(), 15, 80)
                    age = func_nihpo_calculate_age(
                        datetime.datetime.strptime(date_birth, "%Y-%m-%d").date()
                    )

                if "times" in DEBUG:
                    age_time = time_1() - time_age_I
                    print("Age time:", age_time)

                # Create locations
                time_locat_I = time_1()

                random_location_1 = Domains.geography(
                    in_country_code_iso=country, in_location_state=province
                )["NIHPO_API"]["Results"][0]
                try:
                    random_location_1_state_name = (
                        unicodedata.normalize("NFKD", random_location_1["State_Name"])
                        .encode("ASCII", "ignore")
                        .decode()
                    )
                except:
                    random_location_1_state_name = random_location_1["State_Name"]
                    pass
                try:
                    random_location_1_place_name = (
                        unicodedata.normalize("NFKD", random_location_1["Place_Name"])
                        .encode("ASCII", "ignore")
                        .decode()
                    )
                except:
                    random_location_1_place_name = random_location_1["Place_Name"]
                    pass
                random_location_2 = Domains.geography(
                    in_country_code_iso=country, in_location_state=province
                )["NIHPO_API"]["Results"][0]
                try:
                    random_location_2_state_name = (
                        unicodedata.normalize("NFKD", random_location_2["State_Name"])
                        .encode("ASCII", "ignore")
                        .decode()
                    )
                except:
                    random_location_2_state_name = random_location_2["State_Name"]
                    pass
                try:
                    random_location_2_place_name = (
                        unicodedata.normalize("NFKD", random_location_2["Place_Name"])
                        .encode("ASCII", "ignore")
                        .decode()
                    )
                except:
                    random_location_2_place_name = random_location_2["Place_Name"]
                    pass
                if "times" in DEBUG:
                    locat_time = time_1() - time_locat_I
                    print("Locations time:", locat_time)

                time_cond_I = time_1()
                # Create conditions
                random_conditions = Domains.condition(
                    in_number=current_app.config["CT_NUMBER_CONDITIONS_PER_PERSON"]
                )
                if "times" in DEBUG:
                    cond_time = time_1() - time_cond_I
                    print("Conditions time:", cond_time)

                # Create drugs
                time_drug_I = time_1()

                if in_drug_regulator == "FDA":
                    list_drugs.append(
                        Domains.drug(
                            in_regulator_code_list="us_fda",
                            in_marketing_status="pre",
                            in_drugs_filter=in_drugs_filter,
                            in_number=current_app.config[
                                "CT_NUMBER_DRUGS_PRE_PER_PERSON"
                            ],
                        )["NIHPO_API"]["Results"]
                    )

                    list_drugs.append(
                        Domains.drug(
                            in_regulator_code_list="us_fda",
                            in_marketing_status="otc",
                            in_drugs_filter=in_drugs_filter,
                            in_number=current_app.config[
                                "CT_NUMBER_DRUGS_OTC_PER_PERSON"
                            ],
                        )["NIHPO_API"]["Results"]
                    )

                    for i in range(
                        0, current_app.config["CT_NUMBER_DRUGS_OTHER_PER_PERSON"]
                    ):
                        status = random.choice(
                            current_app.config["CT_RANDOMIZE_OTHER_DRUG"]
                        )
                        list_drugs.append(
                            Domains.drug(
                                in_regulator_code_list="us_fda",
                                in_marketing_status=status,
                                in_drugs_filter=in_drugs_filter,
                            )["NIHPO_API"]["Results"]
                        )

                elif in_drug_regulator == "EMA":
                    list_drugs.append(
                        Domains.drug(
                            in_regulator_code_list="eu_ema",
                            in_drugs_filter=in_drugs_filter,
                            in_number=current_app.config[
                                "CT_NUMBER_DRUGS_EMA_PER_PERSON"
                            ],
                        )["NIHPO_API"]["Results"]
                    )

                elif in_drug_regulator == "AEMPS":
                    list_drugs.append(
                        Domains.drug(
                            in_regulator_code_list="spain",
                            in_drugs_filter=in_drugs_filter,
                            in_number=current_app.config[
                                "CT_NUMBER_DRUGS_EMA_PER_PERSON"
                            ],
                        )["NIHPO_API"]["Results"]
                    )
                if "times" in DEBUG:
                    drug_time = time_1() - time_drug_I
                    print("Drugs time:", drug_time)

                # Create providers (only for US subjects)
                time_prov_I = time_1()
                if country == "us":
                    for i in range(
                        0, current_app.config["CT_NUMBER_PROVIDERS_PER_PERSON"]
                    ):
                        status = str(
                            random.choice(current_app.config["CT_RANDOMIZE_PROVIDER"])
                        )
                        state_code = random_location_2["State_Code"]
                        list_providers.append(
                            Domains.provider(
                                in_state=state_code, in_entity_type_code=status
                            )["NIHPO_API"]["Results"]
                        )
                if "times" in DEBUG:
                    prov_time = time_1() - time_prov_I
                    print("Providers time:", prov_time)

                time_lab_res_I = time_1()
                # Create lab results
                list_lab_results.append(
                    Domains.lab_result(
                        in_atc_code_filter=in_drugs_filter,
                        in_number=current_app.config[
                            "CT_NUMBER_LAB_RESULTS_PER_PERSON"
                        ],
                    )["NIHPO_API"]["Results"]
                )
                if "times" in DEBUG:
                    lab_time = time_1() - time_lab_res_I
                    print("Lab results time:", lab_time)

                time_proc_I = time_1()
                # Create procedures
                list_procedures.append(
                    Domains.procedure(
                        in_number=current_app.config["CT_NUMBER_PROCEDURES_PER_PERSON"]
                    )["NIHPO_API"]["Results"]
                )

                if "times" in DEBUG:
                    proc_time = time_1() - time_proc_I
                    print("Procedures time:", proc_time)

                time_dev_I = time_1()
                # Create devices
                list_devices.append(
                    Domains.device(
                        in_number=current_app.config["CT_NUMBER_DEVICES_PER_PERSON"]
                    )["NIHPO_API"]["Results"]
                )
                if "times" in DEBUG:
                    dev_time = time_1() - time_dev_I
                    print("Devices time:", dev_time)

                # Create vitals
                time_vit_I = time_1()
                for i in range(
                    0, current_app.config["CT_NUMBER_VITALS_PRE_PER_PERSON"]
                ):
                    random_date = func_nihpo_random_date_birth(date.today(), 0, age)
                    year_vital = age - func_nihpo_calculate_age(
                        datetime.datetime.strptime(random_date, "%Y-%m-%d").date()
                    )
                    random_vital = Domains.vital(in_age=year_vital)["NIHPO_API"][
                        "Results"
                    ]
                    list_vitals.append(random_vital)
                    list_vitals[i][0]["Event_Date[YYYY-MM-DD]"] = random_date
                if "times" in DEBUG:
                    vit_time = time_1() - time_vit_I
                    print("Vitals time:", vit_time)

                time_first_names_I = time_1()
                # Create subjects name
                first_name = Domains.first_name(in_gender=gender)["NIHPO_API"][
                    "Results"
                ][0]["first_name"]
                middle_name = Domains.middle_name(in_gender=gender)["NIHPO_API"][
                    "Results"
                ][0]["middle_name"]

                if "times" in DEBUG:
                    names_time = time_1() - time_first_names_I
                    print("Names time:", names_time)

                time_last_name_I = time_1()
                last_name = Domains.last_name()["NIHPO_API"]["Results"][0]["last_name"]

                if "times" in DEBUG:
                    last_time = time_1() - time_last_name_I
                    print("Last name time:", last_time)

                time_person_inj_I = time_1()
                # Create JSON variable with all the data:
                person = {
                    title: {
                        "Demographics": {
                            "Patient_ID": str(uuid.uuid4()),
                            "First_Name": first_name,
                            "Middle_Name": middle_name,
                            "Last_Name": last_name,
                            "Gender": gender,
                            "Race": random.choice(current_app.config["CT_RACES"]),
                            "Date_Of_Birth[YYYY-MM-DD]": date_birth,
                            "Country_Of_Birth": random_location_1["Country_Name"],
                            "State_Province_Of_Birth": random_location_1_state_name,
                            "Location_Of_Birth": random_location_1_place_name,
                            "Location_Of_Birth_Lat": random_location_1["Latitude"],
                            "Location_Of_Birth_Long": random_location_1["Longitude"],
                            "Country_Of_Residence": random_location_2["Country_Name"],
                            "State_Province_Of_Residence": random_location_2_state_name,
                            "Location_Of_Residence": random_location_2_place_name,
                            "Location_Of_Residence_Lat": random_location_2["Latitude"],
                            "Location_Of_Residence_Long": random_location_2[
                                "Longitude"
                            ],
                            "Age": age,
                            "Age_Units": "Years",
                            "Civil_Status": random.choice(
                                current_app.config["CT_CIVIL_STATUS"]
                            ),
                        },
                        "Conditions": {
                            "Note_Source": current_app.config[
                                "CT_CONDITION_NOTE_SOURCE"
                            ],
                            "Note_Copyright": current_app.config[
                                "CT_CONDITION_NOTE_COPYRIGHT"
                            ],
                            "Note_Description": current_app.config[
                                "CT_CONDITION_NOTE_DESCRIPTION"
                            ],
                        },
                        "Devices": {
                            "Note_Source": current_app.config["CT_DEVICE_NOTE_SOURCE"],
                        },
                        "Drugs": {
                            "Drugs_Prescription": {},
                            "Drugs_Over_The_Counter": {},
                            "Drugs_Other": {},
                            "Note_Source": current_app.config[
                                "CT_DRUG_NOTE_SOURCE_FDA"
                            ],
                        },
                        "Lab_Results": {
                            "Note_Source": current_app.config[
                                "CT_LAB_RESULT_NOTE_SOURCE"
                            ],
                            "Note_Copyright": current_app.config[
                                "CT_LAB_RESULT_NOTE_COPYRIGHT"
                            ],
                        },
                        "Procedures": {
                            "Note_Source": current_app.config[
                                "CT_PROCEDURE_NOTE_SOURCE"
                            ],
                            "Note_Copyright": current_app.config[
                                "CT_PROCEDURE_NOTE_COPYRIGHT"
                            ],
                            "Note_Description": current_app.config[
                                "CT_PROCEDURE_NOTE_DESCRIPTION"
                            ],
                        },
                        "Providers": {
                            "Note_Source": current_app.config[
                                "CT_PROVIDER_NOTE_SOURCE"
                            ],
                        },
                        "Vitals": {
                            "Note_Source": current_app.config["CT_VITAL_NOTE_SOURCE"],
                        },
                    }
                }
                cond_counter = 1
                pre_counter = 1
                otc_counter = 1
                other_counter = 1
                pro_counter = 1
                lab_counter = 1
                vit_counter = 1
                proce_counter = 1
                dev_counter = 1
                for condition in random_conditions["NIHPO_API"]["Results"]:
                    condition["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                        date.today(), 0, age
                    )
                    person[title]["Conditions"][
                        "Condition" + str(cond_counter)
                    ] = condition
                    cond_counter = cond_counter + 1
                for list_1 in list_drugs:
                    for drug in list_1:
                        drug_date = func_nihpo_random_date_birth(date.today(), 0, age)
                        drug["drug_start_date[YYYY-MM-DD]"] = drug_date
                        drug["drug_end_date[YYYY-MM-DD]"] = func_nihpo_random_date(
                            drug_date, 0, 500
                        )
                        if drug["marketing_status"] == "Prescription":
                            person[title]["Drugs"]["Drugs_Prescription"][
                                "Drug" + str(pre_counter)
                            ] = drug
                            pre_counter = pre_counter + 1
                        elif drug["marketing_status"] == "Over-the-counter":
                            person[title]["Drugs"]["Drugs_Over_The_Counter"][
                                "OTC" + str(otc_counter)
                            ] = drug
                            otc_counter = otc_counter + 1
                        else:
                            person[title]["Drugs"]["Drugs_Other"][
                                "Other" + str(other_counter)
                            ] = drug
                            other_counter = other_counter + 1
                for list_2 in list_providers:
                    for provider in list_2:
                        provider_date = func_nihpo_random_date_birth(
                            date.today(), 0, age
                        )
                        provider[
                            "Provider_Visit_Start_Date[YYYY-MM-DD]"
                        ] = provider_date
                        provider[
                            "Provider_Visit_End_Date[YYYY-MM-DD]"
                        ] = func_nihpo_random_date(provider_date, 0, 500)
                        person[title]["Providers"][
                            "Provider" + str(pro_counter)
                        ] = provider
                        pro_counter = pro_counter + 1
                for list_3 in list_lab_results:
                    for lab_result in list_3:
                        lab_result[
                            "Event_Date[YYYY-MM-DD]"
                        ] = func_nihpo_random_date_birth(date.today(), 0, age)
                        person[title]["Lab_Results"][
                            "Lab_Result" + str(lab_counter)
                        ] = lab_result
                        lab_counter = lab_counter + 1
                for vital in list_vitals:
                    person[title]["Vitals"]["Vital" + str(vit_counter)] = vital[0]
                    vit_counter = vit_counter + 1
                for list_4 in list_devices:
                    for device in list_4:
                        device["Event_Date[YYYY-MM-DD]"] = func_nihpo_random_date_birth(
                            date.today(), 0, age
                        )
                        person[title]["Devices"]["Device" + str(dev_counter)] = device
                        dev_counter = dev_counter + 1
                for list_5 in list_procedures:
                    for procedure in list_5:
                        procedure[
                            "Event_Date[YYYY-MM-DD]"
                        ] = func_nihpo_random_date_birth(date.today(), 0, age)
                        person[title]["Procedures"][
                            "Procedure" + str(proce_counter)
                        ] = procedure
                        proce_counter = proce_counter + 1
                result["NIHPO_API"]["Results"][title] = person[title]

                if "times" in DEBUG:
                    person_inj_time = time_1() - time_person_inj_I
                    print("Persons injection time:", person_inj_time)

                if current_app.config["CT_LOGS"]:
                    message = (
                        "Person "
                        + str(number_person)
                        + " created in: "
                        + str(time_1() - time_total_I)
                    )
                    current_app.logger.info(message)

                time_estimation_I = time_1()
                time_person_creation_F = time_1()
                time_person_creation = time_person_creation_F - time_person_creation_I
                times.append(time_person_creation)
                estimated_time_in_seconds = (
                    sum(times) * (total_subjects - number_person) / len(times)
                )
                if estimated_time_in_seconds > 600:
                    estimated_time = (
                        time.strftime("%M", time.gmtime(estimated_time_in_seconds))
                        + " (min)"
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

                if "times" in DEBUG:
                    estimation_time = time_1() - time_estimation_I
                    print("Times estimation time:", estimation_time)

                time_task_I = time_1()
                if not current_app.config["PROFILE"]:
                    # Update task state:
                    if in_task and current_app.env != "testing":
                        in_task.update_state(
                            state="PROGRESS",
                            meta={
                                "current": number_person,
                                "total": total_subjects,
                                "status": "Creating "
                                + '"'
                                + in_file_name
                                + '" '
                                + "file in "
                                + str(estimated_time),
                            },
                        )

                if "times" in DEBUG:
                    task_time = time_1() - time_task_I
                    print("Task update time:", task_time)

    if "times_report" in DEBUG:
        total_time = time_1() - time_age_I
        print("Total domains time:", total_time)
        print(
            f"Report of creation times:\nAge: {round(age_time, 2)} ({round(age_time*100/total_time, 2)}%)\nLocations: {round(locat_time, 2)} ({round(locat_time*100/total_time, 2)}%)\
            \nConditions: {round(cond_time, 2)} ({round(cond_time*100/total_time, 2)}%)\nDevices: {round(dev_time, 2)} ({round(dev_time*100/total_time, 2)}%)\nDrugs: {round(drug_time, 2)} ({round(drug_time*100/total_time, 2)}%)\
            \nProviders: {round(prov_time, 2)} ({round(prov_time*100/total_time, 2)}%)\nLaboratory Results: {round(lab_time, 2)} ({round(lab_time*100/total_time, 2)}%)\nProcedures: {round(proc_time, 2)} ({round(proc_time*100/total_time, 2)}%)\
            \nVitals: {round(vit_time, 2)} ({round(vit_time*100/total_time, 2)}%)\nNames: {round(names_time, 2)} ({round(names_time*100/total_time, 2)}%)\nLast names: {round(last_time, 2)} ({round(last_time*100/total_time, 2)}%)\
            \nPersons injection: {round(person_inj_time, 2)} ({round(person_inj_time*100/total_time, 2)}%)\nTimes estimation: {round(estimation_time, 2)} ({round(estimation_time*100/total_time, 2)}%)\
            \nUpdate task: {round(task_time, 2)} ({round(task_time*100/total_time, 2)}%)"
        )

    if current_app.config["CT_LOGS"]:
        message = (
            str(number_person) + " subjects created in: " + str(time_1() - time_total_I)
        )
        current_app.logger.info(message)

    # except Exception as e:
    #     current_app.logger.info(e)

    return result
