from flask import Flask, render_template, jsonify, redirect, url_for
from flask import request
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
n, p, k, sm, wl = 0, 0, 0, 0, 0
ESP8266_IP = 'http://192.168.254.163'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Garden DB model
class PlotData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plot_number = db.Column(db.Integer, unique=True, nullable=False)
    plant_type = db.Column(db.String(100), nullable=False)
    date_planted = db.Column(db.Date, nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    
# Define the PlantHarvest DB model
class PlantHarvest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_harvested = db.Column(db.Date, nullable=False)
    
# Define the NPK DB model
class NPK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nitrogen = db.Column(db.String(50), nullable=False)
    n_value = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.String(50), nullable=False)
    p_value = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.String(50), nullable=False)
    k_value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    
def calculate_harvest_date(plant_type, date_planted):
    plant_growth_days = {
        "Okra": 60,
        "Kamatis": 80,
        "Petchay": 30
    }
    days_to_harvest = plant_growth_days.get(plant_type, 0)
    return date_planted + timedelta(days=days_to_harvest)

# Create database tables if they don't exist
def create_database():
    with app.app_context():
        db.create_all()  # Creates the database and tables

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sensor_updates')
def sensor_updates():
    return render_template('sensor_updates.html')

@app.route('/controllers')
def controllers():
    return render_template('controllers.html')

@app.route('/forecasting')
def forecasting():
    plants = PlotData.query.all()
    return render_template('forecasting.html', plants=plants)

@app.route('/history')
def history():
    harvest_data = PlantHarvest.query.all()
    npk_data = NPK.query.all()
    return render_template('history.html', harvest_data=harvest_data, npk_data=npk_data)

@app.route('/harvest-data')
def harvest_data():
    okra_data = []
    kamatis_data = []
    petchay_data = []

    # Query all harvest data
    harvests = PlantHarvest.query.all()

    # Organize data by plant type and convert dates to timestamps
    for harvest in harvests:
        date_harvested_datetime = datetime.combine(harvest.date_harvested, datetime.min.time())
        data_point = [int(date_harvested_datetime.timestamp() * 1000), harvest.quantity]  # [timestamp, quantity]
        if harvest.plant_type == 'Okra':
            okra_data.append(data_point)
        elif harvest.plant_type == 'Kamatis':
            kamatis_data.append(data_point)
        elif harvest.plant_type == 'Petchay':
            petchay_data.append(data_point)

    return jsonify({
        'okra': okra_data,
        'kamatis': kamatis_data,
        'petchay': petchay_data
    })
    
@app.route('/npk-data')
def npk_data():
    n_data = []
    p_data = [] 
    k_data = []
    nutrients = NPK.query.all()
    
    for nutrient in nutrients:
        date = nutrient.date
        n_data_point = [int(date.timestamp() * 1000), nutrient.n_value]
        p_data_point = [int(date.timestamp() * 1000), nutrient.p_value]
        k_data_point = [int(date.timestamp() * 1000), nutrient.k_value]
        n_data.append(n_data_point)
        p_data.append(p_data_point)
        k_data.append(k_data_point)
        
    # Return outside of the loop
    return jsonify({
        'nitrogen': n_data,
        'phosphorus': p_data,
        'potassium': k_data
    })

@app.route('/submit', methods=['POST'])
def submit():
    plot_number = int(request.form['plot_number'])
    plant_type = request.form['plant_type']
    date_planted = datetime.strptime(request.form['date_planted'], '%Y-%m-%d').date()
    harvest_date = calculate_harvest_date(plant_type, date_planted)
    plot = PlotData.query.filter_by(plot_number=plot_number).first()
    if plot:
        plot.plant_type = plant_type
        plot.date_planted = date_planted
        plot.harvest_date = harvest_date
    else:
        plot = PlotData(
            plot_number=plot_number,
            plant_type=plant_type,
            date_planted=date_planted,
            harvest_date=harvest_date
        )
        db.session.add(plot)
    try:
        db.session.commit()
        return redirect(url_for('forecasting'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('forecasting'))

@app.route('/add_harvest', methods=['POST'])
def add_harvest():
    plant_type = request.form.get('plant_type')
    quantity = request.form.get('value')
    date_harvested = request.form.get('date_harvested')
    quantity = int(quantity)
    date_harvested = datetime.strptime(date_harvested, "%Y-%m-%d").date()

    new_harvest = PlantHarvest(plant_type=plant_type, quantity=quantity, date_harvested=date_harvested)
    db.session.add(new_harvest)
    try:
        db.session.commit()
        return redirect(url_for('history'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('history'))

def add_npk():
    with app.app_context():
        nitrogen = "Nitrogen"
        n_value = n
        phosphorus = "Phosphorus"
        p_value = p
        potassium = "Potassium"
        k_value = k
        date = datetime.now()

        new_npk = NPK(nitrogen=nitrogen, n_value=n_value, phosphorus=phosphorus, p_value=p_value, potassium=potassium, k_value=k_value, date=date)
        db.session.add(new_npk)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

@app.route('/nitrogen', methods=['GET'])
def get_nitrogen():
    # global n
    # n = random.randint(0, 100)  # Generate a random nitrogen value between 0 and 100
    # return jsonify({"status": "success", "nitrogen": n}), 200
    try:
        response = requests.get(f'{ESP8266_IP}/nitrogen')
        if response.status_code == 200:
            nitrogen = response.text
            global n
            return jsonify({"status": "success", "nitrogen": n}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to retrieve nitrogen value"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/phosphorus', methods=['GET'])
def get_phosphorus():
    # global p
    # p = random.randint(0, 100)  # Generate a random phosphorus value between 0 and 100
    # return jsonify({"status": "success", "phosphorus": p}), 200
    try:
        response = requests.get(f'{ESP8266_IP}/phosphorus')
        if response.status_code == 200:
            phosphorus = response.text
            global p
            return jsonify({"status": "success", "phosphorus": p}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to retrieve phosphorus value"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/potassium', methods=['GET'])
def get_potassium():
    # global k
    # k = random.randint(0, 100)  # Generate a random potassium value between 0 and 100
    # return jsonify({"status": "success", "potassium": k}), 200
    try:
        response = requests.get(f'{ESP8266_IP}/potassium')
        if response.status_code == 200:
            potassium = response.text
            global k
            return jsonify({"status": "success", "potassium": k}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to retrieve potassium value"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/soil_moisture', methods=['GET'])
def get_soil_moisture():
    # global sm
    # sm = random.randint(0, 100)  # Generate a random soil moisture value between 0 and 100
    # return jsonify({"status": "success", "soil_moisture": sm}), 200
    try:
        response = requests.get(f'{ESP8266_IP}/soil_moisture')
        if response.status_code == 200:
            soil_moisture = response.text
            global sm
            return jsonify({"status": "success", "soil_moisture": sm}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to retrieve soil_moisture value"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/water_level', methods=['GET'])
def get_water_level():
    # global wl
    # wl = random.randint(0, 100)  # Generate a random water level value between 0 and 100
    # return jsonify({"status": "success", "water_level": wl}), 200
    try:
        response = requests.get(f'{ESP8266_IP}/water_level')
        if response.status_code == 200:
            water_level = response.text
            global wl
            return jsonify({"status": "success", "water_level": wl}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to retrieve water_level value"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard_updates', methods=['GET'])
def get_updates():
    get_nitrogen()
    get_phosphorus()
    get_potassium()
    get_soil_moisture()
    get_water_level()
    updates = {
        "nitrogen": n,
        "phosphorus": p,
        "potassium": k,
        "soil_moisture": sm,
        "water_level": wl
    }
    return jsonify(updates)

@app.route('/on_water_pump', methods=['GET'])
def on_water_pump():
    return control_device('on_water_pump', "Water pump turned on.")

@app.route('/off_water_pump', methods=['GET'])
def off_water_pump():
    return control_device('off_water_pump', "Water pump turned off.")

@app.route('/on_fertilizer_pump', methods=['GET'])
def on_fertilizer_pump():
    return control_device('on_fertilizer_pump', "Fertlizer pump turned on.")

@app.route('/off_fertilizer_pump', methods=['GET'])
def off_fertilizer_pump():
    return control_device('off_fertilizer_pump', "Fertilizer turned off.")

@app.route('/open_roof', methods=['GET'])
def open_roof():
    return control_device('open_roof', "Roof open.")

@app.route('/close_roof', methods=['GET'])
def close_roof():
    return control_device('close_roof', "Roof closed.")


def control_device(action, success_message):
    """Helper function to control devices."""
    try:
        response = requests.get(f'{ESP8266_IP}/{action}')
        if response.status_code == 200:
            return jsonify({"status": "success", "message": success_message}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to control device."}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
scheduler = BackgroundScheduler()
scheduler.add_job(add_npk, 'interval', minutes=5)
scheduler.start()

if __name__ == "__main__":
    create_database()
    app.run(host='0.0.0.0', port=5000)
