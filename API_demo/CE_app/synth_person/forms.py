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
from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, NumberRange, InputRequired, StopValidation
from flask_babel import _, lazy_gettext as _l
from flask_login import current_user
from CE_app.models import Files

class Country(Form):
    CT_COUNTRIES = [('NC', 'Not chosen'),('af', 'Afghanistan'),('al', 'Albania'),('dz', 'Algeria'),('ad', 'Andorra'),('ao', 'Angola'),('ag', 'Antigua and Barbuda'),('ar', 'Argentina'),('am', 'Armenia'),('au', 'Australia'),('at', 'Austria'),('az', 'Azerbaijan'),('bs', 'Bahamas, The'),('bh', 'Bahrain'),('bd', 'Bangladesh'),('bb', 'Barbados'),('by', 'Belarus'),('be', 'Belgium'),('bz', 'Belize'),('bj', 'Benin'),('bm', 'Bermuda'),('bt', 'Bhutan'),('bo', 'Bolivia'),('ba', 'Bosnia and Herzegovina'),('bw', 'Botswana'),('br', 'Brazil'),('bn', 'Brunei'),('bg', 'Bulgaria'),('bf', 'Burkina Faso'),('mm', 'Burma'),('bi', 'Burundi'),('cv', 'Cabo Verde'),('kh', 'Cambodia'),('cm', 'Cameroon'),('ca', 'Canada'),('cf', 'Central African Republic'),('td', 'Chad'),('cl', 'Chile'),('cn', 'China'),('co', 'Colombia'),('km', 'Comoros'),('cg', 'Congo (Brazzaville)'),('cd', 'Congo (Kinshasa)'),('cr', 'Costa Rica'),('ci', 'Côte d’Ivoire'),('hr', 'Croatia'),('cu', 'Cuba'),('cy', 'Cyprus'),('cz', 'Czechia'),('dk', 'Denmark'),('dj', 'Djibouti'),('dm', 'Dominica'),('do', 'Dominican Republic'),('ec', 'Ecuador'),('eg', 'Egypt'),('sv', 'El Salvador'),('gq', 'Equatorial Guinea'),('er', 'Eritrea'),('ee', 'Estonia'),('sz', 'Eswatini'),('et', 'Ethiopia'),('fo', 'Faroe Islands'),('fj', 'Fiji'),('fi', 'Finland'),('fr', 'France'),('pf', 'French Polynesia'),('ga', 'Gabon'),('gm', 'Gambia, The'),('ge', 'Georgia'),('de', 'Germany'),('gh', 'Ghana'),('gr', 'Greece'),('gl', 'Greenland'),('gd', 'Grenada'),('gt', 'Guatemala'),('gn', 'Guinea'),('gw', 'Guinea-Bissau'),('gy', 'Guyana'),('ht', 'Haiti'),('hn', 'Honduras'),('hu', 'Hungary'),('is', 'Iceland'),('in', 'India'),('id', 'Indonesia'),('ir', 'Iran'),('iq', 'Iraq'),('ie', 'Ireland'),('il', 'Israel'),('it', 'Italy'),('jm', 'Jamaica'),('jp', 'Japan'),('jo', 'Jordan'),('kz', 'Kazakhstan'),('ke', 'Kenya'),('kp', 'Korea, North'),('kr', 'Korea, South'),('xk', 'Kosovo'),('kw', 'Kuwait'),('kg', 'Kyrgyzstan'),('la', 'Laos'),('lv', 'Latvia'),('lb', 'Lebanon'),('ls', 'Lesotho'),('lr', 'Liberia'),('ly', 'Libya'),('li', 'Liechtenstein'),('lt', 'Lithuania'),('lu', 'Luxembourg'),('mg', 'Madagascar'),('mw', 'Malawi'),('my', 'Malaysia'),('mv', 'Maldives'),('ml', 'Mali'),('mt', 'Malta'),('mh', 'Marshall Islands'),('mr', 'Mauritania'),('mu', 'Mauritius'),('mx', 'Mexico'),('fm', 'Micronesia, Federated States of'),('md', 'Moldova'),('mn', 'Mongolia'),('me', 'Montenegro'),('ms', 'Montserrat'),('ma', 'Morocco'),('mz', 'Mozambique'),('na', 'Namibia'),('nr', 'Nauru'),('np', 'Nepal'),('nl', 'Netherlands'),('nc', 'New Caledonia'),('nz', 'New Zealand'),('ni', 'Nicaragua'),('ne', 'Niger'),('ng', 'Nigeria'),('mk', 'North Macedonia'),('no', 'Norway'),('om', 'Oman'),('pk', 'Pakistan'),('pw', 'Palau'),('pa', 'Panama'),('pg', 'Papua New Guinea'),('py', 'Paraguay'),('pe', 'Peru'),('ph', 'Philippines'),('pl', 'Poland'),('pt', 'Portugal'),('qa', 'Qatar'),('ro', 'Romania'),('ru', 'Russia'),('rw', 'Rwanda'),('sh', 'Saint Helena, Ascension, and Tristan da Cunha'),('kn', 'Saint Kitts and Nevis'),('lc', 'Saint Lucia'),('vc', 'Saint Vincent and the Grenadines'),('ws', 'Samoa'),('sm', 'San Marino'),('st', 'Sao Tome and Principe'),('sa', 'Saudi Arabia'),('sn', 'Senegal'),('rs', 'Serbia'),('sc', 'Seychelles'),('sl', 'Sierra Leone'),('sk', 'Slovakia'),('si', 'Slovenia'),('sb', 'Solomon Islands'),('so', 'Somalia'),('za', 'South Africa'),('ss', 'South Sudan'),('es', 'Spain'),('lk', 'Sri Lanka'),('sd', 'Sudan'),('sr', 'Suriname'),('se', 'Sweden'),('ch', 'Switzerland'),('sy', 'Syria'),('tw', 'Taiwan'),('tj', 'Tajikistan'),('tz', 'Tanzania'),('th', 'Thailand'),('tl', 'Timor-Leste'),('tg', 'Togo'),('to', 'Tonga'),('tt', 'Trinidad and Tobago'),('tn', 'Tunisia'),('tr', 'Turkey'),('tm', 'Turkmenistan'),('tv', 'Tuvalu'),('ug', 'Uganda'),('ua', 'Ukraine'),('ae', 'United Arab Emirates'),('gb', 'United Kingdom'),('us', 'United States'),('uy', 'Uruguay'),('uz', 'Uzbekistan'),('vu', 'Vanuatu'),('ve', 'Venezuela'),('vn', 'Vietnam'),('wf', 'Wallis and Futuna'),('ye', 'Yemen'),('zm', 'Zambia'),('zw', 'Zimbabwe')]
    country = SelectField('Country', choices=CT_COUNTRIES)
    number = IntegerField('Number Subjects:')
    
def select_countries_form_generator(current_app):
    class SelectCountries(FlaskForm):
        country = FieldList(FormField(Country), min_entries=1, max_entries=current_app.config['CT_MAXIMUM_NUMBER_SUBJECTS_PER_COUNTRY'])
        add = SubmitField('Add')
        remove = SubmitField('Remove')
        submit = SubmitField('Continue')

        def validate_submit(self, filed):
            if not self.submit.data:
                raise StopValidation()
            countries = []
            for i in self.country.data:
                if not i['number'] or i['country']=='NC':
                    raise ValidationError('You must choose at least one country with a correct number of subjects')
                if i['country'] in countries:
                    raise ValidationError('Please do not reapeat countries')
                if i['number'] > current_app.config['CT_MAXIMUM_NUMBER_SUBJECTS_PER_COUNTRY']:
                    raise ValidationError('The maximum number of subjects per country is %d, if you want to create more please contact us to obtain an enterprise edition' % current_app.config['CT_MAXIMUM_NUMBER_SUBJECTS_PER_COUNTRY'])
                countries.append(i['country'])
    return SelectCountries()

def synthetic_person_form_generator(current_app):
    class CreateSyntheticPersonForm(FlaskForm):

        # Create fields
        output_file_name = StringField('File Name:', validators=[DataRequired()])
        # (To do): Create a correct field where choosing a distribution of gender in percentage.
        female = IntegerField('% Female:', validators=[InputRequired(), NumberRange(min=0, max=100)])
        male = IntegerField('% Male:', validators=[InputRequired(), NumberRange(min=0, max=100)])
        min_age = IntegerField('Minimum Age:', validators=[InputRequired(), NumberRange(min=0, max=120)])
        max_age = IntegerField('Maximum Age:', validators=[InputRequired(), NumberRange(min=0, max=120)])
        output_type = SelectField('Output Type:', choices=[('SQLITE3', 'SQLite3'), ('JSON', 'JSON')])
        submit = SubmitField('Submit PHR')

        def validate_max_age(self, filed):
            next_validation = True
            try:
                filed.data = int(filed.data)
            except:
                next_validation = False
            try:
                self.min_age.data = int(self.min_age.data)
            except:
                next_validation = False
            if next_validation:
                if filed.data < self.min_age.data:
                    raise ValidationError('Maximum age must be higher or equal minimum age.')
        def validate_male(self, filed):
            next_validation = True
            try:
                filed.data = int(filed.data)
            except:
                next_validation = False
            try:
                self.female.data = int(self.female.data)
            except:
                next_validation = False
            if next_validation:
                if (filed.data + self.female.data) != 100:
                    raise ValidationError('The sum of % female and male must be equal to 100.')
        if current_app.env == 'production' or current_app.env == 'development':
            def validate_output_file_name(self, filed):
                files = Files.query.filter_by(user_id=current_user.id, module = "PERSON").all()
                for file in files:
                    if filed.data == file.file_name:
                        if file.file_status == 'Created':
                            raise ValidationError('The name of the file is already in use, please use a different one')
                        elif file.file_status == 'Pending':
                            raise ValidationError('There is a file being created with that name, please use a different one')
                for character in filed.data:
                    if character in current_app.config['CT_SPECIAL_CHARACTERS_TO_AVOID']:
                        raise ValidationError(f"Please do not use special characters in the file name ({current_app.config['CT_SPECIAL_CHARACTERS_TO_AVOID_STRING']})")
    return CreateSyntheticPersonForm()