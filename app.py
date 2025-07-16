from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from utils.calculations import calculate_area, calculate_elevation
from utils.updated_cal import compute_design
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for securely signing session cookies


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual', methods=['GET', 'POST'])
def manual():
    if request.method == 'POST':
        session['area'] = float(request.form['area'])
        session['elevation'] = float(request.form['elevation'])
        return redirect(url_for('inputs'))
    return render_template('manual.html')



@app.route('/boundary', methods=['GET', 'POST'])
def boundary():
    if request.method == 'POST':
        boundary_coords = request.json.get('coordinates', [])
        if not boundary_coords:
            return jsonify({'status': 'error', 'message': 'No coordinates received'}), 400

        area = calculate_area(boundary_coords)
        elev = calculate_elevation(boundary_coords)

        session['area'] = area
        session['elevation'] = elev

        return jsonify({'status': 'ok'})
    return render_template('boundary.html')


@app.route('/inputs', methods=['GET', 'POST'])
def inputs():
    if 'area' not in session:
        return redirect(url_for('index'))  # User must visit boundary first

    if request.method == 'POST':
        session['soil'] = request.form['soil']
        session['slope'] = float(request.form['slope'])
        session['water_demand'] = float(request.form['water_demand'])
        session['method'] = request.form['method']
        session['pipe_length'] = float(request.form['pipe_length'])
        session['material'] = request.form['material']
        session['Zone'] = request.form['Zone']

        return redirect(url_for('results'))

    return render_template('inputs.html')

@app.route('/results')
def results():
    required_keys = ['area', 'elevation', 'soil', 'slope', 'water_demand', 'method', 'pipe_length', 'material', 'Zone']
    if not all(k in session for k in required_keys):
        return "Missing input fields. Please complete all steps.", 400

    data_store = {k: session[k] for k in required_keys}
    global design
    design = compute_design(data_store)

    # Use the value of Zone to decide what to do
    if session['Zone'] == "Suggest":
        return render_template('results.html', design=design)
    else:
        return render_template('results1.html', design=design)






@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('boundary'))

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        inventory_data = {
            "Pump Type": request.form.get("pump_type"),
            "Filter": request.form.get("filter"),
            "Fertilizer Injector": request.form.get("injector"),
            "Pressure Regulator": request.form.get("pressure_regulator"),
            "Motor HP": request.form.get("motor_hp"),
            "Mainline Pipe": request.form.get("mainline_pipe"),
            "Sub-mains": request.form.get("submains"),
            "Drip Laterals": request.form.get("drip_laterals"),
            "Emitters": request.form.get("emitters"),
            "Tees": request.form.get("tees"),
            "Elbows": request.form.get("elbows"),
            "Reducers": request.form.get("reducers"),
            "End Caps": request.form.get("end_caps"),
            "Air Valve": request.form.get("air_valve"),
            "Controller": request.form.get("controller"),
            "Solenoid Valves": request.form.get("valves"),
            "Sprinklers": request.form.get("sprinklers"),
            "Ball Valves": request.form.get("ball_valves"),
        }
        session["inventory_data"] = inventory_data
        return redirect("/final-summary")
    
    return render_template("inventory.html", design=design)

@app.route('/final-summary')
def final_summary():
    summary = session.get('inventory_data', {})
    return render_template("final-summary.html", summary=summary)



if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.103', port=5000)

