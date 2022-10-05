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
from flask import render_template
from flask import current_app
import psycopg2
import psycopg2.extras
import copy
import random
from random import randint
from collections import defaultdict
from psycopg2 import sql
from CE_app.synth_phr.synth_phr_func import func_nihpo_randomize

########### Constants ###########

error_path = 'errors/error.html'

default_query = """WITH min_max AS MATERIALIZED
	(
	  SELECT MIN(id) AS min_s, MAX(id) AS max_s, (MAX(id) - MIN(id)) AS diff_s
	  FROM <filters>
	),
	other  AS MATERIALIZED
	(
	  SELECT FLOOR(RANDOM() * (SELECT diff_s FROM min_max) + (SELECT min_s FROM min_max))::INT AS seq_val<floor_lines>
	)
	SELECT <select_parameters>
	FROM <table_name>
	WHERE id = (SELECT seq_val FROM other)
	"""

str_new_row = 'FLOOR(RANDOM() * (SELECT diff_s FROM min_max) + (SELECT min_s FROM min_max))::INT AS seq_val'
str_new_rows = ' union all SELECT <select_parameters> FROM <table_name> WHERE id = (SELECT seq_val<number_row> FROM other)'

def func_nihpo_add_filters_to_query(in_table_name, in_parameters, in_filter=None, in_number=1):
	"""
	Add filters to queries created for domains
	
	:param in_query: Original query to modify
	:type in_query: String
	:param in_table_name: Table name
	:type in_table_name: String
	:param in_parameters: List of lists with 2 elements: field name, value
	:type in_parameters: List
	:param in_filter: List of parameters to get from the table
	:type in_filter: List
	:param in_number: Number of values
	:type in_number: Int
	:returns: Query updated
	:rtype: String
	"""
	
	# Initialize variables
	conditions = ''
	parameters = ''
	new_floor_lines = ''
	new_select_lines = ''
	number_row = 0
	filter_fields_checked = []
	
	# Create conditions string
	if in_filter:
		for i in range(0, len(in_filter)):
			field = in_filter[i][0]
			value = in_filter[i][1]
			
			if i != len(in_filter) -1:
				if field in filter_fields_checked:
					conditions = conditions[:-4] + f"OR {field} = '{value}' AND "
				else:
					if field == 'atc_code':
						conditions += f"{field} LIKE '{value}%' AND "
					else:
						conditions += f"{field} = '{value}' AND "
			else:
				if field in filter_fields_checked:
					conditions = conditions[:-4] + f"OR {field} = '{field}'"
				else:
					if field == 'atc_code':
						conditions += f"{field} LIKE '{value}%'"
					else:
						conditions += f"{field} = '{value}'"
			filter_fields_checked.append(field)

		# Create filter string
		filter_to_add = f'(SELECT id FROM {in_table_name} WHERE {conditions}) a'
	else:
		filter_to_add = in_table_name
	
	# Create parameters string
	for par in in_parameters:
		parameters += f'{par}, '
	parameters = parameters[:-2]
	
	# Create new floor and select rows
	for j in range(in_number-1):
		new_floor_lines += f', {str_new_row}{j}'
		new_select_lines += str_new_rows.replace('<select_parameters>', parameters).replace('<table_name>', in_table_name).replace('<number_row>', str(j))
	
	# Replace default query with new arguments
	query = default_query.replace('<filters>', filter_to_add).replace('<table_name>', in_table_name).replace(
		'<select_parameters>', parameters).replace('<floor_lines>', new_floor_lines)
	
	# Add new lines to create more values
	query += new_select_lines
	
	query += ';'

	return query

class Domains(object):
	def condition(in_hierarchy_list=None, in_source=None, in_number=1):
		"""
		Creates random conditions
		
		:param in_hierarchy_list: Allowed values: disorder, finding, situation
		:type in_hierarchy_list: String
		:param in_source: Source where data is collected. Allowed values: snomed
		:type in_source: String
		:param in_number: Number of conditions.
		:type in_number: Integer
		:returns: Conditions in JSON format.
		:rtype: JSON dictionary
		"""
		
		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []

		parameters = ['snomed_cid', 'snomed_fsn', 'umls_cui', 'occurrence', 'usage', 'hierarchy']
		snomedct_filter = []

		if in_hierarchy_list:
			in_hierarchy_list = in_hierarchy_list.split(',')

		if in_source:
			in_source = in_source.split(',')

		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number =current_app.config["CT_NUMBER_FREE_RECORDS"]
		
		# Check inputs
		if in_hierarchy_list:
			for record in in_hierarchy_list:
				snomedct_filter.append(['hierarchy', record])

		else:
			hierarchy = random.choice(['disorder', 'finding', 'situation'])
			snomedct_filter.append(['hierarchy', hierarchy])
		
		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_snomedct', parameters, in_filter=snomedct_filter, in_number=in_number)

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:
			
			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict type
		i = 0
		for row in choose:
			final_result.append(dict(row))
			final_result[i]['Source'] = 'SNOMED_CT_CORE'
			for key in final_result[i]:
				if not final_result[i][key]:
					final_result[i][key] = ""
			i = i +1

		# Put correct names
		for data in final_result:
			data['TermID'] = data.pop('snomed_cid')
			data['TermName'] = data.pop('snomed_fsn')
			data['UMLS_CUI'] = data.pop('umls_cui')
			if data['occurrence']:
				data['Occurrence'] = int(data.pop('occurrence'))
			else:
				data['Occurrence'] = data.pop('occurrence')
			if data['usage']:
				data['Usage'] = float(data.pop('usage'))
			else:
				data['Usage'] = data.pop('usage')
			data['NIHPO_Hierarchy'] = data.pop('hierarchy')
		
		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1["NIHPO_API"]["Note_Source"] =  current_app.config['CT_CONDITION_NOTE_SOURCE']
		final_result_1["NIHPO_API"]["Node_Description"] = current_app.config['CT_CONDITION_NOTE_DESCRIPTION']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def device(in_number=1):
		"""
		Creates random devices
		
		:param in_number: Number of devices.
		:type in_number: Integer
		:returns: Devices in JSON format.
		:rtype: JSON dictionary
		"""
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		to_filter = {}
		
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		
		parameters = ['k_number', 'applicant', 'date_received', 'decision', 'decision_date','review_advise_comm', 'product_code', 'class_advise_comm', 'type', 'third_party',
			'expedited_review', 'device_name', 'state_or_sum']
		
		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_devices', parameters, in_number=in_number)
		
		# Execute query
		try:
			cur.execute(query, to_filter)
		except:
			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query, to_filter)

		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict type
		i = 0
		for row in choose:
			final_result.append(dict(row))
			for key in final_result[i]:
				if not final_result[i][key]:
					final_result[i][key] = ""
			i = i +1

		# Put correct names
		for data in final_result:
			data['KNumber'] = data.pop('k_number')
			data['Applicant'] = data.pop('applicant')
			data['DateReceived'] = data.pop('date_received')
			data['DecisionDate'] = data.pop('decision_date')
			data['Decision'] = data.pop('decision')
			data['ReviewAdviseComm'] = data.pop('review_advise_comm')
			data['ProductCode'] = data.pop('product_code')
			data['ClassAdviseComm'] = data.pop('class_advise_comm')
			data['Type'] = data.pop('type')
			data['ThirdParty'] = data.pop('third_party')
			data['ExpeditedReview'] = data.pop('expedited_review')
			data['DeviceName'] = data.pop('device_name')
			data['StateOrSumm'] = data.pop('state_or_sum')
		
		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_DEVICE_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def drug(in_active_ingredient=None, in_applno=None, in_form=None, in_regulator_code_list=None, in_inn=None, in_source=None, in_submission_type=None, in_name=None,\
	 	in_sponsor=None, in_marketing_status=None, in_help_active_ingredients=None, in_help_names=None, in_help_sponsors=None, in_list_active_ingredients=None,\
	 	in_list_drugs=None, in_list_sponsors=None, in_indication= None, in_drugs_filter=None, in_number=1):
		"""
		Creates random drugs
		
		:param in_active_ingredient: Drug active ingredient
		:type in_active_ingredient: String
		:param in_applno: Drug unique identifier
		:type in_applno: Integer
		:param in_form: Drug form of application
		:type in_form: String
		:param in_regulator_code_list: Drug regulator. Allowed values: fda, ema
		:type in_regulator_code_list: String
		:param in_inn: Drug international name
		:type in_inn: String
		:param in_source: Source where data is collected. Allowed values: snomed
		:type in_source: String
		:param in_submission_type: Drug submission type
		:type in_submission_type: String
		:param in_name: Drug market name
		:type in_name: String
		:param in_sponsor: Company that developed the drug
		:type in_sponsor: String
		:param in_marketing_status: Drug market status
		:type in_marketing_status: String
		:param in_help_active_ingredients: Starting characters of the drug ingredients
		:type in_help_active_ingredients: String
		:param in_help_names: Starting characters of the drug names
		:type in_help_names: String
		:param in_help_sponsors: Starting characters of the sponsors names
		:type in_help_sponsors: String
		:param in_list_active_ingredients: Starting characters of the drug ingredients
		:type in_list_active_ingredients: String
		:param in_list_drugs: Starting characters of the drug names
		:type in_list_drugs: String
		:param in_list_sponsors: SStarting characters of the sponsors names
		:type in_list_sponsors: String
		:param in_indication: Drug indication.
		:type in_indication: String
		:param in_drugs_filter: Drugs filter level
		:type in_drugs_filter: String
		:param in_number: Number of drugs
		:type in_number: Integer
		:returns: Drugs in JSON format
		:rtype: JSON dictionary
		"""
		
		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		drug_filter = []
		parameters_fda = ['applno', 'atc_code', 'activeingredient', 'form', 'drugname', 'marketingstatusid_nihpo', 'sponsorname',
					'submissiontype']
		parameters_ema = ['applno', 'atc_code', 'active_ingredient', 'drug_name', 'indication', 'marketing_status', 'medicine_name',
					'sponsor_name']
		parameters_spain= ['active_ingredient', 'atc_code', 'drug_name', 'drug_name', 'marketing_status']
	
		# Handle inputs
		if in_inn:
			in_inn = in_inn.upper().replace('"', '')

		if in_source:
			in_source = in_source.upper().replace('"', '')
			in_source = in_source.split(',')

		if in_regulator_code_list:
			in_regulator_code_list = in_regulator_code_list.lower().replace('"', '')
			in_regulator_code_list = in_regulator_code_list.split(',')
		else:	   
			return "A regulator code list is necessary."

		# Set the limit of number of records that can be returned at the same call with a free account:
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)

		# Filters for the fda regulatory agency records:
		if 'us_fda' in in_regulator_code_list:

			# Define query to select unique values in the fields requested by help endpoint:
			if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type or in_drugs_filter):
				if in_drugs_filter:
					drug_filter.append(['atc_code', in_drugs_filter])

				if in_active_ingredient:
					in_active_ingredient = in_active_ingredient.upper().replace('"', '')
					drug_filter.append(['activeingredient', in_active_ingredient])

				if in_applno: 
					drug_filter.append(['applno', in_applno])

				if in_form:
					in_form = in_form.upper().replace('"', '')
					drug_filter.append(['form', in_form])

				if in_name:
					in_name = in_name.upper().replace('"', '')
					drug_filter.append(['drugname', in_name])
					
				if in_marketing_status:
					in_marketing_status = in_marketing_status.upper().replace('"', '')
					if in_marketing_status == 'PRE':
						drug_filter.append(['marketingstatusid_nihpo', 'Prescription'])
					elif in_marketing_status == 'OTC':
						drug_filter.append(['marketingstatusid_nihpo', 'Over-the-counter'])
					elif in_marketing_status == 'DISC':
						drug_filter.append(['marketingstatusid_nihpo', 'Discontinued'])
					elif in_marketing_status == 'NONE':
						drug_filter.append(['marketingstatusid_nihpo', 'None (Tentative Approval)'])

				if in_sponsor:
					in_sponsor = in_sponsor.upper().replace('"', '')
					drug_filter.append(['sponsorname', in_sponsor])

				if in_submission_type:
					in_submission_type = in_submission_type.upper().replace('"', '')
					drug_filter.append(['submissiontype', in_submission_type])
			
			# Help queries
			# if in_help_active_ingredients:
			# 	in_help_active_ingredients = in_help_active_ingredients.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT activeingredient" + query_help_final
				
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND activeingredient LIKE %(in_help_active_ingredients)s'
			# 	else:
			# 		query_help_final += ' WHERE activeingredient LIKE %(in_help_active_ingredients)s'
				
			# 	to_filter_help['in_help_active_ingredients'] = in_help_active_ingredients + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	in_list_active_ingredients = cur.fetchall()
				
			# 	for row in in_list_active_ingredients:
			# 		final_result.append(dict(row))
			# 	for data in final_result:
			# 		data['active_ingredients'] = data.pop('activeingredient')
				
			# 	res = defaultdict(list) 
				
			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['active_ingredients'] = sorted(dict(res)['active_ingredients'])
			# 	except:
			# 		pass
				
			# 	final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# elif in_help_names:
			# 	in_help_names = in_help_names.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT drugname" + query_help_final

			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND drugname LIKE %(in_help_names)s'
			# 	else:
			# 		query_help_final += ' WHERE drugname LIKE %(in_help_names)s'
				
			# 	to_filter_help['in_help_names'] = in_help_names + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_HN = cur.fetchall()
				
			# 	for row in list_HN:
			# 		final_result.append(dict(row))
				
			# 	for data in final_result:
			# 		data['drug_name'] = data.pop('drugname')
				
			# 	res = defaultdict(list) 
				
			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['drug_name'] = sorted(dict(res)['drug_name'])
			# 	except:
			# 		pass
				
			# 	final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# elif in_help_sponsors:
			# 	in_help_sponsors = in_help_sponsors.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT sponsorname" + query_help_final
				
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND sponsorname LIKE %(in_help_sponsors)s'
			# 	else:
			# 		query_help_final += ' WHERE sponsorname LIKE %(in_help_sponsors)s'
				
			# 	to_filter_help['in_help_sponsors'] = in_help_sponsors + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	in_list_sponsors = cur.fetchall()
				
			# 	for row in in_list_sponsors:
			# 		final_result.append(dict(row))
				
			# 	for data in final_result:
			# 		data['sponsor_name'] = data.pop('sponsorname')
				
			# 	res = defaultdict(list) 
				
			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['sponsor_name'] = sorted(dict(res)['sponsor_name'])
			# 	except:
			# 		return render_template(error_path)
				
			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# elif in_list_active_ingredients:
			# 	in_list_active_ingredients = in_list_active_ingredients.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT activeingredient" + query_help_final

			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND activeingredient LIKE %(in_list_active_ingredients)s'
			# 	else:
			# 		query_help_final += ' WHERE activeingredient LIKE %(in_list_active_ingredients)s'
				
			# 	to_filter_help['in_list_active_ingredients'] = in_list_active_ingredients + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_AI = cur.fetchall()
				
			# 	for row in list_AI:
			# 		final_result.append(dict(row))
				
			# 	for data in final_result:
			# 		data['active_ingredients'] = data.pop('activeingredient')
				
			# 	res = defaultdict(list) 
				
			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['active_ingredients'] = sorted(dict(res)['active_ingredients'])
			# 	except:
			# 		pass
				
			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# elif in_list_drugs:
			# 	in_list_drugs = in_list_drugs.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT drugname" + query_help_final
				
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND drugname LIKE %(in_list_drugs)s'
			# 	else:
			# 		query_help_final += ' WHERE drugname LIKE %(in_list_drugs)s'
				
			# 	to_filter_help['in_list_drugs'] = in_list_drugs + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_N = cur.fetchall()
				
			# 	for row in list_N:
			# 		final_result.append(dict(row))
			# 	for data in final_result:
			# 		data['drug_name'] = data.pop('drugname')
				
			# 	res = defaultdict(list) 
				
			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['drug_name'] = sorted(dict(res)['drug_name'])
			# 	except:
			# 		pass
				
			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# elif in_list_sponsors:
			# 	in_list_sponsors = in_list_sponsors.upper().replace('"', '')
			# 	query_help_final = "SELECT DISTINCT sponsorname" + query_help_final
				
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type):
			# 		query_help_final += ' AND sponsorname LIKE %(in_list_sponsors)s'
			# 	else:
			# 		query_help_final += ' WHERE sponsorname LIKE %(in_list_sponsors)s'
				
			# 	to_filter_help['in_list_sponsors'] = in_list_sponsors + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_S = cur.fetchall()
				
			# 	for row in list_S:
			# 		final_result.append(dict(row))
				
			# 	for data in final_result:
			# 		data['sponsor_name'] = data.pop('sponsorname')
				
			# 	res = defaultdict(list) 

			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])
				
			# 	try:
			# 		res['sponsor_name'] = sorted(dict(res)['sponsor_name'])
			# 	except:
			# 		pass
				
			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# Produce query
			query = func_nihpo_add_filters_to_query('nihpo_drugs_fda', parameters_fda, in_filter=drug_filter, in_number=in_number)

			# Execute query
			try:
				cur.execute(query)
			except Exception as e:
			
				if current_app.config['CT_LOGS']:
					current_app.logger.info(e)
					
				con = current_app.config['CT_POSTGRESQL_CON']
				con.close()
				con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
					user = current_app.config["CT_DATABASE_USER"],
					password = current_app.config["CT_DATABASE_PASSWORD"],
					host = current_app.config["CT_DATABASE_HOST"],
					port = current_app.config["CT_DATABASE_PORT"])
				cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
				current_app.config['CT_POSTGRESQL_CUR'] = cur
				cur.execute(query)
			
			# Get rows
			chosen = cur.fetchall()
			
			# Parse rows into dict format
			try:
				i = 0
				for row in chosen:
					final_result.append(dict(row))
					final_result[i]['inn'] = 'NA'
					final_result[i]['regulator'] = 'us_fda'
					final_result[i]['source'] = 'drugsatfda'
					final_result[i]['indication'] = 'NA'
					if not final_result[i]['submissiontype']:
						final_result[i]['submissiontype'] = ""
					i = i + 1

				if len(final_result) != 0:
					while (len(final_result) < in_number):
						j = randint(0,len(chosen)-1)
						final_result.append(dict(chosen[j]))
						final_result[i]['inn'] = 'NA'
						final_result[i]['regulator'] = 'us_fda'
						final_result[i]['source'] = 'drugsatfda'
						final_result[i]['indication'] = 'NA'
			except:
				pass

			# Put correct names
			for data in final_result:
				data['active_ingredient'] = data.pop('activeingredient')
				data['applno'] = data.pop('applno')
				data['atc_code'] = data.pop('atc_code')
				data['form'] = data.pop('form')
				data['drug_name'] = data.pop('drugname')
				data['marketing_status'] = data.pop('marketingstatusid_nihpo')
				data['sponsor_name'] = data.pop('sponsorname')
				data['submission_type'] = data.pop('submissiontype')

			# Produce JSON format
			final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_DRUG_NOTE_SOURCE_FDA']
			final_result_1['NIHPO_API']['Results'] = final_result
			return final_result_1

		elif 'eu_ema' in in_regulator_code_list:
			# Define query to select unique values in the fields requested by help endpoint:
			if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type or in_drugs_filter):

				if in_applno: 
					drug_filter.append(['applno', in_applno])

				if in_active_ingredient:
					in_active_ingredient = in_active_ingredient.upper().replace('"', '')
					drug_filter.append(['active_ingredient', in_active_ingredient])

				if in_drugs_filter:
					drug_filter.append(['atc_code', in_drugs_filter])

				if in_name:
					in_name = in_name.upper().replace('"', '')
					drug_filter.append(['medicine_name', in_name])

				if in_marketing_status:
					in_marketing_status = in_marketing_status.upper().replace('"', '')
					drug_filter.append(['marketing_status', in_marketing_status])

				if in_sponsor:
					in_sponsor = in_sponsor.upper().replace('"', '')
					drug_filter.append(['sponsor_name', in_sponsor])
			
			# Help queries
			# if in_help_active_ingredients:
			# 	query_help_final = 'SELECT DISTINCT active_ingredient ' + query_help_final
			# 	in_help_active_ingredients = in_help_active_ingredients.upper().replace('"', '')

			# 	# if (in_help_active_ingredients != 'ALL'):
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type or in_drugs_filter):
			# 		query_help_final += ' AND active_ingredient LIKE %(in_help_active_ingredients)s'
			# 	else:
			# 		query_help_final += ' WHERE active_ingredient LIKE %(in_help_active_ingredients)s'
			# 	to_filter_help['in_help_active_ingredients'] = in_help_active_ingredients + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_HAI = cur.fetchall()

			# 	for row in list_HAI:
			# 		final_result.append(dict(row))

			# 	res = defaultdict(list) 

			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])

			# 	try:
			# 		res['active_ingredients'] = sorted(dict(res)['Active_Ingredients'])
			# 	except:
			# 		pass

			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# if in_help_names:
			# 	in_help_names = in_help_names.upper().replace('"', '')
			# 	query_help_final = 'SELECT DISTINCT medicine_name ' + query_help_final
				
			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type or in_drugs_filter):
			# 		query_help_final += ' AND medicine_name LIKE %(in_help_names)s'
			# 	else:
			# 		query_help_final += ' WHERE medicine_name LIKE %(in_help_names)s'

			# 	to_filter_help['in_help_names'] = in_help_names + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_HN = cur.fetchall()

			# 	for row in list_HN:
			# 		final_result.append(dict(row))

			# 	res = defaultdict(list) 

			# 	for sub in final_result: 
			# 		for key in sub: 
			# 			res[key].append(sub[key])

			# 	try:
			# 		res['medicine_name'] = sorted(dict(res)['medicine_name'])
			# 	except:
			# 		pass

			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# if in_help_sponsors:
			# 	in_help_sponsors = in_help_sponsors.upper().replace('"', '')
			# 	query_help_final = 'SELECT DISTINCT sponsor_name ' + query_help_final

			# 	if (in_active_ingredient or in_applno or in_form or in_name or in_marketing_status or in_sponsor or in_submission_type or in_drugs_filter):
			# 		query_help_final += ' AND sponsor_name LIKE %(in_help_sponsors)s'
			# 	else:
			# 		query_help_final += ' WHERE sponsor_name LIKE %(in_help_sponsors)s'

			# 	to_filter_help['in_help_sponsors'] = in_help_sponsors + '%'
			# 	cur.execute(query_help_final, to_filter_help)
			# 	list_HS = cur.fetchall()

			# 	for row in list_HS:
			# 		final_result.append(dict(row))

			# 	res = defaultdict(list) 

			# 	for sub in final_result: 
			# 		for key in sub: 
	 		#  			res[key].append(sub[key])
						  
			# 	try:
			# 		res['sponsor_name'] = sorted(dict(res)['sponsor_name'])
			# 	except:
			# 		pass

			# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			# 	final_result_1['NIHPO_API']['Results'] = res
			# 	return final_result_1

			# Produce query
			query = func_nihpo_add_filters_to_query('nihpo_drugs_ema', parameters_ema, in_filter=drug_filter, in_number=in_number)

			# Execute query
			try:
				cur.execute(query)
			except Exception as e:
				
				if current_app.config['CT_LOGS']:
					current_app.logger.info(e)
					
				con = current_app.config['CT_POSTGRESQL_CON']
				con.close()
				con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
					user = current_app.config["CT_DATABASE_USER"],
					password = current_app.config["CT_DATABASE_PASSWORD"],
					host = current_app.config["CT_DATABASE_HOST"],
					port = current_app.config["CT_DATABASE_PORT"])
				cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
				current_app.config['CT_POSTGRESQL_CUR'] = cur
				cur.execute(query)
			
			# Get rows
			chosen = cur.fetchall()
			
			# Parse rows into dict format
			try:
				i = 0
				for row in chosen:
					final_result.append(dict(row))
					final_result[i]['regulator'] = 'eu_ema'
					final_result[i]['source'] = 'ema'
					final_result[i]['submission_type'] = 'NA'
					final_result[i]['form'] = 'NA'
					i += 1

				while (len(final_result) < in_number):
					j = randint(0,len(chosen)-1)
					final_result.append(dict(chosen[j]))
					final_result[len(final_result)-1]['regulator'] = 'eu_ema'
					final_result[len(final_result)-1]['source'] = 'ema'
					final_result[len(final_result)-1]['submission_type'] = 'NA'
					final_result[len(final_result)-1]['form'] = 'NA'
			except:
				pass
			
			# Put correct names
			for data in final_result:
				data['inn'] = data.pop('medicine_name')

			# Produce JSON format
			final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_DRUG_NOTE_SOURCE_EMA']
			final_result_1['NIHPO_API']['Results'] = final_result

			return final_result_1

		elif 'spain' in in_regulator_code_list:
			# Define query to select unique values in the fields requested by help endpoint:
			if (in_active_ingredient or in_name or in_marketing_status or in_drugs_filter):

				if in_active_ingredient:
					in_active_ingredient = in_active_ingredient.upper().replace('"', '')
					drug_filter.append(['active_ingredient', in_active_ingredient])

				if in_drugs_filter:
					drug_filter.append(['atc_code', in_drugs_filter])

				if in_name:
					in_name = in_name.upper().upper().replace('"', '')
					drug_filter.append(['medicine_name', in_name])

				if in_marketing_status:
					in_marketing_status = in_marketing_status.upper().replace('"', '')
					drug_filter.append(['marketing_status', in_marketing_status])
		
			# Produce query
			query = func_nihpo_add_filters_to_query('nihpo_drugs_spain', parameters_spain, in_filter=drug_filter, in_number=in_number)

			# Execute query
			try:
				cur.execute(query)
			except Exception as e:
				
				if current_app.config['CT_LOGS']:
						current_app.logger.info(e)
						
				con = current_app.config['CT_POSTGRESQL_CON']
				con.close()
				con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
					user = current_app.config["CT_DATABASE_USER"],
					password = current_app.config["CT_DATABASE_PASSWORD"],
					host = current_app.config["CT_DATABASE_HOST"],
					port = current_app.config["CT_DATABASE_PORT"])
				cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
				current_app.config['CT_POSTGRESQL_CUR'] = cur
				cur.execute(query)
			
			# Get rows
			chosen = cur.fetchall()

			# Parse rows into dict format
			try:
				i = 0
				for row in chosen:
					final_result.append(dict(row))
					final_result[i]['regulator'] = 'aemps'
					final_result[i]['source'] = 'aemps'
					final_result[i]['submission_type'] = 'NA'
					final_result[i]['form'] = 'NA'
					final_result[i]['inn'] = 'NA'
					final_result[i]['applno'] = 'NA'
					final_result[i]['indication'] = 'NA'
					final_result[i]['sponsor_name'] = 'NA'
					i += 1

				while (len(final_result) < in_number):
					j = randint(0,len(chosen)-1)
					final_result.append(dict(chosen[j]))
					final_result[len(final_result)-1]['regulator'] = 'aemps'
					final_result[len(final_result)-1]['source'] = 'aemps'
					final_result[len(final_result)-1]['submission_type'] = 'NA'
					final_result[len(final_result)-1]['form'] = 'NA'
					final_result[i]['inn'] = 'NA'
					final_result[i]['applno'] = 'NA'
					final_result[i]['sponsor_name'] = 'NA'
			except:
				pass
			
			# Produce JSON format
			final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
			final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_DRUG_NOTE_SOURCE_EMA']
			final_result_1['NIHPO_API']['Results'] = final_result
			return final_result_1


	def geography(in_country_code_iso=None, in_location_state=None, in_location=None, in_help_country=None, in_help_countries=None,\
		in_states=None, in_locations=None, in_randomize=1, in_number=1):
		"""
		Creates random geography locations
		
		:param in_country_code_iso: Name of countries in ISO 3166 alpha-2, separated by commas.
		:type in_country_code_iso: String
		:param in_location_state: Name of province/state in ISO 3166 alpha-2, separated by commas.
		:type in_location_state: String
		:param in_help_country: Name of a country in ISO 3166 alpha-2.
		:type in_help_country: String
		:param in_randomize: Decide if latitud/longitud is randomized or fixed. Allowable values: 1 randomize, 0 not randomize (1 by default)
		:type in_randomize: Integer
		:param in_number: Number of geography locations.
		:type in_number: Intger
		:returns: Geography locations in JSON format.
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		parameters = ['country_name', 'location_state_iso', 'location_state', 'location_name', 'location_display',
			'location_lat', 'location_long']
		geog_filter = []
		final_result = []

		# Get values from input parameters
		if in_country_code_iso:
			in_country_code_iso = in_country_code_iso.upper()
			in_country_code_iso = in_country_code_iso.split(',')
		if in_location_state:
			in_location_state = in_location_state.upper()
			in_location_state = in_location_state.split(',')
		if in_help_country:
			in_help_country = in_help_country.upper()
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)
		

		if in_country_code_iso:
			for country in in_country_code_iso:
				geog_filter.append(['country_code_iso', country])
		
		query = func_nihpo_add_filters_to_query('nihpo_locations', parameters, in_filter=geog_filter, in_number=in_number)

		# if in_help_country:
		# 	query += ' country_code_iso=%(in_help_country)s AND'
		# 	to_filter['in_help_country'] = in_help_country
		# if in_location_state:
		# 	query += ' ('
		# 	for state in in_location_state:
		# 		query += 'location_state_iso= %(state)s OR '
		# 		to_filter['state'] = state
		# 	query = query[:-4] + ') AND'
		# if in_help_countries:
		# 	query = "SELECT DISTINCT country_code_iso, country_name FROM nihpo_states ORDER BY country_name"
		# 	results = cur.execute(query, to_filter)
		# 	choose_all = cur.fetchall()
		# 	for row in choose_all:
		# 		final_result.append(dict(row))
		# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# 	final_result_1['NIHPO_API']['Results'] = final_result
		# 	return final_result_1

		# if in_states:
		# 	query = "SELECT state_code, state_name FROM nihpo_states WHERE country_code_iso= %(in_help_country)s"
		# 	to_filter['in_help_country'] = in_help_country
		# 	results = cur.execute(query, to_filter)
		# 	choose_all = cur.fetchall()
		# 	for row in choose_all:
		# 		final_result.append(dict(row))
		# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# 	final_result_1['NIHPO_API']['Results'] = final_result
		# 	return final_result_1
		# if in_locations:
		# 	query = "SELECT DISTINCT location_name FROM nihpo_locations WHERE country_code_iso= %(in_help_country)s AND location_state_iso = %(location_state)s ;"
		# 	to_filter['in_help_country'] = in_help_country
		# 	to_filter['location_state'] = in_location_state[0]
		# 	results = cur.execute(query, to_filter)
		# 	list_LN = cur.fetchall()
		# 	for row in list_LN:
		# 		final_result.append(dict(row))
		# 	for data in final_result:
		# 		data['Location_Names'] = data.pop('location_name')
		# 	res = defaultdict(list)
		# 	for sub in final_result:
		# 		for key in sub:
		# 			res[key].append(sub[key])
		# 	try:
		# 		res['Location_Names'] = sorted(dict(res)['Location_Names'])
		# 	except:
		# 		pass
		# 	final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# 	final_result_1['NIHPO_API']['Results'] = res
		# 	return final_result_1

		try:
			cur.execute(query)
		except:
			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)

		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict format
		i = 0
		for row in choose:
			final_result.append(dict(row))
			if in_randomize == '1':
				final_result[i]['Randomized'] = 'Y'
			elif in_randomize == '0':
				final_result[i]['Randomized'] = 'N'
			i = i + 1

		# Randomize location
		if in_randomize == 1:
			func_nihpo_randomize(final_result)

		# Put correct names
		for data in final_result:
			data['Country_Name'] = data.pop('country_name')
			data['State_Code'] = data.pop('location_state_iso')
			data['State_Name'] = data.pop('location_state')
			data['Place_Name'] = data.pop('location_name')
			data['Display'] = data.pop('location_display')
			data['Latitude'] = float(data.pop('location_lat'))
			data['Longitude'] = float(data.pop('location_long'))

		# Produce JSON format
		final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def lab_result(in_cdisc_common_tests=None, in_class_type=None, in_loinc_num=None, in_panel_type=None, in_rank=None, in_record_type=None, in_source=None,\
		in_status=None, in_atc_code_filter=None, in_number=1):
		"""
		Creates random laboratory results
		
		:param in_cdisc_common_tests: Common tests
		:type in_cdisc_common_tests: String
		:param in_class_type: Class of laboratory result
		:type in_class_type: String
		:param in_loinc_num: Unique identifier of the laboratory result
		:type in_loinc_num: String
		:param in_panel_type: Panel type of laboratory results
		:type in_panel_type: String
		:param in_rank: Rank of laboratory results
		:type in_rank: String
		:param in_record_type: Record type of laboratory results
		:type in_record_type: String
		:param in_source: Source where data is collected. Allowed values: loinc
		:type in_source: String
		:param in_status: Current status of laboratory results
		:type in_status: String
		:param in_atc_code_filter: ATC code filter
		:type in_atc_code_filter: String
		:param in_number: Number of records
		:type in_number: Intger
		:returns: Laboratory results in JSON format
		:rtype: JSON dictionary
		"""
		
		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		lab_filter = []
		parameters = ['*']
		
		# Set number of records
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)
		
		if in_atc_code_filter:
			lab_filter.append(['atc_code', in_atc_code_filter])
		
		# # Check filters
		# if in_cdisc_common_tests:
		# 	in_cdisc_common_tests = in_cdisc_common_tests.upper().replace('"', '')
		# 	query += ' cdisc_common_tests = %(in_cdisc_common_tests)s AND'
		# 	to_filter['in_cdisc_common_tests'] = in_cdisc_common_tests
		

		# if in_class_type:
		# 	in_class_type = in_class_type.replace('"', '')
		# 	in_class_type = in_class_type.split(',')

		# 	if '1' in in_class_type:
		# 		query += ' class_type = 1 OR'

		# 	if '2' in in_class_type:
		# 		query += ' class_type = 2 OR'

		# 	if '3' in in_class_type:
		# 		query += ' class_type = 3 OR'

		# 	if '4' in in_class_type:
		# 		query += ' class_type = 4 OR'
		# 	query = query[:-2] + "AND"

		# if in_loinc_num:
		# 	in_loinc_num = in_loinc_num.replace('"', '')
		# 	query += ' loinc_num = %(in_loinc_num)s AND'
		# 	to_filter['in_loinc_num'] = in_loinc_num

		# if in_panel_type:
		# 	in_panel_type = in_panel_type.replace('"', '').lower()
		# 	in_panel_type = in_panel_type.split(',')

		# 	if 'convenience' in in_panel_type:
		# 		query += ' panel_type = %(Convenience_group)s OR'
		# 		to_filter['Convenience_group'] = 'Convenience group'

		# 	if 'organizer' in in_panel_type:
		# 		query += ' panel_type = %(Organizer)s OR'
		# 		to_filter['Organizer'] = 'Organizer'

		# 	if 'panel' in in_panel_type:
		# 		query += ' panel_type = %(Panel)s OR'
		# 		to_filter['Panel'] = 'Panel'
		# 	query = query[:-2] + 'AND'

		# if in_rank:
		# 	in_rank = in_rank.lower().replace('"', '')
		# 	in_rank = in_rank.split(',')

		# 	if 'order' in in_rank:
		# 		query += ' common_order_rank != 0 OR'

		# 	if 'si_test' in in_rank:
		# 		query += ' common_order_rank != 0 OR'

		# 	if 'test' in in_rank:
		# 		query += ' common_order_rank != 0 OR'

		# 	query = query[:-2] + 'AND'

		# if in_source:
		# 	in_source = in_source.lower().replace('"', '')

		# if in_status:
		# 	in_status = in_status.upper().replace('"', '').upper()
		# 	in_status = in_status.split(',')

		# 	i = 0
		# 	for term in in_status:
		# 		new_status= '%(term)s'.replace('term', 'term_%s' % i)
		# 		query += ' status = %(term)s OR'.replace('%(term)s', new_status)
		# 		to_filter['term_%s' % i] = term
		# 		i += 1

		# 	query = query[:-2] + 'AND'

		# else:
		# 	in_status = 'ACTIVE'
		# 	query += ' status = %(status)s AND'
		# 	to_filter['status'] = 'ACTIVE'

		# if (in_cdisc_common_tests or in_class_type or in_loinc_num or in_panel_type or in_rank or in_record_type or in_status):
		# 	query = query[:-3] + "ORDER BY RANDOM() LIMIT %(in_number)s;"
		
		# else:
		# 	query = query[:-5] + "ORDER BY RANDOM() LIMIT %(in_number)s;"
		
		query = func_nihpo_add_filters_to_query('nihpo_loinc', parameters, in_filter=lab_filter, in_number=in_number)

		try:
			cur.execute(query)
		except:
			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		chosen = cur.fetchall()
		
		# Parse rows into dict format
		i = 0
		for row in chosen:
			final_result.append(dict(row))
			final_result[i]['Source'] = "loinc"

			# Remove 'id' field
			final_result[i].pop('id', None)

			# Fill Null values with an empty string
			for key in final_result[i]:
				if not final_result[i][key]:
					final_result[i][key] = ""
			i = i + 1
		
		# Put correct names
		for data in final_result:
			if data['class_type']:
				data['class_type'] = int(data['class_type'])
			if data['common_test_rank']:
				data['common_test_rank'] = int(data['common_test_rank'])
			if data['common_si_test_rank']:
				data['common_si_test_rank'] = int(data['common_si_test_rank'])
			if data['common_order_rank']:
				data['common_order_rank'] = int(data['common_order_rank'])
			

		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_LAB_RESULT_NOTE_SOURCE']
		final_result_1['NIHPO_API']["Note_Copyright"] = current_app.config['CT_LAB_RESULT_NOTE_COPYRIGHT']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def procedure(in_hierarchy_list=None, in_source=None, in_number=1):
		"""
		Creates random procedures
		
		:param in_hierarchy_list: Type of procedure. Allowable values: procedure, regime/therapy
 		:type in_hierarchy_list: String
		:param in_source: Source where data is collected. Allowed values: snomed
		:type in_source: String
		:param in_number: Number of records.
		:type in_number: Intger
		:returns: Procedures in JSON format.
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []

		parameters = ['snomed_cid', 'snomed_fsn', 'umls_cui', 'occurrence', 'usage', 'hierarchy']
		snomedct_filter = []
		
		if in_hierarchy_list:
			in_hierarchy_list = in_hierarchy_list.split(',')
		if in_source:
			in_source = in_source.split(',')
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]

		if in_hierarchy_list:
			for record in in_hierarchy_list:
				snomedct_filter.append(['hierarchy', record])
		else:
			snomedct_filter.append(['hierarchy', 'procedure'])
			snomedct_filter.append(['hierarchy', 'regime/therapy'])

		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_snomedct', parameters, in_filter=snomedct_filter, in_number=in_number)
		
		# Execute query
		try:
			cur.execute(query)
		except Exception as e:
			
			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict type
		i = 0
		for row in choose:
			final_result.append(dict(row))
			final_result[i]['Source'] = 'SNOMED_CT_CORE'
			for key in final_result[i]:
				if not final_result[i][key]:
					final_result[i][key] = ""
			i = i +1

		# Put correct names
		for data in final_result:
			data['TermID'] = data.pop('snomed_cid')
			data['TermName'] = data.pop('snomed_fsn')
			data['UMLS_CUI'] = data.pop('umls_cui')
			if data['occurrence']:
				data['Occurrence'] = int(data.pop('occurrence'))
			else:
				data['Occurrence'] = data.pop('occurrence')
			if data['usage']:
				data['Usage'] = float(data.pop('usage'))
			else:
				data['Usage'] = data.pop('usage')
			data['NIHPO_Hierarchy'] = data.pop('hierarchy')
		
		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1["NIHPO_API"]["Note_Source"] =  current_app.config['CT_PROCEDURE_NOTE_SOURCE']
		final_result_1["NIHPO_API"]["Node_Description"] = current_app.config['CT_PROCEDURE_NOTE_DESCRIPTION']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def provider(in_state=None, in_city=None, in_npi=None, in_entity_type_code=None, in_number=1):
		"""
		Creates random providers
		
		:param in_state: State where the provider is placed, in ISO 3166 alpha-2, separated by commas.
 		:type in_state: String
		:param in_city: City where the provider is placed.
		:type in_city: String
		:param in_npi: Provider unique identifier
		:type in_npi: Integer
		:param in_entity_type_code: Type of provider. Allowable values: 1 for a single person, 2 for organizations
		:type in_entity_type_code: Integer
		:param in_number: Number of records.
		:type in_number: Intger
		:returns: Providers in JSON format.
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		provider_filter = []
		parameters = ['npi', 'entity_type_code', 'auth_off_tel_number', 'pbma_city_name', 'pbma_country_code', 'pbma_fax_number', 'pbma_postal_code', 'pbma_state_name', 'pbma_telephone_number', 'pbpla_city_name',
			'pbpla_country_code', 'pbpla_fax_number', 'pbpla_postal_code', 'pbpla_state_name', 'pbpla_telephone_number', 'is_sole_proprietor', 'provider_gender_code', 'npi_deactivation_reason_code', 'npi_deactivation_date',
			'npi_reactivation_date', 'nihpo_api_taxonomy_1', 'nihpo_api_taxonomy_2', 'nihpo_api_taxonomy_3', 'nihpo_api_taxonomy_4', 'nihpo_api_taxonomy_5', 'nihpo_api_taxonomy_6', 'nihpo_api_taxonomy_7', 'nihpo_api_taxonomy_8',
			'nihpo_api_taxonomy_9', 'nihpo_api_taxonomy_10', 'nihpo_api_taxonomy_11', 'nihpo_api_taxonomy_12', 'nihpo_api_taxonomy_13', 'nihpo_api_taxonomy_14', 'nihpo_api_taxonomy_15', 'ao_last_name', 'ao_first_name',
			'ao_middle_name', 'ao_tittle_or_position', 'ao_telephone_number', 'organization_name_legal_name', 'last_name_legal_name', 'first_name', 'middle_name', 'name_prefix_text', 'name_suffix_text', 'credential_text',
			'other_last_name', 'other_first_name', 'other_middle_name', 'other_name_prefix_text', 'other_name_suffix_text', 'other_credential_text', 'other_last_name_type_code', 'other_organization_name',
			'other_organization_name_type_code']
		
		# Get correct number of values
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)

		# Apply input conditions
		if in_npi:
			provider_filter.append(['npi', in_npi])

		if in_entity_type_code:
			provider_filter.append(['entity_type_code', in_entity_type_code])

			if in_state:
				in_state = in_state.upper().replace('"', '')
				provider_filter.append(['pbma_state_name', in_state])

			if in_city:
				in_city = in_city.upper().replace('"', '')
				provider_filter.append(['pbma_city_name', in_city])

		else:
			return render_template(error_path)
		'''
		if help_states:
			query = "SELECT state_code, state_name FROM nihpo_states WHERE country_code_iso= 'US' ORDER BY state_code ASC;"
			results = cur.execute(query)
			choose_all = cur.fetchall()
			for row in choose_all:
				final_result.append(dict(row))
			return final_result
		if help_cities:
			query = """SELECT DISTINCT "Provider Business Mailing Address City Name" FROM hhs_cms_npi_npidata_pfile WHERE "Provider Business Mailing Address State Name" = '%(in_state)s';"""
			to_filter['in_state'] = in_state
			results = cur.execute(query)
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
			final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_PROVIDER_NOTE_SOURCE']
			return final_result_1'''

		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_providers', parameters, in_filter=provider_filter, in_number=in_number)

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict format
		for row in choose:
			final_result.append(dict(row))

		# Fill empty values
		j = 0
		for i in final_result:
			for key in i:
				if not i[key]:
					final_result[j][key] = ""
		
		# Put correct names
		for data in final_result:
			if data['entity_type_code']:
				data['entity_type_code'] = int(data.pop('entity_type_code'))

		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_PROVIDER_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def vital(in_age=None, in_number=1):
		"""
		Creates random vital signs
		
		:param in_age: Age of the subject.
 		:type in_age: Integer
		:param in_number: Number of records.
		:type in_number: Integer
		:returns: Vital signs in JSON format.
		:rtype: JSON dictionary
		"""
		final_result = []
		
		if in_number:
			in_number = int(in_number)
		if not in_number:
			in_number = 1
		if int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)
		
		if in_age==None:
			return render_template(error_path)
		
		for j in range(0, in_number):
			#(To do): Put rules to make it works making sense (higher age, higher height and weight, at least until 18 years)
			#(To do): Use different ages for each vital record, randomizing them.
			# Temperature:
			temp_method = random.choice(current_app.config['CT_TEMPERATURE_METHOD'])
			temp_celsius = round(random.uniform(current_app.config['CT_TEMPERATURE_RANGES'][temp_method[1]][0], current_app.config['CT_TEMPERATURE_RANGES'][temp_method[1]][1]), 2)
			temp_fahrenheit = round(temp_celsius*9/5 + 32, 2)
			
			# Pulse:
			if (0<=in_age<=1):
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][1][0], current_app.config['CT_PULSE_RATE_RANGES'][1][1]), 2)
			elif (1<in_age<=6):
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][2][0], current_app.config['CT_PULSE_RATE_RANGES'][2][1]), 2)
			elif (6<in_age<=11):
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][3][0], current_app.config['CT_PULSE_RATE_RANGES'][3][1]), 2)
			elif (11<in_age<=17):
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][4][0], current_app.config['CT_PULSE_RATE_RANGES'][4][1]), 2)
			elif (18<=in_age):
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][5][0], current_app.config['CT_PULSE_RATE_RANGES'][5][1]), 2)
			else:
				pulse_rate = round(random.uniform(current_app.config['CT_PULSE_RATE_RANGES'][0][0], current_app.config['CT_PULSE_RATE_RANGES'][0][1]), 2)
			pulse_method = random.choice(current_app.config['CT_PULSE_METHOD'])
			pulse_force = random.random()*5
			if (0<=pulse_force<1):
				pulse_force_descrip = 'Absent/non-palpable'
			elif (1<=pulse_force<2):
				pulse_force_descrip = 'Weak, diinished, thready'
			elif (2<=pulse_force<3):
				pulse_force_descrip = 'Normal/strong'
			elif (3<=pulse_force):
				pulse_force_descrip = 'Full, bounding'
			
			# Respiration:
			if (0<=in_age<=1):
				respiratory_rate = random.randint(current_app.config['CT_RESPIRATORY_RATE_RANGES'][1][0], current_app.config['CT_RESPIRATORY_RATE_RANGES'][1][1])
			elif (1<in_age<=10):
				respiratory_rate = random.randint(current_app.config['CT_RESPIRATORY_RATE_RANGES'][2][0], current_app.config['CT_RESPIRATORY_RATE_RANGES'][2][1])
			elif (10<in_age<=18):
				respiratory_rate = random.randint(current_app.config['CT_RESPIRATORY_RATE_RANGES'][3][0], current_app.config['CT_RESPIRATORY_RATE_RANGES'][3][1])
			elif (18<in_age):
				respiratory_rate = random.randint(current_app.config['CT_RESPIRATORY_RATE_RANGES'][4][0], current_app.config['CT_RESPIRATORY_RATE_RANGES'][4][1])
			else:
				respiratory_rate = random.randint(current_app.config['CT_RESPIRATORY_RATE_RANGES'][0][0], current_app.config['CT_RESPIRATORY_RATE_RANGES'][0][1])

			# Oxigen saturations:
			if (0<=in_age<=18):
				oxigen_saturation = random.randint(current_app.config['CT_OXYGEN_SATURATION_RANGES'][0][0], current_app.config['CT_OXYGEN_SATURATION_RANGES'][0][1])
			elif (18<in_age<=80):
				oxigen_saturation = random.randint(current_app.config['CT_OXYGEN_SATURATION_RANGES'][1][0], current_app.config['CT_OXYGEN_SATURATION_RANGES'][1][1])
			elif (80<in_age):
				oxigen_saturation = random.randint(current_app.config['CT_OXYGEN_SATURATION_RANGES'][2][0], current_app.config['CT_OXYGEN_SATURATION_RANGES'][2][1])
			
			# Blood pressure:
			if (in_age==0):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][1][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][1][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][1][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][1][1][1])
			elif (1<=in_age<=5):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][2][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][2][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][2][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][2][1][1])
			elif (6<=in_age<=13):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][3][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][3][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][3][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][3][1][1])
			elif (14<=in_age<=18):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][4][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][4][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][4][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][4][1][1])
			elif (19<=in_age<=40):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][5][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][5][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][5][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][5][1][1])
			elif (41<=in_age<=60):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][6][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][6][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][6][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][6][1][1])
			elif (in_age>60):
				systolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][7][0][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][7][0][1])
				diastolic_pressure = random.randint(current_app.config['CT_BLOOD_PRESSURE_RANGES'][7][1][0], current_app.config['CT_BLOOD_PRESSURE_RANGES'][7][1][1])

			blood_pressure_method = random.choice(current_app.config['CT_BLOOD_PRESSURE_METHOD'])

			# Weight and height:
			height_imperial = 0
			weight_imperial = 0
			if (0<=in_age<=1):
				while (current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0] > height_imperial and height_imperial <= current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][2]):
					height_imperial = current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0] + (current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][2] - current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0]) * random.random()
				height_metric = height_imperial * 0.3048
				while (current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0] > weight_imperial and weight_imperial <= current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][2]):
					weight_imperial = current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0] + (current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][2] - current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0]) * random.random()
				weight_metric = weight_imperial * 0.45359237 
			elif (1<in_age<18):
				slope_height = (current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][1] - 1 - current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0])/(18 - 1)
				slope_weight = (current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][3] - 1 - current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0])/(18 - 1)
				height_imperial = in_number * slope_height + (current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0] - slope_height * 1) + random.random()
				height_metric = height_imperial * 0.3048
				weight_imperial = in_number * slope_weight + (current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0] - slope_weight * 1) + random.random()
				weight_metric = weight_imperial * 0.45359237
			elif (18<=in_age):
				height_imperial = current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][1]/current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0] + (current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][1] - current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][1]/current_app.config['CT_HEIGHT_LOW_HIGHT_LIMITS'][0]) * random.random()
				height_metric = height_imperial * 0.3048
				weight_imperial = current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][1]/current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0] + (current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][3] - current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][3]/current_app.config['CT_WEIGHT_LOW_HIGHT_LIMITS'][0]) * random.random()
				if (random.random() > 0.75):
					weight_imperial = weight_imperial * 2.14
				weight_metric = weight_imperial * 0.45359237
			else:
				return render_template(error_path)

			result = {
			"Temperature": {
			"Temp_Method": temp_method[0],
			"Temp_Celsius": float(temp_celsius),
			"Temp_Fahrenheit": float(temp_fahrenheit)
			},
			"Pulse": {
			"Pulse_Method": pulse_method,
			"Pulse_Rate": float(pulse_rate),
			"Pulse_Force": float(round(pulse_force,2)),
			"Pulse_Force_Description": pulse_force_descrip
			},
			"Respiration": {
			"Respiratory_Rate": float(respiratory_rate)
			},
			"Oxigen_Saturation": {
			"Oxigen_Saturation": float(oxigen_saturation)
			},
			"Blood_Pressure": {
			"Systolic_Pressure": float(systolic_pressure),
			"Diastolic_Pressure": float(diastolic_pressure),
			"Blood_Pressure_Method": blood_pressure_method
			},
			"Weight_And_Height":{
			"Height[ft]": float(round(height_imperial,2)),
			"Height[m]": float(round(height_metric,2)),
			"Weight[lb]": float(round(weight_imperial,2)),
			"Weight[kg]": float(round(weight_metric,2))
			}
			}
			final_result.append(result)
			
		final_result_1 = final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_VITAL_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1

	def drugs_atc_top_levels():
		"""
		Retrieve a list of lists with the ATC top levels

		:returns: ATC top levels
		:rtype: List of lists
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']

		query = 'SELECT atc_code_top, atc_level_name_top FROM drug_atc_top_levels;'

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		result = cur.fetchall()

		return result
	
	def drugs_atc_second_levels(in_atc_top_level=None):
		"""
		Retrieve a list of lists with the ATC second levels

		:returns: ATC second levels
		:rtype: List of lists
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']

		query = 'SELECT atc_code, atc_level_name FROM drug_atc_second_levels;'

		if in_atc_top_level:
			query = sql.SQL("""SELECT atc_code, atc_level_name FROM drug_atc_second_levels WHERE atc_code LIKE {top_level};""").format(top_level = sql.Literal(in_atc_top_level+'%'))

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		result = cur.fetchall()
		return result
	
	def first_name(in_gender, in_number=1):
		"""
		Creates random first name

		:param in_gender: Name gender
 		:type in_gender: String
		 :param in_number: Number of records
		:type in_number: Intger
		:returns: First name JSON format
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		first_name_filter = []
		parameters = ['first_name']

		# Get correct number of values
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)
		
		# Apply input conditions
		if in_gender:
			first_name_filter.append(['gender', in_gender])

		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_first_name', parameters, in_filter=first_name_filter, in_number=in_number)

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict format
		for row in choose:
			final_result.append(dict(row))

		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_PROVIDER_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1
	
	def middle_name(in_gender, in_number=1):
		"""
		Creates random middle name

		:param in_gender: Name gender
 		:type in_gender: String
		 :param in_number: Number of records
		:type in_number: Intger
		:returns: Middle name JSON format
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		middle_name_filter = []
		parameters = ['middle_name']

		# Get correct number of values
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)
		
		# Apply input conditions
		if in_gender:
			middle_name_filter.append(['gender', in_gender])

		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_first_name', parameters, in_filter=middle_name_filter, in_number=in_number)

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict format
		for row in choose:
			final_result.append(dict(row))

		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_PROVIDER_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1
	
	def last_name(in_number=1):
		"""
		Creates random last name

		:param in_gender: Name gender
 		:type in_gender: String
		 :param in_number: Number of records
		:type in_number: Intger
		:returns: Last name JSON format
		:rtype: JSON dictionary
		"""

		# Initialize variables
		cur = current_app.config['CT_POSTGRESQL_CUR']
		final_result = []
		last_name_filter = []
		parameters = ['last_name']

		# Get correct number of values
		if not in_number:
			in_number = 1
		elif int(in_number) > current_app.config["CT_NUMBER_FREE_RECORDS"]:
			in_number = current_app.config["CT_NUMBER_FREE_RECORDS"]
		else:
			in_number = int(in_number)

		# Produce query
		query = func_nihpo_add_filters_to_query('nihpo_last_name', parameters, in_filter=None, in_number=in_number)

		# Execute query
		try:
			cur.execute(query)
		except Exception as e:

			if current_app.config['CT_LOGS']:
					current_app.logger.info(e)

			con = current_app.config['CT_POSTGRESQL_CON']
			con.close()
			con = psycopg2.connect(database = current_app.config["CT_DATABASE"],
				user = current_app.config["CT_DATABASE_USER"],
				password = current_app.config["CT_DATABASE_PASSWORD"],
				host = current_app.config["CT_DATABASE_HOST"],
				port = current_app.config["CT_DATABASE_PORT"])
			cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
			current_app.config['CT_POSTGRESQL_CUR'] = cur
			cur.execute(query)
		
		# Get rows
		choose = cur.fetchall()

		# Parse rows into dict format
		for row in choose:
			final_result.append(dict(row))

		# Produce JSON format
		final_result_1 = copy.deepcopy(current_app.config['CT_JSON_FORMAT'])
		# final_result_1['NIHPO_API']["Note_Source"] = current_app.config['CT_PROVIDER_NOTE_SOURCE']
		final_result_1['NIHPO_API']['Results'] = final_result
		return final_result_1