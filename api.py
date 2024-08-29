from flask import Flask, request, jsonify
import json
import random
import openai

app = Flask(__name__)

# Configuración de la API Key de OpenAI
openai.api_key = 'sk-bDXiyKSGw2pZr2HubUfqb9vp8wEtNtvjJGZiIKeo6IT3BlbkFJ-OJgaMyDwVQd61BK9gpwgTTuCwfFEt0SiEJWiV6P4A'

# Cargar el archivo JSON con las recomendaciones
with open('recommendations.json', 'r') as file:
    recommendations = json.load(file)

# Método GET para obtener la lista completa de recomendaciones
@app.route('/recommendations', methods=['GET'])
def get_all_recommendations():
    return jsonify(recommendations)

# Ruta para obtener recomendaciones
@app.route('/recommend', methods=['POST'])
def get_recommendation():
    data = request.get_json()

    # Obtener los parámetros de la solicitud
    place = data.get('place')
    genre = data.get('genre')
    song = data.get('song')
    use_chatgpt = data.get('use_chatgpt', False)

    # Verificar si se debe usar ChatGPT
    if use_chatgpt:
        return get_recommendation_from_chatgpt(place, genre, song)

    # Contar cuántos inputs ha proporcionado el usuario
    input_count = sum(x is not None for x in [place, genre, song])

    # Si el usuario envía un solo input
    if input_count == 1:
        if place:
            if place in recommendations:
                recommendation = random.choice(recommendations[place])
                return jsonify(recommendation)
            else:
                return jsonify({"message": "Place not found"}), 404

        elif genre:
            matches = [key for key, values in recommendations.items() if any(value['genre'].lower() == genre.lower() for value in values)]
            if matches:
                match = random.choice(matches)
                recommendation = random.choice([value for value in recommendations[match] if value['genre'].lower() == genre.lower()])
                return jsonify({"place": match, "song": recommendation['song']})
            else:
                return jsonify({"message": "Genre not found"}), 404

        elif song:
            matches = [key for key, values in recommendations.items() if any(value['song'].lower() == song.lower() for value in values)]
            if matches:
                match = random.choice(matches)
                recommendation = random.choice([value for value in recommendations[match] if value['song'].lower() == song.lower()])
                return jsonify({"place": match, "genre": recommendation['genre']})
            else:
                return jsonify({"message": "Song not found"}), 404

    # Si el usuario envía dos inputs
    elif input_count == 2:
        if genre and song:
            matches = [key for key, values in recommendations.items() if any(value['genre'].lower() == genre.lower() and value['song'].lower() == song.lower() for value in values)]
            if matches:
                match = random.choice(matches)
                return jsonify({"place": match})
            else:
                return jsonify({"message": "No matching place found"}), 404

        elif genre and place:
            if place in recommendations:
                matches = [value for value in recommendations[place] if value['genre'].lower() == genre.lower()]
                if matches:
                    recommendation = random.choice(matches)
                    return jsonify({"song": recommendation['song']})
                else:
                    return jsonify({"message": "No matching song found"}), 404

        elif place and song:
            if place in recommendations:
                matches = [value for value in recommendations[place] if value['song'].lower() == song.lower()]
                if matches:
                    recommendation = random.choice(matches)
                    return jsonify({"genre": recommendation['genre']})
                else:
                    return jsonify({"message": "No matching genre found"}), 404

    # Si no se proporcionó input o se proporcionaron más de dos inputs
    else:
        return jsonify({"message": "Invalid request format. Please send one or two of the following: place, genre, song."}), 400

def get_recommendation_from_chatgpt(place, genre, song):
    # Construir el prompt para ChatGPT
    prompt = f"Provide a recommendation based on the following inputs:\nPlace: {place}\nGenre: {genre}\nSong: {song}\n"

    try:
        # Configuración de la solicitud a ChatGPT usando la librería openai
        response = openai.Completion.create(
            model="text-davinci-003",  # O usa otro modelo disponible como "gpt-3.5-turbo" o "gpt-4"
            prompt=prompt,
            max_tokens=150
        )
        recommendation = response.choices[0].text.strip()
        return jsonify({"recommendation": recommendation})
    except Exception as e:
        return jsonify({"message": f"Failed to get a recommendation from ChatGPT: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)