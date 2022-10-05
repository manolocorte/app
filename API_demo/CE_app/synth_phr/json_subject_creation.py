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
from CE_app.synth_phr.subjects_creation import func_nihpo_subjects_creation, func_nihpo_subjects_creation_in_provinces
from CE_app import celery, db
from CE_app.models import Files
import json

@celery.task(bind=True)
def func_nihpo_json_file(self, in_min_age, in_max_age, in_female, in_male, in_drug_regulator, in_drugs_filter, in_countries,
		in_folder_name, in_file_name, in_first_name, in_last_name, in_email, in_country_names=None, in_provinces=None):
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
		if in_provinces:
			result = func_nihpo_subjects_creation_in_provinces(in_min_age, in_max_age, in_female, in_male, in_drug_regulator, in_drugs_filter,
				in_countries, in_file_name, in_provinces, in_task = self)
		else:
			result = func_nihpo_subjects_creation(in_min_age, in_max_age, in_female, in_male, in_drug_regulator, in_drugs_filter,
				in_countries, in_file_name, in_task = self)

		with open(current_app.config["CT_DOWNLOADS_PATH"] + \
			in_file_name + '.json', 'w') as json_file:
			json.dump(result, json_file, indent=4)


		# Change file status to created
		file = Files.query.filter_by(file_name=in_file_name, module='PHR').first()
		if file:
			file.file_status = 'Created'
			db.session.commit()
			
	except Exception as e:
		current_app.logger.info(e)

		# Remove file from DB if there is some failure
		file = Files.query.filter_by(file_name=in_file_name, module='PHR').first()
		if file:
			db.session.delete(file)
			db.session.commit()

	return {'current': 100, 'total': 100, 'status': 'File ' + '"' + in_file_name + '"' + ' ready to download!!',\
		'result': 'File created successfully'}