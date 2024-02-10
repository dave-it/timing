# app.py

from flask import Flask, render_template, request, current_app, jsonify
from timer import start_timer, stop_timer
from athletes import add_athlete, get_all_athletes, get_all_athletes_category, init_db, get_athlete_data, get_db
import csv
import codecs  # Fügen Sie diese Zeile hinzu

app = Flask(__name__)

# Initialisiere die Datenbank beim Start der Anwendung
with app.app_context():
    init_db()

def update_current_category(category):    
    conn = get_db()
    cursor = conn.cursor()

    # Annahme: Die Tabelle heißt 'global_settings'
    # Den globalen Offset-Wert in der Datenbank aktualisieren
    cursor.execute('UPDATE global_settings SET current_category = ? WHERE id = 1', (category,))
    conn.commit()

    conn.close()

@app.route('/')
def index():
    athletes = get_all_athletes()
    return render_template('index.html', athletes=athletes)


@app.route('/men')
def men():
    athletes = get_all_athletes_category('Men')
    update_current_category('Men')
    return render_template('index.html', athletes=athletes, category='Men')


@app.route('/women')
def women():
    athletes = get_all_athletes_category('Women')
    update_current_category('Women')
    return render_template('index.html', athletes=athletes, category='Women')

@app.route('/set_rider_active', methods=['POST'])
def set_rider_active():
    start_number = int(request.form.get('start_number'))
    conn = get_db()
    cursor = conn.cursor()

    # Annahme: Die Tabelle heißt 'global_settings'
    # Den globalen Offset-Wert in der Datenbank aktualisieren
    cursor.execute('UPDATE global_settings SET current_rider_number = ? WHERE id = 1', (start_number,))
    conn.commit()

    conn.close()

    return jsonify({'status': 'success', 'message': 'Rider set active'})

@app.route('/start', methods=['POST'])
def start():
    global timer_running
    print("IN START?")
    timer_running = True

    start_number = int(request.form.get('start_number'))
    athlete_data = get_athlete_data(start_number)

    if athlete_data:
        duration_minutes = 5  # Set the desired duration in minutes
        duration_seconds = duration_minutes * 60
        print("DATA")
        start_timer(duration_seconds, athlete_data)
        print("SUCCESS??")
        # Sendet eine JSON-Antwort mit einer Meldung für das Popup
        return jsonify({'status': 'success', 'message': 'Timer started successfully!'})
    else:
        return jsonify({'status': 'error', 'message': 'Athlete not found or data incomplete.'})

@app.route('/stop', methods=['POST'])
def stop():
    global timer_running
    stop_timer()
    return jsonify({'status': 'success', 'message': 'Timer stopped successfully!'})

@app.route('/get_current_rider', methods=['GET'])
def get_current_rider():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT current_rider_number FROM global_settings WHERE id = 1')
    current_rider_number = cursor.fetchone()[0]

    # SQL-Abfrage mit dem globalen OFFSET-Wert
    cursor.execute('SELECT * FROM athletes WHERE start_number = ?', (current_rider_number,))
    drivers = cursor.fetchall()
    conn.close()

    driver = drivers[0]
    
    flag_path = 'C:\\Users\\David\\Downloads\\'


    return jsonify([
        {
            'id': driver[0],
            'first_name': driver[1],
            'last_name': driver[2],
            'category': driver[3],
            'nation': driver[4],
            'birthdate': driver[5],
            'start_number': driver[6],
            'runtime': driver[7],
            'split1': driver[8],
            'split2': driver[9],
            'split3': driver[10],
            'split4': driver[11],
            'split5': driver[12],
            'name': driver[2].upper() + ' '  + driver [1],
            'flag_path': flag_path + driver[4] + '.png'
        }
    ])


@app.route('/get_runtime', methods=['POST'])
def get_runtime():
    start_number = request.form.get('start_number')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Rufe die Laufzeit für den angegebenen Athleten ab
    cursor.execute('SELECT runtime FROM athletes WHERE start_number = ?', (start_number,))
    result = cursor.fetchone()
    
    conn.close()

    if result:
        return jsonify({'runtime': result[0]})
    else:
        return jsonify({'runtime': 0})


@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})

    if file and file.filename.endswith('.csv'):
        try:
            # Änderungen hier: Die Datei mit codecs.iterdecode öffnen
            decoded_file = codecs.iterdecode(file, 'utf-8')
            save_csv_to_database(decoded_file)
            return jsonify({'status': 'success', 'message': 'CSV data imported successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error importing CSV data: {str(e)}'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file format. Please upload a CSV file'})


def save_csv_to_database(csv_file):
    conn = get_db()
    cursor = conn.cursor()

    # Annahme: CSV-Datei hat Spaltenüberschriften in der ersten Zeile
    csv_reader = csv.DictReader(csv_file)

    for row in csv_reader:
        cursor.execute('''
            INSERT INTO athletes (first_name, last_name, nation, birthdate, start_number, category, start_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (row['First Name'], row['Last Name'], row['Nation'], 
            row['Birthdate'], row['Start Number'], row['Category'], row['Order']))

    conn.commit()
    conn.close()

    return True

@app.route('/top_drivers', methods=['GET'])
def top_drivers():
    conn = get_db()
    cursor = conn.cursor()

    # cursor.execute('INSERT INTO global_settings (offset, current_category) VALUES (10, "Men")')
    # conn.commit()
   
    cursor.execute('SELECT offset FROM global_settings WHERE id = 1')
    global_offset_result = cursor.fetchone()
    cursor.execute('SELECT current_category FROM global_settings WHERE id = 1')
    category = cursor.fetchone()[0]

    if global_offset_result is not None:
        global_offset = global_offset_result[0]
    else:
        global_offset = 0  # Set a default value if the offset is not found in the database

    # SQL-Abfrage mit dem globalen OFFSET-Wert
    cursor.execute('SELECT * FROM athletes WHERE category = ? ORDER BY start_number LIMIT 10 OFFSET ?', (category, global_offset,))
    drivers = cursor.fetchall()

    conn.close()

    flag_path = 'C:\\Users\\David\\Downloads\\'

    # Konvertieren Sie die Daten in ein JSON-Format
    drivers_json = [
        {
            'id': driver[0],
            'first_name': driver[1],
            'last_name': driver[2],
            'category': driver[3],
            'nation': driver[4],
            'birthdate': driver[5],
            'start_number': driver[6],
            'runtime': driver[7],
            'split1': driver[8],
            'split2': driver[9],
            'split3': driver[10],
            'split4': driver[11],
            'split5': driver[12],
            'name': driver[2].upper() + ' '  + driver [1],
            'flag_path': flag_path + driver[4] + '.png'
        } for driver in drivers
    ]
    while len(drivers_json) < 10:
        empty_driver = {
            'id': '',
            'first_name': '',
            'last_name': '',
            'nation': '',
            'birthdate': '',
            'start_number': '',
            'runtime': '',
            'split1': '',
            'split2': '',
            'split3': '',
            'split4': '',
            'split5': '',
            'name': '',
            'flag_path': flag_path + 'EMP.png'
        }
        drivers_json.append(empty_driver)

    return jsonify({'top_drivers': drivers_json})

@app.route('/update_global_offset/<int:new_offset>', methods=['POST'])
def update_global_offset(new_offset):
    conn = get_db()
    cursor = conn.cursor()

    # Annahme: Die Tabelle heißt 'global_settings'
    # Den globalen Offset-Wert in der Datenbank aktualisieren
    cursor.execute('UPDATE global_settings SET offset = ? WHERE id = 1', (new_offset,))
    conn.commit()

    conn.close()
    print('updated?')
    return jsonify({'status': 'success', 'message': 'Global offset updated successfully'})


if __name__ == "__main__":
    app.run(debug=True)
