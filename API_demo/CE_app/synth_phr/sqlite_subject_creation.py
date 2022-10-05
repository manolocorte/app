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
from time import perf_counter as time_1
from CE_app.synth_phr.subjects_creation import (
    func_nihpo_subjects_creation,
    func_nihpo_subjects_creation_in_provinces,
)
from CE_app import celery, db
from CE_app.models import Files
import sqlite3

event_date = "Event_Date[YYYY-MM-DD]"
drug_start_date = "drug_start_date[YYYY-MM-DD]"
drug_end_date = "drug_end_date[YYYY-MM-DD]"


@celery.task(bind=True)
def func_nihpo_generate_SQLite3_file(
    self,
    in_min_age,
    in_max_age,
    in_female,
    in_male,
    in_drug_regulator,
    in_drugs_filter,
    in_countries,
    in_folder_name,
    in_file_name,
    in_first_name,
    in_last_name,
    in_email,
    in_country_names=None,
    in_user_id=None,
    in_provinces=None,
):
    """
    Generates all the information for a number of subjects, in a range of ages, with a specific distribution by gender and country,
    in SQLite3 format.

    :param in_file_name: Name of the file where the information will be saved
    :type in_file_name: String
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
    :param in_countries: Number of subjects oer country
    :type in_countries: List of tuples: (Integer, String) Example: (100, 'ES')
    :param in_folder_name: Name of the current user folder
    :type in_folder_name: String
    :param in_file_name: Name of the output file
    :type in_file_name: String
    :param in_first_name: Current user first name
    :type in_first_name: String
    :param in_last_name: Current user last name
    :type in_last_name: String
    :param in_email: Current user email
    :type in_email: String
    :param in_country_names: Name of the selected countries
    :type in_country_names: List
    :returns: Subjects created in SQLite3 format
    :rtype: SQLite3 file
    """
    # try:
    time_I = time_1()

    data_email = {
        "Min Age": in_min_age,
        "Max Age": in_max_age,
        "Female": in_female,
        "Male": in_male,
        "Drug Regulator": in_drug_regulator,
    }

    if in_min_age:
        in_min_age = int(in_min_age)
    if in_max_age:
        in_max_age = int(in_max_age)

    number_subjects = 0
    for data in in_countries:
        number_subjects = number_subjects + int(data[1])

    in_debug = 0

    """
        in_debug: integer
            1 - Demographics
            2 - Conditions
            3 - Devices
            4 - Drugs
            5 - Lab_Results
            6 - Procedures
            7 - Providers
            8 - Vitals
    """

    # Create a SQLite3 file in memory
    sqlite3_conn = sqlite3.connect(":memory:")
    cur = sqlite3_conn.cursor()

    # Base table
    sqlite3_conn.execute("DROP TABLE IF EXISTS NIHPO_API;")
    sqlite3_conn.execute(
        """CREATE TABLE NIHPO_API
        (Note_Disclaimer TEXT,
        Note_Copyright TEXT,
        Note_Feedback TEXT,
        Note_Version TEXT);"""
    )
    sql_insert_base = """INSERT INTO NIHPO_API (Note_Disclaimer, Note_Copyright, Note_Feedback, Note_Version) VALUES (?, ?, ?, ?);"""
    data_insert_base = (
        current_app.config["CT_NOTE_DISCLAIMER"],
        current_app.config["CT_NOTE_COPYRIGHT"],
        current_app.config["CT_NOTE_FEEDBACK"],
        current_app.config["CT_NOTE_VERSION"],
    )
    sqlite3_conn.execute(sql_insert_base, data_insert_base)
    sqlite3_conn.commit()

    # Create Demographics table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Demographics;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Demographics
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Patient_ID TEXT,
        First_Name TEXT,
        Middle_Name TEXT,
        Last_Name TEXT,
        Gender TEXT,
        Race TEXT,
        Date_Of_Birth TEXT,
        Country_Of_Birth TEXT,
        State_Province_Of_Birth TEXT,
        Location_Of_Birth TEXT,
        Location_Of_Birth_Lat TEXT,
        Location_Of_Birth_Long TEXT,
        Country_Of_Residence TEXT,
        State_Province_Of_Residence TEXT,
        Location_Of_Residence TEXT,
        Location_Of_Residence_Lat TEXT,
        Location_Of_Residence_Long TEXT,
        Age TEXT,
        Age_Units TEXT,
        Civil_Status TEXT);"""
    )

    # Create Conditions table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Conditions;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Conditions
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Event_Date TEXT,
        TermID TEXT,
        TermName TEXT,
        UMLS_CUI TEXT,
        Occurrence TEXT,
        Usage TEXT,
        NIHPO_Hierarchy TEXT);"""
    )

    # Create Devices table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Devices;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Devices
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Event_Date TEXT,
        KNumber TEXT,
        Applicant TEXT,
        Date_Received TEXT,
        Decision_Date TEXT,
        Decision TEXT,
        Review_Advise_Comm TEXT,
        Product_Code TEXT,
        Class_Advise_Comm TEXT,
        Type TEXT,
        Third_Party TEXT,
        Expedited_Review TEXT,
        Device_Name TEXT,
        State_Or_Summ TEXT);"""
    )

    # Create Drugs table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Drugs;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Drugs
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,        
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        drug_type TEXT,
        active_ingredient TEXT,
        applno TEXT,
        atc_code TEXT,
        drug_end_date TEXT,
        drug_start_date TEXT,
        form TEXT,
        indication TEXT,
        inn TEXT,
        marketing_status TEXT,
        name TEXT,
        regulator TEXT,
        source TEXT,
        sponsor TEXT,
        submission_type TEXT);"""
    )

    # Create Lab_Results table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Lab_Results;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Lab_Results
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Ask_At_Order_Entry TEXT,
        Associated_Observations TEXT,
        ATC_Code TEXT,
        CDISC_Common_Tests TEXT,
        Class TEXT,
        Class_Type TEXT,
        Common_Order_Rank TEXT,
        Common_Si_Test_Rank TEXT,
        Common_Test_Rank TEXT,
        Component TEXT,
        Consumer_Name TEXT,
        Definition_Description TEXT,
        Display_Name TEXT,
        Example_Si_Ucum_Units TEXT,
        Example_Ucum_Units TEXT,
        Example_Units TEXT,
        Example_Answers TEXT,
        External_Copyright_Link TEXT,
        External_Copyright_Notice TEXT,
        Event_Date TEXT,
        Formula TEXT,
        LOINC_Number TEXT,
        Long_Common_Name TEXT,
        Method_Type TEXT,
        Order_Observation TEXT,
        Property TEXT,
        Panel_Type TEXT,
        Related_Names_2 TEXT,
        Scale_Type TEXT,
        Short_Name TEXT,
        Status TEXT,
        Status_Reason TEXT,
        Status_Text TEXT,
        Submitted_Units TEXT,
        System TEXT,
        Source TEXT,
        Time_Aspect TEXT,
        Units_Required TEXT,
        Units_And_Range TEXT);"""
    )

    # Create Procedures table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Procedures;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Procedures
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Event_Date TEXT,
        NIHPO_Hierarchy TEXT,
        Occurrence TEXT,
        Source TEXT,
        TermID TEXT,
        TermName TEXT,
        UMLS_CUI TEXT,
        Usage TEXT);"""
    )

    # Create Providers table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Providers;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Providers
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Authorized_Official_First_Name TEXT,
        Authorized_Official_Last_Name TEXT,
        Authorized_Official_Middle_Name TEXT,
        Authorized_Official_Telephone_Number TEXT,
        Authorized_Official_Title_Or_Position TEXT,
        Entity_Type_Code TEXT,
        Healthcare_Provider_Taxonomy_Code_1 TEXT,
        Healthcare_Provider_Taxonomy_Code_2 TEXT,
        Healthcare_Provider_Taxonomy_Code_3 TEXT,
        Healthcare_Provider_Taxonomy_Code_4 TEXT,
        Healthcare_Provider_Taxonomy_Code_5 TEXT,
        Healthcare_Provider_Taxonomy_Code_6 TEXT,
        Healthcare_Provider_Taxonomy_Code_7 TEXT,
        Healthcare_Provider_Taxonomy_Code_8 TEXT,
        Healthcare_Provider_Taxonomy_Code_9 TEXT,
        Healthcare_Provider_Taxonomy_Code_10 TEXT,
        Healthcare_Provider_Taxonomy_Code_11 TEXT,
        Healthcare_Provider_Taxonomy_Code_12 TEXT,
        Healthcare_Provider_Taxonomy_Code_13 TEXT,
        Healthcare_Provider_Taxonomy_Code_14 TEXT,
        Healthcare_Provider_Taxonomy_Code_15 TEXT,
        Is_Sole_Proprietor TEXT,
        NPI_Deactivation_Date TEXT,
        NPI_Deactivation_Reason_Code TEXT,
        NPI_Reactivation_Date TEXT,
        Provider_Business_Mailing_Address_City_Name TEXT,
        Provider_Business_Mailing_Address_Country_Code_If_outside_U_S TEXT,
        Provider_Business_Mailing_Address_Fax_Number TEXT,
        Provider_Business_Mailing_Address_Postal_Code TEXT,
        Provider_Business_Mailing_Address_State_Name TEXT,
        Provider_Business_Mailing_Address_Telephone_Number TEXT,
        Provider_Business_Practice_Location_Address_City_Name TEXT,
        Provider_Business_Practice_Location_Address_Country_Code_If_outside_U_S TEXT,
        Provider_Business_Practice_Location_Address_Fax_Number TEXT,
        Provider_Business_Practice_Location_Address_Postal_Code TEXT,
        Provider_Business_Practice_Location_Address_State_Name TEXT,
        Provider_Business_Practice_Location_Address_Telephone_Number TEXT,
        Provider_Credential TEXT,
        Provider_First_Name,
        Provider_Gender_Code TEXT,
        Provider_Last_Name_Legal_Name TEXT,
        Provider_Middle_Name TEXT,
        Provider_Name_Prefix TEXT,
        Provider_Name_Suffix TEXT,
        Provider_Organization_Name_Legal_Business_Name TEXT,
        Provider_Other_Credential TEXT,
        Provider_Other_First_Name TEXT,
        Provider_Other_Last_Name TEXT,
        Provider_Other_Last_Name_Type_Code TEXT,
        Provider_Other_Middle_Name TEXT,
        Provider_Other_Name_Prefix TEXT,
        Provider_Other_Name_Suffix TEXT,
        Provider_Other_Organization_Name TEXT,
        Provider_Other_Organization_Name_Type_Code TEXT,
        Provider_Visit_Start_Date TEXT,
        Provider_Visit_End_Date TEXT,
        npi TEXT);"""
    )

    # Create Vitals table
    sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Vitals;")
    sqlite3_conn.execute(
        """CREATE TABLE Synth_PHR_Vitals
        (
        id INTEGER PRIMARY KEY AUTOINCREMENT,    
        Patient_ID TEXT,
        Note_Source TEXT,
        Note_Copyright TEXT,
        Note_Description TEXT,
        Vital_Number INT,
        Event_Date TEXT,
        Vital_Type TEXT,
        Vital_Detail TEXT,
        Vital_Result TEXT);"""
    )

    if in_provinces:
        one_Person = func_nihpo_subjects_creation_in_provinces(
            in_min_age,
            in_max_age,
            in_female,
            in_male,
            in_drug_regulator,
            in_drugs_filter,
            in_countries,
            in_file_name,
            in_provinces,
            in_task=self,
        )
        number_subjects = len(one_Person["NIHPO_API"]["Results"])
    else:
        one_Person = func_nihpo_subjects_creation(
            in_min_age,
            in_max_age,
            in_female,
            in_male,
            in_drug_regulator,
            in_drugs_filter,
            in_countries,
            in_file_name,
            in_task=self,
        )

    root_node = one_Person["NIHPO_API"]
    results_node = root_node["Results"]

    var_Person_counter = 1
    while var_Person_counter <= number_subjects:
        node_Person = results_node[
            "Person_%d" % (var_Person_counter)
        ]  # Pensing: %d' % (var_Person_counter)] # Dynamically adjust for each Person's number.

        # = = "Demographics" = =
        node_Demographics = node_Person["Demographics"]

        # VERY important value to be used for all insertions below:
        var_Person_ID = node_Demographics["Patient_ID"]
        #
        sql_insert_demographic = """INSERT INTO Synth_PHR_Demographics (Patient_ID, First_Name, Middle_Name, Last_Name, Gender, Race, Date_Of_Birth, Country_Of_Birth, State_Province_Of_Birth, Location_Of_Birth, Location_Of_Birth_Lat, Location_Of_Birth_Long, Country_Of_Residence, State_Province_Of_Residence, Location_Of_Residence, Location_Of_Residence_Lat, Location_Of_Residence_Long, Age, Age_Units, Civil_Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        data_insert_demographic = (
            node_Demographics["Patient_ID"],
            node_Demographics["First_Name"],
            node_Demographics["Middle_Name"],
            node_Demographics["Last_Name"],
            node_Demographics["Gender"],
            node_Demographics["Race"],
            node_Demographics["Date_Of_Birth[YYYY-MM-DD]"],
            node_Demographics["Country_Of_Birth"],
            node_Demographics["State_Province_Of_Birth"],
            node_Demographics["Location_Of_Birth"],
            node_Demographics["Location_Of_Birth_Lat"],
            node_Demographics["Location_Of_Birth_Long"],
            node_Demographics["Country_Of_Residence"],
            node_Demographics["State_Province_Of_Residence"],
            node_Demographics["Location_Of_Residence"],
            node_Demographics["Location_Of_Residence_Lat"],
            node_Demographics["Location_Of_Residence_Long"],
            node_Demographics["Age"],
            node_Demographics["Age_Units"],
            node_Demographics["Civil_Status"],
        )
        sqlite3_conn.execute(sql_insert_demographic, data_insert_demographic)
        sqlite3_conn.commit()

        # = = "Conditions" = =
        node_Conditions = node_Person["Conditions"]
        var_number_Conditions = len(node_Conditions)

        var_Condition_counter = 1
        while var_Condition_counter <= var_number_Conditions:
            try:
                one_Condition_node = node_Conditions[
                    "Condition%d" % (var_Condition_counter)
                ]
                sql_insert_condition = """INSERT INTO Synth_PHR_Conditions (Patient_ID, Note_Source, Note_Copyright, Note_Description, Event_Date, TermID, TermName, UMLS_CUI, Occurrence, Usage, NIHPO_Hierarchy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_condition = (
                    var_Person_ID,
                    current_app.config["CT_CONDITION_NOTE_SOURCE"],
                    current_app.config["CT_CONDITION_NOTE_COPYRIGHT"],
                    current_app.config["CT_CONDITION_NOTE_DESCRIPTION"],
                    one_Condition_node[event_date],
                    one_Condition_node["TermID"],
                    one_Condition_node["TermName"],
                    one_Condition_node["UMLS_CUI"],
                    str(one_Condition_node["Occurrence"]),
                    str(one_Condition_node["Usage"]),
                    one_Condition_node["NIHPO_Hierarchy"],
                )
                sqlite3_conn.execute(sql_insert_condition, data_insert_condition)
                sqlite3_conn.commit()
            except KeyError:  # For nodes that do not contain "Condition" label.
                pass

            var_Condition_counter += 1

        # = = "Devices" = =
        node_Devices = node_Person["Devices"]
        var_number_Devices = len(node_Devices) - 1
        var_Device_counter = 1
        while var_Device_counter <= var_number_Devices:
            one_Device_node = node_Devices["Device%d" % (var_Device_counter)]
            sql_insert_device = """INSERT INTO Synth_PHR_Devices (Patient_ID, Note_Source, Note_Copyright, Note_Description, Event_Date, KNumber, Applicant, Date_Received, Decision_Date, Decision, Review_Advise_Comm, Product_Code, Class_Advise_Comm, Type, Third_Party, Expedited_Review, Device_Name, State_Or_Summ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            data_insert_device = (
                var_Person_ID,
                current_app.config["CT_DEVICE_NOTE_SOURCE"],
                current_app.config["CT_DEVICE_NOTE_COPYRIGHT"],
                current_app.config["CT_DEVICE_NOTE_DESCRIPTION"],
                one_Device_node[event_date],
                one_Device_node["KNumber"],
                one_Device_node["Applicant"],
                one_Device_node["DateReceived"],
                one_Device_node["DecisionDate"],
                one_Device_node["Decision"],
                one_Device_node["ReviewAdviseComm"],
                one_Device_node["ProductCode"],
                one_Device_node["ClassAdviseComm"],
                one_Device_node["Type"],
                one_Device_node["ThirdParty"],
                one_Device_node["ExpeditedReview"],
                one_Device_node["DeviceName"],
                one_Device_node["StateOrSumm"],
            )
            sqlite3_conn.execute(sql_insert_device, data_insert_device)
            sqlite3_conn.commit()

            var_Device_counter += 1

        # = = "Drugs" = =
        node_Drugs = node_Person["Drugs"]
        node_Drugs_Other = node_Drugs["Drugs_Other"]
        node_Drugs_OTC = node_Drugs["Drugs_Over_The_Counter"]
        node_Drugs_Prescription = node_Drugs["Drugs_Prescription"]
        var_number_Drugs_Other = len(node_Drugs_Other)
        var_number_Drugs_OTC = len(node_Drugs_OTC)
        var_number_Drugs_Prescription = len(node_Drugs_Prescription)

        var_Drug_Other_counter = 1
        while var_Drug_Other_counter <= var_number_Drugs_Other:
            one_Drug_Other_node = node_Drugs_Other["Other%d" % (var_Drug_Other_counter)]

            if in_drug_regulator == "FDA":
                source_note = current_app.config["CT_DRUG_NOTE_SOURCE_FDA"]
                copyright_note = current_app.config["CT_DRUG_NOTE_COPYRIGHT_FDA"]
                description_note = current_app.config["CT_DRUG_NOTE_DESCRIPTION_FDA"]
            elif in_drug_regulator == "EMA":
                source_note = current_app.config["CT_DRUG_NOTE_SOURCE_EMA"]
                copyright_note = current_app.config["CT_DRUG_NOTE_COPYRIGHT_EMA"]
                description_note = current_app.config["CT_DRUG_NOTE_DESCRIPTION_EMA"]
            elif in_drug_regulator == "AEMPS":
                source_note = current_app.config["CT_DRUG_NOTE_SOURCE_SPAIN"]
                copyright_note = current_app.config["CT_DRUG_NOTE_COPYRIGHT_SPAIN"]
                description_note = current_app.config["CT_DRUG_NOTE_DESCRIPTION_SPAIN"]
            sql_insert_drug = """INSERT INTO Synth_PHR_Drugs (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                active_ingredient,
                applno,
                atc_code,
                drug_end_date,
                drug_start_date,
                form,
                indication,
                inn,
                marketing_status,
                name,
                regulator,
                source,
                sponsor,
                submission_type,
                drug_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            data_insert_drug = (
                var_Person_ID,
                source_note,
                copyright_note,
                description_note,
                one_Drug_Other_node["active_ingredient"],
                one_Drug_Other_node["applno"],
                one_Drug_Other_node["atc_code"],
                one_Drug_Other_node[drug_end_date],
                one_Drug_Other_node[drug_start_date],
                one_Drug_Other_node["form"],
                one_Drug_Other_node["indication"],
                one_Drug_Other_node["inn"],
                one_Drug_Other_node["marketing_status"],
                one_Drug_Other_node["drug_name"],
                one_Drug_Other_node["regulator"],
                one_Drug_Other_node["source"],
                one_Drug_Other_node["sponsor_name"],
                one_Drug_Other_node["submission_type"],
                "Other",
            )
            sqlite3_conn.execute(sql_insert_drug, data_insert_drug)
            sqlite3_conn.commit()
            var_Drug_Other_counter += 1

        var_Drug_OTC_counter = 1
        while var_Drug_OTC_counter <= var_number_Drugs_OTC:
            try:
                one_Drug_OTC_node = node_Drugs_OTC["OTC%d" % (var_Drug_OTC_counter)]
                sql_insert_drug = """INSERT INTO Synth_PHR_Drugs (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    active_ingredient,
                    applno,
                    atc_code,
                    drug_end_date,
                    drug_start_date,
                    form,
                    indication,
                    inn,
                    marketing_status,
                    name,
                    regulator,
                    source,
                    sponsor,
                    submission_type,
                    drug_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_drug = (
                    var_Person_ID,
                    current_app.config["CT_DRUG_NOTE_SOURCE_FDA"],
                    current_app.config["CT_DRUG_NOTE_COPYRIGHT_FDA"],
                    current_app.config["CT_DRUG_NOTE_DESCRIPTION_FDA"],
                    one_Drug_OTC_node["active_ingredient"],
                    one_Drug_OTC_node["applno"],
                    one_Drug_OTC_node["atc_code"],
                    one_Drug_OTC_node[drug_end_date],
                    one_Drug_OTC_node[drug_start_date],
                    one_Drug_OTC_node["form"],
                    one_Drug_OTC_node["indication"],
                    one_Drug_OTC_node["inn"],
                    one_Drug_OTC_node["marketing_status"],
                    one_Drug_OTC_node["drug_name"],
                    one_Drug_OTC_node["regulator"],
                    one_Drug_OTC_node["source"],
                    one_Drug_OTC_node["sponsor_name"],
                    one_Drug_OTC_node["submission_type"],
                    "OTC",
                )
                sqlite3_conn.execute(sql_insert_drug, data_insert_drug)
                sqlite3_conn.commit()

            except KeyError:  # For nodes that do not contain "Drug_Other" label.
                pass
            var_Drug_OTC_counter += 1

        var_Drug_Prescription_counter = 1
        while var_Drug_Prescription_counter <= var_number_Drugs_Prescription:
            try:
                one_Drug_Prescription_node = node_Drugs_Prescription[
                    "Drug%d" % (var_Drug_Prescription_counter)
                ]
                sql_insert_drug = """INSERT INTO Synth_PHR_Drugs (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    active_ingredient,
                    applno,
                    atc_code,
                    drug_end_date,
                    drug_start_date,
                    form,
                    indication,
                    inn,
                    marketing_status,
                    name,
                    regulator,
                    source,
                    sponsor,
                    submission_type,
                    drug_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_drug = (
                    var_Person_ID,
                    current_app.config["CT_DRUG_NOTE_SOURCE_FDA"],
                    current_app.config["CT_DRUG_NOTE_COPYRIGHT_FDA"],
                    current_app.config["CT_DRUG_NOTE_DESCRIPTION_FDA"],
                    one_Drug_Prescription_node["active_ingredient"],
                    one_Drug_Prescription_node["applno"],
                    one_Drug_Prescription_node["atc_code"],
                    one_Drug_Prescription_node[drug_end_date],
                    one_Drug_Prescription_node[drug_start_date],
                    one_Drug_Prescription_node["form"],
                    one_Drug_Prescription_node["indication"],
                    one_Drug_Prescription_node["inn"],
                    one_Drug_Prescription_node["marketing_status"],
                    one_Drug_Prescription_node["drug_name"],
                    one_Drug_Prescription_node["regulator"],
                    one_Drug_Prescription_node["source"],
                    one_Drug_Prescription_node["sponsor_name"],
                    one_Drug_Prescription_node["submission_type"],
                    "Prescription",
                )
                sqlite3_conn.execute(sql_insert_drug, data_insert_drug)
                sqlite3_conn.commit()
            except KeyError:  # For nodes that do not contain "Drug_Other" label.
                pass
            var_Drug_Prescription_counter += 1

        # = = "Lab_Results" = =
        node_Lab_Results = node_Person["Lab_Results"]
        var_number_Lab_Results = len(node_Lab_Results)
        var_Lab_Results_counter = 1
        while var_Lab_Results_counter <= var_number_Lab_Results:
            try:
                one_Lab_Result_node = node_Lab_Results[
                    "Lab_Result%d" % (var_Lab_Results_counter)
                ]
                data_insert_Lab_Result = tuple(
                    (str(v)) for k, v in one_Lab_Result_node.items()
                )
                sql_insert_Lab_Result = """INSERT INTO Synth_PHR_Lab_Results (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    LOINC_Number,
                    Component,
                    Property,
                    Time_Aspect,
                    System,
                    Scale_Type,
                    Method_Type,
                    Class,
                    Definition_Description,
                    Status,
                    Consumer_Name,
                    Class_Type,
                    Formula,
                    Example_Answers,
                    Units_Required,
                    Submitted_Units,
                    Related_Names_2,
                    Short_Name,
                    Order_Observation,
                    CDISC_Common_Tests,
                    External_Copyright_Notice,
                    Example_Units,
                    Long_Common_Name,
                    Units_And_Range,
                    Example_Ucum_Units,
                    Example_Si_Ucum_Units,
                    Status_Reason,
                    Status_Text,
                    Common_Test_Rank,
                    Common_Order_Rank,
                    Common_Si_Test_Rank,
                    External_Copyright_Link,
                    Panel_Type,
                    Ask_At_Order_Entry,
                    Associated_Observations,
                    Display_Name,
                    ATC_Code,
                    Source,
                    Event_Date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_Lab_Result = (
                    var_Person_ID,
                    current_app.config["CT_LAB_RESULT_NOTE_SOURCE"],
                    current_app.config["CT_LAB_RESULT_NOTE_COPYRIGHT"],
                    current_app.config["CT_LAB_RESULT_NOTE_DESCRIPTION"],
                ) + data_insert_Lab_Result
                sqlite3_conn.execute(sql_insert_Lab_Result, data_insert_Lab_Result)
                sqlite3_conn.commit()
                #
            except KeyError:  # For nodes that do not contain "Lab_Result" label.
                pass
            #
            var_Lab_Results_counter += 1
        #
        #
        # = = "Procedures" = =
        node_Procedures = node_Person["Procedures"]
        var_number_Procedures = len(node_Procedures)
        var_Procedure_counter = 1
        while var_Procedure_counter <= var_number_Procedures:
            try:
                one_Procedure_node = node_Procedures[
                    "Procedure%d" % (var_Procedure_counter)
                ]
                data_insert_Procedure = tuple(
                    (str(v)) for k, v in one_Procedure_node.items()
                )
                sql_insert_Procedure = """INSERT INTO Synth_PHR_Procedures (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    Source,
                    TermID,
                    TermName,
                    UMLS_CUI,
                    Occurrence,
                    Usage,
                    NIHPO_Hierarchy,
                    Event_Date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_Procedure = (
                    var_Person_ID,
                    current_app.config["CT_PROCEDURE_NOTE_SOURCE"],
                    current_app.config["CT_PROCEDURE_NOTE_COPYRIGHT"],
                    current_app.config["CT_PROCEDURE_NOTE_DESCRIPTION"],
                ) + data_insert_Procedure
                sqlite3_conn.execute(sql_insert_Procedure, data_insert_Procedure)
                sqlite3_conn.commit()
            except KeyError:  # For nodes that do not contain "Procedure" label.
                pass
            var_Procedure_counter += 1

        # = = "Providers" = =
        node_Providers = node_Person["Providers"]
        var_number_Providers = len(node_Providers)
        var_Provider_counter = 1
        while var_Provider_counter <= var_number_Providers:
            try:
                one_Provider_node = node_Providers[
                    "Provider%d" % (var_Provider_counter)
                ]
                data_insert_Provider = tuple(
                    (str(v)) for k, v in one_Provider_node.items()
                )
                sql_insert_Provider = """INSERT INTO Synth_PHR_Providers (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    npi,
                    Entity_Type_Code,
                    Authorized_Official_Telephone_Number,
                    Provider_Business_Mailing_Address_City_Name,
                    Provider_Business_Mailing_Address_Country_Code_If_outside_U_S,
                    Provider_Business_Mailing_Address_Fax_Number,
                    Provider_Business_Mailing_Address_Postal_Code,
                    Provider_Business_Mailing_Address_State_Name,
                    Provider_Business_Mailing_Address_Telephone_Number,
                    Provider_Business_Practice_Location_Address_City_Name,
                    Provider_Business_Practice_Location_Address_Country_Code_If_outside_U_S,
                    Provider_Business_Practice_Location_Address_Fax_Number,
                    Provider_Business_Practice_Location_Address_Postal_Code,
                    Provider_Business_Practice_Location_Address_State_Name,
                    Provider_Business_Practice_Location_Address_Telephone_Number,
                    Is_Sole_Proprietor,
                    Provider_Gender_Code,
                    NPI_Deactivation_Reason_Code,
                    NPI_Deactivation_Date,
                    NPI_Reactivation_Date,
                    Healthcare_Provider_Taxonomy_Code_1,
                    Healthcare_Provider_Taxonomy_Code_2,
                    Healthcare_Provider_Taxonomy_Code_3,
                    Healthcare_Provider_Taxonomy_Code_4,
                    Healthcare_Provider_Taxonomy_Code_5,
                    Healthcare_Provider_Taxonomy_Code_6,
                    Healthcare_Provider_Taxonomy_Code_7,
                    Healthcare_Provider_Taxonomy_Code_8,
                    Healthcare_Provider_Taxonomy_Code_9,
                    Healthcare_Provider_Taxonomy_Code_10,
                    Healthcare_Provider_Taxonomy_Code_11,
                    Healthcare_Provider_Taxonomy_Code_12,
                    Healthcare_Provider_Taxonomy_Code_13,
                    Healthcare_Provider_Taxonomy_Code_14,
                    Healthcare_Provider_Taxonomy_Code_15,
                    Authorized_Official_Last_Name,
                    Authorized_Official_First_Name,
                    Authorized_Official_Middle_Name,
                    Authorized_Official_Title_Or_Position,
                    Authorized_Official_Telephone_Number,
                    Provider_Organization_Name_Legal_Business_Name,
                    Provider_Last_Name_Legal_Name,
                    Provider_First_Name,
                    Provider_Middle_Name,
                    Provider_Name_Prefix,
                    Provider_Name_Suffix,
                    Provider_Credential,
                    Provider_Other_Last_Name,
                    Provider_Other_First_Name,
                    Provider_Other_Middle_Name,
                    Provider_Other_Name_Prefix,
                    Provider_Other_Name_Suffix,
                    Provider_Other_Credential,
                    Provider_Other_Last_Name_Type_Code,
                    Provider_Other_Organization_Name,
                    Provider_Other_Organization_Name_Type_Code,
                    Provider_Visit_Start_Date,
                    Provider_Visit_End_Date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                data_insert_Provider = (
                    var_Person_ID,
                    current_app.config["CT_PROVIDER_NOTE_SOURCE"],
                    current_app.config["CT_PROVIDER_NOTE_COPYRIGHT"],
                    current_app.config["CT_PROVIDER_NOTE_DESCRIPTION"],
                ) + data_insert_Provider
                sqlite3_conn.execute(sql_insert_Provider, data_insert_Provider)
                sqlite3_conn.commit()
            except KeyError:  # For nodes that do not contain "Procedure" label.
                pass
            var_Provider_counter += 1

        # = = "Vitals" = =
        node_Vitals = node_Person["Vitals"]
        var_number_Vitals = len(node_Vitals)
        var_Vital_counter = 1
        while var_Vital_counter <= var_number_Vitals:
            try:
                one_Vital_node = node_Vitals["Vital%d" % (var_Vital_counter)]
                one_Vital_node_Blood_Pressure = one_Vital_node["Blood_Pressure"]
                one_Vital_node_Oxigen = one_Vital_node["Oxigen_Saturation"]
                one_Vital_node_Pulse = one_Vital_node["Pulse"]
                one_Vital_node_Respiration = one_Vital_node["Respiration"]
                one_Vital_node_Temperature = one_Vital_node["Temperature"]
                one_Vital_node_Weight_Height = one_Vital_node["Weight_And_Height"]
                date = one_Vital_node[event_date]
                del one_Vital_node[event_date]
                sql_insert_Vital = """INSERT INTO Synth_PHR_Vitals (Patient_ID, Note_Source, Note_Copyright, Note_Description,
                    Vital_Number,
                    Event_Date, 
                    Vital_Type, 
                    Vital_Detail, 
                    Vital_Result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                for vital_type in one_Vital_node:
                    for vital_detail in one_Vital_node[vital_type]:
                        data_insert_Vital = (
                            var_Person_ID,
                            current_app.config["CT_VITAL_NOTE_SOURCE"],
                            current_app.config["CT_VITAL_NOTE_COPYRIGHT"],
                            current_app.config["CT_VITAL_NOTE_DESCRIPTION"],
                            var_Vital_counter,
                            date,
                            vital_type,
                            vital_detail,
                            one_Vital_node[vital_type][vital_detail],
                        )
                        sqlite3_conn.execute(sql_insert_Vital, data_insert_Vital)
                        sqlite3_conn.commit()
            except KeyError:  # For nodes that do not contain "Vital" label.
                pass
            var_Vital_counter += 1

        # This counter cycles through the number of Person records.
        if current_app.config["CT_LOGS"]:
            message = "Parameters for person " + str(var_Person_counter) + " created."
            current_app.logger.info(message)
        var_Person_counter += 1

    # Create indices
    # CREATE INDEX index_name ON table_name (column_name);
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Patient_ID ON Synth_PHR_Demographics (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Gender ON Synth_PHR_Demographics (Gender);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Race ON Synth_PHR_Demographics (Race);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Country_Of_birth ON Synth_PHR_Demographics (Country_Of_birth);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_State_Province_Of_Birth ON Synth_PHR_Demographics (State_Province_Of_Birth);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Location_Of_Birth ON Synth_PHR_Demographics (Location_Of_Birth);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Country_Of_Residence ON Synth_PHR_Demographics (Country_Of_Residence);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_State_Province_Of_Residence ON Synth_PHR_Demographics (State_Province_Of_Residence);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Location_Of_Residence ON Synth_PHR_Demographics (Location_Of_Residence);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Age ON Synth_PHR_Demographics (Age);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Age_Units ON Synth_PHR_Demographics (Age_Units);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Civil_Status ON Synth_PHR_Demographics (Civil_Status);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_Date_Of_Birth ON Synth_PHR_Demographics (Date_Of_Birth);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Conditions_Patient_ID ON Synth_PHR_Conditions (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Conditions_Event_Date ON Synth_PHR_Conditions (Event_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Devices_Patient_ID ON Synth_PHR_Devices (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Devices_Event_Date ON Synth_PHR_Devices (Event_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Devices_Date_Received ON Synth_PHR_Devices (Date_Received);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Devices_Decision_Date ON Synth_PHR_Devices (Decision_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Patient_ID ON Synth_PHR_Drugs (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Drug_Type ON Synth_PHR_Drugs (Drug_Type);"""
    )
    try:
        sqlite3_conn.execute("""CREATE INDEX Drugs_Form ON Synth_PHR_Drugs (Form);""")
    except:
        pass
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Marketing_Status ON Synth_PHR_Drugs (Marketing_Status);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Regulator ON Synth_PHR_Drugs (Regulator);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Drug_End_Date ON Synth_PHR_Drugs (Drug_End_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Drugs_Drug_Start_Date ON Synth_PHR_Drugs (Drug_Start_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Lab_Results_Patient_ID ON Synth_PHR_Lab_results (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Lab_Results_Event_Date ON Synth_PHR_Lab_results (Event_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Procedures_Patient_ID ON Synth_PHR_Procedures (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Procedures_Event_Date ON Synth_PHR_Procedures (Event_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Providers_Patient_ID ON Synth_PHR_Providers (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Providers_Provider_Visit_End_Date ON Synth_PHR_Providers (Provider_Visit_End_Date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Providers_Provider_Visit_Start_date ON Synth_PHR_Providers (Provider_Visit_Start_date);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Vitals_Patient_ID ON Synth_PHR_Vitals (Patient_ID);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Vitals_Vital_Number ON Synth_PHR_Vitals (Vital_Number);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Vitals_Vital_Type ON Synth_PHR_Vitals (Vital_Type);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Vitals_Vital_Detail ON Synth_PHR_Vitals (Vital_Detail);"""
    )
    sqlite3_conn.execute(
        """CREATE INDEX Vitals_Event_Date ON Synth_PHR_Vitals (Event_Date);"""
    )
    sqlite3_conn.execute("""CREATE INDEX Conditions_id ON Synth_PHR_Conditions (id);""")
    sqlite3_conn.execute("""CREATE INDEX Devices ON Synth_PHR_Devices (id);""")
    sqlite3_conn.execute(
        """CREATE INDEX Demographics_id ON Synth_PHR_Demographics (id);"""
    )
    sqlite3_conn.execute("""CREATE INDEX Drugs_id ON Synth_PHR_Drugs (id);""")
    sqlite3_conn.execute(
        """CREATE INDEX Lab_Results_id ON Synth_PHR_Lab_Results (id);"""
    )
    sqlite3_conn.execute("""CREATE INDEX Procedures_id ON Synth_PHR_Procedures(id);""")
    sqlite3_conn.execute("""CREATE INDEX Providers_id ON Synth_PHR_Providers (id);""")
    sqlite3_conn.execute("""CREATE INDEX Vitals_id ON Synth_PHR_Vitals(id);""")

    # Commit changes and close connection:
    bckup = sqlite3.connect(
        current_app.config["CT_DOWNLOADS_PATH"] + in_file_name + ".sqlite3",
        detect_types=sqlite3.PARSE_DECLTYPES,
        uri=True,
    )
    with bckup:
        sqlite3_conn.backup(bckup)
    bckup.close()
    sqlite3_conn.close()

    if current_app.config["CT_LOGS"]:
        time_F = time_1()
        message = (
            "SQLite3 file created successfully in:" + str(time_F - time_I) + "seconds."
        )
        current_app.logger.info(message)

    sqlite3_conn.close()

    # Change file status to 'Created'
    if in_user_id != None:
        file = Files.query.filter_by(user_id=in_user_id, file_name=in_file_name).first()
        if file:
            file.file_status = "Created"
            db.session.commit()

    # except Exception as e:
    #     current_app.logger.info(e)

    #     # Remove file from DB if there is some failure
    #     if in_user_id != None:
    #         file = Files.query.filter_by(user_id=in_user_id, file_name=in_file_name).first()
    #         if file:
    #             db.session.delete(file)
    #             db.session.commit()

    return {
        "current": 100,
        "total": 100,
        "status": "File " + '"' + in_file_name + '"' " ready to download!!",
        "result": "File created successfully",
    }
