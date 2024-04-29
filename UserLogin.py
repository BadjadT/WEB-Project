from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.user = db.getUser(user_id)
        return self

    def create(self, user):
        self.user = user
        return self

    def get_id(self):
        return str(self.user['id'])

    def getName(self):
        if self.user:
            return self.user['name']
        else:
            return False

    def getMail(self):
        if self.user:
            return self.user['email']
        else:
            return False

    def getAvatar(self, app):
        img = None
        if not self.user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.png'), 'rb') as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Avatar not found: " + str(e))

        else:
            img = self.user['avatar']

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == "png" or ext == "PNG":
            return True
        return False
