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
import os
from dotenv import load_dotenv

CT_NOTE_VERSION = "21.03"

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

APP_NAME = os.path.dirname(os.path.abspath(__file__))[:-7]
SQLALCHEMY_TRACK_MODIFICATIONS = False

SESSION_TYPE = "redis"

MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")

# App environments
APP_ENV_LOCAL = "local"
APP_ENV_TESTING = "testing"
APP_ENV_DEVELOPMENT = "development"
APP_ENV_PROFILE = "profile"
APP_ENV_PRODUCTION = "production"
APP_ENV = ""
DEBUG = False
PROFILE = False

# Show logs:
CT_LOGS = False

# Days to remove old files:
CT_DAYS_TO_DELETE_FILES = 60

# Maximum number od subjects per country:
CT_MAXIMUM_NUMBER_SUBJECTS_PER_COUNTRY = 1000

SECRET_KEY = "adancbvvsbjkv733285s823@njdnq8"
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:nihpoQWERTYU27@localhost:5432/api_nihpo'
SQLALCHEMY_SCHEMA = "user"
LANGUAGES = ["en", "es"]
CT_DOWNLOADS_PATH = '/home/nihpo/venv/downloads/'

# Flask Profiler settings
CT_PROFILER_USER = "O1nCuW85If"
CT_PROFILER_PASSWORD = "ba33db97-8fb6-44f4-ab55-2c0150fd04ad"

# Mail settings
MAIL_SERVER = "smtp.office365.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "nihpo_portal@nihpo.com"
MAIL_PASSWORD = "Te%$xn904%^"

# The ADMINS variable has to be a list with 2 parameters. First parameter is for the subject information. Second parameter is the mail address.
ADMINS = ["NIHPO Portal (nihpo_portal@nihpo.com)", "nihpo_portal@nihpo.com"]

# Variables to connect to the API NIHPO PostgreSQL
CT_DATABASE_HOST = "localhost"
CT_DATABASE_PORT = 5432
CT_DATABASE = "api_nihpo"
CT_DATABASE_USER = "postgres"
CT_DATABASE_PASSWORD = "nihpoQWERTYU27"

# These are variables to choose the PostgreSQL server where creating users.
CT_DATABASE_PODR = "nihpo"
CT_DATABASE_PODR_USER = "postgres"
CT_DATABASE_PODR_PASSWORD = "dTF2Etwt9inYCMSzKo"
CT_DATABASE_PODR_HOST = "52.186.82.150"
CT_DATABASE_PODR_PORT = "5432"

# Accesible URL for PODR database
CT_DATABASE_PODR_URL = "https://podr.phuse.global/"

# Variables to use Celery
CT_CELERY_BROKER_URL = "redis://localhost:6379"
CT_CELERY_RESULT_BACKEND = "redis://localhost:6379"

# Variables to use Kong
CT_PORTAL = False
CT_KONG_HOST = "localhost"
CT_KONG_PORT_ADMIN = "8001"
CT_KONG_PORT_USER = "8000"

# These are variables to set the format of the Synthetic PHR creation.
CT_CIVIL_STATUS = ["Single", "Married", "Divorced", "Widowed"]
CT_NUMBER_FREE_RECORDS = 10
CT_NUMBER_DRUGS_EMA_PER_PERSON = 15
CT_NUMBER_DRUGS_PRE_PER_PERSON = 5
CT_NUMBER_DRUGS_OTC_PER_PERSON = 5
CT_NUMBER_DRUGS_OTHER_PER_PERSON = 5
CT_NUMBER_CONDITIONS_PER_PERSON = 5
CT_NUMBER_PROVIDERS_PER_PERSON = 5
CT_NUMBER_LAB_RESULTS_PER_PERSON = 5
CT_NUMBER_VITALS_PRE_PER_PERSON = 5
CT_NUMBER_PROCEDURES_PER_PERSON = 5
CT_NUMBER_DEVICES_PER_PERSON = 5

"""Variables to set the format of the Synthetic Trial design creation, 
they will be removed when the option to let the user develop a full customized design is available"""

# General variables
CT_PROBABILITY_DEAD_DURING_TRIAL = 0.025
CT_NUMBER_VISIT_MEASUREMENTS = 2
CT_NUMBER_AES = 2
CT_NUMBER_FINDINGS = 2

# Trial summary lists choices
CT_STUDY_TYPE_OPTIONS = [
    "EXPANDED ACCESS",
    "INTERVENTIONAL",
    "OBSERVATIONAL",
    "PATIENT REGISTRY",
]
CT_TRIAL_TYPE_OPTIONS = [
    "ADHESION PERFORMANCE",
    "ALCOHOL EFFECT",
    "BIO-AVAILABILITY",
    "BIO-EQUIVALENCE",
    "BIOSIMILARITY",
    "DEVICE-DRUG INTERACTION",
    "DIAGNOSIS",
    "DOSE FINDING",
    "DOSE PROPORTIONALITY",
    "DOSE RESPONSE",
    "DRUG-DRUG INTERACTION",
    "EFFICACY",
    "FOOD EFFECT",
    "IMMUNOGENICITY",
    "PHARMACODYNAMIC",
    "PHARMACOECONOMIC",
    "PHARMACOGENETIC",
    "PHARMACOGENOMIC",
    "PHARMACOKINETIC",
    "POSITION EFFECT",
    "PREVENTION",
    "REACTOGENICITY",
    "SAFETY",
    "SWALLOWING FUNCTION",
    "THOROUGH QT",
    "TOLERABILITY",
    "TREATMENT",
    "USABILITY TESTING",
    "WATER EFFECT",
]
CT_CONTROL_TYPE_OPTIONS = ["ACTIVE", "DOSE RESPONSE", "NONE", "PLACEBO"]
CT_TRIAL_PHASE_OPTIONS = [
    "NOT APPLICABLE",
    "PHASE 0 TRIAL",
    "PHASE I TRIAL",
    "PHASE I/II TRIAL",
    "PHASE II TRIAL",
    "PHASE II/III TRIAL",
    "PHASE IIA TRIAL",
    "PHASE IIB TRIAL",
    "PHASE III TRIAL",
    "PHASE IIIA TRIAL",
    "PHASE IIIB TRIAL",
    "PHASE IV TRIAL",
    "PHASE V TRIAL",
]
CT_TRIAL_BLINDING_SCHEMA_OPTIONS = [
    "DOUBLE BLIND",
    "OPEN LABEL",
    "OPEN LABEL TO TREATMENT AND DOUBLE BLIND TO IMP DOSE",
    "SINGLE BLIND",
]

# Assessments variables
CT_NUMBER_PLANNED_ASSESSMENT_SCHEDULE = 5
CT_MAX_NUMBER_ACTUAL_ASSESSMENTS = [2, 6, 4, 5, 3]

# Disease milestones variables
CT_NUMBER_DISEASE_MILESTONES = 3
CT_DISEASE_MILESTONES_TYPE = ["DIAGNOSIS", "HYPOGLYCEMIC EVENT", "HYPERGLYCEMIC EVENT"]
CT_DISEASE_MILESTONES_DEFINITION = [
    "Initial diagnosis of diabetes, the first time a physician told the subject they had diabetes",
    "Hypoglicemic event, the occurrence of a glucose level below (threshold level)",
    "Hyperglicemic event, the occurrence of a glucose level above (threshold level)",
]

# Inclusion/exclusion variables
CT_NUMBER_INCLUSION_CRITERIA = 2
CT_NUMBER_EXCLUSION_CRITERIA = 1
CT_INCLUSION_CRITERIA = [
    ["INCLUSION", "INCL1", "Has disease under study"],
    ["INCL2", "Age 21 or greater"],
]
CT_EXCLUSION_CRITERIA = [["EXCLUSION", "EXCL1", "Pregnant or lactating"]]
CT_INCLUSION_EXCLUSION = [
    ["INCLUSION", "INCL1", "Has disease under study"],
    ["INCLUSION", "INCL2", "Age 21 or greater"],
    ["EXCLUSION", "EXCL1", "Pregnant or lactating"],
]

# Summary variables
CT_LIST_TS_PARAMETERS = [
    ("SSTDTC", "Study Start Date"),
    ("SENDTC", "Study End Date"),
    ("ACTSUB", "Actual Number of Subjects"),
    ("ADDON", "Added on to Existing Treatments"),
    ("AGEMAX", "Planned Maximum Age of Subjects"),
    ("AGEMIN", "Planned Minimum Age of Subjects"),
    ("LENGTH", "Trial Length"),
    ("PLANSUB", "Planned Number of Subjects"),
    ("RANDOM", "Trial is Randomized"),
    ("SEXPOP", "Sex of Participants"),
    ("STOPRULE", "Study Stop Rules"),
    ("TBLIND", "Trial Blinding Schema"),
    ("TCNTRL", "Control Type"),
    ("TITLE", "Trial Title"),
    ("TPHASE", "Trial Phase Classification"),
    ("TTYPE", "Trial Type"),
    ("OBJPRIM", "Trial Primary Objective"),
    ("SPONSOR", "Clinical Study Sponsor"),
    ("OUTMSPRI", "Primary Outcome Measure"),
    ("ADAPT", "Adaptive Design"),
    ("DCUTDTC", "Data Cutoff Date"),
    ("DCUTDESC", "Data Cutoff Description"),
    ("NARMS", "Planned Number of Arms"),
    ("STYPE", "Study Type"),
    ("REGID", "Registry Identifier"),
    ("EXTTIND", "Extension Trial Indicator"),
    ("NCOHORT", "Number of Groups/Cohorts"),
    ("OBJSEC", "Trial Secondary Objective"),
    ("PDPSTIND", "Pediatric Postmarket Study Indicator"),
    ("PDSTIND", "Pediatric Study Indicator"),
    ("PIPIND", "Pediatric Investigation Plan Indicator"),
    ("RDIND", "Rare Disease Indicator"),
    ("SDTIGVER", "SDTM IG Version"),
    ("SDTMVER", "SDTM Version"),
    ("THERAREA", "Therapeutic Area"),
    ("HLTSUBJI", "Healthy Subject Indicator"),
    ("FCNTRY", "Planned Country of Investigational Sites"),
]
CT_TS_FIELDS_MATCH_CODE = [
    "ADDON",
    "RANDOM",
    "EXTTIND",
    "PDSTIND",
    "PIPIND",
    "PDPSTIND",
    "RDIND",
    "HLTSUBJI",
    "SEXPOP",
    "STYPE",
    "TCNTRL",
    "TTYPE",
    "TPHASE",
    "TBLIND",
]

# --TPT, --TPTREF, --TPTNUM variables
CT_TPT_PARAMETERS = [
    (1, "PREVIUOUS DOSE", "PREVIOUS DOSE"),
    (2, "PREVIOUS MEAL", "PREVIOUS MEAL"),
]

# Fields to fix when an Adverse Event is serious or not
CT_SERIOUS_ADVERSE_EVENT_FIELDS = [
    "AESCAN",
    "AESCONG",
    "AESDISAB",
    "AESHOSP",
    "AESLIFE",
    "AESMIE",
]

# Values for SSSTRESC when subject doesn't die during the trial
CT_SSSTRESC_VALUES_NOT_DIE = ["ALIVE", "UNKNOWN"]

# Path of the JSON file as sample to fill variables with Controlled_Terms = '*'
CT_JSON_SAMPLE_CONTROLLED_TERMINOLOGY = (
    APP_NAME + "/resources/controlled_terminology.zip"
)
CT_JSON_SAMPLE_ARMS_ELEMENTS_VISITS = APP_NAME + "/resources/arms_elements_visits.zip"
CT_JSON_SAMPLE_CONTROLLED_TERMINOLOGY_DECOMPRESSED = (
    APP_NAME + "/resources/controlled_terminology.json"
)
CT_JSON_SAMPLE_ARMS_ELEMENTS_VISITS_DECOMPRESSED = (
    APP_NAME + "/resources/arms_elements_visits.json"
)

# Countries choices
CT_COUNTRIES = [
    ("NC", "Not chosen"),
    ("af", "Afghanistan"),
    ("al", "Albania"),
    ("dz", "Algeria"),
    ("ad", "Andorra"),
    ("ao", "Angola"),
    ("ag", "Antigua and Barbuda"),
    ("ar", "Argentina"),
    ("am", "Armenia"),
    ("au", "Australia"),
    ("at", "Austria"),
    ("az", "Azerbaijan"),
    ("bs", "Bahamas, The"),
    ("bh", "Bahrain"),
    ("bd", "Bangladesh"),
    ("bb", "Barbados"),
    ("by", "Belarus"),
    ("be", "Belgium"),
    ("bz", "Belize"),
    ("bj", "Benin"),
    ("bm", "Bermuda"),
    ("bt", "Bhutan"),
    ("bo", "Bolivia"),
    ("ba", "Bosnia and Herzegovina"),
    ("bw", "Botswana"),
    ("br", "Brazil"),
    ("bn", "Brunei"),
    ("bg", "Bulgaria"),
    ("bf", "Burkina Faso"),
    ("mm", "Burma"),
    ("bi", "Burundi"),
    ("cv", "Cabo Verde"),
    ("kh", "Cambodia"),
    ("cm", "Cameroon"),
    ("ca", "Canada"),
    ("cf", "Central African Republic"),
    ("td", "Chad"),
    ("cl", "Chile"),
    ("cn", "China"),
    ("co", "Colombia"),
    ("km", "Comoros"),
    ("cg", "Congo (Brazzaville)"),
    ("cd", "Congo (Kinshasa)"),
    ("cr", "Costa Rica"),
    ("ci", "Côte d’Ivoire"),
    ("hr", "Croatia"),
    ("cu", "Cuba"),
    ("cy", "Cyprus"),
    ("cz", "Czechia"),
    ("dk", "Denmark"),
    ("dj", "Djibouti"),
    ("dm", "Dominica"),
    ("do", "Dominican Republic"),
    ("ec", "Ecuador"),
    ("eg", "Egypt"),
    ("sv", "El Salvador"),
    ("gq", "Equatorial Guinea"),
    ("er", "Eritrea"),
    ("ee", "Estonia"),
    ("sz", "Eswatini"),
    ("et", "Ethiopia"),
    ("fo", "Faroe Islands"),
    ("fj", "Fiji"),
    ("fi", "Finland"),
    ("fr", "France"),
    ("pf", "French Polynesia"),
    ("ga", "Gabon"),
    ("gm", "Gambia, The"),
    ("ge", "Georgia"),
    ("de", "Germany"),
    ("gh", "Ghana"),
    ("gr", "Greece"),
    ("gl", "Greenland"),
    ("gd", "Grenada"),
    ("gt", "Guatemala"),
    ("gn", "Guinea"),
    ("gw", "Guinea-Bissau"),
    ("gy", "Guyana"),
    ("ht", "Haiti"),
    ("hn", "Honduras"),
    ("hu", "Hungary"),
    ("is", "Iceland"),
    ("in", "India"),
    ("id", "Indonesia"),
    ("ir", "Iran"),
    ("iq", "Iraq"),
    ("ie", "Ireland"),
    ("il", "Israel"),
    ("it", "Italy"),
    ("jm", "Jamaica"),
    ("jp", "Japan"),
    ("jo", "Jordan"),
    ("kz", "Kazakhstan"),
    ("ke", "Kenya"),
    ("kp", "Korea, North"),
    ("kr", "Korea, South"),
    ("xk", "Kosovo"),
    ("kw", "Kuwait"),
    ("kg", "Kyrgyzstan"),
    ("la", "Laos"),
    ("lv", "Latvia"),
    ("lb", "Lebanon"),
    ("ls", "Lesotho"),
    ("lr", "Liberia"),
    ("ly", "Libya"),
    ("li", "Liechtenstein"),
    ("lt", "Lithuania"),
    ("lu", "Luxembourg"),
    ("mg", "Madagascar"),
    ("mw", "Malawi"),
    ("my", "Malaysia"),
    ("mv", "Maldives"),
    ("ml", "Mali"),
    ("mt", "Malta"),
    ("mh", "Marshall Islands"),
    ("mr", "Mauritania"),
    ("mu", "Mauritius"),
    ("mx", "Mexico"),
    ("fm", "Micronesia, Federated States of"),
    ("md", "Moldova"),
    ("mn", "Mongolia"),
    ("me", "Montenegro"),
    ("ms", "Montserrat"),
    ("ma", "Morocco"),
    ("mz", "Mozambique"),
    ("na", "Namibia"),
    ("nr", "Nauru"),
    ("np", "Nepal"),
    ("nl", "Netherlands"),
    ("nc", "New Caledonia"),
    ("nz", "New Zealand"),
    ("ni", "Nicaragua"),
    ("ne", "Niger"),
    ("ng", "Nigeria"),
    ("mk", "North Macedonia"),
    ("no", "Norway"),
    ("om", "Oman"),
    ("pk", "Pakistan"),
    ("pw", "Palau"),
    ("pa", "Panama"),
    ("pg", "Papua New Guinea"),
    ("py", "Paraguay"),
    ("pe", "Peru"),
    ("ph", "Philippines"),
    ("pl", "Poland"),
    ("pt", "Portugal"),
    ("qa", "Qatar"),
    ("ro", "Romania"),
    ("ru", "Russia"),
    ("rw", "Rwanda"),
    ("sh", "Saint Helena, Ascension, and Tristan da Cunha"),
    ("kn", "Saint Kitts and Nevis"),
    ("lc", "Saint Lucia"),
    ("vc", "Saint Vincent and the Grenadines"),
    ("ws", "Samoa"),
    ("sm", "San Marino"),
    ("st", "Sao Tome and Principe"),
    ("sa", "Saudi Arabia"),
    ("sn", "Senegal"),
    ("rs", "Serbia"),
    ("sc", "Seychelles"),
    ("sl", "Sierra Leone"),
    ("sk", "Slovakia"),
    ("si", "Slovenia"),
    ("sb", "Solomon Islands"),
    ("so", "Somalia"),
    ("za", "South Africa"),
    ("ss", "South Sudan"),
    ("es", "Spain"),
    ("lk", "Sri Lanka"),
    ("sd", "Sudan"),
    ("sr", "Suriname"),
    ("se", "Sweden"),
    ("ch", "Switzerland"),
    ("sy", "Syria"),
    ("tw", "Taiwan"),
    ("tj", "Tajikistan"),
    ("tz", "Tanzania"),
    ("th", "Thailand"),
    ("tl", "Timor-Leste"),
    ("tg", "Togo"),
    ("to", "Tonga"),
    ("tt", "Trinidad and Tobago"),
    ("tn", "Tunisia"),
    ("tr", "Turkey"),
    ("tm", "Turkmenistan"),
    ("tv", "Tuvalu"),
    ("ug", "Uganda"),
    ("ua", "Ukraine"),
    ("ae", "United Arab Emirates"),
    ("gb", "United Kingdom"),
    ("us", "United States"),
    ("uy", "Uruguay"),
    ("uz", "Uzbekistan"),
    ("vu", "Vanuatu"),
    ("ve", "Venezuela"),
    ("vn", "Vietnam"),
    ("wf", "Wallis and Futuna"),
    ("ye", "Yemen"),
    ("zm", "Zambia"),
    ("zw", "Zimbabwe"),
]
CT_COUNTRIES_EMAIL = [
    ("Not chosen", "Not chosen"),
    ("Afghanistan", "Afghanistan"),
    ("Albania", "Albania"),
    ("Algeria", "Algeria"),
    ("Andorra", "Andorra"),
    ("Angola", "Angola"),
    ("Antigua and Barbuda", "Antigua and Barbuda"),
    ("Argentina", "Argentina"),
    ("Armenia", "Armenia"),
    ("Australia", "Australia"),
    ("Austria", "Austria"),
    ("Azerbaijan", "Azerbaijan"),
    ("Bahamas, The", "Bahamas, The"),
    ("Bahrain", "Bahrain"),
    ("Bangladesh", "Bangladesh"),
    ("Barbados", "Barbados"),
    ("Belarus", "Belarus"),
    ("Belgium", "Belgium"),
    ("Belize", "Belize"),
    ("Benin", "Benin"),
    ("Bermuda", "Bermuda"),
    ("Bhutan", "Bhutan"),
    ("Bolivia", "Bolivia"),
    ("Bosnia and Herzegovina", "Bosnia and Herzegovina"),
    ("Botswana", "Botswana"),
    ("Brazil", "Brazil"),
    ("Brunei", "Brunei"),
    ("Bulgaria", "Bulgaria"),
    ("Burkina Faso", "Burkina Faso"),
    ("Burma", "Burma"),
    ("Burundi", "Burundi"),
    ("Cabo Verde", "Cabo Verde"),
    ("Cambodia", "Cambodia"),
    ("Cameroon", "Cameroon"),
    ("Canada", "Canada"),
    ("Central African Republic", "Central African Republic"),
    ("Chad", "Chad"),
    ("Chile", "Chile"),
    ("China", "China"),
    ("Colombia", "Colombia"),
    ("Comoros", "Comoros"),
    ("Congo (Brazzaville)", "Congo (Brazzaville)"),
    ("Congo (Kinshasa)", "Congo (Kinshasa)"),
    ("Costa Rica", "Costa Rica"),
    ("Côte d’Ivoire", "Côte d’Ivoire"),
    ("Croatia", "Croatia"),
    ("Cuba", "Cuba"),
    ("Cyprus", "Cyprus"),
    ("Czechia", "Czechia"),
    ("Denmark", "Denmark"),
    ("Djibouti", "Djibouti"),
    ("Dominica", "Dominica"),
    ("Dominican Republic", "Dominican Republic"),
    ("Ecuador", "Ecuador"),
    ("Egypt", "Egypt"),
    ("El Salvador", "El Salvador"),
    ("Equatorial Guinea", "Equatorial Guinea"),
    ("Eritrea", "Eritrea"),
    ("Estonia", "Estonia"),
    ("Eswatini", "Eswatini"),
    ("Ethiopia", "Ethiopia"),
    ("Faroe Islands", "Faroe Islands"),
    ("Fiji", "Fiji"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("French Polynesia", "French Polynesia"),
    ("Gabon", "Gabon"),
    ("Gambia, The", "Gambia, The"),
    ("Georgia", "Georgia"),
    ("Germany", "Germany"),
    ("Ghana", "Ghana"),
    ("Greece", "Greece"),
    ("Greenland", "Greenland"),
    ("Grenada", "Grenada"),
    ("Guatemala", "Guatemala"),
    ("Guinea", "Guinea"),
    ("Guinea-Bissau", "Guinea-Bissau"),
    ("Guyana", "Guyana"),
    ("Haiti", "Haiti"),
    ("Honduras", "Honduras"),
    ("Hungary", "Hungary"),
    ("Iceland", "Iceland"),
    ("India", "India"),
    ("Indonesia", "Indonesia"),
    ("Iran", "Iran"),
    ("Iraq", "Iraq"),
    ("Ireland", "Ireland"),
    ("Israel", "Israel"),
    ("Italy", "Italy"),
    ("Jamaica", "Jamaica"),
    ("Japan", "Japan"),
    ("Jordan", "Jordan"),
    ("Kazakhstan", "Kazakhstan"),
    ("Kenya", "Kenya"),
    ("Korea, North", "Korea, North"),
    ("Korea, South", "Korea, South"),
    ("Kosovo", "Kosovo"),
    ("Kuwait", "Kuwait"),
    ("Kyrgyzstan", "Kyrgyzstan"),
    ("Laos", "Laos"),
    ("Latvia", "Latvia"),
    ("Lebanon", "Lebanon"),
    ("Lesotho", "Lesotho"),
    ("Liberia", "Liberia"),
    ("Libya", "Libya"),
    ("Liechtenstein", "Liechtenstein"),
    ("Lithuania", "Lithuania"),
    ("Luxembourg", "Luxembourg"),
    ("Madagascar", "Madagascar"),
    ("Malawi", "Malawi"),
    ("Malaysia", "Malaysia"),
    ("Maldives", "Maldives"),
    ("Mali", "Mali"),
    ("Malta", "Malta"),
    ("Marshall Islands", "Marshall Islands"),
    ("Mauritania", "Mauritania"),
    ("Mauritius", "Mauritius"),
    ("Mexico", "Mexico"),
    ("Micronesia, Federated States of", "Micronesia, Federated States of"),
    ("Moldova", "Moldova"),
    ("Mongolia", "Mongolia"),
    ("Montenegro", "Montenegro"),
    ("Montserrat", "Montserrat"),
    ("Morocco", "Morocco"),
    ("Mozambique", "Mozambique"),
    ("Namibia", "Namibia"),
    ("Nauru", "Nauru"),
    ("Nepal", "Nepal"),
    ("Netherlands", "Netherlands"),
    ("New Caledonia", "New Caledonia"),
    ("New Zealand", "New Zealand"),
    ("Nicaragua", "Nicaragua"),
    ("Niger", "Niger"),
    ("Nigeria", "Nigeria"),
    ("North Macedonia", "North Macedonia"),
    ("Norway", "Norway"),
    ("Oman", "Oman"),
    ("Pakistan", "Pakistan"),
    ("Palau", "Palau"),
    ("Panama", "Panama"),
    ("Papua New Guinea", "Papua New Guinea"),
    ("Paraguay", "Paraguay"),
    ("Peru", "Peru"),
    ("Philippines", "Philippines"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Qatar", "Qatar"),
    ("Romania", "Romania"),
    ("Russia", "Russia"),
    ("Rwanda", "Rwanda"),
    (
        "Saint Helena, Ascension, and Tristan da Cunha",
        "Saint Helena, Ascension, and Tristan da Cunha",
    ),
    ("Saint Kitts and Nevis", "Saint Kitts and Nevis"),
    ("Saint Lucia", "Saint Lucia"),
    ("Saint Vincent and the Grenadines", "Saint Vincent and the Grenadines"),
    ("Samoa", "Samoa"),
    ("San Marino", "San Marino"),
    ("Sao Tome and Principe", "Sao Tome and Principe"),
    ("Saudi Arabia", "Saudi Arabia"),
    ("Senegal", "Senegal"),
    ("Serbia", "Serbia"),
    ("Seychelles", "Seychelles"),
    ("Sierra Leone", "Sierra Leone"),
    ("Slovakia", "Slovakia"),
    ("Slovenia", "Slovenia"),
    ("Solomon Islands", "Solomon Islands"),
    ("Somalia", "Somalia"),
    ("South Africa", "South Africa"),
    ("South Sudan", "South Sudan"),
    ("Spain", "Spain"),
    ("Sri Lanka", "Sri Lanka"),
    ("Sudan", "Sudan"),
    ("Suriname", "Suriname"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
    ("Syria", "Syria"),
    ("Taiwan", "Taiwan"),
    ("Tajikistan", "Tajikistan"),
    ("Tanzania", "Tanzania"),
    ("Thailand", "Thailand"),
    ("Timor-Leste", "Timor-Leste"),
    ("Togo", "Togo"),
    ("Tonga", "Tonga"),
    ("Trinidad and Tobago", "Trinidad and Tobago"),
    ("Tunisia", "Tunisia"),
    ("Turkey", "Turkey"),
    ("Turkmenistan", "Turkmenistan"),
    ("Tuvalu", "Tuvalu"),
    ("Uganda", "Uganda"),
    ("Ukraine", "Ukraine"),
    ("United Arab Emirates", "United Arab Emirates"),
    ("United Kingdom", "United Kingdom"),
    ("United States", "United States"),
    ("Uruguay", "Uruguay"),
    ("Uzbekistan", "Uzbekistan"),
    ("Vanuatu", "Vanuatu"),
    ("Venezuela", "Venezuela"),
    ("Vietnam", "Vietnam"),
    ("Wallis and Futuna", "Wallis and Futuna"),
    ("Yemen", "Yemen"),
    ("Zambia", "Zambia"),
    ("Zimbabwe", "Zimbabwe"),
]
CT_COUNTRIES_DM = [
    ["Afghanistan", "AFG"],
    ["Albania", "ALB"],
    ["Algeria", "DZA"],
    ["American Samoa", "ASM"],
    ["Andorra", "AND"],
    ["Angola", "AGO"],
    ["Anguilla", "AIA"],
    ["Antarctica", "ATA"],
    ["Antigua and Barbuda", "ATG"],
    ["Argentina", "ARG"],
    ["Armenia", "ARM"],
    ["Aruba", "ABW"],
    ["Australia", "AUS"],
    ["Austria", "AUT"],
    ["Azerbaijan", "AZE"],
    ["Bahamas", "BHS"],
    ["Bahrain", "BHR"],
    ["Bangladesh", "BGD"],
    ["Barbados", "BRB"],
    ["Belarus", "BLR"],
    ["Belgium", "BEL"],
    ["Belize", "BLZ"],
    ["Benin", "BEN"],
    ["Bermuda", "BMU"],
    ["Bhutan", "BTN"],
    ["Bolivia, Plurinational State of", "BOL"],
    ["Bolivia", "BOL"],
    ["Bosnia and Herzegovina", "BIH"],
    ["Botswana", "BWA"],
    ["Bouvet Island", "BVT"],
    ["Brazil", "BRA"],
    ["British Indian Ocean Territory", "IOT"],
    ["Brunei Darussalam", "BRN"],
    ["Brunei", "BRN"],
    ["Bulgaria", "BGR"],
    ["Burkina Faso", "BFA"],
    ["Burundi", "BDI"],
    ["Cambodia", "KHM"],
    ["Cameroon", "CMR"],
    ["Canada", "CAN"],
    ["Cape Verde", "CPV"],
    ["Cayman Islands", "CYM"],
    ["Central African Republic", "CAF"],
    ["Chad", "TCD"],
    ["Chile", "CHL"],
    ["China", "CHN"],
    ["Christmas Island", "CXR"],
    ["Cocos (Keeling) Islands", "CCK"],
    ["Colombia", "COL"],
    ["Comoros", "COM"],
    ["Congo", "COG"],
    ["Congo, the Democratic Republic of the", "COD"],
    ["Cook Islands", "COK"],
    ["Costa Rica", "CRI"],
    ["Côte d'Ivoire", "CIV"],
    ["Ivory Coast", "CIV"],
    ["Croatia", "HRV"],
    ["Cuba", "CUB"],
    ["Cyprus", "CYP"],
    ["Czech Republic", "CZE"],
    ["Denmark", "DNK"],
    ["Djibouti", "DJI"],
    ["Dominica", "DMA"],
    ["Dominican Republic", "DOM"],
    ["Ecuador", "ECU"],
    ["Egypt", "EGY"],
    ["El Salvador", "SLV"],
    ["Equatorial Guinea", "GNQ"],
    ["Eritrea", "ERI"],
    ["Estonia", "EST"],
    ["Ethiopia", "ETH"],
    ["Falkland Islands (Malvinas)", "FLK"],
    ["Faroe Islands", "FRO"],
    ["Fiji", "FJI"],
    ["Finland", "FIN"],
    ["France", "FRA"],
    ["French Guiana", "GUF"],
    ["French Polynesia", "PYF"],
    ["French Southern Territories", "ATF"],
    ["Gabon", "GAB"],
    ["Gambia", "GMB"],
    ["Georgia", "GEO"],
    ["Germany", "DEU"],
    ["Ghana", "GHA"],
    ["Gibraltar", "GIB"],
    ["Greece", "GRC"],
    ["Greenland", "GRL"],
    ["Grenada", "GRD"],
    ["Guadeloupe", "GLP"],
    ["Guam", "GUM"],
    ["Guatemala", "GTM"],
    ["Guernsey", "GGY"],
    ["Guinea", "GIN"],
    ["Guinea-Bissau", "GNB"],
    ["Guyana", "GUY"],
    ["Haiti", "HTI"],
    ["Heard Island and McDonald Islands", "HMD"],
    ["Holy See (Vatican City State)", "VAT"],
    ["Honduras", "HND"],
    ["Hong Kong", "HKG"],
    ["Hungary", "HUN"],
    ["Iceland", "ISL"],
    ["India", "IND"],
    ["Indonesia", "IDN"],
    ["Iran, Islamic Republic of", "IRN"],
    ["Iraq", "IRQ"],
    ["Ireland", "IRL"],
    ["Isle of Man", "IMN"],
    ["Israel", "ISR"],
    ["Italy", "ITA"],
    ["Jamaica", "JAM"],
    ["Japan", "JPN"],
    ["Jersey", "JEY"],
    ["Jordan", "JOR"],
    ["Kazakhstan", "KAZ"],
    ["Kenya", "KEN"],
    ["Kiribati", "KIR"],
    ["Korea, Democratic People's Republic of", "PRK"],
    ["Korea, Republic of", "KOR"],
    ["South Korea", "KOR"],
    ["Kuwait", "KWT"],
    ["Kyrgyzstan", "KGZ"],
    ["Lao People's Democratic Republic", "LAO"],
    ["Latvia", "LVA"],
    ["Lebanon", "LBN"],
    ["Lesotho", "LSO"],
    ["Liberia", "LBR"],
    ["Libyan Arab Jamahiriya", "LBY"],
    ["Libya", "LBY"],
    ["Liechtenstein", "LIE"],
    ["Lithuania", "LTU"],
    ["Luxembourg", "LUX"],
    ["Macao", "MAC"],
    ["Macedonia, the former Yugoslav Republic of", "MKD"],
    ["Madagascar", "MDG"],
    ["Malawi", "MWI"],
    ["Malaysia", "MYS"],
    ["Maldives", "MDV"],
    ["Mali", "MLI"],
    ["Malta", "MLT"],
    ["Marshall Islands", "MHL"],
    ["Martinique", "MTQ"],
    ["Mauritania", "MRT"],
    ["Mauritius", "MUS"],
    ["Mayotte", "MYT"],
    ["Mexico", "MEX"],
    ["Micronesia, Federated States of", "FSM"],
    ["Moldova, Republic of", "MDA"],
    ["Monaco", "MCO"],
    ["Mongolia", "MNG"],
    ["Montenegro", "MNE"],
    ["Montserrat", "MSR"],
    ["Morocco", "MAR"],
    ["Mozambique", "MOZ"],
    ["Myanmar", "MMR"],
    ["Burma", "MMR"],
    ["Namibia", "NAM"],
    ["Nauru", "NRU"],
    ["Nepal", "NPL"],
    ["Netherlands", "NLD"],
    ["Netherlands Antilles", "ANT"],
    ["New Caledonia", "NCL"],
    ["New Zealand", "NZL"],
    ["Nicaragua", "NIC"],
    ["Niger", "NER"],
    ["Nigeria", "NGA"],
    ["Niue", "NIU"],
    ["Norfolk Island", "NFK"],
    ["Northern Mariana Islands", "MNP"],
    ["Norway", "NOR"],
    ["Oman", "OMN"],
    ["Pakistan", "PAK"],
    ["Palau", "PLW"],
    ["Palestinian Territory, Occupied", "PSE"],
    ["Panama", "PAN"],
    ["Papua New Guinea", "PNG"],
    ["Paraguay", "PRY"],
    ["Peru", "PER"],
    ["Philippines", "PHL"],
    ["Pitcairn", "PCN"],
    ["Poland", "POL"],
    ["Portugal", "PRT"],
    ["Puerto Rico", "PRI"],
    ["Qatar", "QAT"],
    ["Réunion", "REU"],
    ["Romania", "ROU"],
    ["Russian Federation", "RUS"],
    ["Russia", "RUS"],
    ["Rwanda", "RWA"],
    ["Saint Helena, Ascension and Tristan da Cunha", "SHN"],
    ["Saint Kitts and Nevis", "KNA"],
    ["Saint Lucia", "LCA"],
    ["Saint Pierre and Miquelon", "SPM"],
    ["Saint Vincent and the Grenadines", "VCT"],
    ["Saint Vincent & the Grenadines", "VCT"],
    ["St. Vincent and the Grenadines", "VCT"],
    ["Samoa", "WSM"],
    ["San Marino", "SMR"],
    ["Sao Tome and Principe", "STP"],
    ["Saudi Arabia", "SAU"],
    ["Senegal", "SEN"],
    ["Serbia", "SRB"],
    ["Seychelles", "SYC"],
    ["Sierra Leone", "SLE"],
    ["Singapore", "SGP"],
    ["Slovakia", "SVK"],
    ["Slovenia", "SVN"],
    ["Solomon Islands", "SLB"],
    ["Somalia", "SOM"],
    ["South Africa", "ZAF"],
    ["South Georgia and the South Sandwich Islands", "SGS"],
    ["South Sudan", "SSD"],
    ["Spain", "ESP"],
    ["Sri Lanka", "LKA"],
    ["Sudan", "SDN"],
    ["Suriname", "SUR"],
    ["Svalbard and Jan Mayen", "SJM"],
    ["Swaziland", "SWZ"],
    ["Sweden", "SWE"],
    ["Switzerland", "CHE"],
    ["Syrian Arab Republic", "SYR"],
    ["Taiwan, Province of China", "TWN"],
    ["Taiwan", "TWN"],
    ["Tajikistan", "TJK"],
    ["Tanzania, United Republic of", "TZA"],
    ["Thailand", "THA"],
    ["Timor-Leste", "TLS"],
    ["Togo", "TGO"],
    ["Tokelau", "TKL"],
    ["Tonga", "TON"],
    ["Trinidad and Tobago", "TTO"],
    ["Tunisia", "TUN"],
    ["Turkey", "TUR"],
    ["Turkmenistan", "TKM"],
    ["Turks and Caicos Islands", "TCA"],
    ["Tuvalu", "TUV"],
    ["Uganda", "UGA"],
    ["Ukraine", "UKR"],
    ["United Arab Emirates", "ARE"],
    ["United Kingdom", "GBR"],
    ["United States", "USA"],
    ["United States Minor Outlying Islands", "UMI"],
    ["Uruguay", "URY"],
    ["Uzbekistan", "UZB"],
    ["Vanuatu", "VUT"],
    ["Venezuela, Bolivarian Republic of", "VEN"],
    ["Venezuela", "VEN"],
    ["Viet Nam", "VNM"],
    ["Vietnam", "VNM"],
    ["Virgin Islands, British", "VGB"],
    ["Virgin Islands, U.S.", "VIR"],
    ["Wallis and Futuna", "WLF"],
    ["Western Sahara", "ESH"],
    ["Yemen", "YEM"],
    ["Zambia", "ZMB"],
    ["Zimbabwe", "ZWE"],
]

# Available domains
CT_MAIN_DOMAINS = [
    "DM",
    "AE",
    "AG",
    "BE",
    "BS",
    "CE",
    "CM",
    "CO",
    "CP",
    "CV",
    "DA",
    "DD",
    "DS",
    "DV",
    "EC",
    "EG",
    "EX",
    "FA",
    "FT",
    "GF",
    "HO",
    "IE",
    "IS",
    "LB",
    "MB",
    "MH",
    "MI",
    "MK",
    "ML",
    "NV",
    "OE",
    "PC",
    "PE",
    "PP",
    "PR",
    "QS",
    "RE",
    "RP",
    "RS",
    "SC",
    "SE",
    "SM",
    "SR",
    "SS",
    "SU",
    "SV",
    "TR",
    "TU",
    "UR",
    "VS",
]  # MS, OI

# List of races
CT_RACES = [
    "AMERICAN INDIAN OR ALASKA NATIVE",
    "ASIAN",
    "BLACK OR AFRICAN AMERICAN",
    "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER",
    "NOT REPORTED",
    "UNKNOWN",
    "WHITE",
]

# Notes
CT_NOTE_DISCLAIMER = "The information in this file is intended for testing and development purposes only. This information does not represent real patient data. Do not use this information for clinical care purposes."
CT_NOTE_COPYRIGHT = "(c) 2007-2022 NIHPO, Inc. (http://nihpo.com) This document is licensed under the GPL version 3."
CT_NOTE_FEEDBACK = (
    "Comments and suggestions for improvement are most welcome: Jose.Lacal@NIHPO.com"
)

# JSON format
CT_JSON_FORMAT = {
    "NIHPO_API": {
        "Results": {},
        "Note_Disclaimer": CT_NOTE_DISCLAIMER,
        "Note_Copyright": CT_NOTE_COPYRIGHT,
        "Note_Feedback": CT_NOTE_FEEDBACK,
        "Note_Version": CT_NOTE_VERSION,
    }
}

# Randomizations
CT_RANDOMIZE_OTHER_DRUG = ["none", "disc"]
CT_RANDOMIZE_PROVIDER = [1, 2]

# Constants to vitals endpoint
CT_TEMPERATURE_METHOD = [["Oral", 0], ["Axillary", 1], ["Tympanic", 2], ["Rectal", 3]]
CT_TEMPERATURE_RANGES = [[35.8, 37.3], [34.8, 36.3], [36.1, 37.9], [36.8, 38.2]]
CT_PULSE_RATE_RANGES = [
    [100, 175],
    [90, 160],
    [70, 150],
    [60, 130],
    [50, 110],
    [60, 100],
]
CT_PULSE_METHOD = ["Radial", "Carotid", "Brachial", "Apical"]
CT_RESPIRATORY_RATE_RANGES = [[30, 65], [26, 60], [14, 50], [12, 22], [10, 20]]
CT_OXYGEN_SATURATION_RANGES = [[97, 100], [92, 100], [95, 100]]
CT_BLOOD_PRESSURE_RANGES = [
    [[45, 80], [30, 55]],
    [[65, 100], [35, 65]],
    [[80, 115], [55, 80]],
    [[80, 120], [45, 80]],
    [[90, 120], [50, 80]],
    [[95, 135], [60, 80]],
    [[110, 145], [70, 90]],
    [[95, 145], [70, 90]],
]
CT_BLOOD_PRESSURE_METHOD = ["Manual BP reading", "Automatic BP reading"]
CT_HEIGHT_LOW_HIGHT_LIMITS = [
    1.6,
    8,
    2,
]  # In imperial units (from 1.6 ft to 8 ft, 2 ft for child under 1)
CT_WEIGHT_LOW_HIGHT_LIMITS = [
    5,
    600,
    15,
    200,
]  # In imperial units (from 1 lb to 600 lb, 15 lb for child under 1, 200 lb for child under 18)

######## Constants for JSON file ########
# Conditions
CT_CONDITION_NOTE_SOURCE = "The Clinical Observations Recordings and Encoding (CORE) Problem List Subset is a UMLS CORE Project with the purpose of defining a UMLS subset that is most useful for documenting and encoding clinical information at a summary level. The CORE Problem List Subset includes SNOMED CT concepts and codes that can be used for the problem list, discharge diagnoses, or reason of encounter."
CT_CONDITION_NOTE_COPYRIGHT = "SNOMED CT is owned by the International Health Terminology Standards Development Organisation (IHTSDO). The NLM is the U.S. Member of the IHTSDO and, as such, distributes SNOMED CT at no cost in accordance with the Member rights and responsibilities outlined in the IHTSDO's Articles. The license terms are incorporated into the License for Use of the UMLS Metathesaurus. Use of SNOMED CT is subject to the IHTSDO Affiliate license provisions and is free in IHTSDO Member territories including the United States, in low income countries, and for Qualifying Research Projects in any country."
CT_CONDITION_NOTE_DESCRIPTION = "Occurrence refers to number of institutions having this concept on their problem list (from 1 to 8), not populated for concepts retired from Subset. Usage refers to the average usage percentage among all institutions (i.e. sum of individual usage percentages divided by 8), not populated for concepts retired from Subset."

# Devices
CT_DEVICE_NOTE_SOURCE = "U. S. Food & Drug Administration; Downloadable 510(k) Files"
CT_DEVICE_NOTE_COPYRIGHT = "US Government's Open Data."
CT_DEVICE_NOTE_DESCRIPTION = (
    "U. S. Food & Drug Administration; Downloadable 510(k) Files"
)

# Drugs
CT_DRUG_NOTE_SOURCE_FDA = "U. S. Food & Drug Administration"
CT_DRUG_NOTE_SOURCE_EMA = "European Medicines Agency"
CT_DRUG_NOTE_SOURCE_SPAIN = "https://cima.aemps.es/cima/publico/nomenclator.html"
CT_DRUG_NOTE_COPYRIGHT_FDA = "US Government's Open Data"
CT_DRUG_NOTE_COPYRIGHT_EMA = "European Medicines Agency"
CT_DRUG_NOTE_COPYRIGHT_SPAIN = "https://www.aemps.gob.es/avisoLegal/"
CT_DRUG_NOTE_DESCRIPTION_FDA = (
    "Drug listings sources from U. S. Food & Drug Administration"
)
CT_DRUG_NOTE_DESCRIPTION_EMA = (
    "Drug listings sources from the European Medicines Agency"
)
CT_DRUG_NOTE_DESCRIPTION_SPAIN = "Nomenclator for Prescription is a medicine database intended to provide core prescription information to the care information services"
CT_DRUG_NOTE_DESCRIPTION_FDA_EMA = "Drug listings sources from both U. S. Food & Drug Administration and the European Medicines Agency."

# Laboratory results
CT_LAB_RESULT_NOTE_SOURCE = "https://loinc.org/downloads/loinc-table/"
CT_LAB_RESULT_NOTE_COPYRIGHT = "This material contains content from LOINC (http://loinc.org). LOINC is copyright (c) 1995-2020, Regenstrief Institute, Inc. and the Logical Observation Identifiers Names and Codes (LOINC) Committee and is available at no cost under the license at http://loinc.org/license. LOINC(r) is a registered United States trademark of Regenstrief Institute, Inc."
CT_LAB_RESULT_NOTE_DESCRIPTION = ".."

# Procedures
CT_PROCEDURE_NOTE_SOURCE = "The Clinical Observations Recordings and Encoding (CORE) Problem List Subset is a UMLS CORE Project with the purpose of defining a UMLS subset that is most useful for documenting and encoding clinical information at a summary level. The CORE Problem List Subset includes SNOMED CT concepts and codes that can be used for the problem list, discharge diagnoses, or reason of encounter."
CT_PROCEDURE_NOTE_COPYRIGHT = "SNOMED CT is owned by the International Health Terminology Standards Development Organisation (IHTSDO). The NLM is the U.S. Member of the IHTSDO and, as such, distributes SNOMED CT at no cost in accordance with the Member rights and responsibilities outlined in the IHTSDO's Articles. The license terms are incorporated into the License for Use of the UMLS Metathesaurus. Use of SNOMED CT is subject to the IHTSDO Affiliate license provisions and is free in IHTSDO Member territories including the United States, in low income countries, and for Qualifying Research Projects in any country."
CT_PROCEDURE_NOTE_DESCRIPTION = "Occurrence refers to number of institutions having this concept on their problem list (from 1 to 8), not populated for concepts retired from Subset. Usage refers to the average usage percentage among all institutions (i.e. sum of individual usage percentages divided by 8), not populated for concepts retired from Subset."

# Providers
CT_PROVIDER_NOTE_SOURCE = "U.S. Centers for Medicare & Medicaid Services' NPI registry (https://npiregistry.cms.hhs.gov). The National Provider Identifier (NPI) is a Health Insurance Portability and Accountability Act (HIPAA) Administrative Standard. An NPI is a unique identification number for covered health care providers, created to improve the efficiency and effectiveness of electronic transmission of health information. Covered health care providers and all health plans and health care clearinghouses must use NPIs in their administrative and financial transactions."
CT_PROVIDER_NOTE_COPYRIGHT = "US Government's Open Data."
CT_PROVIDER_NOTE_DESCRIPTION = ".."

# Vitals
CT_VITAL_NOTE_SOURCE = "Vital Sign Measurement Across the Lifespan - 1st Canadian edition. Authors: Jennifer L. Lapum, Margaret Verkuyl, Wendy Garcia, Oona St-Amant, and Andy Tan. Available at https://opentextbc.ca/vitalsign/"
CT_VITAL_NOTE_COPYRIGHT = ".."
CT_VITAL_NOTE_DESCRIPTION = ".."

# Constants for rules
CT_YES_OR_NULL_ONLY_FIELDS = [
    "AEPRESP",
    "AGPRESP",
    "BSBLFL",
    "CEPRESP",
    "CMPRESP",
    "CPBLFL",
    "CPDRVFL",
    "CPLOBXFL",
    "CVBLFL",
    "CVDRVFL",
    "CVLOBXFL",
    "DTHFL",
    "ECPRESP",
    "EGBLFL",
    "EGDRVFL",
    "EGLOBXFL",
    "FABLFL",
    "FALOBXFL",
    "FTBLF",
    "FTBLFL",
    "FTDRVFL",
    "FTLOBXFL",
    "GFBLFL",
    "GFDRVFL",
    "HOPRESP",
    "ISBLFL",
    "ISDRVFL",
    "ISLOBXFL",
    "LBBLFL",
    "LBDRVFL",
    "LBLOBXFL",
    "MBBLFL",
    "MBDRVFL",
    "MBLOBXFL",
    "MHPRESP",
    "MIBLFL",
    "MILOBXFL",
    "MKBLFL",
    "MKDRVFL",
    "MKLOBXFL",
    "MLPRESP",
    "NVBLFL",
    "NVDRVFL",
    "NVLOBXFL",
    "OEBLFL",
    "OEDRVFL",
    "OELOBXFL",
    "PCDRVFL",
    "PEBLFL",
    "PELOBXFL",
    "PRPRESP",
    "QSBLFL",
    "QSDRVFL",
    "QSLOBXFL",
    "REBLFL",
    "REDRVFL",
    "RELOBXFL",
    "RPBLFL",
    "RPDRVFL",
    "RPLOBXFL",
    "RSBLFL",
    "RSDRVFL",
    "RSLOBXFL",
    "SRBLFL",
    "SRLOBXFL",
    "SUPRESP",
    "TRBLFL",
    "TRLOBXFL",
    "TUBLFL",
    "TULOBXFL",
    "URBLFL",
    "URDRVFL",
    "URLOBXFL",
    "VSBLFL",
    "VSDRVFL",
    "VSLOBXFL",
]
CT_NO_OR_NULL_ONLY_FIELDS = ["ISSPCUFL", "LBSPCUFL"]
CT_NO_OR_YES_ONLY_FIELDS = ["AESER", "AESOD"]

# Special characters to avoid in file names
CT_SPECIAL_CHARACTERS_TO_AVOID = [
    "/",
    "|",
    "\\",
    "#",
    "%",
    "!",
    "@",
    "$",
    "<",
    ">",
    "+",
    "'",
    "`",
    '"',
    "&",
    "*",
    "{",
    "}",
    "?",
    "=",
    ":",
    " ",
]
CT_SPECIAL_CHARACTERS_TO_AVOID_STRING = (
    """/, |, \\, #, %, !, @, $, <, >, +, ', `, ", &, *, {, }, ?, =, :, space"""
)

###### SUPERSET ######

# Config
CT_SUPERSET_DB_PATH = "/home/nihpo/venv/apache/data/superset.db"

# Reference
CT_SUPERSET_HREF = "http://127.0.0.1:7888/superset/dashboard/6"
CT_SUPERSET_USER = "nihpo"
CT_SUPERSET_PASSWORD = "nihpo"
