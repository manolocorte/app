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
import random, datetime
from random import randint
from datetime import date

date_format = '%Y-%m-%d'

def func_nihpo_randomize(in_final_result):
    """
    Returns a random latitude and longitude depending of the display variable around the
    latitude and longitude of the input location. 

    :param fin_inal_result: Dictionary with the fields: 'location_display', 'location_lat', 'location_long'
    :type in_final_result: Dictionary
    :returns: Same dictionary with the latitude and longitude randomized
    :rtype: Dictionary
    """
    for data in in_final_result:
        display = int(data['location_display'])
        if (display <= 5):
            delta_1 = randint(-5, 5) * 0.0005
            delta_2 = randint(-5, 5) * 0.0005
        elif (display == 6 or display == 7):
            delta_1 = randint(-5, 5) * 0.005
            delta_2 = randint(-5, 5) * 0.005
        elif (display >= 8):
            delta_1 = randint(-5, 5) * 0.05
            delta_2 = randint(-5, 5) * 0.05
        data['location_lat'] = data['location_lat'] + delta_1
        data['location_long'] = data['location_long'] + delta_2

def func_nihpo_random_date_birth(in_base_date_object, in_minimum_age, in_maximum_age):
    """
    Returns a random Date of Birth, using a base date, and with a range of ages defined by a Minimum Age and a Maximum Age

    :param in_base_date_object: Date object formatted as YYYY-MM-DD 
    :type in_base_date_object: Date object
    :param in_minimum_age: Minimum age (in years) at in_base_date 
    :type in_minimum_age: Integer
    :param in_maximum_age: Maximum age (in years) at in_base_date 
    :type in_maximum_age: Integer
    :returns:  Date string, randomly selected
    :rtype: Date String
    """
    #
    # Validation
    #     assert (CT_AGE_MINIMUM <= in_minimum_age <= CT_AGE_MAXIMUM),"Please enter a value between %d and %d" % (CT_AGE_MINIMUM, CT_AGE_MAXIMUM)
    #     assert (in_minimum_age <= in_maximum_age <= CT_AGE_MAXIMUM),"Please enter a value between %d and %d" % (in_minimum_age, CT_AGE_MAXIMUM)
    #
    var_number_days_earliest = in_minimum_age * 365 # Number of days before in_base_date for minimum age. 
    var_number_days_latest = (in_maximum_age + 1) * 365 # Number of days before in_base_date for maximum age. 
    #
    var_days_birth_before_in_base_date = random.randrange(var_number_days_earliest, var_number_days_latest)
    var_dob = in_base_date_object - datetime.timedelta(days=var_days_birth_before_in_base_date)
    #
    return var_dob.strftime(date_format)

def func_nihpo_calculate_age(in_born):
    """
    Calculates the age of a subject born in a selected date

    :param in_born: Date object as YYYY-MM-DD
    :type in_born: Date object
    :returns:  Age of the subject
    :rtype: Integer
    """
    today = date.today() 
    try:  
        birthday = in_born.replace(year = today.year) 
  
    # raised when birth date is February 29 
    # and the current year is not a leap year 
    except ValueError:  
        birthday = in_born.replace(year = today.year, 
                  month = in_born.month + 1, day = 1) 
  
    if birthday > today: 
        return today.year - in_born.year - 1
    else: 
        return today.year - in_born.year