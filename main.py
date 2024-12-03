import random
import os
import json
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File for saving results
RESULTS_FILE = "results.txt"

# Probability distributions for single and 11-pull gachas
rarity_prob_single = {
    "N": 0.33,
    "N+": 0.25,
    "R": 0.2,
    "R+": 0.15,
    "SR": 0.05,
    "SR+": 0.02
}
rarity_prob_11 = {
    "R": 0.57,
    "R+": 0.3,
    "SR": 0.1,
    "SR+": 0.03
}

# Define file names for each rarity type, assuming each has 10 images
rarity_images = {
    "N": [f"N_{i}.png" for i in range(1, 11)],
    "N+": [f"N_plus_{i}.png" for i in range(1, 11)],
    "R": [f"R_{i}.png" for i in range(1, 11)],
    "R+": [f"R_plus_{i}.png" for i in range(1, 11)],
    "SR": [f"SR_{i}.png" for i in range(1, 11)],
    "SR+": [f"SR_plus_{i}.png" for i in range(1, 11)]
}

sr_plus_characters = [f"Character {i}" for i in range(1, 11)]

# Save cumulative results to a file
def save_results_to_file(results):
    with open(RESULTS_FILE, 'w') as file:
        json.dump(results, file)

# Load cumulative results from a file
def load_results_from_file():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as file:
            return json.load(file)
    return {rarity: 0 for rarity in rarity_images}

def init_session():
    session['results'] = load_results_from_file()
    session['images'] = []
    session['total_pulls'] = 0
    session['total_cost'] = 0
    session['sr_plus_obtained'] = []  # Initialize as a list

def pull_gacha(probabilities):
    rand = random.random()
    cumulative = 0
    for rarity, prob in probabilities.items():
        cumulative += prob
        if rand < cumulative:
            return rarity
    return "N"

@app.route('/reset')
def reset():
    init_session()
    save_results_to_file(session['results'])  # Reset saved results
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'results' not in session:
        init_session()
    return render_template('index.html', results=session['results'], images=session['images'],
                           total_pulls=session['total_pulls'], total_cost=session['total_cost'])

@app.route('/single_pull')
def single_pull():
    if 'results' not in session:
        init_session()
    result = pull_gacha(rarity_prob_single)
    session['results'][result] += 1

    # Select a random image from the chosen rarity
    image_file = random.choice(rarity_images[result])
    session['images'].append(image_file)

    # Track SR+ character collection
    if result == "SR+":
        character = random.choice(sr_plus_characters)
        if character not in session['sr_plus_obtained']:
            session['sr_plus_obtained'].append(character)  # Append to list

    session['total_pulls'] += 1
    session['total_cost'] += 100

    # Save updated results to file
    save_results_to_file(session['results'])

    return redirect(url_for('index'))

@app.route('/eleven_pull')
def eleven_pull():
    if 'results' not in session:
        init_session()
    for _ in range(10):
        result = pull_gacha(rarity_prob_11)
        session['results'][result] += 1
        image_file = random.choice(rarity_images[result])
        session['images'].append(image_file)

        if result == "SR+":
            character = random.choice(sr_plus_characters)
            if character not in session['sr_plus_obtained']:
                session['sr_plus_obtained'].append(character)  # Append to list

    # Guarantee SR for the 11th pull
    session['results']['SR'] += 1
    session['images'].append(random.choice(rarity_images["SR"]))
    session['total_pulls'] += 11
    session['total_cost'] += 1000

    # Save updated results to file
    save_results_to_file(session['results'])

    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(RESULTS_FILE):
        save_results_to_file({rarity: 0 for rarity in rarity_images})
    app.run(debug=True, host='0.0.0.0', port=8080)
