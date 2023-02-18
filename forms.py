from flask_wtf import FlaskForm

from wtforms import IntegerField, DecimalField
from wtforms.validators import InputRequired, NumberRange


class ParametersForm(FlaskForm):
    power = IntegerField('power', validators=[InputRequired(), NumberRange(max=5000)], default=2200)
    max_volume = DecimalField('max_volume', validators=[InputRequired(), NumberRange(min=0.001, max=10)], default=1.0)
    start_temp = DecimalField('start_temp', validators=[InputRequired(), NumberRange(min=0, max=99.9)], default=20.0)
    end_temp = DecimalField('end_temp', validators=[InputRequired(), NumberRange(min=0.1, max=100)], default=100.0)
    boiling_time = DecimalField('boiling_time', validators=[InputRequired(), NumberRange(max=120.0)], default=10.0)

