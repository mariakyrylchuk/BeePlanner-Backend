import hashlib
import json
import os
import random
import uuid
from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Файли для зберігання даних
USERS_FILE = 'users.json'
APIARIES_FILE = 'apiaries.json'
JOURNAL_FILE = 'journal.json'
VERIFICATIONS_FILE = 'verifications.json'
REVIEWS_FILE = 'reviews.json'
LAYERS_FILE = 'layers.json'
HONEY_PLANTS_FILE = 'honey_plants.json'
NOTIFICATIONS_FILE = 'notifications.json'
ROUTES_FILE = 'routes.json'
COOPERATION_FILE = 'cooperation.json'
LOCATIONS_FILE = 'locations.json'


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


def init_files():
    """Створює пусті файли, якщо їх немає"""
    files = [USERS_FILE, APIARIES_FILE, JOURNAL_FILE, VERIFICATIONS_FILE,
             REVIEWS_FILE, LAYERS_FILE, HONEY_PLANTS_FILE, NOTIFICATIONS_FILE,
             ROUTES_FILE, COOPERATION_FILE, LOCATIONS_FILE]

    for file in files:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)


def load_data(filename):
    """Завантажує дані з файлу"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []


def save_data(filename, data):
    """Зберігає дані у файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def hash_password(password):
    """Хешує пароль"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    """Перевіряє пароль"""
    return hash_password(password) == hashed_password


def get_month_name(month):
    months = [
        'Січень', 'Лютий', 'Березень', 'Квітень',
        'Травень', 'Червень', 'Липень', 'Серпень',
        'Вересень', 'Жовтень', 'Листопад', 'Грудень'
    ]
    return months[month - 1] if 1 <= month <= 12 else 'Невідомо'


def get_demo_weather_data(lat, lon):
    """Повертає демо-дані погоди"""
    current_date = datetime.now()

    # Генеруємо демо-дані на основі пори року
    current_month = current_date.month
    if 5 <= current_month <= 9:  # Літо/весна
        base_temp = random.randint(18, 28)
    else:  # Осінь/зима
        base_temp = random.randint(5, 15)

    current_weather = {
        'temp': base_temp,
        'feels_like': base_temp - random.randint(0, 3),
        'humidity': random.randint(50, 85),
        'pressure': random.randint(990, 1020),
        'wind_speed': round(random.uniform(1.0, 6.0), 1),
        'weather': [{
            'main': random.choice(['Clear', 'Clouds', 'Clouds', 'Partly Cloudy']),
            'description': random.choice(['ясно', 'хмарно', 'мінлива хмарність']),
            'icon': random.choice(['01d', '02d', '03d', '04d'])
        }],
        'sunrise': int((datetime.now().replace(hour=5, minute=30, second=0).timestamp())),
        'sunset': int((datetime.now().replace(hour=20, minute=45, second=0).timestamp())),
        'clouds': random.randint(0, 50),
        'visibility': random.randint(8000, 12000)
    }

    # Демо прогноз
    forecast = []
    for i in range(1, 4):
        date = (current_date + timedelta(days=i)).strftime('%Y-%m-%d')

        if base_temp >= 20:
            temp_day = base_temp + random.randint(-3, 3)
            temp_night = temp_day - random.randint(5, 10)
        else:
            temp_day = base_temp + random.randint(-2, 2)
            temp_night = temp_day - random.randint(3, 8)

        condition = random.choice(['sunny', 'partly_cloudy', 'cloudy'])

        if temp_day >= 15 and temp_day <= 28 and condition != 'cloudy':
            bee_activity = 'висока'
            foraging_hours = 10
        elif temp_day >= 10 and temp_day <= 30:
            bee_activity = 'середня'
            foraging_hours = 7
        else:
            bee_activity = 'низька'
            foraging_hours = 4

        forecast.append({
            'date': date,
            'temp_day': temp_day,
            'temp_night': temp_night,
            'humidity': random.randint(55, 90),
            'wind_speed': round(random.uniform(1.0, 8.0), 1),
            'precipitation': random.choice([0, 0, 0, 5, 10]),
            'condition': condition,
            'bee_activity': bee_activity,
            'foraging_hours': foraging_hours
        })

    return jsonify({
        'success': True,
        'current': current_weather,
        'forecast': forecast,
        'location': {
            'name': 'Демо локація',
            'country': 'Україна'
        },
        'demo_data': True,
        'message': 'Використовуються демо-дані. Додайте API ключ для реальної погоди.',
        'timestamp': datetime.now().isoformat()
    })


# ==================== БАЗОВІ МАРШРУТИ ====================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'message': 'Сервер працює!'})


@app.route('/api/test', methods=['GET'])
def test():
    """Тестовий endpoint для перевірки"""
    return jsonify({
        'success': True,
        'message': 'API працює коректно!',
        'timestamp': datetime.now().isoformat(),
        'endpoints': [
            '/api/health',
            '/api/register',
            '/api/login',
            '/api/profile',
            '/api/apiaries',
            '/api/journal-notes'
        ]
    })


# ==================== АВТЕНТИФІКАЦІЯ ====================
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        user_type = data.get('user_type', 'Пасічник')

        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Невірний email'})

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Пароль має бути від 6 символів'})

        if not full_name:
            return jsonify({'success': False, 'message': "Введіть повне ім'я"})

        users = load_data(USERS_FILE)

        for user in users:
            if user['email'].lower() == email:
                return jsonify({'success': False, 'message': 'Користувач з таким email вже існує'})

        new_user = {
            'id': str(uuid.uuid4()),
            'email': email,
            'password': hash_password(password),
            'full_name': full_name,
            'phone': phone,
            'user_type': user_type,
            'is_verified': False,
            'apiaries_count': 0,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }

        users.append(new_user)
        save_data(USERS_FILE, users)

        return jsonify({
            'success': True,
            'message': 'Реєстрація успішна!',
            'user': {
                'id': new_user['id'],
                'email': email,
                'full_name': full_name,
                'user_type': user_type,
                'phone': phone,
                'is_verified': False
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка сервера: {str(e)}'})


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'success': False, 'message': 'Введіть email та пароль'})

        users = load_data(USERS_FILE)

        for user in users:
            if user['email'].lower() == email:
                if verify_password(password, user['password']):
                    user['last_login'] = datetime.now().isoformat()
                    save_data(USERS_FILE, users)

                    return jsonify({
                        'success': True,
                        'message': 'Вхід успішний!',
                        'user': {
                            'id': user['id'],
                            'email': user['email'],
                            'full_name': user['full_name'],
                            'user_type': user['user_type'],
                            'phone': user.get('phone', ''),
                            'is_verified': user.get('is_verified', False)
                        }
                    })
                else:
                    return jsonify({'success': False, 'message': 'Невірний пароль'})

        return jsonify({'success': False, 'message': 'Користувача не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка сервера: {str(e)}'})


# ==================== ПРОФІЛЬ ====================
@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        users = load_data(USERS_FILE)

        for user in users:
            if user['id'] == user_id:
                # Отримуємо статистику для профілю
                apiaries = load_data(APIARIES_FILE)
                user_apiaries = [a for a in apiaries if a.get('user_id') == user_id]
                total_hives = sum(a.get('hive_count', 0) for a in user_apiaries)

                notes = load_data(JOURNAL_FILE)
                user_notes = [n for n in notes if n.get('user_id') == user_id]

                return jsonify({
                    'success': True,
                    'profile': {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': user['full_name'],
                        'user_type': user['user_type'],
                        'phone': user.get('phone', ''),
                        'is_verified': user.get('is_verified', False),
                        'created_at': user['created_at'],
                        'last_login': user.get('last_login'),
                        'apiaries_count': len(user_apiaries),
                        'total_hives': total_hives,
                        'journal_entries': len(user_notes)
                    }
                })

        return jsonify({'success': False, 'message': 'Профіль не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Оновлення профілю користувача"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        users = load_data(USERS_FILE)

        for i, user in enumerate(users):
            if user['id'] == user_id:
                # Оновлюємо дані
                if 'full_name' in data:
                    users[i]['full_name'] = data['full_name'].strip()
                if 'phone' in data:
                    users[i]['phone'] = data['phone'].strip()
                if 'user_type' in data:
                    users[i]['user_type'] = data['user_type']

                # Оновлюємо пароль, якщо надано
                if 'password' in data and data['password']:
                    if len(data['password']) >= 6:
                        users[i]['password'] = hash_password(data['password'])
                    else:
                        return jsonify({'success': False, 'message': 'Пароль має бути від 6 символів'})

                users[i]['updated_at'] = datetime.now().isoformat()
                save_data(USERS_FILE, users)

                return jsonify({
                    'success': True,
                    'message': 'Профіль успішно оновлено',
                    'profile': {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': users[i]['full_name'],
                        'phone': users[i].get('phone', ''),
                        'user_type': users[i]['user_type']
                    }
                })

        return jsonify({'success': False, 'message': 'Користувача не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== ПАСІКИ ====================
@app.route('/api/apiaries', methods=['GET'])
def get_apiaries():
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        apiaries = load_data(APIARIES_FILE)
        user_apiaries = [a for a in apiaries if a.get('user_id') == user_id]

        # Сортуємо за датою створення (нові спочатку)
        user_apiaries.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'apiaries': user_apiaries,
            'count': len(user_apiaries)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/apiary/<apiary_id>', methods=['GET'])
def get_apiary(apiary_id):
    try:
        user_id = request.args.get('user_id')

        if not apiary_id or not user_id:
            return jsonify({'success': False, 'message': 'ID пасіки або користувача не вказано'})

        apiaries = load_data(APIARIES_FILE)

        for apiary in apiaries:
            if apiary['id'] == apiary_id and apiary['user_id'] == user_id:
                # Отримуємо нотатки для цієї пасіки
                notes = load_data(JOURNAL_FILE)
                apiary_notes = [n for n in notes if n.get('apiary_id') == apiary_id]

                apiary['notes_count'] = len(apiary_notes)
                apiary['last_note'] = apiary_notes[0] if apiary_notes else None

                return jsonify({
                    'success': True,
                    'apiary': apiary
                })

        return jsonify({'success': False, 'message': 'Пасіку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/add-apiary', methods=['POST'])
def add_apiary():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        # Перевіряємо користувача
        users = load_data(USERS_FILE)
        user_exists = False
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users[i]['apiaries_count'] = users[i].get('apiaries_count', 0) + 1
                save_data(USERS_FILE, users)
                user_exists = True
                break

        if not user_exists:
            return jsonify({'success': False, 'message': 'Користувача не знайдено'})

        new_apiary = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': data.get('name', 'Нова пасіка'),
            'location': data.get('location', 'Не вказано'),
            'latitude': data.get('latitude', 50.45),
            'longitude': data.get('longitude', 30.52),
            'hive_count': int(data.get('hive_count', 0)),
            'hive_type': data.get('hive_type', 'Дадан'),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        apiaries = load_data(APIARIES_FILE)
        apiaries.append(new_apiary)
        save_data(APIARIES_FILE, apiaries)

        return jsonify({
            'success': True,
            'message': 'Пасіку додано',
            'apiary': new_apiary
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/update-apiary', methods=['POST'])
def update_apiary():
    try:
        data = request.json
        apiary_id = data.get('id')
        user_id = data.get('user_id')

        if not apiary_id or not user_id:
            return jsonify({'success': False, 'message': 'ID пасіки або користувача не вказано'})

        apiaries = load_data(APIARIES_FILE)

        # Шукаємо пасіку
        for i, apiary in enumerate(apiaries):
            if apiary['id'] == apiary_id and apiary['user_id'] == user_id:
                # Оновлюємо поля
                apiaries[i]['name'] = data.get('name', apiary['name'])
                apiaries[i]['location'] = data.get('location', apiary['location'])
                apiaries[i]['latitude'] = data.get('latitude', apiary.get('latitude', 50.45))
                apiaries[i]['longitude'] = data.get('longitude', apiary.get('longitude', 30.52))
                apiaries[i]['hive_count'] = int(data.get('hive_count', apiary.get('hive_count', 0)))
                apiaries[i]['hive_type'] = data.get('hive_type', apiary.get('hive_type', 'Дадан'))
                apiaries[i]['description'] = data.get('description', apiary.get('description', ''))
                apiaries[i]['updated_at'] = datetime.now().isoformat()

                # Зберігаємо
                save_data(APIARIES_FILE, apiaries)

                return jsonify({
                    'success': True,
                    'message': 'Пасіку оновлено успішно',
                    'apiary': apiaries[i]
                })

        return jsonify({'success': False, 'message': 'Пасіку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/delete-apiary', methods=['POST'])
def delete_apiary():
    try:
        data = request.json
        apiary_id = data.get('apiary_id')
        user_id = data.get('user_id')

        if not apiary_id or not user_id:
            return jsonify({'success': False, 'message': 'ID пасіки або користувача не вказано'})

        apiaries = load_data(APIARIES_FILE)

        # Шукаємо пасіку
        for i, apiary in enumerate(apiaries):
            if apiary['id'] == apiary_id and apiary['user_id'] == user_id:
                # Видаляємо пасіку
                deleted_apiary = apiaries.pop(i)

                # Оновлюємо кількість пасік у користувача
                users = load_data(USERS_FILE)
                for j, user in enumerate(users):
                    if user['id'] == user_id:
                        users[j]['apiaries_count'] = max(0, users[j].get('apiaries_count', 0) - 1)
                        save_data(USERS_FILE, users)
                        break

                # Видаляємо нотатки цієї пасіки
                notes = load_data(JOURNAL_FILE)
                notes = [n for n in notes if n.get('apiary_id') != apiary_id]
                save_data(JOURNAL_FILE, notes)

                # Зберігаємо оновлений список пасік
                save_data(APIARIES_FILE, apiaries)

                return jsonify({
                    'success': True,
                    'message': 'Пасіку видалено успішно',
                    'deleted_apiary': deleted_apiary
                })

        return jsonify({'success': False, 'message': 'Пасіку не знайдено або у вас немає прав'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== ЖУРНАЛ ====================
@app.route('/api/journal-notes', methods=['GET'])
def get_journal_notes():
    try:
        user_id = request.args.get('user_id')
        apiary_id = request.args.get('apiary_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        notes = load_data(JOURNAL_FILE)

        if apiary_id:
            user_notes = [n for n in notes if n.get('user_id') == user_id and n.get('apiary_id') == apiary_id]
        else:
            user_notes = [n for n in notes if n.get('user_id') == user_id]

        user_notes.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'notes': user_notes,
            'count': len(user_notes)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/journal-note/<note_id>', methods=['GET'])
def get_journal_note(note_id):
    try:
        user_id = request.args.get('user_id')

        if not note_id or not user_id:
            return jsonify({'success': False, 'message': 'ID нотатки або користувача не вказано'})

        notes = load_data(JOURNAL_FILE)

        for note in notes:
            if note['id'] == note_id and note['user_id'] == user_id:
                # Додаємо інформацію про пасіку, якщо є apiary_id
                if note.get('apiary_id'):
                    apiaries = load_data(APIARIES_FILE)
                    apiary_info = next((a for a in apiaries if a['id'] == note['apiary_id']), None)
                    if apiary_info:
                        note['apiary_name'] = apiary_info.get('name', 'Невідома пасіка')

                return jsonify({
                    'success': True,
                    'note': note
                })

        return jsonify({'success': False, 'message': 'Нотатку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/add-journal-note', methods=['POST'])
def add_journal_note():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        new_note = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'apiary_id': data.get('apiary_id'),
            'title': data.get('title', 'Нова нотатка'),
            'content': data.get('content', ''),
            'work_type': data.get('work_type', 'інше'),
            'hives_affected': int(data.get('hives_affected', 0)),
            'temperature': data.get('temperature'),
            'weather': data.get('weather'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        notes = load_data(JOURNAL_FILE)
        notes.append(new_note)
        save_data(JOURNAL_FILE, notes)

        return jsonify({
            'success': True,
            'message': 'Нотатку додано',
            'note': new_note
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/update-journal-note', methods=['POST'])
def update_journal_note():
    try:
        data = request.json
        note_id = data.get('id')
        user_id = data.get('user_id')

        if not note_id or not user_id:
            return jsonify({'success': False, 'message': 'ID нотатки або користувача не вказано'})

        notes = load_data(JOURNAL_FILE)

        # Шукаємо нотатку
        for i, note in enumerate(notes):
            if note['id'] == note_id and note['user_id'] == user_id:
                # Оновлюємо поля
                notes[i]['title'] = data.get('title', note['title'])
                notes[i]['content'] = data.get('content', note['content'])
                notes[i]['work_type'] = data.get('work_type', note.get('work_type', 'інше'))
                notes[i]['hives_affected'] = int(data.get('hives_affected', note.get('hives_affected', 0)))
                notes[i]['temperature'] = data.get('temperature', note.get('temperature'))
                notes[i]['weather'] = data.get('weather', note.get('weather'))
                notes[i]['apiary_id'] = data.get('apiary_id', note.get('apiary_id'))
                notes[i]['updated_at'] = datetime.now().isoformat()

                save_data(JOURNAL_FILE, notes)

                return jsonify({
                    'success': True,
                    'message': 'Нотатку оновлено успішно',
                    'note': notes[i]
                })

        return jsonify({'success': False, 'message': 'Нотатку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/delete-journal-note', methods=['POST'])
def delete_journal_note():
    try:
        data = request.json
        note_id = data.get('note_id')
        user_id = data.get('user_id')

        if not note_id or not user_id:
            return jsonify({'success': False, 'message': 'ID нотатки або користувача не вказано'})

        notes = load_data(JOURNAL_FILE)

        # Шукаємо нотатку
        for i, note in enumerate(notes):
            if note['id'] == note_id and note['user_id'] == user_id:
                deleted_note = notes.pop(i)
                save_data(JOURNAL_FILE, notes)

                return jsonify({
                    'success': True,
                    'message': 'Нотатку видалено успішно',
                    'deleted_note': deleted_note
                })

        return jsonify({'success': False, 'message': 'Нотатку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== СПІВПРАЦЯ ПАСІЧНИК-ФЕРМЕР ====================
@app.route('/api/cooperation/requests', methods=['GET'])
def get_cooperation_requests():
    """Отримання заявок на співпрацю"""
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        # Завантажуємо збережені запити
        requests_data = load_data(COOPERATION_FILE)
        user_requests = [r for r in requests_data if r.get('to_user_id') == user_id]

        # Якщо немає збережених, створюємо демо-дані
        if not user_requests:
            user_requests = [
                {
                    'id': 'req1',
                    'from_user': 'Фермер Петренко',
                    'from_user_id': 'farmer1',
                    'to_user_id': user_id,
                    'type': 'pollination',
                    'message': 'Потрібні бджоли для запилення яблуневого саду',
                    'location': 'с. Зелене, Київська обл.',
                    'area_ha': 5,
                    'crop': 'Яблуня',
                    'bloom_period': '15.04 - 05.05',
                    'status': 'pending',
                    'created_at': '2024-04-01T10:00:00'
                },
                {
                    'id': 'req2',
                    'from_user': 'Фермер Коваленко',
                    'from_user_id': 'farmer2',
                    'to_user_id': user_id,
                    'type': 'placement',
                    'message': 'Пропоную місце для пасіки на моїх полях',
                    'location': 'м. Вінниця',
                    'area_ha': 3,
                    'price_per_month': 0,
                    'status': 'pending',
                    'created_at': '2024-04-02T14:30:00'
                }
            ]
            # Зберігаємо демо-дані
            for req in user_requests:
                requests_data.append(req)
            save_data(COOPERATION_FILE, requests_data)

        # Сортуємо за датою (нові спочатку)
        user_requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'requests': user_requests,
            'count': len(user_requests)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/cooperation/send-request', methods=['POST'])
def send_cooperation_request():
    """Надсилання заявки на співпрацю"""
    try:
        data = request.json

        required_fields = ['from_user_id', 'to_user_id', 'type', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Не вказано поле: {field}'})

        new_request = {
            'id': str(uuid.uuid4()),
            'from_user': data.get('from_user', 'Анонімний користувач'),
            'from_user_id': data['from_user_id'],
            'to_user_id': data['to_user_id'],
            'type': data['type'],
            'message': data['message'],
            'location': data.get('location', ''),
            'area_ha': data.get('area_ha', 0),
            'crop': data.get('crop', ''),
            'bloom_period': data.get('bloom_period', ''),
            'price_per_month': data.get('price_per_month', 0),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }

        # Завантажуємо існуючі запити
        requests_data = load_data(COOPERATION_FILE)
        requests_data.append(new_request)

        # Зберігаємо оновлений список
        save_data(COOPERATION_FILE, requests_data)

        return jsonify({
            'success': True,
            'message': 'Заявку надіслано успішно!',
            'request': new_request
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/cooperation/respond', methods=['POST'])
def respond_to_cooperation_request():
    """Відповідь на заявку співпраці (прийняти/відхилити)"""
    try:
        data = request.json

        request_id = data.get('request_id')
        response = data.get('response')  # 'accept' або 'reject'
        message = data.get('message', '')

        if not request_id or not response:
            return jsonify({'success': False, 'message': 'Не вказано ID запиту або відповідь'})

        requests_data = load_data(COOPERATION_FILE)

        # Шукаємо запит
        for i, req in enumerate(requests_data):
            if req['id'] == request_id:
                requests_data[i]['status'] = 'accepted' if response == 'accept' else 'rejected'
                requests_data[i]['response_message'] = message
                requests_data[i]['responded_at'] = datetime.now().isoformat()

                # Зберігаємо оновлені дані
                save_data(COOPERATION_FILE, requests_data)

                return jsonify({
                    'success': True,
                    'message': f'Заявку успішно {"прийнято" if response == "accept" else "відхилено"}',
                    'request': requests_data[i]
                })

        return jsonify({'success': False, 'message': 'Заявку не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== СПОВІЩЕННЯ ====================
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Отримання сповіщення для користувача"""
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        # Завантажуємо сповіщення з файлу
        notifications_data = load_data(NOTIFICATIONS_FILE)
        user_notifications = [n for n in notifications_data if n.get('user_id') == user_id]

        # Якщо немає сповіщень, створюємо демо-дані
        if not user_notifications:
            user_notifications = [
                {
                    'id': 'notif1',
                    'user_id': user_id,
                    'type': 'info',
                    'title': 'Початок цвітіння ріпаку',
                    'message': 'Ріпак почне цвісти через 3 дні в вашому регіоні',
                    'is_read': False,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': 'notif2',
                    'user_id': user_id,
                    'type': 'warning',
                    'title': 'Прогноз погоди',
                    'message': 'Завтра очікується дощ, обмежте роботи з бджолами',
                    'is_read': True,
                    'created_at': (datetime.now() - timedelta(days=1)).isoformat()
                },
                {
                    'id': 'notif3',
                    'user_id': user_id,
                    'type': 'success',
                    'title': 'Нова заявка',
                    'message': 'Фермер Петренко запрошує вас для співпраці',
                    'is_read': False,
                    'created_at': datetime.now().isoformat()
                }
            ]
            # Зберігаємо демо-дані
            for notif in user_notifications:
                notifications_data.append(notif)
            save_data(NOTIFICATIONS_FILE, notifications_data)

        # Сортуємо за датою (нові спочатку)
        user_notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Рахуємо непрочитані
        unread_count = sum(1 for n in user_notifications if not n.get('is_read', False))

        return jsonify({
            'success': True,
            'notifications': user_notifications,
            'unread_count': unread_count,
            'total': len(user_notifications)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notification_read():
    """Позначити сповіщення як прочитане"""
    try:
        data = request.json
        notification_id = data.get('notification_id')
        user_id = data.get('user_id')

        if not notification_id or not user_id:
            return jsonify({'success': False, 'message': 'Не вказано ID сповіщення або користувача'})

        notifications_data = load_data(NOTIFICATIONS_FILE)

        # Шукаємо сповіщення
        for i, notif in enumerate(notifications_data):
            if notif['id'] == notification_id and notif['user_id'] == user_id:
                notifications_data[i]['is_read'] = True
                notifications_data[i]['read_at'] = datetime.now().isoformat()

                # Зберігаємо оновлені дані
                save_data(NOTIFICATIONS_FILE, notifications_data)

                return jsonify({
                    'success': True,
                    'message': 'Сповіщення позначено як прочитане'
                })

        return jsonify({'success': False, 'message': 'Сповіщення не знайдено'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Позначити всі сповіщення користувача як прочитані"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        notifications_data = load_data(NOTIFICATIONS_FILE)

        # Позначаємо всі сповіщення користувача як прочитані
        for i, notif in enumerate(notifications_data):
            if notif['user_id'] == user_id and not notif.get('is_read', False):
                notifications_data[i]['is_read'] = True
                notifications_data[i]['read_at'] = datetime.now().isoformat()

        # Зберігаємо оновлені дані
        save_data(NOTIFICATIONS_FILE, notifications_data)

        return jsonify({
            'success': True,
            'message': 'Усі сповіщення позначено як прочитані'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== МЕДОНОСИ ====================
@app.route('/api/honey-plants', methods=['GET'])
def get_honey_plants():
    try:
        plants = load_data(HONEY_PLANTS_FILE)

        if not plants:
            plants = [
                {
                    'id': 1,
                    'name': 'Липа дрібнолиста',
                    'bloom_start': '15.06',
                    'bloom_end': '10.07',
                    'coefficient': 1.0,
                    'honey_yield': 800,
                    'pollen_yield': 30,
                    'description': 'Основний літній медонос'
                },
                {
                    'id': 2,
                    'name': 'Гречка',
                    'bloom_start': '20.06',
                    'bloom_end': '30.07',
                    'coefficient': 0.8,
                    'honey_yield': 60,
                    'pollen_yield': 20,
                    'description': 'Сільськогосподарська культура'
                },
                {
                    'id': 3,
                    'name': 'Ріпак',
                    'bloom_start': '01.05',
                    'bloom_end': '25.05',
                    'coefficient': 0.6,
                    'honey_yield': 50,
                    'pollen_yield': 15,
                    'description': 'Ранній медонос'
                },
                {
                    'id': 4,
                    'name': 'Акація',
                    'bloom_start': '10.05',
                    'bloom_end': '31.05',
                    'coefficient': 0.9,
                    'honey_yield': 700,
                    'pollen_yield': 25,
                    'description': 'Весняний медонос'
                },
                {
                    'id': 5,
                    'name': 'Конюшина',
                    'bloom_start': '15.06',
                    'bloom_end': '15.08',
                    'coefficient': 0.7,
                    'honey_yield': 100,
                    'pollen_yield': 40,
                    'description': 'Луговий медонос'
                }
            ]
            save_data(HONEY_PLANTS_FILE, plants)

        return jsonify({
            'success': True,
            'plants': plants,
            'total': len(plants)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/bloom-calendar', methods=['GET'])
def bloom_calendar():
    try:
        month = int(request.args.get('month', datetime.now().month))

        plants = load_data(HONEY_PLANTS_FILE)
        if not plants:
            return jsonify({'success': True, 'month': month, 'blooming_plants': [], 'count': 0})

        blooming_plants = []
        for plant in plants:
            bloom_start_month = int(plant.get('bloom_start', '01.01').split('.')[1])
            bloom_end_month = int(plant.get('bloom_end', '31.12').split('.')[1])

            if bloom_start_month <= month <= bloom_end_month:
                blooming_plants.append(plant)

        return jsonify({
            'success': True,
            'month': month,
            'month_name': get_month_name(month),
            'blooming_plants': blooming_plants,
            'count': len(blooming_plants)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== АНАЛІЗ ЛОКАЦІЇ ====================
@app.route('/api/analyze-location', methods=['POST'])
def analyze_location():
    try:
        data = request.json
        lat = data.get('lat', 50.45)
        lon = data.get('lon', 30.52)
        radius_km = data.get('radius', 3)

        # Симулюємо аналіз
        potential_yield = random.uniform(50, 300)
        recommended_hives = max(1, int(potential_yield / 30))
        efficiency_score = min(100, int((potential_yield / 300) * 100))

        # Отримуємо список рослин в радіусі
        plants = load_data(HONEY_PLANTS_FILE)
        nearby_plants = random.sample(plants, min(3, len(plants)))

        return jsonify({
            'success': True,
            'analysis': {
                'location': {'lat': lat, 'lon': lon},
                'radius_km': radius_km,
                'potential_yield_kg': round(potential_yield, 2),
                'recommended_hives': recommended_hives,
                'efficiency_percent': efficiency_score,
                'nearby_plants': nearby_plants,
                'message': f'Потенційний збір: {round(potential_yield, 2)} кг. Рекомендовано вуликів: {recommended_hives}.'
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка аналізу: {str(e)}'})


# ==================== ПОГОДА ====================
@app.route('/api/weather/forecast', methods=['GET'])
def get_weather_forecast():
    try:
        lat = float(request.args.get('lat', 50.45))
        lon = float(request.args.get('lon', 30.52))
        days = int(request.args.get('days', 3))

        forecast = []
        for i in range(days):
            date = datetime.now() + timedelta(days=i)

            current_month = datetime.now().month
            if 5 <= current_month <= 9:
                temp_day = random.randint(18, 32)
                temp_night = random.randint(12, 20)
            else:
                temp_day = random.randint(10, 22)
                temp_night = random.randint(5, 15)

            if temp_day >= 15 and temp_day <= 30:
                bee_activity = 'висока' if temp_day >= 20 else 'середня'
            else:
                bee_activity = 'низька'

            forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'temp_day': temp_day,
                'temp_night': temp_night,
                'humidity': random.randint(50, 85),
                'wind_speed': random.randint(1, 10),
                'precipitation': random.choice([0, 0, 0, 10, 20, 30]),
                'condition': random.choice(['sunny', 'partly_cloudy', 'cloudy']),
                'bee_activity': bee_activity,
                'foraging_hours': random.randint(4, 12)
            })

        return jsonify({
            'success': True,
            'location': {'lat': lat, 'lon': lon},
            'forecast': forecast
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Ендпоінт /api/weather - перенаправляє на /api/weather/real"""
    try:
        lat = request.args.get('lat', 50.45)
        lon = request.args.get('lon', 30.52)

        # Просто викликаємо ту саму функцію, що й для /api/weather/real
        return get_real_weather()

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка отримання погоди: {str(e)}'})


@app.route('/api/weather/real', methods=['GET'])
def get_real_weather():
    """Отримання реальної погоди за геолокацією"""
    try:
        lat = request.args.get('lat', 50.45)
        lon = request.args.get('lon', 30.52)

        # ВАШ НОВИЙ API КЛЮЧ
        API_KEY = '2d5269ffcc91aebf9cb1193ca0507537'

        # Перевірка ключа
        print(f"🔑 Використовую API ключ: {API_KEY[:8]}...")
        print(f"📍 Запит погоди для координат: {lat}, {lon}")

        # Використовуємо OpenWeatherMap API
        current_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ua'
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=ua&cnt=40'

        # Робимо запити до API
        print(f"🌤️ Запит поточної погоди...")
        current_response = requests.get(current_url, timeout=10)

        # Перевіряємо статус
        if current_response.status_code != 200:
            print(f"⚠️ API помилка: {current_response.status_code}")
            print(f"📄 Відповідь: {current_response.text[:100]}")
            # Повертаємо демо-дані
            return get_demo_weather_data(lat, lon)

        current_data = current_response.json()

        # Перевіряємо, чи API повернуло помилку
        if current_data.get('cod') != 200:
            error_msg = current_data.get('message', 'Невідома помилка API')
            print(f"⚠️ API помилка: {error_msg}")
            return get_demo_weather_data(lat, lon)

        print(f"✅ Поточна погода отримана: {current_data.get('name', 'Невідомо')}")

        # Отримуємо прогноз
        print(f"📅 Запит прогнозу погоди...")
        forecast_response = requests.get(forecast_url, timeout=10)

        forecast_data = None
        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            print(f"✅ Прогноз отримано: {len(forecast_data.get('list', []))} записів")
        else:
            print(f"⚠️ Не вдалося отримати прогноз: {forecast_response.status_code}")

        # Обробка поточної погоди
        current_weather = {
            'temp': current_data['main']['temp'],
            'feels_like': current_data['main']['feels_like'],
            'humidity': current_data['main']['humidity'],
            'pressure': current_data['main']['pressure'],
            'wind_speed': current_data['wind']['speed'],
            'weather': current_data['weather'],
            'sunrise': current_data['sys']['sunrise'],
            'sunset': current_data['sys']['sunset'],
            'clouds': current_data.get('clouds', {}).get('all', 0),
            'visibility': current_data.get('visibility', 10000)
        }

        # Обробка прогнозу (якщо є дані)
        forecast = []
        if forecast_data and forecast_data.get('list'):
            daily_forecasts = {}

            # Групуємо прогнози по днях
            for item in forecast_data['list']:
                date_time = datetime.fromtimestamp(item['dt'])
                date = date_time.strftime('%Y-%m-%d')
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)

            # Видаляємо сьогоднішній день
            today = datetime.now().strftime('%Y-%m-%d')
            if today in daily_forecasts:
                del daily_forecasts[today]

            # Беремо наступні 3 дні
            dates = sorted(daily_forecasts.keys())[:3]

            for date in dates:
                day_forecasts = daily_forecasts[date]

                if not day_forecasts:
                    continue

                # Знаходимо макс/мін температури
                temps = [f['main']['temp'] for f in day_forecasts]
                humidities = [f['main']['humidity'] for f in day_forecasts]
                winds = [f['wind']['speed'] for f in day_forecasts]
                conditions = [f['weather'][0]['main'] for f in day_forecasts]

                # Знаходимо основний стан погоди
                main_condition = max(set(conditions), key=conditions.count) if conditions else 'Clear'

                # Визначення активності бджіл
                temp_day = max(temps) if temps else current_weather['temp']
                temp_night = min(temps) if temps else current_weather['temp'] - 5

                if temp_day >= 15 and temp_day <= 28 and 'Rain' not in main_condition:
                    bee_activity = 'висока'
                    foraging_hours = 10
                elif temp_day >= 10 and temp_day <= 30:
                    bee_activity = 'середня'
                    foraging_hours = 7
                else:
                    bee_activity = 'низька'
                    foraging_hours = 4

                # Сума опадів за день
                precipitation = sum(
                    f.get('rain', {}).get('3h', 0)
                    for f in day_forecasts
                    if f.get('rain')
                )

                forecast.append({
                    'date': date,
                    'temp_day': round(temp_day, 1),
                    'temp_night': round(temp_night, 1),
                    'humidity': round(sum(humidities) / len(humidities), 1) if humidities else current_weather[
                        'humidity'],
                    'wind_speed': round(sum(winds) / len(winds), 1) if winds else current_weather['wind_speed'],
                    'precipitation': round(precipitation, 1),
                    'condition': main_condition.lower(),
                    'bee_activity': bee_activity,
                    'foraging_hours': foraging_hours
                })
        else:
            # Якщо немає прогнозу, генеруємо на основі поточних даних
            print(f"ℹ️  Генерую прогноз на основі поточних даних")
            for i in range(1, 4):
                date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                temp_day = current_weather['temp'] + random.randint(-3, 3)
                temp_night = current_weather['temp'] - random.randint(5, 10)

                if temp_day >= 15 and temp_day <= 28 and 'Rain' not in current_weather['weather'][0]['main']:
                    bee_activity = 'висока'
                    foraging_hours = 10
                elif temp_day >= 10 and temp_day <= 30:
                    bee_activity = 'середня'
                    foraging_hours = 7
                else:
                    bee_activity = 'низька'
                    foraging_hours = 4

                forecast.append({
                    'date': date,
                    'temp_day': temp_day,
                    'temp_night': temp_night,
                    'humidity': random.randint(55, 85),
                    'wind_speed': current_weather['wind_speed'] + random.uniform(-1, 1),
                    'precipitation': random.choice([0, 0, 0, 5, 10]),
                    'condition': current_weather['weather'][0]['main'].lower(),
                    'bee_activity': bee_activity,
                    'foraging_hours': foraging_hours
                })

        # Форматуємо час сходу та заходу сонця
        def format_timestamp(timestamp):
            try:
                return datetime.fromtimestamp(timestamp).strftime('%H:%M')
            except:
                return "00:00"

        current_weather['sunrise_formatted'] = format_timestamp(current_weather['sunrise'])
        current_weather['sunset_formatted'] = format_timestamp(current_weather['sunset'])

        print(f"✅ Дані погоди успішно оброблені")

        return jsonify({
            'success': True,
            'current': current_weather,
            'forecast': forecast,
            'location': {
                'name': current_data.get('name', 'Невідомо'),
                'country': current_data['sys']['country']
            },
            'timestamp': datetime.now().isoformat(),
            'demo_data': False,
            'message': 'Реальні дані погоди з OpenWeatherMap'
        })

    except Exception as e:
        print(f'❌ Помилка отримання погоди: {str(e)}')
        import traceback
        traceback.print_exc()
        # Повертаємо демо-дані у разі помилки
        return get_demo_weather_data(
            request.args.get('lat', 50.45),
            request.args.get('lon', 30.52)
        )


# ==================== СТАТИСТИКА ====================
@app.route('/api/statistics/user', methods=['GET'])
def get_user_statistics():
    try:
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'Користувач не вказаний'})

        apiaries = load_data(APIARIES_FILE)
        user_apiaries = [a for a in apiaries if a.get('user_id') == user_id]

        notes = load_data(JOURNAL_FILE)
        user_notes = [n for n in notes if n.get('user_id') == user_id]

        # Розрахунок статистики
        total_hives = sum(a.get('hive_count', 0) for a in user_apiaries)

        # Температура
        temps = [n.get('temperature') for n in user_notes if n.get('temperature') is not None]
        avg_temp = sum(temps) / len(temps) if temps else 0

        # Типи робіт
        work_types = {}
        for note in user_notes:
            work_type = note.get('work_type', 'інше')
            work_types[work_type] = work_types.get(work_type, 0) + 1

        # Останні нотатки
        recent_notes = sorted(user_notes, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

        # Пасіки з найбільшою кількістю вуликів
        top_apiaries = sorted(user_apiaries, key=lambda x: x.get('hive_count', 0), reverse=True)[:3]

        return jsonify({
            'success': True,
            'statistics': {
                'apiaries_count': len(user_apiaries),
                'total_hives': total_hives,
                'journal_entries': len(user_notes),
                'avg_temperature': round(avg_temp, 1) if avg_temp else 'н/д',
                'work_types_distribution': work_types,
                'recent_notes': recent_notes,
                'top_apiaries': top_apiaries,
                'total_notes_last_month': len([n for n in user_notes
                                               if (datetime.now() - datetime.fromisoformat(
                        n.get('created_at', datetime.now().isoformat()))).days <= 30])
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


@app.route('/api/statistics/apiary/<apiary_id>', methods=['GET'])
def get_apiary_statistics(apiary_id):
    """Статистика для конкретної пасіки"""
    try:
        user_id = request.args.get('user_id')

        if not apiary_id or not user_id:
            return jsonify({'success': False, 'message': 'ID пасіки або користувача не вказано'})

        # Перевіряємо, чи пасіка належить користувачу
        apiaries = load_data(APIARIES_FILE)
        apiary = next((a for a in apiaries if a['id'] == apiary_id and a['user_id'] == user_id), None)

        if not apiary:
            return jsonify({'success': False, 'message': 'Пасіку не знайдено'})

        # Отримуємо нотатки для цієї пасіки
        notes = load_data(JOURNAL_FILE)
        apiary_notes = [n for n in notes if n.get('apiary_id') == apiary_id]

        # Розрахунок статистики
        total_notes = len(apiary_notes)

        # Температура
        temps = [n.get('temperature') for n in apiary_notes if n.get('temperature') is not None]
        avg_temp = sum(temps) / len(temps) if temps else 0

        # Типи робіт
        work_types = {}
        for note in apiary_notes:
            work_type = note.get('work_type', 'інше')
            work_types[work_type] = work_types.get(work_type, 0) + 1

        # Останні нотатки
        recent_notes = sorted(apiary_notes, key=lambda x: x.get('created_at', ''), reverse=True)[:5]

        # Загальна кількість задіяних вуликів
        total_hives_affected = sum(n.get('hives_affected', 0) for n in apiary_notes)

        return jsonify({
            'success': True,
            'statistics': {
                'apiary_name': apiary['name'],
                'total_notes': total_notes,
                'avg_temperature': round(avg_temp, 1) if avg_temp else 'н/д',
                'work_types_distribution': work_types,
                'recent_notes': recent_notes,
                'total_hives_affected': total_hives_affected,
                'hive_count': apiary.get('hive_count', 0),
                'notes_by_month': {},  # Можна додати розрахунок по місяцях
                'last_updated': apiary.get('updated_at', apiary.get('created_at'))
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Помилка: {str(e)}'})


# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    init_files()
    print("=" * 60)
    print("🚀 BeePlanner Backend запущено!")
    print("📱 API доступне за адресою:")
    print("   http://localhost:5000")
    print("   http://ВАШ_IP:5000")
    print("\n📊 Доступні ендпоінти:")
    print("   /api/health            - Перевірка сервера")
    print("   /api/test              - Тестовий endpoint")
    print("   /api/register          - Реєстрація")
    print("   /api/login             - Вхід")
    print("   /api/profile           - Профіль")
    print("   /api/update-profile    - Оновити профіль")
    print("   /api/apiaries          - Список пасік")
    print("   /api/apiary/<id>       - Отримати пасіку")
    print("   /api/add-apiary        - Додати пасіку")
    print("   /api/update-apiary     - Оновити пасіку")
    print("   /api/delete-apiary     - Видалити пасіку")
    print("   /api/journal-notes     - Журнал нотаток")
    print("   /api/journal-note/<id> - Отримати нотатку")
    print("   /api/add-journal-note  - Додати нотатку")
    print("   /api/update-journal-note - Оновити нотатку")
    print("   /api/delete-journal-note - Видалити нотатку")
    print("   /api/honey-plants      - Медоноси")
    print("   /api/bloom-calendar    - Календар цвітіння")
    print("   /api/notifications     - Сповіщення")
    print("   /api/weather/forecast  - Демо погода")
    print("   /api/weather/real      - Реальна погода")
    print("   /api/statistics/user   - Статистика користувача")
    print("   /api/statistics/apiary/<id> - Статистика пасіки")
    print("   /api/analyze-location  - Аналіз локації")
    print("   /api/cooperation/*     - Співпраця пасічник-фермер")
    print("=" * 60)
    print(f"🔑 API ключ OpenWeatherMap: 2d5269ffcc91aebf9cb1193ca0507537")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
