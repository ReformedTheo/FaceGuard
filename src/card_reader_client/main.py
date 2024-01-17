from flask import Flask, render_template, jsonify
import socket
import json

app = Flask(__name__)

def get_card_hex():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.0.0.144', 2189))
    command = 'R\r\n'
    s.sendall(command.encode())
    response = s.recv(1024)
    s.close()
    return response.decode()

def get_face_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.0.0.144', 9091))
    face_data = client_socket.recv(1024).decode()
    client_socket.close()
    return json.loads(face_data)

def determine_card(hex_value):
    cards = {
        "H000000000000233748310000": "sete de copas",
        "H000000000000234153310000": "espadilha",
        "H000000000000233744310000": "sete de ouros",
        "HE28011700000233443319A9100000000": "zap"
    }
    return cards.get(hex_value, "Carta desconhecida")

def is_card_owner(card_hex):
    user_face = get_face_data()
    print(user_face)
    return True
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-card')
def get_card():
    card_hex = get_card_hex()
    card_name = determine_card(card_hex)
    card_image = f"/static/images/{card_hex}.png"  # Caminho da imagem baseado no HEX
    is_owner = is_card_owner(card_hex)
    return jsonify(is_owner = is_owner, card_name=card_name, card_image=card_image)

if __name__ == '__main__':
    app.run(debug=True)