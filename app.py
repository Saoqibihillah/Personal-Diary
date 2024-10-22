

from flask import Flask, render_template, jsonify, request, url_for
from pymongo import MongoClient
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# Menghubungkan ke MongoDB
connecting_string = 'mongodb://syaoqibihillah:12345@dbsparta-shard-00-00.ykgta.mongodb.net:27017,dbsparta-shard-00-01.ykgta.mongodb.net:27017,dbsparta-shard-00-02.ykgta.mongodb.net:27017/?ssl=true&replicaSet=atlas-vhrewc-shard-0&authSource=admin&retryWrites=true&w=majority&appName=dbsparta'
client = MongoClient(connecting_string)
db = client['dbsparta']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))  # Mengambil data dari MongoDB
    return jsonify({'articles': articles})

@app.route('/diary', methods=['POST'])
def save_diary():
    try:
        title_receive = request.form.get("title_give")
        content_receive = request.form.get("content_give")

        if not title_receive or not content_receive:
            return jsonify({'msg': 'Data is incomplete'}), 400

        today = datetime.now()
        mytime = today.strftime("%Y-%m-%d-%H-%M-%S")

        # Process file (content image)
        file = request.files.get("file_give")
        filename = None
        if file:
            extension = file.filename.split('.')[-1]
            filename = secure_filename(f'post-{mytime}.{extension}')
            filepath = os.path.join('static', filename)
            
            if not os.path.exists('static'):
                os.makedirs('static')

            file.save(filepath)
            print(f"File saved as: {filepath}")

        # Process profile image
        profile = request.files.get("profile_give")
        profilefilename = None
        if profile:
            extension = profile.filename.split('.')[-1]
            profilefilename = secure_filename(f'profile-{mytime}.{extension}')
            profilepath = os.path.join('static', profilefilename)
            profile.save(profilepath)
            print(f"Profile saved as: {profilepath}")

        # Save to MongoDB
        doc = {
            'title': title_receive,
            'content': content_receive,
            'file': filename,  # Save content image file path
            'profile': profilefilename  # Save profile image file path
        }
        db.diary.insert_one(doc)
        return jsonify({'msg': 'Data inserted successfully!'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'msg': 'Error inserting data!'}), 500

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
