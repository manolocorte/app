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
from CE_app import celery, db
from CE_app.models import Files
import json, sqlite3, uuid, copy, random, datetime, math, unicodedata, time
from time import perf_counter as time_1
from datetime import date
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from CE_app.synth_phr.synth_phr_func import func_nihpo_random_date_birth, func_nihpo_calculate_age
from CE_app.synth_phr.functions import Domains

event_date = 'Event_Date[YYYY-MM-DD]'
drug_start_date =  'drug_start_date[YYYY-MM-DD]'
drug_end_date =  'drug_end_date[YYYY-MM-DD]'

DEBUG = [] # 'times'

def func_nihpo_person_creation(in_min_age, in_max_age, in_female, in_male, in_countries, in_file_name, in_task=None):
    """
    Generates all the information for a number of persons, in a range of ages, with a specific distribution by gender and country, in JSON format.

    :param in_min_age: Minimum age of the subects
    :type in_min_age: Integer
    :param in_max_age: Maximum age of the subects
    :type in_max_age: Integer
    :param in_female: Percentage of women
    :type in_female: Integer (0-100)
    :param in_male: Percentage of men
    :type in_male: Integer (0-100)
    :param in_drug_regulator: Drug regulator (EMA or FDA)
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
    total_people = 0
    times = []
    time_total_I = time_1()
    cur = current_app.config['CT_POSTGRESQL_CUR']
    result = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])

    try:
        # Get total number of people
        for item in in_countries:
            total_people += int(item[1])
        
        # Iterate over countries
        for data in in_countries:
            country = data[0]
            number = int(data[1])

            # Iterate over each subject of the country
            for person_number in range(1, number + 1):

                time_person_creation_I = time_1()

                number_person = number_person + 1
                title = "Person_" + str(number_person)

                # Get random gender
                gender_choose = random.random()*100
                if gender_choose<=int(in_female):
                    gender = 'F'
                else:
                    gender = 'M'

                time_age_I = time_1()

                # Create date of birth and age:
                if in_min_age!=None and in_max_age!=None:
                    in_min_age = int(in_min_age)
                    in_max_age = int(in_max_age)
                    date_birth = func_nihpo_random_date_birth(date.today(), in_min_age, in_max_age)
                    age = func_nihpo_calculate_age(datetime.datetime.strptime(date_birth, '%Y-%m-%d').date())
                else:
                    date_birth = func_nihpo_random_date_birth(date.today(), 15, 80)
                    age = func_nihpo_calculate_age(datetime.datetime.strptime(date_birth, '%Y-%m-%d').date())
                
                if 'times' in DEBUG:
                    print('Age time:', time_1() - time_age_I)
                
                # Create locations:
                time_locat_I = time_1()

                random_location_1 = Domains.geography(in_country_code_iso=country)["NIHPO_API"]["Results"][0]
                try:
                    random_location_1_state_name = unicodedata.normalize('NFKD', random_location_1['State_Name']).encode('ASCII', 'ignore').decode()
                except:
                    random_location_1_state_name = random_location_1['State_Name']
                    pass
                try:
                    random_location_1_place_name = unicodedata.normalize('NFKD', random_location_1['Place_Name']).encode('ASCII', 'ignore').decode()
                except:
                    random_location_1_place_name = random_location_1['Place_Name']
                    pass
                random_location_2 = Domains.geography(in_country_code_iso=country)["NIHPO_API"]["Results"][0]
                try:
                    random_location_2_state_name = unicodedata.normalize('NFKD', random_location_2['State_Name']).encode('ASCII', 'ignore').decode()
                except:
                    random_location_2_state_name = random_location_2['State_Name']
                    pass
                try:
                    random_location_2_place_name = unicodedata.normalize('NFKD', random_location_2['Place_Name']).encode('ASCII', 'ignore').decode()
                except:
                    random_location_2_place_name = random_location_2['Place_Name']
                    pass
                if 'times' in DEBUG:
                    print('Locations time:', time_1() - time_locat_I)

                time_first_names_I = time_1()
                # Create subjects name
                first_name = Domains.first_name(in_gender=gender)["NIHPO_API"]["Results"][0]['first_name']
                middle_name = Domains.middle_name(in_gender=gender)["NIHPO_API"]["Results"][0]['middle_name']

                if 'times' in DEBUG:
                    names_time = time_1() - time_first_names_I
                    print('Names time:', names_time)
                
                time_last_name_I = time_1()
                last_name = Domains.last_name()["NIHPO_API"]["Results"][0]['last_name']

                if 'times' in DEBUG:
                    last_time = time_1() - time_last_name_I
                    print('Last name time:', last_time)
            
                time_json_I = time_1()
                # Create JSON variable with all the data:
                person = {
                    title: {
                        "Demographics": {
                            "Patient_ID": str(uuid.uuid4()),
                            "First_Name": first_name,
                            "Middle_Name": middle_name,
                            "Last_Name": last_name,
                            "Gender": gender,
                            "Race": random.choice(current_app.config['CT_RACES']),
                            "Date_Of_Birth[YYYY-MM-DD]": date_birth,
                            "Country_Of_Birth": random_location_1['Country_Name'],
                            "State_Province_Of_Birth": random_location_1_state_name,
                            "Location_Of_Birth": random_location_1_place_name,
                            "Location_Of_Birth_Lat": random_location_1['Latitude'],
                            "Location_Of_Birth_Long": random_location_1['Longitude'],
                            "Country_Of_Residence": random_location_2['Country_Name'],
                            "State_Province_Of_Residence": random_location_2_state_name,
                            "Location_Of_Residence": random_location_2_place_name,
                            "Location_Of_Residence_Lat": random_location_2['Latitude'],
                            "Location_Of_Residence_Long": random_location_2['Longitude'],
                            "Age": age,
                            "Age_Units": "Years",
                            "Civil_Status": random.choice(current_app.config['CT_CIVIL_STATUS'])
                        }
                    }
                }
                result["NIHPO_API"]["Results"][title] = person[title]

                if 'times' in DEBUG:
                    print('JSON time:', time_1() - time_json_I)

                if current_app.config['CT_LOGS']:
                    message = 'Person ' + str(number_person) + ' created in: ' + str(time_1() - time_total_I)
                    current_app.logger.info(message)

                time_estimation_I = time_1()
                # Estimate times
                time_person_creation_F = time_1()
                time_person_creation = time_person_creation_F - time_person_creation_I
                times.append(time_person_creation)
                estimated_time_in_seconds = sum(times)*(total_people-number_person)/len(times)
                if estimated_time_in_seconds > 600:
                    estimated_time = time.strftime("%M", time.gmtime(estimated_time_in_seconds)) + ' (min)'
                elif estimated_time_in_seconds <= 600:
                    estimated_time = time.strftime("%M:%S", time.gmtime(estimated_time_in_seconds)) + ' (min, s)'
                else:
                    estimated_time = time.strftime("%H:%M", time.gmtime(estimated_time_in_seconds)) + ' (h, min)'
                
                if 'times' in DEBUG:
                    print('JSON time:', time_1() - time_estimation_I)
                
                # Update task state:
                # if in_task and current_app.env != 'testing':
                #     in_task.update_state(state='PROGRESS', meta={'current': number_person, 'total': total_people, 'status': 'Creating ' + '"' + in_file_name + '" ' + 'file in '+ str(estimated_time)})
                        
        if current_app.config['CT_LOGS']:
            message = str(number_person) + ' subjects created in: ' + str(time_1()- time_total_I)
            current_app.logger.info(message)

    except Exception as e:
        current_app.logger.info(e)

    return result

@celery.task(bind=True)
def func_nihpo_generate_json_file(self, in_min_age, in_max_age, in_female, in_male, in_countries, in_folder_name, in_file_name, in_first_name, in_last_name, in_email, in_country_names=None, in_provinces=None):
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
    :returns: Subjects created in JSON format
    :rtype: JSON dictionary
    """

    try:
        result = func_nihpo_person_creation(in_min_age, in_max_age, in_female, in_male, in_countries, in_file_name, in_task = self)

        with open(current_app.config["CT_DOWNLOADS_PATH"] + in_file_name + '.json', 'w') as json_file:
            json.dump(result, json_file, indent=4)


        # Change file status to created
        file = Files.query.filter_by(file_name=in_file_name, module='PERSON').first()
        if file:
            file.file_status = 'Created'
            db.session.commit()
         
    except Exception as e:
        current_app.logger.info(e)

        # Remove file from DB if there is some failure
        file = Files.query.filter_by(file_name=in_file_name, module='PERSON').first()
        if file:
            db.session.delete(file)
            db.session.commit()

    return {'current': 100, 'total': 100, 'status': 'File ' + '"' + in_file_name + '"' + ' ready to download!!',\
        'result': 'File created successfully'}


@celery.task(bind=True)
def func_nihpo_generate_SQLite3_file(self, in_min_age, in_max_age, in_female, in_male, in_countries, in_folder_name, in_file_name, in_first_name, in_last_name, in_email, in_country_names=None,  in_user_id=None, in_provinces=None):
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

    try:
        time_I = time_1()

        data_email = {'Min Age': in_min_age, 'Max Age': in_max_age, 'Female': in_female, 'Male': in_male}

        if in_min_age:
            in_min_age =int(in_min_age)
        if in_max_age:
            in_max_age =int(in_max_age)

        number_subjects = 0
        for data in in_countries:
            number_subjects = number_subjects + int(data[1])

        # Create a SQLite3 file in memory
        sqlite3_conn = sqlite3.connect(':memory:')
        cur  = sqlite3_conn.cursor()

        # Base table
        sqlite3_conn.execute("DROP TABLE IF EXISTS NIHPO_API;")
        sqlite3_conn.execute('''CREATE TABLE NIHPO_API
            (Note_Disclaimer TEXT,
            Note_Copyright TEXT,
            Note_Feedback TEXT,
            Note_Version TEXT);''')
        sql_insert_base = '''INSERT INTO NIHPO_API (Note_Disclaimer, Note_Copyright, Note_Feedback, Note_Version) VALUES (?, ?, ?, ?);'''
        data_insert_base = (current_app.config['CT_NOTE_DISCLAIMER'], current_app.config['CT_NOTE_COPYRIGHT'], current_app.config['CT_NOTE_FEEDBACK'],\
            current_app.config['CT_NOTE_VERSION'])
        sqlite3_conn.execute(sql_insert_base, data_insert_base)
        sqlite3_conn.commit()

        # Create Demographics table
        sqlite3_conn.execute("DROP TABLE IF EXISTS Synth_PHR_Demographics;")
        sqlite3_conn.execute('''CREATE TABLE Synth_PHR_Demographics
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
            Civil_Status TEXT);'''
            )

        one_Person = func_nihpo_person_creation(in_min_age=in_min_age, in_max_age=in_max_age, in_female=in_female, in_male=in_male, in_countries=in_countries, in_file_name=in_file_name, in_task=self)

        root_node = one_Person['NIHPO_API']
        results_node = root_node['Results']

        for person_counter in range(1, number_subjects+1):
            node_Person = results_node['Person_%d' % (person_counter)]      # Pensing: %d' % (var_Person_counter)] # Dynamically adjust for each Person's number.

            # = = "Demographics" = =
            node_Demographics = node_Person['Demographics']

            # VERY important value to be used for all insertions below:
            var_Person_ID = node_Demographics['Patient_ID']

            sql_insert_demographic = '''INSERT INTO Synth_PHR_Demographics (Patient_ID, First_Name, Middle_Name, Last_Name, Gender, Race, Date_Of_Birth, Country_Of_Birth, State_Province_Of_Birth, Location_Of_Birth, Location_Of_Birth_Lat, Location_Of_Birth_Long, Country_Of_Residence, State_Province_Of_Residence, Location_Of_Residence, Location_Of_Residence_Lat, Location_Of_Residence_Long, Age, Age_Units, Civil_Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'''
            data_insert_demographic = (node_Demographics['Patient_ID'], node_Demographics['First_Name'], node_Demographics['Middle_Name'], node_Demographics['Last_Name'], node_Demographics['Gender'], node_Demographics['Race'], node_Demographics['Date_Of_Birth[YYYY-MM-DD]'], node_Demographics['Country_Of_Birth'], node_Demographics['State_Province_Of_Birth'], node_Demographics['Location_Of_Birth'], node_Demographics['Location_Of_Birth_Lat'], node_Demographics['Location_Of_Birth_Long'], node_Demographics['Country_Of_Residence'], node_Demographics['State_Province_Of_Residence'], node_Demographics['Location_Of_Residence'], node_Demographics['Location_Of_Residence_Lat'], node_Demographics['Location_Of_Residence_Long'], node_Demographics['Age'], node_Demographics['Age_Units'], node_Demographics['Civil_Status'])
            sqlite3_conn.execute(sql_insert_demographic, data_insert_demographic)
            sqlite3_conn.commit()

            # This counter cycles through the number of Person records.
            if current_app.config['CT_LOGS']:
                message = "Parameters for person " + str(person_counter) + " created."
                current_app.logger.info(message)
            
        # Create indices
        # CREATE INDEX index_name ON table_name (column_name);
        sqlite3_conn.execute('''CREATE INDEX Demographics_Patient_ID ON Synth_PHR_Demographics (Patient_ID);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Gender ON Synth_PHR_Demographics (Gender);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Race ON Synth_PHR_Demographics (Race);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Country_Of_birth ON Synth_PHR_Demographics (Country_Of_birth);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_State_Province_Of_Birth ON Synth_PHR_Demographics (State_Province_Of_Birth);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Location_Of_Birth ON Synth_PHR_Demographics (Location_Of_Birth);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Country_Of_Residence ON Synth_PHR_Demographics (Country_Of_Residence);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_State_Province_Of_Residence ON Synth_PHR_Demographics (State_Province_Of_Residence);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Location_Of_Residence ON Synth_PHR_Demographics (Location_Of_Residence);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Age ON Synth_PHR_Demographics (Age);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Age_Units ON Synth_PHR_Demographics (Age_Units);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Civil_Status ON Synth_PHR_Demographics (Civil_Status);''')
        sqlite3_conn.execute('''CREATE INDEX Demographics_Date_Of_Birth ON Synth_PHR_Demographics (Date_Of_Birth);''')

        # Commit changes and close connection:
        bckup = sqlite3.connect(current_app.config["CT_DOWNLOADS_PATH"] + in_file_name + '.sqlite3', detect_types=sqlite3.PARSE_DECLTYPES,uri=True)
        with bckup:
            sqlite3_conn.backup(bckup)
        bckup.close()
        sqlite3_conn.close()

        if current_app.config['CT_LOGS']:
            time_F = time_1()
            message = "SQLite3 file created successfully in:" + str(time_F - time_I) + "seconds."
            current_app.logger.info(message)
            

        # Change file status to 'Created'
        if in_user_id != None:
            file = Files.query.filter_by(user_id=in_user_id, file_name=in_file_name, module='PERSON').first()
            if file:
                file.file_status = 'Created'
                db.session.commit()

    except Exception as e:
        current_app.logger.info(e)

        # Remove file from DB if there is some failure
        if in_user_id != None:
            file = Files.query.filter_by(user_id=in_user_id, file_name=in_file_name, module='PERSON').first()
            if file:
                db.session.delete(file)
                db.session.commit()
        
    return {'current': 100, 'total': 100, 'status': 'File ' + '"' + in_file_name + '"' ' ready to download!!',\
        'result': 'File created successfully'}