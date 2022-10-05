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
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from CE_app.auth import bp
import requests
from cryptography.fernet import Fernet
from CE_app.auth.forms import LoginForm
from CE_app.models import User, Roles
from CE_app import db


main = "main.index"
auth = "auth.login"


@bp.route("/login", methods=["GET", "POST"])
def login():
    key = Fernet.generate_key()
    fernet = Fernet(key)

    if current_user.is_authenticated:
        return redirect(url_for(main))
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        username_email = form.username_email.data
        enc_username_email = fernet.encrypt(username_email.encode())
        enc_password = fernet.encrypt(password.encode())
        #         enc_username_email = fernet.encrypt(password.encode())

        url = (
            "http://portal.nihpo.com/auth/community/"
            + str(enc_username_email)
            + "/"
            + str(enc_password)
            + "/"
            + str(key)
        )
        print(url)
        response = requests.post(url)

        if response.json()["Result"] == "True":
            user = User.query.filter_by(username="free_user").first()
            login_user(user, remember=True)
            session["username"] = username_email
            session["first_name"] = response.json()["First Name"]
            session["last_name"] = response.json()["Last Name"]
            user.role = form.role.data
            db.session.commit()
            return redirect(url_for(main))
        elif response.json()["Result"] == "False":
            flash(_("Invalid username or password"))
            return redirect(url_for(auth))
        else:
            flash(_("There is some error with the portal, try again in some minutes"))

    return render_template("auth/login.html", title=_("Sign In"), form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(main))
