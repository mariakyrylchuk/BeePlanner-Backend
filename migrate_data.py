# backend/migrate_data.py
import json
import uuid


def migrate_users():
    users = json.load(open('users.json', 'r', encoding='utf-8'))

    # Додаємо ID для кожного користувача
    for user in users:
        if 'id' not in user:
            user['id'] = str(uuid.uuid4())

    json.dump(users, open('users.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'Мігровано {len(users)} користувачів')


def migrate_apiaries():
    apiaries = json.load(open('apiaries.json', 'r', encoding='utf-8'))

    for apiary in apiaries:
        if 'user_id' not in apiary and 'email' in apiary:
            # Знаходимо user_id за email
            users = json.load(open('users.json', 'r', encoding='utf-8'))
            for user in users:
                if user['email'] == apiary['email']:
                    apiary['user_id'] = user['id']
                    break

    json.dump(apiaries, open('apiaries.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'Мігровано {len(apiaries)} пасік')


if __name__ == '__main__':
    migrate_users()
    migrate_apiaries()
