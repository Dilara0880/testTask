# -----------------------------------------------------------
# kettle simulation -- web app on python-flask using SQLAlchemy
#
# (C) 2023 Dilara Orazmetova
# email dilara.0880@gmail.com
# -----------------------------------------------------------


import logging
from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

logging.basicConfig(filename="logging.log", level=logging.INFO)
file_path = os.path.abspath(os.getcwd()) + "/app.db"

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Parameters(db.Model):

    """Create 'parameters' db."""

    __tablename__ = 'parameters'
    id = db.Column(db.Integer, primary_key=True)
    power = db.Column(db.Integer, nullable=False)
    kettle_max_volume = db.Column(db.Float, nullable=False)
    start_temp = db.Column(db.Float, nullable=False)
    end_temp = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Parameters %r>' % self.id


class Operation(db.Model):

    """Create 'operations' db."""

    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    water_volume = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer)
    end_temp = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Operation %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
@app.route('/off', methods=['GET', 'POST'])
def start():

    """Init home page."""

    if request.method == 'POST':
        return redirect('/parameters')
    return render_template("index.html")


@app.route('/parameters', methods=['GET', 'POST'])
def get_kettle_parameters():

    """Get kettle parameters and add data to 'parameters' db."""

    if request.method == 'POST':
        power = request.form['power']
        kettle_max_volume = request.form['max_volume']
        start_temp = request.form['start_temp']
        end_temp = request.form['end_temp']
        parameters = Parameters(power=power,
                                kettle_max_volume=kettle_max_volume,
                                start_temp=start_temp,
                                end_temp=end_temp)
        try:
            db.session.add(parameters)
            db.session.commit()
            logging.info("Added kettle's parameters to 'Parameters.db'")
            return redirect('/setvolume')
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
    else:
        return render_template("kettleParameters.html")


@app.route('/setvolume', methods=['GET', 'POST'])
def set_volume():

    """Get operation parameters and add data to 'operation' db."""

    parameters = Parameters.query.order_by(Parameters.id.desc()).first()
    max_volume = parameters.kettle_max_volume
    if request.method == 'POST':
        water_volume = request.form['water_volume']
        start_time = datetime.now()
        operation = Operation(water_volume=water_volume,
                              start_time=start_time,
                              end_temp=parameters.end_temp)
        try:
            db.session.add(operation)
            db.session.commit()
            logging.info("Added operation parameters to 'Operations.db'")
            return redirect('/on/' + str(parameters.start_temp))
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
    return render_template('addWater.html',
                           max_volume=max_volume)


@app.route('/on/<float(signed=True):cur_temp>', methods=['GET', 'POST'])
def turn_on(cur_temp):

    """Init working page with current temperature."""

    logging.info("The kettle was turned on")
    operation = Operation.query.order_by(Operation.id.desc()).first()
    parameters = Parameters.query.order_by(Parameters.id.desc()).first()
    volume = operation.water_volume
    power = parameters.power
    end_temp = parameters.end_temp
    cur_time = datetime.now()
    start_time = datetime.strptime(operation.start_time, '%Y-%m-%d %H:%M:%S.%f')
    if request.method == 'POST':
        if request.form['submit-button'] == 'Выключить':
            logging.info("The kettle was turned off")
            return redirect('/')
        elif request.form['submit-button'] == 'Остановить':
            logging.info("The kettle was paused")
            return render_template('kettleIsPaused.html',
                                   cur_temp=cur_temp,
                                   time_delta=(cur_time - start_time).total_seconds())
        try:
            operation.end_time = cur_time
            operation.end_temp = cur_temp
            db.session.commit()
            logging.info("Added operation end_time to 'Operations.db'")
        except Exception as e:
            db.session.rollback()
            logging.exception(e)

    while cur_temp + power / (4200 * volume) < end_temp:
        cur_temp = min(round(cur_temp + power / (4200 * volume), 2), end_temp)
        try:
            operation.end_temp = cur_temp
            db.session.commit()
            logging.info("Added operation end_temp to 'Operations.db'")
        except Exception as e:
            db.session.rollback()
            logging.exception(e)
        return render_template('kettleIsOn.html', cur_temp=cur_temp)
    return render_template('kettleIsOn.html', cur_temp=parameters.start_temp)


@app.route('/pause/<float(signed=True):cur_temp>/<int:time_delta>', methods=['GET', 'POST'])
def pause(cur_temp, time_delta):

    """Init pause page with temperature and working time."""

    if request.method == 'POST':
        if request.form['submit-button'] == 'Выключить':
            logging.info("The kettle was turned off")
            return redirect('/')
        elif request.form['submit-button'] == 'Включить':
            logging.info("The kettle was restored")
            return render_template('kettleIsOn.html', cur_temp=cur_temp)
    return render_template('kettleIsPaused.html',
                           cur_temp=cur_temp,
                           time_delta=time_delta)


if __name__ == '__main__':
    app.run(debug=False)
