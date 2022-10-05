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
from flask import render_template, current_app
from CE_app.email import send_email
from CE_app.nihpo_functions import func_nihpo_html_format_countries
from bs4 import BeautifulSoup

def send_person_file_downloaded(in_first_name, in_last_name, in_email, in_file_name, in_data, in_countries, in_country_names):
    """
    Send an email to the user with the link to reset his/her password
    
    :param user: User created in the DB
    :type user: User
    :returns: Nothing.
    :rtype:
    """
    url_server = current_app.config['URL_SERVER']
    countries_html = func_nihpo_html_format_countries(in_countries, in_country_names)
    with open(current_app.config['APP_NAME'] + '/CE_app/templates/email/download_person_file.html', 'r') as f:

        html_template = f.read()

        soup = str(BeautifulSoup(html_template, 'lxml'))
        new_html_template = soup.format(first_name=in_first_name, last_name=in_last_name, file_name=in_file_name, url_server=url_server, min_age=in_data['Min Age'], max_age=in_data['Max Age'],
                female=in_data['Female'], male=in_data['Male'], countries_html=countries_html)
        send_email('Your Synthetic Person data file is ready for download.',
            in_sender=current_app.config['ADMINS'][0],
            in_recipients=[in_email],
            in_text_body=render_template('email/download_person_file.txt'),
            in_html_body=new_html_template)