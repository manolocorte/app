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
from CE_app import create_app, cli
from flask_dropzone import Dropzone
from CE_app import celery
from CE_app.celery_utils import init_celery
import os
import flask_profiler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

settings_module = os.getenv('APP_SETTINGS_MODULE')
url_server = os.getenv('APP_URL_SERVER')

# Create a new app:
app = create_app(settings_module, url_server)
dropzone = Dropzone(app)
cli.register(app)
init_celery(celery, app)

