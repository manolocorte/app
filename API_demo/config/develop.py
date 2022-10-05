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
from .default import *

ENV = APP_ENV_DEVELOPMENT

CT_LOGS = True
DEBUG = True
CT_DAYS_TO_DELETE_FILES = 100000000

SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5433/api_nihpo"

CT_DATABASE_HOST = "localhost"
CT_DATABASE_PORT = "5433"
CT_DATABASE = "api_nihpo"
CT_DATABASE_USER = "postgres"
CT_DATABASE_PASSWORD = "postgres"

CT_DOWNLOADS_PATH = "/Users/diego/practice/downloads/"
