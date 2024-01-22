from flask import Flask, render_template, jsonify
import socket
import json
import pymysql
import re

app = Flask(__name__)


# Fetches card data from the card reader
def get_card_hex():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.0.0.132', 2189))
    command = 'R\r\n'
    s.sendall(command.encode())
    response = s.recv(1024)
    s.close()
    print(f"reconheceu a carta: {response.decode()}")
    
    decoded_response = response.decode()
    
    hex_pattern = re.compile('H[0-9A-Fa-f]+')
    match = hex_pattern.search(decoded_response)
    if match:
        hex_part = match.group()
        print(f"Recognized card: {hex_part}")
        return hex_part
    else:
        print("No hexadecimal data found")
        return None

# Fetches face data from the face recognition server
def get_face_data():
    try:
       con = pymysql.connect(host='database-1.cvm0aqq86tlh.sa-east-1.rds.amazonaws.com', user='admin',password='Chess.com2409',database='rfid_app', port=3306)
    # Creating a cursor object using the cursor() method
       with con.cursor() as cursor:
            # SQL query to fetch the name of the face with ID 0
            query = "SELECT name FROM last_face WHERE id = 1"
            # Executing the query
            cursor.execute(query)

            # Fetching the result
            result = cursor.fetchone()
            print(f"teoricamente rodou a Query... {result[0]}")
            return result[0]

    except pymysql.MySQLError as e:
        print("Error while connecting to MySQL", e)
        return None

    finally:
        # Closing the connection
        if con:
            con.close()
# Checks if the recognized face is the owner of the card
def is_card_owner(card_hex):
    last_face_data = get_face_data()
    print(last_face_data)
    print(card_hex.strip())
    if last_face_data is None:
        print("nem pegou a cara! é mole?")
        return False  # No face data available
    if card_hex.strip() == "H000000000000233748310000" and last_face_data.strip() == "theo.jpg":
        return True
    elif card_hex.strip() == "HE28011700000233443319A9100000000" and last_face_data.strip() == "paulo.png":
        return True
    elif card_hex.strip() == "H000000000000234153310000" and last_face_data.strip() == "wellington.jpeg":
        return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-card')
def get_card():
    card_hex = get_card_hex()
    card_image = f"/static/images/{card_hex}.png"  # Image path based on HEX
    is_owner = is_card_owner(card_hex)
    return jsonify(is_owner=is_owner, card_image=card_image)

if __name__ == '__main__':
    app.run(debug=True)
