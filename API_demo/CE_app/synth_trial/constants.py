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
class Constants(object):
	CT_FIELDS_INDEX = ['STUDYID', 'DOMAIN', 'USUBJID', 'EPOCH', 'TAETORD', 'VISITNUM', 'VISITDY', 'SITEID', 'SEX', 'RACE', 'ETHNIC', 'AGE', 'AGEU', 'ARMCD', 'SEQ']

	# Constants for trial design (remove):
	CT_DOMAINS_TRIAL_DESIGN = ['TA', 'TD', 'TE', 'TI', 'TM', 'TS', 'TV']
	CT_DOMAINS_VISITS = ['TV']
	CT_DOMAINS_SCHEDULE_FOR_ASSESSMENTS = ['TD', 'TM']
	CT_DOMAINS_INCLUSION_EXCLUSION_SUMMARY = ['TI', 'TS']

	# (To do): Define MO, MS and OI domains.
	CT_DOMAIN_NAMES_CSV_SAS = ['AE', 'AG', 'BE', 'BS', 'CE', 'CM', 'CO', 'CP', 'CV', 'DA', 'DD', 'DM', 'DS', 'DV', 'EC', 'EG', 'EX', 'FA', 'FT', 'GF', 'HO', 'IE', 'IS', 'LB', 'MB', 'MH', 'MI', 'MK', 'ML', 'NV', 'OE', 'PC', 'PE', 'PP', 'PR', 'QS', 'RE', 'RP', 'RS', 'SC', 'SE', 'SM', 'SR', 'SS', 'SU', 'SV', 'TA', 'TD', 'TE', 'TI', 'TM', 'TR', 'TS', 'TU', 'TV', 'UR', 'VS'] # 'MO', 'MS', 'OI'
	CT_CSV_SEPARATOR = "|"