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
from flask import current_app
from wtforms import Form, StringField, SubmitField, SelectField, IntegerField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
from flask_babel import _, lazy_gettext as _l
from datetime import date

today = date.today()

date_format = '%Y-%m-%d'
inclusion = 'Inclusion Criteria'
exclusion = 'Exclusion Criteria'

class TA_Arm(Form):
    description = StringField('Description:')
    code = StringField('Code:', validators = [Length(min=1, max=20)])

class TA_Element(Form):
    description = StringField('Description:')
    code = StringField('Code:', validators = [Length(min=1, max=8)])

def synthetic_creates_trial_form_generator(current_user):
    class CreateSyntheticTrialForm(FlaskForm):
        # To show description text into field: 'render_kw={"placeholder": "test"}''
        file_choices = [('NONE', 'NONE')]
        files = current_user.files.all()
        for file in files:
            if file.file_type == 'SQLITE3' and file.file_status == 'Created':
                file_choices.append((file.file_name + '.' + file.file_type.lower(), file.file_name + '(%s)' % file.file_type))
        phr_files = SelectField('PHR Files:', choices=file_choices)
        study_id = StringField('Study ID:', validators=[DataRequired()])
        trial_name = StringField('Trial Name:', validators=[DataRequired()])
        sponsor = StringField('Clinical Study Sponsor:', validators=[DataRequired()], description='An entity that is responsible for the initiation, management, and/or financing of a clinical study.')
        
        start_date= DateField('Start Date:', format=date_format, validators=[DataRequired("Format: Y-m-d Example: 1990-03-25")])
        end_date = DateField('End Date:', format=date_format, validators=[DataRequired("Format: Y-m-d Example: 1990-03-25")])
        
        planned_num_subjects = IntegerField('Planned Number of Subjects:', validators=[DataRequired('An integer is required for number of subjects')], description='The planned number of subjects to be entered in a clinical trial.')
        planned_number_arms = IntegerField('Planned Number of Arms:', validators=[DataRequired('An integer is required for number of arms')], description='The planned number of intervention groups.')
        # actual_num_subjects = IntegerField('Actual Number of Subjects:', validators=[DataRequired('An integer is required for actual number of subjects')], description='Actual number of subjects enrolled; may include subjects who were not randomized.')
        num_groups = IntegerField('Number of Groups/Cohorts:', validators=[DataRequired('An integer is required for number of groups')], description='The number of groups or cohorts that are part of the study.')
        trial_length = IntegerField('Length observation for each subject:', validators=[DataRequired('An integer is required for trial length')], description='Planned length of observation for a single subject.')
        trial_primary_obj = StringField('Trial Primary Objective:', validators=[DataRequired()], description='The principal purpose of the trial.')
        trial_secondary_obj = StringField('Trial Secondary Objective:', validators=[DataRequired()], description='The auxiliary purpose of the trial.')
        trial_type = SelectField('Trial Type:',choices=current_app.config['CT_TRIAL_TYPE_OPTIONS'], description='The nature of the interventional study for which information is being collected.')
        study_type = SelectField('Study Type:', choices=current_app.config['CT_STUDY_TYPE_OPTIONS'], description='The nature of the investigation for which study information is being collected.')
        ther_area = StringField('Therapeutic Area:', validators=[DataRequired()], description='A knowledge field that focuses on research and development of specific treatments for diseases and pathologic findings, as well as prevention of conditions that negatively impact the health of an individual.')

        stop_rules = StringField('Study Stop Rules:', validators=[DataRequired()], description='The rule, regulation and/or condition that determines the point in time when a clinical trial will be terminated.')
        trial_blinding_schema = SelectField('Trial Blinding Schema:', choices=current_app.config['CT_TRIAL_BLINDING_SCHEMA_OPTIONS'], description='The type of experimental design used to describe the level of awareness of the clinical trial subjects and/or investigators of the intervention(s) that they are receiving and/or administering.')
        control_type = SelectField('Control Type:', choices=current_app.config['CT_CONTROL_TYPE_OPTIONS'], description='Comparator against which the study treatment is evaluated.')
        trial_phase_classification = SelectField('Trial Phase Classification:', choices=current_app.config['CT_TRIAL_PHASE_OPTIONS'], description='Any defined stage in the lifecycle of a clinical trial.')
        
        primary_outcome_measure = StringField('Primary Outcome Measure:', validators=[DataRequired()], description='The outcome measure(s) of greatest importance specified in the protocol, usually the one(s) used in the power calculation, to evaluate the primary endpoint(s) associated with the primary study objective(s). ')
        number_sites_per_country = IntegerField('Number of sites per country:', validators=[DataRequired(), NumberRange(min=1, max=5)])
        adaptative_design = StringField('Adaptive Design:', description='Indicate if the study includes a prospectively planned opportunity for modification of one or more specified aspects of the study design and hypotheses based on analysis of data (usually interim data) from subjects in the study.')
        data_cutoff_date = DateField('Data Cutoff Date:', format=date_format, validators=[DataRequired()], description='A date which indicates any data collected by this date will be used for analysis.')
        data_cutoff_desc = StringField('Data Cutoff Description:', validators=[DataRequired()], description='Text that describes the cutoff date.')
        
        registry_id = StringField('Registry Identifier:', validators=[DataRequired()], description='Identification numbers assigned to the protocol by clinicaltrials.gov, EudraCT, or other registries.')
        
        test_product_added = BooleanField('Added on to Existing Treatments:', description='An indication that an investigational drug or substance has been added to the existing treatment regimen.')
        randomized = BooleanField('Randomized:', description='The process of assigning trial subjects to treatment or control groups using an element of chance to determine the assignments in order to reduce bias. NOTE: Unequal randomization is used to allocate subjects into groups at a differential rate; for example, three subjects may be assigned to a treatment group for every one assigned to the control group. [ICH E6 1.48] See also balanced study.')
        ex_trial_id = BooleanField('Extension Trial Indicator:', description='An indication as to whether the clinical trial is an extension trial.')
        ped_study_id = BooleanField('Pediatric Study Indicator:', description='An indication as to whether the study is a pediatric study.')
        ped_inv_plan_id = BooleanField('Pediatric Investigation Plan Indicator:', description='An indication as to whether the trial is part of a pediatric investigation plan (PIP).')
        ped_postmark_study_id = BooleanField('Pediatric Postmarket Study Indicator:', description='An indication as to whether the study is a pediatric postmarket study.')
        rare_disease_id = BooleanField('Rare Disease Indicator:', description='An indication as to whether the subject has minimal residual disease.')
        healthy_subj_id = BooleanField('Healthy Subject Indicator:', description='Indicate if persons who have not had the condition(s) being studied or otherwise related conditions or symptoms, as specified in the eligibility requirements, may participate in the study.')

        sdtm_ig_version = StringField('SDTM IG Version:', validators=[DataRequired()], description='The version of the CDISC Study Data Tabulation Model implementation guide that is being used in the study submission.')
        sdtm_version = StringField('SDTM Version:', validators=[DataRequired()], description='The version of the CDISC Study Data Tabulation Model that is being used in the study submission.')

        submit = SubmitField('Continue')

        # def validate_start_date(self, filed):
        #     if filed.data <= today:
        #         raise ValidationError(_("Start date must be after today's date"))

        def validate_end_date(self, filed):
            if filed.data <= self.start_date.data:
                raise ValidationError(_('End date must be after start date'))
            if (filed.data - self.start_date.data).days <= 50:
                raise ValidationError(_('Trial length must be bigger than 50 days, please choose a broader range'))
        
        def validate_data_cutoff_date(self, filed):
            if filed.data <= self.start_date.data or filed.data >= self.end_date.data:
                raise ValidationError(_('Cut off date must be between start and end dates'))

        def validate_trial_length(self, filed):
            if (self.end_date.data - self.start_date.data).days < filed.data:
                raise ValidationError(_("Length of observation must not exceed the number of days between start date and end date"))
            if filed.data <= 50:
                raise ValidationError(_("Length of observation must be bigger than 50"))

    return CreateSyntheticTrialForm()

def synthetic_trial_output(current_user, current_app):
    class SyntheticTrialOutput(FlaskForm):
        output_file_name = StringField('File Name:', validators=[DataRequired()])
        sqlite = BooleanField('SQLite3')
        csv = BooleanField('csv')
        sas = BooleanField('SAS XPORT files')
        submit = SubmitField('Submit Trial')

        if current_app.env == 'production' or current_app.env == 'development':
            def validate_output_file_name(self, filed):
                files = current_user.files.all()
                for file in files:
                    if filed.data == file.file_name:
                        if file.file_status == 'Created':
                            raise ValidationError('The name of the file is already in use, please use a different one')
                        elif file.file_status == 'Pending':
                            raise ValidationError('There is a file being created with that name, please use a different one')
                for character in filed.data:
                    if character in current_app.config['CT_SPECIAL_CHARACTERS_TO_AVOID']:
                        raise ValidationError('Please do not use special characters in the output file name (%s)' % current_app.config['CT_SPECIAL_CHARACTERS_TO_AVOID_STRING'])

        def validate_sqlite(self, filled):
            if not (self.csv.data or filled.data or self.sas.data):
                raise ValidationError(_('Please choose at least one output type'))

    return SyntheticTrialOutput()

class SyntheticTrialArmsElementsVisits(FlaskForm):
    download = SubmitField('Download Sample File')

class SyntheticTrialVariablesNotControlled(FlaskForm):
    download = SubmitField('Download Sample File')

class SyntheticTrialTEForm(FlaskForm):
    inclusion = StringField(inclusion, validators=[DataRequired()])
    exclusion = StringField(exclusion, validators=[DataRequired()])
    submit = SubmitField('Submit TE')

class SyntheticTrialTVForm(FlaskForm):
    inclusion = StringField(inclusion, validators=[DataRequired()])
    exclusion = StringField(exclusion, validators=[DataRequired()])
    submit = SubmitField('Submit TV')


