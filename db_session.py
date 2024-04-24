import sqlite3


class dbsession:
    def __init__(self, db):
        self.db = db
        self.cur = db.cursor()

    def add_user(self, Nickname, email, hpassword):
        try:
            self.cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.cur.fetchone()
            if res['count'] > 0:
                print('Такой email уже зарегистрирован')
                return False

            self.cur.execute('INSERT INTO users VALUES(NULL, ?, ?, ?, NULL)',
                             (Nickname, email, hpassword))
            self.db.commit()

        except sqlite3.Error as e:
            print('Ошибка добавления в БД: ' + str(e))
            return False

        return True

    def add_post(self, user_id, username, content):
        try:
            self.cur.execute('INSERT INTO posts (user_id, username, content) VALUES (?, ?, ?)',
                             (user_id, username, content))
            self.db.commit()

        except sqlite3.Error as e:
            print('Ошибка добавления в БД: ' + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.cur.execute(f'SELECT * FROM users WHERE id = {user_id}')
            res = self.cur.fetchall()
            if not res:
                print('Пользователь не найден')
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка БД' + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка БД" + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.cur.execute("UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.db.commit()

        except sqlite3.Error as e:
            print("Ошибка аватара в БД " + str(e))
            return False

        return True

    def get_posts(self, user_id=0):
        try:
            if not user_id:
                self.cur.execute(f"SELECT * FROM posts ORDER BY created_at DESC")
                res = self.cur.fetchall()
            else:
                self.cur.execute(f"SELECT * FROM posts WHERE user_id = {user_id}")
                res = self.cur.fetchall()
            if not res:
                return ''

            return res
        except sqlite3.Error as e:
            print("Ошибка БД" + str(e))

    def delete_post(self, post_id):
        try:
            self.cur.execute(f'DELETE FROM posts WHERE id = {post_id}')
            self.db.commit()
        except sqlite3.Error as e:
            print("Ошибка БД" + str(e))

    def change_profile(self, user_id, name, status, city, about):
        try:
            self.cur.execute(f"UPDATE users SET name = '{name}', status = '{status}', "
                             f"city = '{city}', about = '{about}' WHERE user_id = {user_id}")
        except sqlite3.Error as e:
            print("Ошибка БД" + str(e))

        return False

    def delete_profile(self, user_id):
        try:
            self.cur.execute(f'DELETE FROM users WHERE id = {user_id}')
            self.cur.execute(f'DELETE FROM posts WHERE user_id = {user_id}')
            self.db.commit()
        except sqlite3.Error as e:
            print("Ошибка БД" + str(e))

