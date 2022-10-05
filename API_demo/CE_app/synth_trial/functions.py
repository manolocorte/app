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
import pandas as pd
import random, zipfile, sqlalchemy
from flask import current_app
from datetime import timedelta
from copy import deepcopy
import os.path
from CE_app.nihpo_functions import func_nihpo_synth_data_random_value, func_nihpo_random_date, func_nihpo_random_date_between_dates,\
    func_nihpo_synth_data_random_value_CTCAE, func_nihpo_check_code

# (TO DO): Change in_controlled_terminology for a database created with Sponsor selected values for extensible codelists
def func_nihpo_create_trial_design_domain_row(in_nihpo_cursor, in_domains_df, in_domain, in_df, in_controlled_terminology):
    """
    Creates a full row in one of the following trial design domains: TA, TE, TV, TD, TM, TI

    :param in_nihpo_cursor: Cursor to SQLite3 file
    :type in_nihpo_cursor: SQLite3 cursor
    :param in_domains_df: Pandas Data frame from CDISC_SDTM.sqlite3 file from table CDISC_SDTM_Domains
    :type in_domains_df: Data Frame
    :param in_domain: Abbreviated domain name (TA, TE, TV, TD, TM, TI)
    :type in_domain: str
    :param in_df: Current df where data is being saved
    :type in_df: Data Frame
    :returns: Single Data Frame with a new row randomly created
    :rtype: Data frame
    """
    list_fields = []
    list_values = []
    match_code = ""
    matching = False
    for variable in in_domains_df[in_domains_df['domain_name'] == in_domain].itertuples():
        value = ""
        controlled_terminology = variable[5]
        variable_name = variable[2]
        if controlled_terminology:
            if '(' in controlled_terminology:
                controlled_terminology = controlled_terminology.replace('(', '')
                controlled_terminology = controlled_terminology.replace(')', '')
                # Check if the controlled_terminology is in CDISC SDTM CT, if not, don't populate that field:
                try:
                    if matching:
                        value = func_nihpo_synth_data_random_value(in_nihpo_cursor, controlled_terminology, in_controlled_terminology, match_code, matching)
                        matching = False
                    else:
                        value = func_nihpo_synth_data_random_value(in_nihpo_cursor, controlled_terminology, in_controlled_terminology)
                        if controlled_terminology[-2:] == 'CD':
                            matching = value[2]
                            match_code = value[1]
                        else:
                            matching = False
                    list_values.append(value[0])
                except TypeError:
                    list_values.append("")
                    matching = False
                    pass
            elif in_domain == controlled_terminology:
                value = in_domain
                list_values.append(value)
            elif 'ISO' in controlled_terminology:
                value = func_nihpo_random_date('1960-01-01', 0, 5000)
                list_values.append(value)
            else:
                list_values.append("")
        else:
            list_values.append("")
        # Assign values to each field:
        list_fields.append(variable_name)
    if in_df.empty:
        in_df = pd.DataFrame([list_values], columns = list_fields) 
    else:
        in_df.loc[len(in_df)] = list_values
    
    return in_df


def func_nihpo_create_trial_random_domain_row(in_nihpo_cursor, in_rules_df, in_domains_df, in_domain, in_df, in_dates_rules_dict, in_seq_number,
        in_person, in_study_id, in_start_participation, in_end_participation, in_start_date_exposure, in_end_date_exposure, in_end_date,
        in_dead, in_controlled_terminology, in_arms_elements_visits, in_arm, in_list_date_fields, in_last_AE=False, in_visit_number=0,
        in_visit=None, in_sites=None):
    """
    Creates a full row in the corresponding domain

    :param in_nihpo_cursor: Cursor to SQLite3 file
    :type in_nihpo_cursor: SQLite3 cursor
    :param in_rules_df: Pandas Fata frame from CDISC_SDTM.sqlite3 file from table CDISC_SDTM_Domain_Rules
    :type in_rules_df: Data Frame
    :param in_domains_df: Pandas Data frame from CDISC_SDTM.sqlite3 file from table CDISC_SDTM_Domains
    :type in_domains_df: Data Frame
    :param in_domain: Abbreviated domain name
    :type in_domain: String
    :param in_df: Current df where data is being saved
    :type in_df: Data Frame
    :param in_dates_rules_dict: Pandas Fata frame from CDISC_SDTM.sqlite3 file from table CDISC_SDTM_Dates_Rules to fix dates
    :type in_dates_rules_dict: Dictionary
    :param in_seq_number: Sequential number to set a unique number for each row assigned to a single subject
    :type in_seq_number: Integer
    :param in_person: Filtered DF with all the information of one subject in one row
    :type in_person: Data Frame
    :param in_study_id: Uniquess identification of the trial design
    :type in_study_id: String
    :param in_start_participation: Date formatted as YYYY-MM-DD. First day of the subject into the trial
    :type in_start_participation: Date string
    :param in_end_participation: Date formatted as YYYY-MM-DD. Last day of the subject into the trial
    :type in_end_participation: Date string
    :param in_start_date_exposure: Date formatted as YYYY-MM-DD. Start day of exposure to any treatment
    :type in_start_date_exposure: Date string
    :param in_end_date_exposure: Date formatted as YYYY-MM-DD. Last day of exposure to any treatment
    :type in_end_date_exposure: Date string
    :param in_end_date: Date formatted as YYYY-MM-DD. Last day of the trial
    :type in_end_date: Date string
    :param in_dead: True iff subject dies during the trial
    :type in_dead: Boolean
    :param in_controlled_terminology: Allowable values for fields whre Controlled_Terms = '*'
    :type in_controlled_terminology: Dict
    :param in_arms_elements_visits: Arms, elements and visits in the trial
    :type in_arms_elements_visits: Dict
    :param in_arm: Arms, elements and visits in the trial
    :type in_arm: Dict
    :param in_last_AE: True iff this AE results in the subject death. 'Forced' to create a 'FATAL' AE.
    :type in_last_AE: Boolean or String
    :param in_visit_number: Number of the current visit
    :type in_visit_number: Integer
    :param in_visit: Number of the current visit
    :type in_visit: String
    :param in_sites: Sites chosen in each country
    :type in_sites: Dict
    :returns: Single Data Frame with a new row randomly created.
    :rtype: Data frame
    """
    list_fields = []
    list_values = []
    match_code = ""
    matching = False

    # If the last AE result in death, don't complete the rest
    if in_domain == 'AE' and in_last_AE == True:
        return in_df, in_last_AE

    # Loop over the fields in the current domain
    for variable in in_domains_df[in_domains_df['domain_name'] == in_domain].itertuples():
        value = ""
        variable_name = variable[2]
        controlled_terminology = variable[5]
        CDISC_Notes = variable[8]
        core = variable[8]

        if variable_name == 'PURPOSE':
            continue

        # Check if the controlled_terminology is between ():
        if controlled_terminology:
            if '(' in controlled_terminology:
                if controlled_terminology.count('(') == 1:
                    controlled_terminology = controlled_terminology.replace('(', '')
                    controlled_terminology = controlled_terminology.replace(')', '')
                else:
                    # (To do): Choose correct controlled_terminology
                    controlled_terminology = controlled_terminology[controlled_terminology.find("(")+1:controlled_terminology.find(")")]
                # Check if the controlled_terminology is in the CDISC_SDTM.sqlite3, if not, don't populate that field:
                try:
                    # Match each pair of fields (full name with abbreviate name):
                    if controlled_terminology[-2:] == 'CD':
                        value = func_nihpo_synth_data_random_value(in_nihpo_cursor, controlled_terminology, in_controlled_terminology, match_code, True)
                    else:
                        value = func_nihpo_synth_data_random_value(in_nihpo_cursor, controlled_terminology, in_controlled_terminology)

                        # Match each pair of fields (full name with abbreviate name):
                        match_code = value[1]

                        # Assure there is not fatal adverse event if the subject is alive after trial:
                        if variable_name == 'AEOUT' and value[0] == 'FATAL':
                            if not in_dead:
                                while value[0] == 'FATAL':
                                    value = func_nihpo_synth_data_random_value(in_nihpo_cursor, controlled_terminology, in_controlled_terminology)
                            else:
                                # If the the subject is in_dead and the current AE results in death, then this will be the last one:
                                in_last_AE = True
                        # Assure there is always a FATAL AE if the subject dies during the trial:
                        elif variable_name == 'AEOUT' and in_last_AE == 'Forced':
                            value = 'FATAL'
                            list_values.append(value)
                        # Fix field values that only can be 'Y' or Null:
                        if variable_name in current_app.config['CT_YES_OR_NULL_ONLY_FIELDS']:
                            if value[0] != 'Y':
                                value[0] = ''
                        # Fix field values that only can be 'N' or Null:
                        if variable_name in current_app.config['CT_NO_OR_NULL_ONLY_FIELDS']:
                            if value[0] != 'N':
                                value[0] = ''
                        # Fix field values that only can be 'Y' or 'N':
                        if variable_name in current_app.config['CT_NO_OR_YES_ONLY_FIELDS']:
                            if value[0] != 'Y':
                                value[0] = 'N'
                        elif variable_name == in_domain + 'STAT':
                            value[0] = random.choice(['NOT DONE', '']) 
                        else:
                            matching = False
                    if not (variable_name == 'AEOUT' and in_last_AE == 'Forced'):
                        list_values.append(value[0])
                except TypeError:
                    list_values.append("")
                    matching = False
                    pass
            # Assign domain name to the field of the domain name:
            elif in_domain == controlled_terminology:
                value = in_domain
                list_values.append(value)
            # Assign dates to fields wher controlled_terminology got the word 'ISO':
            elif 'ISO' in controlled_terminology:
                # Assign dates:
                if not 'ISO 8601 duration' in controlled_terminology:
                    # Add field to list to create indices
                    in_list_date_fields.append(variable_name)
                    if in_domain == 'DM':
                        # Starting day of participation in the trial:
                        if variable_name == 'RFSTDTC':
                            value = in_start_participation
                        # Final day of participation in the trial;
                        elif variable_name == 'RFPENDTC':
                            value = in_end_participation
                        # First day of exposure to any treatment:
                        elif variable_name == 'RFXSTDTC':
                            value = in_start_date_exposure
                        # Last day of exposure to any treatment:
                        elif variable_name == 'RFXENDTC':
                            value = in_end_date_exposure
                        # Allocation needed to avoid mistakes
                        elif variable_name == 'RFICDTC':
                            value = func_nihpo_random_date_between_dates(in_start_date_exposure, in_end_date_exposure)
                            while value == in_start_participation:
                                value = func_nihpo_random_date_between_dates(in_start_participation, in_end_date)
                        # Set if the subject dies during the trial:
                        elif variable_name == 'DTHDTC':
                            if in_dead:
                                value = in_end_participation
                        # Set random dates between start and end of subject participation in other case in the DM domain:
                        else:
                            value = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                    # Set random dates between start and end of subject participation in other case in the rest of domains:
                    else:
                        # If this is the last adverse event that results in death, assign thecorrect date of death:
                        if variable_name == 'AEENDTC' and in_last_AE:
                            value = in_end_participation
                        else:
                            # Try to choose a date between first and last day of the subject into the trial:
                            try:
                                value = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                            except AssertionError:
                                pass

                    list_values.append(value)
                # Assign durations:
                else:
                    # (To do): Set correct durations
                    value = 'P1DT2H'
                    list_values.append(value)
            # Assign random values to to not controlled by standards fields:
            elif controlled_terminology == '*':
                if in_controlled_terminology:
                    if variable_name in in_controlled_terminology:
                        if len(in_controlled_terminology[variable_name]) > 0:
                            value = random.choice(in_controlled_terminology[variable_name])
                            list_values.append(value)
                        else:
                            if core == 'Req':
                                value = '[?]'
                                list_values.append(value)
                            else:
                                value = ''
                                list_values.append(value)
                    else:
                        if core == 'Req':
                            value = '[?]'
                            list_values.append(value)
                        else:
                            value = ''
                            list_values.append(value)
                else:
                    if core == 'Req':
                        value = '[?]'
                        list_values.append(value)
                    else:
                        value = ''
                        list_values.append(value)
            else:
                value = ''
                list_values.append(value)
        else:
            value = ''
            list_values.append(value)
        # Assign values to each field:
        list_fields.append(variable_name)

        if 'date/time in ISO 8601' in CDISC_Notes:
            in_list_date_fields.append(variable_name)
    
    # Create the DF if this is the first time the function is called:
    if in_df.empty:
        in_df = pd.DataFrame([list_values], columns = list_fields) 
    else:
        # Add in_data to the DF n other case:
        in_df.loc[len(in_df)] = list_values
    #
    # FIX FIELDS BY RULES
    # 
    # Fix dates that must be before or after others:
    i = 0
    for field in in_dates_rules_dict['Dates_Before']:
        try:
            date_before = in_df.at[len(in_df)-1, field]
            date_after = in_df.at[len(in_df)-1, in_dates_rules_dict['Dates_After'][i]]
            if in_dates_rules_dict['Same_date'][i] == 1:
                in_df.at[len(in_df)-1, field] = date_after
            elif in_dates_rules_dict['Same_date'][i] == 0:
                if date_before >= date_after:
                    if field == 'RFSTDTC':
                        in_df.at[len(in_df)-1, in_dates_rules_dict['Dates_After'][i]] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                    else:
                        in_df.at[len(in_df)-1, field] = func_nihpo_random_date_between_dates(in_start_participation, date_after)
            i = i + 1
        except KeyError:
            i = i + 1
            pass
        except AssertionError:
            while in_df.at[len(in_df)-1, in_dates_rules_dict['Dates_After'][i]] == in_start_participation:
                in_df.at[len(in_df)-1, in_dates_rules_dict['Dates_After'][i]] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
            date_after = in_df.at[len(in_df)-1, in_dates_rules_dict['Dates_After'][i]]
            if date_before >= date_after:
                in_df.at[len(in_df)-1, field] = func_nihpo_random_date_between_dates(in_start_participation, date_after)
            i = i + 1
            pass
        except ValueError:
            i = i + 1
            pass
        except TypeError:
            i = i + 1
            pass

    # Set the sequetial numbers:
    if in_domain != 'DM':
        in_df.at[len(in_df)-1, in_domain + 'SEQ'] = in_seq_number

    # Set visit variables properly:
    if int(in_rules_df[in_rules_df['domain_code'] == in_domain]['per_visit']) == 1:
        in_df.at[len(in_df)-1, 'VISITNUM'] = in_visit_number
        in_df.at[len(in_df)-1, 'VISIT'] = 'Visit_' + str(in_visit_number)
        in_df.at[len(in_df)-1, 'VISITDY'] = int(in_arm['VISITS'][in_visit]['PLANNED_DAY_VISIT'])

    # Set DM variables from the subjects created:
    if in_domain == 'DM':
        in_df.at[len(in_df)-1, 'AGE'] = in_person['Age'].item()
        in_df.at[len(in_df)-1, 'AGEU'] = in_person['Age_Units'].item().upper()
        in_df.at[len(in_df)-1, 'SEX'] = in_person['Gender'].item()
        in_df.at[len(in_df)-1, 'RACE'] = in_person['Race'].item()
        for country in current_app.config['CT_COUNTRIES_DM']:
            if in_person['Country_Of_Residence'].item() == country[0]:
                in_df.at[len(in_df)-1, 'COUNTRY'] = country[1]
        in_df.at[len(in_df)-1, 'SUBJID'] = in_person['Patient_ID'].item()
        # Set random arms to each subject:
        in_df.at[len(in_df)-1, 'ARM'] = random.choice(list(in_arms_elements_visits['ARMS'].keys()))
        in_df.at[len(in_df)-1, 'ACTARM'] = in_df.at[len(in_df)-1, 'ARM']
        in_df.at[len(in_df)-1, 'ARMCD'] = in_arms_elements_visits['ARMS'][in_df.at[len(in_df)-1, 'ARM']]['ARM_CODE']
        in_df.at[len(in_df)-1, 'ACTARMCD'] = in_df.at[len(in_df)-1, 'ARMCD']
        # (To do): Set a correct siteid.
        in_df.at[len(in_df)-1, 'SITEID'] = random.choice(in_sites[in_person['Country_Of_Residence'].item()])
        # Flag that indicates if the subject died during the trial:
        if in_dead:
            in_df.at[len(in_df)-1, 'DTHFL'] = 'Y'
        else:
            in_df.at[len(in_df)-1, 'DTHFL'] = ''
        # Fix day of collection:
        if  in_df.at[len(in_df)-1, 'DMDTC']:
            if in_df.at[len(in_df)-1, 'DMDTC'] >= in_df.at[len(in_df)-1, 'RFSTDTC']:
                in_df.at[len(in_df)-1, 'DMDY'] = (in_df.at[len(in_df)-1, 'DMDTC'] - in_df.at[len(in_df)-1, 'RFSTDTC']).days + 1
            elif in_df.at[len(in_df)-1, 'DMDTC'] < in_df.at[len(in_df)-1, 'RFSTDTC']:
                in_df.at[len(in_df)-1, 'DMDY'] = (in_df.at[len(in_df)-1, 'DMDTC'] - in_df.at[len(in_df)-1, 'RFSTDTC']).days

    # Must be before variables repeated:
    # Set USUBJID variable in all the domains where USUBJID is in the domain:
    try:
        in_df.at[len(in_df)-1, 'USUBJID'] = in_person['Patient_ID'].item()
    except:
        pass
    # (To do): Set correct duration
    for a in ['DUR', 'ELTM', 'EVLINT', 'STINT', 'ENINT']:
        # If some those fields are in the domain, fill them:
        try:
            if in_df.at[len(in_df)-1, in_domain + a] or not in_df.at[len(in_df)-1, in_domain + a]:
                in_df.at[len(in_df)-1, in_domain + a] = 'P1Y2M10DT2H30M'
        except KeyError:
            pass

    # SET VARIABLES REPEATED IN MANY DOMAINS:
    # --ORRES is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, in_domain + 'ORRES']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, in_domain + 'ORRES'] = '[?]'
    except KeyError:
        pass
    # VISITNUM is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'VISITNUM']:
            # (To do): Set a correct number
            in_df.at[len(in_df)-1, 'VISITNUM'] = 1
    except KeyError:
        pass
    # # --STRESC is expected to be populated:
    # try:
    #     if not in_df.at[len(in_df)-1, in_domain + '--STRESC']:
    #         # (To do): Set a correct result
    #         in_df.at[len(in_df)-1, in_domain + '--STRESC'] = '[?]'
    # except KeyError:
    #     pass
    # ARMNRS is expected to be populated, only when ARM/ARMCS are null:
    try:
        if in_df.at[len(in_df)-1, 'ARMNRS'] or not in_df.at[len(in_df)-1, 'ARMNRS']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'ARMNRS'] = ''
    except KeyError:
        pass
    # ACTARMUD is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'ACTARMUD']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'ACTARMUD'] = '[?]'
    except KeyError:
        pass
    # --DOSE is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, in_domain + 'DOSE']:
            # (To do): Set a correct amount
            in_df.at[len(in_df)-1, in_domain + 'DOSE'] = 1
    except KeyError:
        pass
    # PCLLOQ is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'PCLLOQ']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'PCLLOQ'] = 1
    except KeyError:
        pass
    # ISLLOQ is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'ISLLOQ']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'ISLLOQ'] = 1
    except KeyError:
        pass
    # --STRESN is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, in_domain + 'STRESN']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, in_domain + 'STRESN'] = 1
    except KeyError:
        pass
    # --CAT is expected to be populated in the FT/IE/QS/TI/DS/LB/PP/RS domains:
    try:
        if in_domain in ['FT', 'IE', 'QS', 'TI', 'DS', 'LB', 'PP', 'RS']:
            if not in_df.at[len(in_df)-1, in_domain + 'CAT']:
                # (To do): Set a correct result
                in_df.at[len(in_df)-1, in_domain + 'CAT'] = '[?]'
    except KeyError:
        pass
    # LBORNRHI is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'LBORNRHI']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'LBORNRHI'] = '[?]'
    except KeyError:
        pass
    # LBORNRLO is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'LBORNRLO']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'LBORNRLO'] = '[?]'
    except KeyError:
        pass
    # LBSTNRHI is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'LBSTNRHI']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'LBSTNRHI'] = 1
    except KeyError:
        pass
    # LBSTNRLO is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'LBSTNRLO']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'LBSTNRLO'] = 1
    except KeyError:
        pass
    # PCNAM is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'PCNAM']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'PCNAM'] = '[?]'
    except KeyError:
        pass
    # TRLNKID is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'TRLNKID']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'TRLNKID'] = '[?]'
    except KeyError:
        pass
     # TULNKID is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'TULNKID']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'TULNKID'] = '[?]'
    except KeyError:
        pass
    # AEHLGT is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AEHLGT']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AEHLGT'] = '[?]'
    except KeyError:
        pass
    # AEHLGTCD is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AEHLGTCD']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AEHLGTCD'] = 1
    except KeyError:
        pass
    # AEHLT is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AEHLT']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AEHLT'] = '[?]'
    except KeyError:
        pass
    # AEHLTCD is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AEHLTCD']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AEHLTCD'] = 1
    except KeyError:
        pass
    # AELLT is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AELLT']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AELLT'] = '[?]'
    except KeyError:
        pass
    # AELLTCD is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AELLTCD']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AELLTCD'] = 1
    except KeyError:
        pass
    # AEREL is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AEREL']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AEREL'] = '[?]'
    except KeyError:
        pass
    # AESOC is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AESOC']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AESOC'] = '[?]'
    except KeyError:
        pass
    # AESOCCD is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'AESOCCD']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'AESOCCD'] = 1
    except KeyError:
        pass
    # LBSTREFC is expected to be populated:
    try:
        if not in_df.at[len(in_df)-1, 'LBSTREFC']:
            # (To do): Set a correct result
            in_df.at[len(in_df)-1, 'LBSTREFC'] = '[?]'
    except KeyError:
        pass

    # If --ORRES is in the domain and is ppulated, then if is in the domain --ORRESU/--STRESC must be populated:
    try:
        # (To do): Set a correct result
        if in_df.at[len(in_df)-1, in_domain + 'ORRES']:
            try:
                if not in_df.at[len(in_df)-1, in_domain + 'ORRESU']:
                    in_df.at[len(in_df)-1, in_domain + 'ORRESU'] = '[?]'
            except KeyError:
                pass
            try:
                if not in_df.at[len(in_df)-1, in_domain + 'STRESC']:
                    in_df.at[len(in_df)-1, in_domain + 'STRESC'] = '[?]'
            except KeyError:
                pass
    except KeyError:
        pass
    # If --STRESU is in the domain and is populated, --STRESC must be populated:
    try:
        # (To do): Set a correct result
        if in_df.at[len(in_df)-1, in_domain + 'STRESU']:
            if not in_df.at[len(in_df)-1, in_domain + 'STRESC']:
                in_df.at[len(in_df)-1, in_domain + 'STRESC'] = '[?]'
    except KeyError:
        pass
    # If --DRVFL is in the domain and is 'Y', --STRESC must be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'DRVFL'] == 'Y':
            # (To do): Set a correct result
            if not in_df.at[len(in_df)-1, in_domain + 'STRESC']:
                in_df.at[len(in_df)-1, in_domain + 'STRESC'] = '[?]'
    except KeyError:
        pass
    # If --LOBXFL is in the domain and is 'Y', --STRESC must be populated. Moreover, if --DRVFL is in the domain and is not populated, --ORRES must be populated:
    try:
        # (To do): Set correct result
        if in_df.at[len(in_df)-1, in_domain + 'LOBXFL'] == 'Y':
            if not in_df.at[len(in_df)-1, in_domain + 'STRESC']:
                in_df.at[len(in_df)-1, in_domain + 'STRESC'] = '[?]'
    except KeyError:
        pass
    # If --STAT is in the domain and is 'NOT DONE', --REASND must be populated. Moreover, if --ORRES and --ORRESU are in the domain, they must be empty:
    try:
        # (To do): Set a correct response
        if in_df.at[len(in_df)-1, in_domain + 'STAT'] == 'NOT DONE':
            in_df.at[len(in_df)-1, in_domain + 'REASND'] = '[?]'
            try:
                if in_df.at[len(in_df)-1, in_domain + 'ORRES'] or not in_df.at[len(in_df)-1, in_domain + 'ORRES']:
                    in_df.at[len(in_df)-1, in_domain + 'ORRES'] = ''
            except KeyError:
                pass
            try:
                if in_df.at[len(in_df)-1, in_domain + 'ORRESU'] or not in_df.at[len(in_df)-1, in_domain + 'ORRESU']:
                    in_df.at[len(in_df)-1, in_domain + 'ORRESU'] = ''
            except KeyError:
                pass
    except KeyError:
                pass
    # If --DRVFL is in the domain and is 'Y', --ORRES must not be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'DRVFL'] == 'Y':
            in_df.at[len(in_df)-1, in_domain + 'ORRES'] = ''
            in_df.at[len(in_df)-1, in_domain + 'ORRESU'] = ''
    except KeyError:
        pass
    # If --STTPT is in the domain, --STTPT/--STRTPT must be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'STTPT'] or not in_df.at[len(in_df)-1, in_domain + 'STTPT']:
            # Start of reference time point:
            try:
                if in_df.at[len(in_df)-1, in_domain + 'STDTC']:
                    in_df.at[len(in_df)-1, in_domain + 'STTPT'] = func_nihpo_random_date_between_dates(in_df.at[len(in_df)-1, in_domain + 'STDTC'], in_df.at[len(in_df)-1, in_domain + 'ENDTC'])
            except KeyError:
                in_df.at[len(in_df)-1, in_domain + 'STTPT'] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                pass
            try:
                # If reference time point (--ENTPT) is the date of collection or assessment:
                if in_df.at[len(in_df)-1, in_domain + 'STTPT'] == in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                    in_df.at[len(in_df)-1, in_domain + 'STRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'UNKNOWN'])
                # If reference time point (--ENTPT) is priot to the date of collection or assessment:
                elif in_df.at[len(in_df)-1, in_domain + 'STTPT'] < in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                    in_df.at[len(in_df)-1, in_domain + 'STRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'AFTER', 'UNKNOWN'])
            except KeyError:
                in_df.at[len(in_df)-1, in_domain + 'STRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'AFTER', 'UNKNOWN'])
                pass
    except KeyError:
        pass
    # If --ENTPT is in the domain, --STTPT/--ENRTPT must be populated (--STTPT only if is in the domain):
    try:
        if in_df.at[len(in_df)-1, in_domain + 'ENTPT'] or not in_df.at[len(in_df)-1, in_domain + 'ENTPT']:
            # If --STTPT is in the domain, --ENRTPT must be populated between --STTPT and --ENDTC; otherwise, --ENRTPT must be populated between --STDTC and --ENDTC:
            try:
                if in_df.at[len(in_df)-1, in_domain + 'STTPT']:
                    try:
                        if in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                            in_df.at[len(in_df)-1, in_domain + 'ENTPT'] = func_nihpo_random_date_between_dates(in_df.at[len(in_df)-1, in_domain + 'STTPT'], in_df.at[len(in_df)-1, in_domain + 'ENDTC'])
                    except KeyError:
                        in_df.at[len(in_df)-1, in_domain + 'ENTPT'] = func_nihpo_random_date_between_dates(in_df.at[len(in_df)-1, in_domain + 'STTPT'], in_end_participation)
                        pass
            except KeyError:
                in_df.at[len(in_df)-1, in_domain + 'ENTPT'] = func_nihpo_random_date_between_dates(in_start_participation,  in_df.at[len(in_df)-1, in_domain + 'ENDTC'])
                pass
            try:
                # If reference time point (--ENTPT) is the date of collection or assessment:
                if in_df.at[len(in_df)-1, in_domain + 'ENTPT'] == in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                    # Section 4.4.7 ('U' should be an option, but it gives a Pinnacle21 issue)
                    in_df.at[len(in_df)-1, in_domain + 'ENRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'ONGOING'])
                # If reference time point (--ENTPT) is priot to the date of collection or assessment:
                elif in_df.at[len(in_df)-1, in_domain + 'ENTPT'] < in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                    # Section 4.4.7 ('U' should be an option, but it gives a Pinnacle21 issue)
                    in_df.at[len(in_df)-1, in_domain + 'ENRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'AFTER', 'ONGOING'])
            except KeyError:
                in_df.at[len(in_df)-1, in_domain + 'ENRTPT'] = random.choice(['BEFORE', 'COINCIDENT', 'AFTER', 'ONGOING'])
                pass
    except KeyError:
        pass
    # If --DTC is in the domain, --DTC must be populated between --STDTC and --ENDTC:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'DTC'] or not in_df.at[len(in_df)-1, in_domain + 'DTC']:
            if int(in_rules_df[in_rules_df['domain_code'] == in_domain]['per_visit']) == 1:
                in_df.at[len(in_df)-1, in_domain + 'DTC'] = in_start_participation + timedelta(in_df.at[len(in_df)-1, 'VISITDY'] - 1)
                try:
                    if in_df.at[len(in_df)-1, in_domain + 'STDTC'] or not in_df.at[len(in_df)-1, in_domain + 'STDTC']:
                        in_df.at[len(in_df)-1, in_domain + 'STDTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_df.at[len(in_df)-1, in_domain + 'DTC'])
                except KeyError:
                    pass
                try:
                    if in_df.at[len(in_df)-1, in_domain + 'ENDTC'] or not in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                        in_df.at[len(in_df)-1, in_domain + 'ENDTC'] = func_nihpo_random_date_between_dates(in_df.at[len(in_df)-1, in_domain + 'DTC'], in_end_participation)
                except KeyError:
                    pass
            else:
                in_df.at[len(in_df)-1, in_domain + 'DTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                try:
                    if in_df.at[len(in_df)-1, in_domain + 'STDTC'] or not in_df.at[len(in_df)-1, in_domain + 'STDTC']:
                        in_df.at[len(in_df)-1, in_domain + 'STDTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_df.at[len(in_df)-1, in_domain + 'DTC'])
                except KeyError:
                    pass
                try:
                    if in_df.at[len(in_df)-1, in_domain + 'ENDTC'] or not in_df.at[len(in_df)-1, in_domain + 'ENDTC']:
                        in_df.at[len(in_df)-1, in_domain + 'ENDTC'] = func_nihpo_random_date_between_dates(in_df.at[len(in_df)-1, in_domain + 'DTC'], in_end_participation)
                except KeyError:
                    pass
    except KeyError:
        pass
    # If --DTC is in the domain and is populated, --DY must be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'DTC']:
            if in_df.at[len(in_df)-1, in_domain + 'DY'] or not in_df.at[len(in_df)-1, in_domain + 'DY']:
                if in_df.at[len(in_df)-1, in_domain + 'DTC'] >= in_start_participation:
                    in_df.at[len(in_df)-1, in_domain + 'DY'] = (in_df.at[len(in_df)-1, in_domain + 'DTC'] - in_start_participation).days + 1
                else:
                    in_df.at[len(in_df)-1, in_domain + 'DY'] = (in_df.at[len(in_df)-1, in_domain + 'DTC'] - in_start_participation).days
    except KeyError:
        pass
    # If --ELTM is in the domain and is populated, --TPT/--TPTREF/--TPTNUM must be populated:
    try:
        # (To do): Set a correct name, description, number
        if in_df.at[len(in_df)-1, in_domain + 'ELTM']:
            if len(in_df) > 1:
                # Check if --DTC field exists in the domain:
                try:
                    if (in_df.at[len(in_df)-1, in_domain + 'DTC'] == in_df.at[len(in_df)-2, in_domain + 'DTC']) and (in_df.at[len(in_df)-1, 'USUBJID'] == in_df.at[len(in_df)-2, 'USUBJID']):
                        in_df.at[len(in_df)-1, in_domain + 'TPT'] = in_df.at[len(in_df)-2, in_domain + 'TPT']
                        in_df.at[len(in_df)-1, in_domain + 'TPTREF'] = in_df.at[len(in_df)-2, in_domain + 'TPTREF']
                        in_df.at[len(in_df)-1, in_domain + 'RFTDTC'] = in_df.at[len(in_df)-2, in_domain + 'RFTDTC']
                        in_df.at[len(in_df)-1, in_domain + 'TPTNUM'] = in_df.at[len(in_df)-2, in_domain + 'TPTNUM']
                    else:
                        var_tpt = random.choice(current_app.config['CT_TPT_PARAMETERS'])
                        in_df.at[len(in_df)-1, in_domain + 'TPT'] = var_tpt[1]
                        in_df.at[len(in_df)-1, in_domain + 'TPTREF'] = var_tpt[2]
                        in_df.at[len(in_df)-1, in_domain + 'RFTDTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                        in_df.at[len(in_df)-1, in_domain + 'TPTNUM'] = var_tpt[0]
                except KeyError:
                    if in_df.at[len(in_df)-1, 'USUBJID'] == in_df.at[len(in_df)-2, 'USUBJID']:
                        in_df.at[len(in_df)-1, in_domain + 'TPT'] = in_df.at[len(in_df)-2, in_domain + 'TPT']
                        in_df.at[len(in_df)-1, in_domain + 'TPTREF'] = in_df.at[len(in_df)-2, in_domain + 'TPTREF']
                        in_df.at[len(in_df)-1, in_domain + 'RFTDTC'] = in_df.at[len(in_df)-2, in_domain + 'RFTDTC']
                        in_df.at[len(in_df)-1, in_domain + 'TPTNUM'] = in_df.at[len(in_df)-2, in_domain + 'TPTNUM']
                    else:
                        var_tpt = random.choice(current_app.config['CT_TPT_PARAMETERS'])
                        in_df.at[len(in_df)-1, in_domain + 'TPT'] = var_tpt[1]
                        in_df.at[len(in_df)-1, in_domain + 'TPTREF'] = var_tpt[2]
                        in_df.at[len(in_df)-1, in_domain + 'RFTDTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                        in_df.at[len(in_df)-1, in_domain + 'TPTNUM'] = var_tpt[0]
                    pass
            else:
                var_tpt = random.choice(current_app.config['CT_TPT_PARAMETERS'])
                in_df.at[len(in_df)-1, in_domain + 'TPT'] = var_tpt[1]
                in_df.at[len(in_df)-1, in_domain + 'TPTREF'] = var_tpt[2]
                in_df.at[len(in_df)-1, in_domain + 'RFTDTC'] = func_nihpo_random_date_between_dates(in_start_participation, in_end_participation)
                in_df.at[len(in_df)-1, in_domain + 'TPTNUM'] = var_tpt[0]
    except KeyError:
        pass
    # If --TRT is in the domain, --TRT must be populated:
    try:
        # (To do): Set correct names
        if in_df.at[len(in_df)-1, in_domain + 'TRT'] or not in_df.at[len(in_df)-1, in_domain + 'TRT']:
            in_df.at[len(in_df)-1, in_domain + 'TRT'] = '[?]'
    except KeyError:
        pass
    # If --TERM is in the domain, --TERM must be populated:
    try:
        # (To do): Set correct names
        if in_df.at[len(in_df)-1, in_domain + 'TERM'] or not in_df.at[len(in_df)-1, in_domain + 'TERM']:
            in_df.at[len(in_df)-1, in_domain + 'TERM'] = '[?]'
    except KeyError:
        pass
    # If --DECOD is in the domain, --DECOD must be populated:
    try:
        # (To do): Set correct names
        if in_df.at[len(in_df)-1, in_domain + 'DECOD'] or not in_df.at[len(in_df)-1, in_domain + 'DECOD']:
            in_df.at[len(in_df)-1, in_domain + 'DECOD'] = '[?]'
    except KeyError:
        pass
    # If --STDY is in the domain, --STDY must be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'STDY'] or not in_df.at[len(in_df)-1, in_domain + 'STDY']:
            if in_df.at[len(in_df)-1, in_domain + 'STDTC'] >= in_start_participation:
                in_df.at[len(in_df)-1, in_domain + 'STDY'] = (in_df.at[len(in_df)-1, in_domain + 'STDTC'] - in_start_participation).days + 1
            else:
                in_df.at[len(in_df)-1, in_domain + 'STDY'] = (in_df.at[len(in_df)-1, in_domain + 'STDTC'] - in_start_participation).days
    except KeyError:
        pass
    # If --ENDY is in the domain, --ENDY must be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'ENDY'] or not in_df.at[len(in_df)-1, in_domain + 'ENDY']:
            if in_df.at[len(in_df)-1, in_domain + 'ENDTC'] >= in_start_participation:
                in_df.at[len(in_df)-1, in_domain + 'ENDY'] = (in_df.at[len(in_df)-1, in_domain + 'ENDTC'] - in_start_participation).days + 1
            elif in_df.at[len(in_df)-1, in_domain + 'ENDTC'] < in_start_participation:
                in_df.at[len(in_df)-1, in_domain + 'ENDY'] = (in_df.at[len(in_df)-1, in_domain + 'ENDTC'] - in_start_participation).days
            else:
                in_df.at[len(in_df)-1, in_domain + 'ENDY'] = ''
    except KeyError:
        pass
    # Set TAETORD variable number:
    # (To do): Set correctly this variable (number of element in the arm)
    if 'TAETORD' in in_df:
            in_df.at[len(in_df)-1, 'TAETORD'] = random.randint(1, 7)
    # If --EPOCH is in the domain, --EPOCH must be populated:
    try:
        if (in_df.at[len(in_df)-1, 'EPOCH'] or not in_df.at[len(in_df)-1, 'EPOCH']) and in_domain != 'SE':
            random_arm = random.choice(list(in_arms_elements_visits['ARMS'].keys()))
            try:
                element = in_arms_elements_visits['ARMS'][random_arm]['ELEMENTS'][in_df.at[len(in_df)-1, 'TAETORD'] - 1]
                in_df.at[len(in_df)-1, 'EPOCH'] = in_arms_elements_visits['ELEMENTS'][element]['EPOCH']
            except KeyError:
                pass
    except KeyError:
        pass
    # If --PRESP != 'Y', --OCCUR must not be populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'PRESP'] != 'Y':
            if in_df.at[len(in_df)-1, in_domain + 'OCCUR'] or not in_df.at[len(in_df)-1, in_domain + 'OCCUR']:
                in_df.at[len(in_df)-1, in_domain + 'OCCUR'] = ''
    except KeyError:
        pass
    # If --OCCUR = 'N', --STRF/--ENRF msut be not populated:
    try:
        if in_df.at[len(in_df)-1, in_domain + 'OCCUR'] == 'N':
            try:
                if in_df.at[len(in_df)-1, in_domain + 'STRF'] or not in_df.at[len(in_df)-1, in_domain + 'STRF']:
                    in_df.at[len(in_df)-1, in_domain + 'STRF'] = ''
            except KeyError:
                pass
            try:
                if in_df.at[len(in_df)-1, in_domain + 'ENRF'] or not in_df.at[len(in_df)-1, in_domain + 'ENRF']:
                    in_df.at[len(in_df)-1, in_domain + 'ENRF'] = ''
            except KeyError:
                pass  
    except KeyError:
        pass

    # Set AE variables:
    if in_domain == 'AE':
        # If AE hasn't finished yet, delete finish date:
        if in_df.at[len(in_df)-1, 'AEOUT'] == 'NOT RECOVERED/NOT RESOLVED':
            in_df.at[len(in_df)-1, 'AEENRTPT'] = ''
            in_df.at[len(in_df)-1, 'AEENTPT'] = ''
            in_df.at[len(in_df)-1, 'AEENDTC'] = ''

        # If subject got a FATAL AE, then it has to be serious (AESER = 'Y'):
        if in_df.at[len(in_df)-1, 'AEOUT'] == 'FATAL':
            in_df.at[len(in_df)-1, 'AESER'] = 'Y'
        # If subject got serious event, one of these fields must be 'Y' and the rest 'N':
        options = list.copy(current_app.config['CT_SERIOUS_ADVERSE_EVENT_FIELDS'])
        if in_df.at[len(in_df)-1, 'AESER'] == 'Y':
            if in_last_AE:
                in_df.at[len(in_df)-1, 'AESDTH'] = 'Y'
                for i in options:
                    in_df.at[len(in_df)-1, i] = 'N'
            else:
                seriousness_criteria = random.choice(options)
                in_df.at[len(in_df)-1, seriousness_criteria] = 'Y'
                options.remove(seriousness_criteria)
                for i in options:
                    in_df.at[len(in_df)-1, i] = 'N'
                in_df.at[len(in_df)-1, 'AESDTH'] = 'N'
        else:
            for i in options:
                in_df.at[len(in_df)-1, i] = 'N'
            in_df.at[len(in_df)-1, 'AESDTH'] = 'N'
            in_df.at[len(in_df)-1, 'AESOD'] = ''
        # If AEBDSYCD is populated, AEBODSYS must be populated:
        # (To do): Set corect value
        in_df.at[len(in_df)-1, 'AEBDSYCD'] = func_nihpo_synth_data_random_value_CTCAE(in_nihpo_cursor)
        in_df.at[len(in_df)-1, 'AEBODSYS'] = func_nihpo_synth_data_random_value_CTCAE(in_nihpo_cursor, in_code=in_df.at[len(in_df)-1, 'AEBDSYCD'])
        # (To do): Set a correct MEDRA term
        in_df.at[len(in_df)-1, 'AEPTCD'] = func_nihpo_synth_data_random_value_CTCAE(in_nihpo_cursor, in_code=in_df.at[len(in_df)-1, 'AEBDSYCD'], in_term=True)
        in_df.at[len(in_df)-1, 'AETERM'] = func_nihpo_synth_data_random_value_CTCAE(in_nihpo_cursor, in_code_term=in_df.at[len(in_df)-1, 'AEPTCD'])
        in_df.at[len(in_df)-1, 'AEDECOD'] = in_df.at[len(in_df)-1, 'AETERM']
        #
        if in_df.at[len(in_df)-1, in_domain + 'ENDTC'] == '':
            in_df.at[len(in_df)-1, in_domain + 'ENDY'] = ''
        elif in_df.at[len(in_df)-1, in_domain + 'ENDTC'] >= in_start_participation:
            in_df.at[len(in_df)-1, in_domain + 'ENDY'] = (in_df.at[len(in_df)-1, in_domain + 'ENDTC'] - in_start_participation).days + 1
        elif in_df.at[len(in_df)-1, in_domain + 'ENDTC'] < in_start_participation:
            in_df.at[len(in_df)-1, in_domain + 'ENDY'] = (in_df.at[len(in_df)-1, in_domain + 'ENDTC'] - in_start_participation).days

    # Set DD variables:
    # if in_domain == 'DD':
        # If DDSTAT or DDDRVFL are not populated, DDORRES must be populated:
        # (To do): Set a correct result
        # if not in_df.at[len(in_df)-1, 'DDSTAT'] or not in_df.at[len(in_df)-1, 'DDDRVFL']:
        #     in_df.at[len(in_df)-1, 'DDORRES'] = 'Result...'
        # If DDSTAT is null, DDSTRESC must be populated:
        # (To do): Set a correct result
        # if not in_df.at[len(in_df)-1, 'DDSTAT']:
        #     in_df.at[len(in_df)-1, 'DDSTRESC'] = 'Result...'


    # Set CO variables:
    if in_domain == 'CO':
        #COVAL is required
        # (TO do): Set correct text
        in_df.at[len(in_df)-1, 'COVAL'] = '[?]'

    # Set CP variables:
    if in_domain == 'CP':
        # CPTEST/CPTESTCD are required
        # (TO do): Set correct names
        in_df.at[len(in_df)-1, 'CPTEST'] = '[?]'
        in_df.at[len(in_df)-1, 'CPTESTCD'] = 'SHORT'

    # Set DA variables:
    if in_domain == 'DA':
        # DASTRESU has the same value when using same DATESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'DATESTCD'] in in_df['DATESTCD'].values:
            in_df.at[len(in_df)-1, 'DASTRESU'] = in_df[in_df['DATESTCD'] == in_df.at[len(in_df)-1, 'DATESTCD']]['DASTRESU'].iloc[0]

     # Set DS variables:
    if in_domain == 'DS':
        # DS has a record with DSDECOD='DEATH' when subject dies duing the trial
        if not 'DEATH' in in_df[in_df['USUBJID'] == in_df.at[len(in_df)-1, 'USUBJID']]['DSDECOD'].values and in_dead:
            in_df.at[len(in_df)-1, 'DSDECOD'] = 'DEATH'

    # Set FA variables:
    if in_domain == 'FA':
        # FAOBJ is required
        # (TO do): Set correct description
        in_df.at[len(in_df)-1, 'FAOBJ'] = '[?]'
        # FASTRESU has the same value when using same FATESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'FATESTCD'] in in_df['FATESTCD'].values:
            in_df.at[len(in_df)-1, 'FASTRESU'] = in_df[in_df['FATESTCD'] == in_df.at[len(in_df)-1, 'FATESTCD']]['FASTRESU'].iloc[0]

    # Set FT variables:
    if in_domain == 'FT':
        # FTTEST/FTTESTCD are required
        # (TO do): Set correct name
        in_df.at[len(in_df)-1, 'FTTEST'] = '[?]'
        in_df.at[len(in_df)-1, 'FTTESTCD'] = 'SHORT'

    # Set GF variables:
    if in_domain == 'GF':
        # GFTEST/GFTESTCD are required
        # (TO do): Set correct name (GFTEST/GFTESTCD not in controlled terms)
        in_df.at[len(in_df)-1, 'GFTEST'] = '[?]'
        in_df.at[len(in_df)-1, 'GFTESTCD'] = 'SHORT'

    # Set IE/TI variables:
    if in_domain == 'IE':
        # IETEST/IETESTCD are required
        # (TO do): Set correct name
        choice = random.choice(current_app.config['CT_INCLUSION_EXCLUSION'])
        in_df.at[len(in_df)-1, 'IECAT'] = choice[0]
        in_df.at[len(in_df)-1, 'IETESTCD'] = choice[1]
        in_df.at[len(in_df)-1, 'IETEST'] = choice[2]
        if choice[0] == 'EXCLUSION':
            in_df.at[len(in_df)-1, 'IEORRES'] = 'Y'
        elif choice[0] == 'INCLUSION':
            in_df.at[len(in_df)-1, 'IEORRES'] = 'N'
        in_df.at[len(in_df)-1, 'IESTRESC'] = in_df.at[len(in_df)-1, 'IEORRES']
    
    # Set MH variables:
    if in_domain == 'MH':
        # (To do): Fix problem when subject was born after start participation
        in_df.at[len(in_df)-1, 'MHSTDTC'] = func_nihpo_random_date_between_dates(in_person['Date_Of_Birth'].item(), in_start_participation)

    # Set PC variables:
    if in_domain == 'PC':
        # PCTEST/PCTESTCD are required
        # (TO do): Set correct name
        in_df.at[len(in_df)-1, 'PCTEST'] = '[?]'
        in_df.at[len(in_df)-1, 'PCTESTCD'] = 'SHORT'

    # Set PE variables:
    if in_domain == 'PE':
        # PETEST/PETESTCD are required
        # (TO do): Set correct name
        in_df.at[len(in_df)-1, 'PETEST'] = '[?]'
        in_df.at[len(in_df)-1, 'PETESTCD'] = 'SHORT'

    # Set QS variables:
    if in_domain == 'QS':
        # QSTEST/QSTESTCD are required
        # (TO do): Set correct name
        in_df.at[len(in_df)-1, 'QSTEST'] = '[?]'
        in_df.at[len(in_df)-1, 'QSTESTCD'] = 'SHORT'

    # Set RP variables:
    if in_domain == 'RP':
        # RPSTRESU has the same value when using same RPTESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'RPTESTCD'] in in_df['RPTESTCD'].values:
            in_df.at[len(in_df)-1, 'RPSTRESU'] = in_df[in_df['RPTESTCD'] == in_df.at[len(in_df)-1, 'RPTESTCD']]['RPSTRESU'].iloc[0]

    # Set SC variables:
    if in_domain == 'SC':
        # SCSTRESU has the same value when using same SCTESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'SCTESTCD'] in in_df['SCTESTCD'].values:
            in_df.at[len(in_df)-1, 'SCSTRESU'] = in_df[in_df['SCTESTCD'] == in_df.at[len(in_df)-1, 'SCTESTCD']]['SCSTRESU'].iloc[0]

    # Set SE/TE variables:
    if in_domain == 'SE':
        # ETCD is required
        # (To do): Set correct element code
        element = in_arm['ELEMENTS'][in_seq_number - 1]
        in_df.at[len(in_df)-1, 'ETCD'] = in_arms_elements_visits['ELEMENTS'][element]['ELEMENT_CODE']
        in_df.at[len(in_df)-1, 'EPOCH'] = in_arms_elements_visits['ELEMENTS'][element]['EPOCH']
    # Set SM variables:
    if in_domain == 'SM':
        # MIDS is required
        # (To do): Set correct name
        in_df.at[len(in_df)-1, 'MIDS'] = '[?]'
        # MIDSTYPE is required
        # (To do): Set correct disease milestone
        in_df.at[len(in_df)-1, 'MIDSTYPE'] = random.choice(current_app.config["CT_DISEASE_MILESTONES_TYPE"])

    # Set SR variables:
    if in_domain == 'SR':
        # SROBJ is required
        # (TO do): Set correct description
        in_df.at[len(in_df)-1, 'SROBJ'] = '[?]'

    # Set SS variables:
    if in_domain == 'SS':
        # SSSTRESC is DEAD only if the subject dies during the trial:
        if in_dead:
            in_df.at[len(in_df)-1, 'SSSTRESC'] = 'DEAD'
            in_df.at[len(in_df)-1, 'SSDTC'] = func_nihpo_random_date_between_dates(in_end_participation, in_end_participation)
            in_df.at[len(in_df)-1, 'SSDY'] = (in_df.at[len(in_df)-1, 'SSDTC'] - in_start_participation).days + 1
        else:
            in_df.at[len(in_df)-1, 'SSSTRESC'] = random.choice(current_app.config['CT_SSSTRESC_VALUES_NOT_DIE'])

    # Set UR variables:
    if in_domain == 'UR':
        # URSTRESU has the same value when using same URTESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'URTESTCD'] in in_df['URTESTCD'].values:
            index_list = in_df.index[in_df['URTESTCD'] == in_df.at[len(in_df)-1, 'URTESTCD']].tolist()
            for index in index_list:
                if in_df.at[len(in_df)-1, 'URMETHOD'] == in_df['URMETHOD'][index]:
                    in_df.at[len(in_df)-1, 'URSTRESU'] = in_df['URSTRESU'][index]

    # Set VS variables:
    if in_domain == 'VS':
        # VSSTRESU has the same value when using same VSTESTCD
        # (TO do): Set correct standard units
        if in_df.at[len(in_df)-1, 'VSTESTCD'] in in_df['VSTESTCD'].values:
            in_df.at[len(in_df)-1, 'VSSTRESU'] = in_df[in_df['VSTESTCD'] == in_df.at[len(in_df)-1, 'VSTESTCD']]['VSSTRESU'].iloc[0]

    # Set STUDYID variable in all the domains:
    in_df.at[len(in_df)-1, 'STUDYID'] = in_study_id

    if int(in_rules_df[in_rules_df['domain_code'] == in_domain]['per_adverse_event']) == 1:
        return in_df, in_last_AE, in_list_date_fields
    else:
        return in_df, in_list_date_fields

def func_nihpo_create_TS_domain(in_nihpo_cursor, in_df, in_domains_df, in_data, in_countries):
    """
    Creates a full table with all the Trial Summary Parameters (TS domain)
    
    :param in_nihpo_cursor: Cursor to SQLite3 file
    :type in_nihpo_cursor: SQLite3 cursor
    :param in_df: Pandas Data Frame where all the data is saved
    :type in_df: Data Frame
    :param in_domains_df: Pandas Data frame from CDISC_SDTM.sqlite3 file from table CDISC_SDTM_Domains
    :type in_domains_df: Data Frame
    :param in_data: All the data set by the user to fill the TS table
    :type in_data: Dictionary
    :param in_countries: Countries used in the trial
    :type in_countries: List
    :returns: Single Data Frame with all the information to fill the TS domain
    :rtype: Data frame
    """

    # Initialize variables
    countries_counter = 0
    trial_summary_parameters = in_data['Trial Summary Parameters']
    indicators = in_data['Indicators']
    versions = in_data['Standard Versions']

    # Get a list ot TS parameters
    list_tsparm = deepcopy(current_app.config['CT_LIST_TS_PARAMETERS'])

    # Add a new investigational country row per additional country chosen
    for _ in range(len(in_countries)-1):
        list_tsparm.append(current_app.config['CT_LIST_TS_PARAMETERS'][-1])

    # Create rows
    for seq_counter in range(0, len(list_tsparm)):
        list_fields = []
        list_values = []

        for variable in in_domains_df[in_domains_df['domain_name'] == 'TS'].itertuples():
            value = ""
            controlled_terminology = variable[5]
            variable_name = variable[2]
            if variable_name == 'STUDYID':
                value = trial_summary_parameters['Study ID']
            elif variable_name == 'DOMAIN':
                value = 'TS'
            elif variable_name == 'TSSEQ':
                value = seq_counter + 1
            elif variable_name == 'TSPARM':
                value = list_tsparm[seq_counter][1]
            elif variable_name == 'TSPARMCD':
                value = list_tsparm[seq_counter][0]
            elif variable_name == 'TSVAL':
                if list_tsparm[seq_counter][0] == 'SPONSOR':
                    value = trial_summary_parameters['Sponsor']
                elif list_tsparm[seq_counter][0] == 'TITLE':
                    value = trial_summary_parameters['Trial Name']
                elif list_tsparm[seq_counter][0] == 'SEXPOP':
                    value = in_data['Demography']['Gender']
                elif list_tsparm[seq_counter][0] == 'AGEMAX':
                    value = 'P' + in_data['Demography']['Maximum Age'] + 'Y'
                elif list_tsparm[seq_counter][0] == 'AGEMIN':
                    value = 'P' + in_data['Demography']['Minimum Age'] + 'Y'
                elif list_tsparm[seq_counter][0] == 'SSTDTC':
                    value = trial_summary_parameters['Start Date']
                elif list_tsparm[seq_counter][0] == 'SENDTC':
                    value = trial_summary_parameters['End Date']
                elif list_tsparm[seq_counter][0] == 'PLANSUB':
                    value = trial_summary_parameters['Planned Number of Subjects']
                elif list_tsparm[seq_counter][0] == 'NARMS':
                    value = trial_summary_parameters['Planned Number of Arms']
                elif list_tsparm[seq_counter][0] == 'ACTSUB':
                    value = in_data['Demography']['Number of Subjects']
                elif list_tsparm[seq_counter][0] == 'NCOHORT':
                    value = trial_summary_parameters['Number of Groups']
                elif list_tsparm[seq_counter][0] == 'LENGTH':
                    value = 'P' + str(trial_summary_parameters['Trial Length']) + 'D'
                elif list_tsparm[seq_counter][0] == 'OBJPRIM':
                    value = trial_summary_parameters['Trial Primary Objective']
                elif list_tsparm[seq_counter][0] == 'OBJSEC':
                    value = trial_summary_parameters['Trial Secondary Objective']
                elif list_tsparm[seq_counter][0] == 'TTYPE':
                    value = trial_summary_parameters['Trial Type']
                elif list_tsparm[seq_counter][0] == 'STYPE':
                    value = trial_summary_parameters['Study Type']
                elif list_tsparm[seq_counter][0] == 'THERAREA':
                    value = trial_summary_parameters['Therapeutic Area']
                elif list_tsparm[seq_counter][0] == 'ADDON':
                    if indicators['Added on to Existing Treatments']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'STOPRULE':
                    value = trial_summary_parameters['Study Stop Rules']
                elif list_tsparm[seq_counter][0] == 'TBLIND':
                    value = trial_summary_parameters['Trial Blinding Schema']
                elif list_tsparm[seq_counter][0] == 'TCNTRL':
                    value = trial_summary_parameters['Control Type']
                elif list_tsparm[seq_counter][0] == 'TPHASE':
                    value = trial_summary_parameters['Trial Phase Classification']
                elif list_tsparm[seq_counter][0] == 'OUTMSPRI':
                    value = trial_summary_parameters['Primary Outcome Measure']
                elif list_tsparm[seq_counter][0] == 'FCNTRY':
                    value = in_countries[countries_counter]
                    countries_counter += 1
                elif list_tsparm[seq_counter][0] == 'ADAPT':
                    if trial_summary_parameters['Adaptive Design']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'DCUTDTC':
                    value = trial_summary_parameters['Data Cutoff Date']
                elif list_tsparm[seq_counter][0] == 'DCUTDESC':
                    value = trial_summary_parameters['Data Cutoff Description']
                elif list_tsparm[seq_counter][0] == 'REGID':
                    value = trial_summary_parameters['Registry Identifier']
                elif list_tsparm[seq_counter][0] == 'RANDOM':
                    if indicators['Randomized']:
                        value = 'Y'
                    else:
                        value = 'N'

                # Indicators:
                elif list_tsparm[seq_counter][0] == 'EXTTIND':
                    if indicators['Extension Trial Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'PDSTIND':
                    if indicators['Pediatric Study Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'PIPIND':
                    if indicators['Pediatric Investigation Plan Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'PDPSTIND':
                    if indicators['Pediatric Postmarket Study Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'RDIND':
                    if indicators['Rare Disease Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                elif list_tsparm[seq_counter][0] == 'HLTSUBJI':
                    if indicators['Healthy Subject Indicator']:
                        value = 'Y'
                    else:
                        value = 'N'
                # SDTM Versions:
                elif list_tsparm[seq_counter][0] == 'SDTIGVER':
                    value = versions['SDTM IG']
                elif list_tsparm[seq_counter][0] == 'SDTMVER':
                    value = versions['SDTM']
            elif variable_name == 'TSVALNF':
                # Only populated if TSVAL is null
                value = ''
            elif variable_name == 'TSVALCD':
                if list_tsparm[seq_counter][0] in current_app.config['CT_TS_FIELDS_MATCH_CODE']:
                    value = func_nihpo_check_code(in_nihpo_cursor, list_values[-3])
                else:
                    value = 'This is the code of the term in TSVAL. For example, "6CW7F3G59X" is the code for gabapentin; "C49488" is the code for Y. The length of this variable can be longer than 8 to accommodate the length of the external terminology.'
            elif variable_name == 'TSVCDREF':
                if list_tsparm[seq_counter][0] == 'FCNTRY':
                    value = 'ISO 3166'
                else:
                    value = 'CDISC'
            elif variable_name == 'TSVCDVER':
                value = '2022-03-26'
            list_values.append(value)
            list_fields.append(variable_name)
        if in_df.empty:
            in_df = pd.DataFrame([list_values], columns = list_fields)
        else:
            in_df.loc[len(in_df)] = list_values
    return in_df

def func_nihpo_update_sqlite3_in_superset(in_folder_path, in_trial_file_name, in_superset_db_path):
    """
    Update the superset.db that contains Superset metadata to upload the DB used in the datasets
    with the sqlite3 included in the given ZIP trial file 

    :param in_folder_path: Folder file path
    :type in_folder_path: String
    :param in_trial_file_name: Trial file name
    :type in_trial_file_name: String
    :param in_superset_db_path: superset.db path
    :type in_superset_db_path: String
    """
    # Initialize variables
    trial_file_path = in_folder_path + in_trial_file_name + '.zip'
    sqlite3_file_path = in_folder_path + in_trial_file_name + '.sqlite3'

    # Connect to superset.db
    engine = sqlalchemy.create_engine('sqlite:///' + in_superset_db_path)

    # Extract data from ZIP file in the same folder
    if not os.path.isfile(sqlite3_file_path):
        with zipfile.ZipFile(trial_file_path, 'r') as zip_ref:
            zip_ref.extract(in_trial_file_name + '.sqlite3', in_folder_path)
    
    # Use the SQLite3 file extracted in Superset
    with engine.connect() as conn:
        conn.execute('UPDATE dbs SET sqlalchemy_uri = "sqlite://///%s" WHERE id = 2;' % (sqlite3_file_path))