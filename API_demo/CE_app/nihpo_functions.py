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
import datetime, random, logging, warnings, time, xport, xport.v56
import pandas as pd
from functools import wraps
import os
from psycopg2 import sql

from flask import current_app
from flask import flash, redirect, url_for
from flask_login import current_user

date_format = "%Y-%m-%d"


def func_nihpo_synth_data_random_value(
    in_cursor,
    in_codelist,
    in_controlled_terminology,
    in_match_code=None,
    in_matching=False,
):
    """
    Returns a random value from a particular codelist from CDISC SDTM CT or Sponsor CT if is extensible

    :param in_sqlite3_cursor: Cursor to SQLite3 file
    :type in_sqlite3_cursor: SQLite3 cursor
    :param in_codelist: Code of interest
    :type in_codelist: String
    :param in_match_code: Code to match (default None)
    :type in_match_code: String
    :param in_matching: True if it is matching with in_match_code, False otherwise (default False)
    :type in_matching: Boolean
    :returns: An item from CDISC_SDTM_Codelist_Choices (Item_Name and Item_NCI_Code)
    :rtype: List
    """

    # Initialize variables
    to_filter = {}

    # Check if the CT is CDISC SDTM or Sponsor-specific
    if in_matching == "CDISC_SDTM":
        to_filter["in_codelist"] = in_codelist
        to_filter["in_match_code"] = in_match_code
        var_sql = sql.SQL(
            """SELECT item_name, item_nci_code FROM cdisc_sdtm_codelist_choices WHERE oid_code = {code_list} AND item_nci_code = {match_code} ORDER BY RANDOM() LIMIT 1;""".format(
                code_list=sql.Literal(in_codelist),
                match_code=sql.Literal(in_match_code),
            )
        )

    elif in_matching == "sponsor":
        value = [in_controlled_terminology[in_codelist][in_match_code]["item_name"]]
        return value

    else:
        to_filter["in_codelist"] = in_codelist

        # # Check if the codelist is extensible
        # var_sql_extensible = '''SELECT item_extensible FROM cdisc_sdtm_codelist_topics WHERE oid_code = '%(in_codelist)s' LIMIT 1;''' % to_filter
        # in_cursor.execute(var_sql_extensible)

        # extensible_fetch = in_cursor.fetchone()
        # if not extensible_fetch:
        #     return ['']

        # extensible_value = extensible_fetch[0]

        # # Check if Sponsor has added some value to the codelist
        # if in_controlled_terminology:
        #     if extensible_value == 'Yes':
        #         if in_codelist in in_controlled_terminology.keys():
        #             sponsor_or_standard = random.choice(['sponsor', 'standard'])
        #             if sponsor_or_standard == 'sponsor':
        #                 item_nci_code = random.choice(list(in_controlled_terminology[in_codelist].keys()))
        #                 return (in_controlled_terminology[in_codelist][item_nci_code]['item_name'], item_nci_code, 'sponsor')
        var_sql = sql.SQL(
            """SELECT item_name, item_nci_code FROM cdisc_sdtm_codelist_choices WHERE oid_code = {code_list} ORDER BY RANDOM() LIMIT 1;"""
        ).format(code_list=sql.Literal(in_codelist))
    in_cursor.execute(var_sql)
    fetch_item = in_cursor.fetchone()

    # Break it if there is no result
    if not fetch_item:
        return ["", ""]

    selected_item = list(fetch_item)

    add_ct = "CDISC_SDTM"

    selected_item.append(add_ct)
    return selected_item


def func_nihpo_synth_data_random_value_CTCAE(
    in_sqlite3_cursor, in_code=None, in_code_term=None, in_term=None
):
    """
    Returns a random value from a particular codelist from the SQLite3 file "CDISC_SDTM.sqlite3", from the table "CDISC_SDTM_CTCAE"

    :param in_sqlite3_cursor: Cursor to SQLite3 file
    :type in_sqlite3_cursor: SQLite3 cursor
    :param in_code: Code of the specific MedDRASOC (MedDRASOCCode)
    :type in_code: Integer
    :param in_code_term: Code of the specific CTCAETerm ()
    :type in_code_term: Integer
    :param in_term: Term of interest
    :type in_term: String
    :returns: Random value from a particular codelist MedDra terms
    :rtype: String
    """

    if in_code:
        if in_term:
            var_sql = sql.SQL(
                """SELECT meddra_code FROM cdisc_sdtm_ctcae WHERE meddra_soc_code = {code} ORDER BY RANDOM() LIMIT 1;"""
            ).format(code=sql.Literal(in_code))
        else:
            var_sql = sql.SQL(
                """SELECT meddra_soc FROM cdisc_sdtm_ctcae WHERE meddra_soc_code = {code} ORDER BY RANDOM() LIMIT 1;"""
            ).format(code=sql.Literal(in_code))
    elif in_code_term:
        var_sql = sql.SQL(
            """SELECT ctcae_term FROM cdisc_sdtm_ctcae WHERE meddra_code = {code_term} ORDER BY RANDOM() LIMIT 1;"""
        ).format(code_term=sql.Literal(in_code_term))
    else:
        var_sql = """SELECT meddra_soc_code FROM cdisc_sdtm_ctcae ORDER BY RANDOM() LIMIT 1;"""

    in_sqlite3_cursor.execute(var_sql)

    return in_sqlite3_cursor.fetchone()[0]

    # if in_code:
    #     if in_term:
    #         var_sql = '''SELECT MedDRACode  FROM CDISC_SDTM_CTCAE WHERE MedDRASOCCode = '%(in_code)s' ORDER BY RANDOM() LIMIT 1;'''
    #         to_filter['in_code'] = in_code
    #     else:
    #         var_sql = '''SELECT MedDRASOC FROM CDISC_SDTM_CTCAE WHERE MedDRASOCCode = '%(in_code)s' ORDER BY RANDOM() LIMIT 1;'''
    #         to_filter['in_code'] = in_code
    # elif in_code_term:
    #     var_sql = '''SELECT CTCAETerm  FROM CDISC_SDTM_CTCAE WHERE MedDRACode = '%(in_code_term)s' ORDER BY RANDOM() LIMIT 1;'''
    #     to_filter['in_code_term'] = in_code_term
    # else:
    #     var_sql = '''SELECT MedDRASOCCode FROM CDISC_SDTM_CTCAE ORDER BY RANDOM() LIMIT 1;'''
    # in_sqlite3_cursor.execute(var_sql, to_filter)
    # return in_sqlite3_cursor.fetchone()[0]


# (To do): Use correct codelist_CT
# def func_nihpo_synth_data_random_value_codelist_CT(in_sqlite3_cursor, in_field):
#     """
#     Returns a random value from the SQLite3 file "CDISC_SDTM.sqlite3", from the table "CDISC_SDTM_Codelist_Choices, from the fields we added from examples where Controlled_Terms are '*'

#     :param in_sqlite3_cursor: Cursor to SQLite3 file
#     :type in_sqlite3_cursor: SQLite3 cursor
#     :param in_field: Field of interest
#     :type in_field: String
#     :returns: Random value from a particular codelist from the SQLite3 file "CDISC_SDTM.sqlite3", from the table "CDISC_SDTM_Codelist_Choices
#     :rtype: String
#     """
#     to_filter = {}
#     var_sql = '''SELECT Item_Name, Item_NCI_Code FROM CDISC_SDTM_Codelist_Choices WHERE OID_Code = 'CT_%(in_field)s' ORDER BY RANDOM() LIMIT 1;'''
#     to_filter['in_field'] = in_field
#     return in_sqlite3_cursor.fetchone()[0]


def func_nihpo_random_date(in_start_date_string, in_minimum_days, in_maximum_days):
    """
    Returns a random Date, using a start date, and with a range of minimum and maximum additional days

    :param in_start_date_string: Date formatted as YYYY-MM-DD
    :type in_start_date_string: Date string
    :param in_minimum_days: Minimum number of additional days
    :type in_minimum_days: Integer
    :param in_maximum_days: Maximum number of additional days
    :type in_maximum_days: Integer
    :returns: Date string, randomly selected
    :rtype: Date string
    """

    # Validate date (asserts are removed in production)
    assert (
        in_minimum_days < in_maximum_days
    ), "Please use a minimum number of days less than the maximum numnber of days."

    var_random_days = random.randrange(in_minimum_days, in_maximum_days)
    var_random_date = datetime.datetime.strptime(
        in_start_date_string, date_format
    ) + datetime.timedelta(days=var_random_days)

    return var_random_date.strftime(date_format)


def func_nihpo_random_date_between_dates(in_start_date_string, in_end_date_string):
    """
    Returns a random Date, using a start date and an end date

    :param in_start_date_string: Date formatted as YYYY-MM-DD
    :type in_start_date_string: Date string
    :param in_end_date_string: Date formatted as YYYY-MM-DD
    :type in_end_date_string: Date string
    :returns: Random Date, using a start date and an end date
    :rtype: Date string
    """
    # Validate date:
    start_date = datetime.datetime.strptime(str(in_start_date_string), date_format)
    end_date = datetime.datetime.strptime(str(in_end_date_string), date_format)
    #
    assert start_date <= end_date, "Please put a start date before the end date."
    #
    days_between_dates = (end_date - start_date).days
    try:
        random_number_of_days = random.randrange(1, days_between_dates)
    except ValueError:
        return end_date.date()
    var_random_date = start_date + datetime.timedelta(days=random_number_of_days)
    #
    return var_random_date.date()


def func_nihpo_convert_to_sas(in_df, in_name, in_url, in_sas_format_df):
    """
    Convert a Pandas Data Frame into a .xpt file, setting the correct labels in each field and the correct format (Char or Num)

    :param in_df: Data Frame with all the data about a single domain
    :type in_df: Data Frame
    :param in_name: Abbreviated name of the domain
    :type in_name: String
    :param in_url: Path of the file where the final .xpt file will be saved
    :type in_url: String
    :param in_sas_format_df: Data Frame with the information from the CDISC_SDTM_.sqlite3 file in the table CDISC_SDTM_Domains
    :type in_sas_format_df: Data Frame
    :returns: Nothing. It jsut save the .xpt file in the folder passed by in_url
    :rtype:
    """

    # Initialize variables
    counter = 0

    # Check NUM type variables and change type from string to numeric
    var_number = in_sas_format_df[
        (in_sas_format_df["variable_type"] == "Num")
        & (in_sas_format_df["domain_name"] == in_name)
    ]["variable_name"]
    for i in var_number:
        if i in in_df.columns:
            if in_df[i].any() == "[?]":
                in_df[i] = 3.1415
            else:
                in_df[i] = pd.to_numeric(in_df[i])
    ds = xport.Dataset(in_df, name=in_name)

    # Fix variables format
    for k, v in ds.items():
        counter = counter + 1
        label_series = in_sas_format_df[
            (in_sas_format_df["variable_name"] == v.name)
            & (in_sas_format_df["domain_name"] == in_name)
        ]["variable_label"]
        var_type_series = in_sas_format_df[
            (in_sas_format_df["variable_name"] == v.name)
            & (in_sas_format_df["domain_name"] == in_name)
        ]["variable_type"]
        for i in label_series:
            label = i
        for j in var_type_series:
            var_type = j
        v.label = label
        if var_type == "Char":
            v.format = "$CHAR20."
        elif var_type == "Num":
            v.format = "10.2"
        # (To do): Remove this when BEDUR problem is solved
        if v.name == "BEDUR":
            v.format = "$CHAR20."

    # Rename columns to correct SAS format
    ds = ds.rename(columns={k: k.upper()[:8] for k in ds})
    # (To do): Try to avoid prints in this function

    # Export file
    library = xport.Library({in_name: ds})

    # Turn off logs and warnings from 'xport' package
    logging.getLogger("xport").setLevel(logging.ERROR)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Create export files
        with open(in_url + ".xpt", "wb") as f:
            xport.v56.dump(library, f)


def func_nihpo_check_code(in_sqlite3_cursor, in_item_name):
    """
    Returns the code of the field 'Item_NCI_Code' that matches the 'Item_Name' from the table "CDISC_SDTM_Codelist_Choices of the SQLite3 file "CDISC_SDTM.sqlite3".

    :param in_sqlite3_cursor: Cursor to SQLite3 file
    :type in_sqlite3_cursor: SQLite3 cursor
    :param in_item_name: Name of the item that matches the code
    :type in_item_name: 'String'
    :returns: An item from CDISC_SDTM_Codelist_Choices (Item_Name and Item_NCI_Code)
    :rtype: List
    """
    to_filter = {}
    var_sql = (
        """SELECT Item_NCI_Code FROM CDISC_SDTM_Codelist_Choices WHERE Item_Name = '%s' ORDER BY RANDOM() LIMIT 1;"""
        % in_item_name
    )
    to_filter["in_item_name"] = in_item_name
    # in_sqlite3_cursor.execute("SELECT Item_NCI_Code FROM CDISC_SDTM_Codelist_Choices WHERE Item_Name = ?", in_item_name);
    in_sqlite3_cursor.execute(var_sql)
    return in_sqlite3_cursor.fetchone()[0]


def func_nihpo_time_counter(method):
    """
    Measures the time when running a function with @func_nihpo_time_counter decorator

    :param method: Function to measure
    :type method: Function
    :returns: Result of function
    :rtype: Return
    :returns: Function time in miliseconds
    :rtype: Float
    """

    @wraps(method)
    def timed(*args, **kw):
        ts = time.perf_counter()
        result = method(*args, **kw)
        te = time.perf_counter()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        total_time = (te - ts) * 1000
        return result, total_time

    return timed


def func_nihpo_html_format_countries(in_countries_subjetcs, in_country_names):
    """
    Creates html list tag with country names and subjects.

    :param in_countries_subjetcs: List of lists with country code at first and number subjects at second
    :type in_countries_subjetcs: List
    :param in_country_names: List of country names
    :type in_country_names: List
    :returns: Html tag in string format
    :rtype: String
    """
    assert len(in_countries_subjetcs) == len(
        in_country_names
    ), "Please use both lists with the same number of elements."
    assert (
        type(in_countries_subjetcs[0]) == list
    ), "Please use lists with country code at first and number subjects at second into the in_countries_subjetcs list."

    html_string = f""
    for number_country in range(len(in_countries_subjetcs)):
        number_subjects = in_countries_subjetcs[number_country][1]
        country_name = in_country_names[number_country]
        html_string += f"<li>%s, Number of subjects:%s</li>" % (
            country_name,
            number_subjects,
        )
    return html_string


def required_permissions(*permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for permission in permissions:
                if permission in get_current_permissions():
                    return f(*args, **kwargs)
            flash(
                "You don't have permissions to access to this page, please ask for them to your administrator",
                "error",
            )
            return redirect(url_for("main.synthtrial"))

        return wrapped

    return wrapper


def get_current_permissions():
    return current_user.get_permissions()


def func_nihpo_create_sphinx_doc(in_data, in_output_path):
    """
    Create a .rst file to be used by Sphinx to create documentation
    Inside .rst file, create titles and tables based on incoming data

    :param in_data: Title and tables data
    :type in_data: Dict with titles as keys, for each key the value is another dict with table names as keys, for each key the values are tables parameters, columns and rows
    :param str in_output_path: Output path
    """

    # Initialize variables
    content = []

    # Create titles
    for title_name, title_data in in_data.items():
        content.append(title_name + "\n")
        content.append("=" * len(title_name) + "\n")

        # Create tables
        for table_name, table_data in title_data.items():

            # Check table parameters
            header_rows = table_data["header_rows"]
            align = table_data["align"]
            widths = table_data["widths"]

            # Create table
            content.append("\n")
            content.append(table_name + "\n")
            content.append("-" * len(table_name) + "\n")
            content.append("\n")
            content.append(f".. list-table:: {table_name}\n")
            if header_rows:
                content.append(f"   :header-rows: {header_rows}\n")
            if align:
                content.append(f"   :align: {align}\n")
            if widths:
                content.append(f"   :widths: {widths}\n")
            content.append("\n")

            # Create columns
            for i, column_name in enumerate(table_data["column_names"]):
                if not i:
                    content.append(f"   * - **{column_name}**\n")
                else:
                    content.append(f"     - **{column_name}**\n")

            # Insert rows
            for row in table_data["rows"]:
                for j, row_value in enumerate(row):
                    if not j:
                        content.append(f"   * - {row_value}\n")
                    else:
                        content.append(f"     - {row_value}\n")

        # Create a blank line to separate next title
        content.append("\n")

    # Write
    with open(in_output_path, "w") as f:
        content_to_write = "".join(content)
        f.write(content_to_write)


def func_nihpo_transform_data_to_sphinx_format(
    in_title, in_data, in_header_rows=None, in_align=None, in_widths=None
):
    """
    Transform normal data from current format to Sphinx readable format

    :param str in_title: Section title
    :param dict in_data: Data in current format
    :param list in_header_rows: List of headers for each table, defaults to None
    :param list in_align: List of alignments for each table, defaults to None
    :param list in_widths: List of widths for each table, defaults to None
    :return: Data in the Sphinx readable format
    :rtype: Dict
    """

    if in_header_rows:
        assert len(in_data) == len(
            in_header_rows
        ), f"Please, use same number of header rows ({len(in_header_rows)}) than data keys ({len(in_data)})"
    if in_align:
        assert len(in_data) == len(
            in_align
        ), f"Please, use same number of aligns ({len(in_align)}) than data keys ({len(in_data)})"
    if in_widths:
        assert len(in_data) == len(
            in_widths
        ), f"Please, use same number of widths ({len(in_widths)}) than data keys ({len(in_data)})"

    # Initialize variables
    new_data = {in_title: {}}

    # Insert data in the new dict
    for key_0, table_data in in_data.items():
        new_data[in_title][key_0] = {}
        new_data[in_title][key_0]["rows"] = []
        new_data[in_title][key_0]["column_names"] = ["Parameter", "Value"]
        if table_data:
            for key_1, row_data in table_data.items():
                new_data[in_title][key_0]["rows"].append([key_1, row_data])
                # new_data[in_title][key_0]['column_names'].append([key_1])

            # Create table parameters
            new_data[in_title][key_0]["header_rows"] = in_header_rows
            new_data[in_title][key_0]["align"] = in_align
            new_data[in_title][key_0]["widths"] = in_widths

    return new_data


def func_nihpo_transform_arms_to_sphinx_format(
    in_arms_data, in_header_rows=[None] * 3, in_align=[None] * 3, in_widths=[None] * 3
):
    """
    Transform arms data from current JSON format to Sphinx readable format

    :param dict in_arms_data: Current Arms, Visits & Elements data
    :param list in_header_rows: List of headers for each table, defaults to [None]*3
    :param list in_align: List of alignments for each table, defaults to [None]*3
    :param list in_widths: List of column widths for each table, defaults to [None]*3
    :return: Arms, Elements & Visits in the Sphinx readable format
    :rtype: Dict
    """

    if in_header_rows:
        assert (
            len(in_header_rows) == 3
        ), f"Please, use same number of header rows ({len(in_header_rows)}) than data keys (3)"
    if in_align:
        assert (
            len(in_align) == 3
        ), f"Please, use same number of aligns ({len(in_align)}) than data keys (3)"
    if in_widths:
        assert (
            len(in_widths) == 3
        ), f"Please, use same number of widths ({len(in_widths)}) than data keys (3)"

    # Initialize variables
    new_arms_data = {
        "Arms, Visits & Elements": {
            "Arms": {
                "column_names": ["Name", "Code", "Condition", "Elements"],
                "rows": [],
            },
            "Visits": {
                "column_names": [
                    "Arm",
                    "Visit",
                    "Planned Day of Visit",
                    "Start rule",
                    "End Rule",
                ],
                "rows": [],
            },
            "Elements": {
                "column_names": [
                    "Name",
                    "Code",
                    "Transition Condition",
                    "Start Condition",
                    "Finish Condition",
                    "Duration",
                    "Epoch",
                ],
                "rows": [],
            },
        }
    }

    # Insert values in the new dict format for arms and visits
    for key_0, arm in in_arms_data["ARMS"].items():
        for key_1, param in arm.items():
            if key_1 == "ARM_CODE":
                arm_code = param
                new_arms_data["Arms, Visits & Elements"]["Arms"]["rows"].append(
                    [key_0, param]
                )
            elif key_1 == "ARM_CONDITION":
                new_arms_data["Arms, Visits & Elements"]["Arms"]["rows"][-1].append(
                    param
                )
            elif key_1 == "ELEMENTS":
                new_arms_data["Arms, Visits & Elements"]["Arms"]["rows"][-1].append(
                    ", ".join(param)
                )
            elif key_1 == "VISITS":
                for visit_key, visit_param in param.items():
                    new_arms_data["Arms, Visits & Elements"]["Visits"]["rows"].append(
                        [
                            arm_code,
                            visit_key,
                            visit_param["PLANNED_DAY_VISIT"],
                            visit_param["START_RULE"],
                            visit_param["END_RULE"],
                        ]
                    )

    # Insert values in the new dict format for elements
    for elem_key_0, elem in in_arms_data["ELEMENTS"].items():
        new_arms_data["Arms, Visits & Elements"]["Elements"]["rows"].append(
            [elem_key_0]
        )
        for elem_key_1, elem_param in elem.items():
            new_arms_data["Arms, Visits & Elements"]["Elements"]["rows"][-1].append(
                elem_param
            )

    # Insert table parameters for each table
    for i, key in enumerate(new_arms_data["Arms, Visits & Elements"]):
        new_arms_data["Arms, Visits & Elements"][key]["header_rows"] = in_header_rows[i]
        new_arms_data["Arms, Visits & Elements"][key]["align"] = in_align[i]
        new_arms_data["Arms, Visits & Elements"][key]["widths"] = in_widths[i]

    return new_arms_data


def func_nihpo_create_trial_doc(in_data):
    """
    Create trial documentation from chosen data

    :param dict in_data: Chosen trial parameters
    :return str: PDF file path
    """

    # Split params in groups
    demography_data = {"Demography": in_data["Demography"].copy()}
    countries_data = {"Countries": in_data["Countries"].copy()}
    rwd_data = {"Real World Data": in_data["Real World Data"].copy()}
    trial_summary_params_data = {
        "Trial Summary Parameters": in_data["Trial Summary Parameters"].copy()
    }
    arms_data = in_data["Arms, Elements & Visits"].copy()
    output_data = {"Output": in_data["Output"].copy()}
    output_data["Output"]["Types"] = ", ".join(
        [x.capitalize() for x in output_data["Output"]["Types"]]
    )

    # Get new folder name
    trial_folder_name = (
        f"{current_app.config['CT_DOWNLOADS_PATH']}{output_data['Output']['File Name']}"
    )

    # Create new trial folder
    os.system(f"mkdir {trial_folder_name}")

    # Copy Sphinx template
    os.system(
        f"cp -R {current_app.config['CT_DOWNLOADS_PATH']}sphinx {trial_folder_name}"
    )
    sphinx_folder_name = f"{trial_folder_name}/sphinx/"

    # Process each group to the correct format
    demography_new_data = func_nihpo_transform_data_to_sphinx_format(
        "Demography", demography_data
    )
    countries_new_data = func_nihpo_transform_data_to_sphinx_format(
        "Countries", countries_data
    )
    rwd_data_new_data = func_nihpo_transform_data_to_sphinx_format(
        "Real World Data", rwd_data
    )
    trial_summary_params_new_data = func_nihpo_transform_data_to_sphinx_format(
        "Trial Parameters", trial_summary_params_data
    )
    arms_new_data = func_nihpo_transform_arms_to_sphinx_format(
        arms_data, in_widths=[None, None, "5 5 5 10 10 5 10"]
    )
    output_new_data = func_nihpo_transform_data_to_sphinx_format("Output", output_data)

    # Create each .rst file
    func_nihpo_create_sphinx_doc(
        demography_new_data, sphinx_folder_name + "demography.rst"
    )
    func_nihpo_create_sphinx_doc(
        countries_new_data, sphinx_folder_name + "countries.rst"
    )
    func_nihpo_create_sphinx_doc(rwd_data_new_data, sphinx_folder_name + "rwd.rst")
    func_nihpo_create_sphinx_doc(
        trial_summary_params_new_data,
        sphinx_folder_name + "trial_summary_parameters.rst",
    )
    func_nihpo_create_sphinx_doc(arms_new_data, sphinx_folder_name + "arms.rst")
    func_nihpo_create_sphinx_doc(output_new_data, sphinx_folder_name + "output.rst")

    # Create PDF
    print(
        f"sphinx-build -b latex {sphinx_folder_name} {sphinx_folder_name}_build/latex/"
    )
    print(f"(cd {sphinx_folder_name} && make latexpdf)")
    os.system(
        f"sphinx-build -b latex {sphinx_folder_name} {sphinx_folder_name}_build/latex/"
    )
    os.system(f"(cd {sphinx_folder_name} && make latexpdf)")

    return f"{sphinx_folder_name}_build/latex/trial_parameters.pdf"
