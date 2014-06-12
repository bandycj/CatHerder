from flask.ext.login import make_secure_token, UserMixin, AnonymousUserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from application import application


db = SQLAlchemy(application)
save = lambda: db.session.commit()
add = lambda object: db.session.add(object)
rollback = lambda: db.session.rollback()

login_serializer = URLSafeTimedSerializer(application.secret_key)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_name = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    user_level_id = Column(Integer, ForeignKey('userlevel.id'), nullable=False, default=-1)
    auth_token = Column(String(256), unique=True, nullable=False)
    placeranks = relationship('PlaceRank', backref='user', lazy='dynamic')
    oauth_identities = relationship('OAuthIdentity', backref='user', lazy='dynamic')

    def add_oauth_identity(self, service_name, service_id):
        try:
            oauth_identity = OAuthIdentity(
                service_name=service_name,
                service_id=service_id,
                user_id=self.id
            )
            add(oauth_identity)

            self.auth_token = make_secure_token(service_name, service_id, key="deterministic")
            save()
        except:
            rollback()

    def get_auth_token(self):
        return self.auth_token

    @classmethod
    def get_user(cls, email=None, user_id=None, auth_token=None, oauth_service_name=None, oauth_service_id=None):
        if email is not None:
            return User.query.filter_by(email=email).first()
        elif user_id is not None:
            return User.query.get(user_id)
        elif auth_token is not None:
            return User.query.filter_by(auth_token=auth_token).first()
        elif oauth_service_name is not None and oauth_service_id is not None:
            return OAuthIdentity.query.filter_by(service_name=oauth_service_name,
                                                 service_id=oauth_service_id).first().user

    @classmethod
    def add_user(cls, user_name, email, oauth_service_name, oauth_service_id):
        user = User()
        try:
            user.user_name = user_name
            user.email = email
            user.user_level = default_user_level()
            user.auth_token = make_secure_token(args=[oauth_service_name, oauth_service_id], key="deterministic")
            add(user)
            save()
        except:
            rollback()
        user.add_oauth_identity(service_name=oauth_service_name, service_id=oauth_service_id)
        return user

    def __repr__(self):
        return '<User %r>' % (self.user_name)


class OAuthIdentity(db.Model):
    __tablename__ = 'oauthidentity'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    service_name = Column(String(64), nullable=False)
    service_id = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('service_name', 'service_id', name='_service_id_uc'), {}
    )

    @classmethod
    def get_user(cls, oauth_service_name=None, oauth_service_id=None):
        if oauth_service_name is not None and oauth_service_id is not None:
            id = OAuthIdentity.query.filter_by(service_name=oauth_service_name, service_id=oauth_service_id).first()
            if id: return id.user

    def __repr__(self):
        return '<OAuthIdentity %r: user_id=%r>' % (self.service_name, self.user_id)


class UserLevel(db.Model):
    __tablename__ = 'userlevel'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    level_name = Column(String(16), unique=True, nullable=False)
    users = relationship('User', backref='user_level', lazy='dynamic')

    def __repr__(self):
        return '<UserLevel %r>' % (self.level_name)


class PlaceType(db.Model):
    __tablename__ = 'placetype'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type_name = Column(String(32), unique=True, nullable=False)
    places = relationship('Place', backref='placetype', lazy='dynamic')

    def __repr__(self):
        return '<PlaceType %r>' % (self.type_name)


class Rank(db.Model):
    __tablename__ = 'rank'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    rank = Column(String(16), unique=True, nullable=False)
    placeranks = relationship('PlaceRank', backref='rank', lazy='dynamic')

    def __repr__(self):
        return '<Rank %r>' % (self.rank)


class Place(db.Model):
    __tablename__ = 'place'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(32), nullable=False)
    address = Column(String(128), unique=True, nullable=False)
    placetype_id = Column(Integer, ForeignKey('placetype.id'), nullable=False)
    placeranks = relationship('PlaceRank', backref='place', lazy='dynamic')

    def __repr__(self):
        return '<Place %r>' % (self.name)


class PlaceRank(db.Model):
    __tablename__ = 'placerank'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    place_id = Column(Integer, ForeignKey('place.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    rank_id = Column(Integer, ForeignKey('rank.id'), nullable=False)

    def __repr__(self):
        return '<PlaceRank %r: %r=%r>' % (self.user_id, self.place_id, self.rank_id)


class AnonymousUser(AnonymousUserMixin):
    """AnonymousUser definition"""


db.create_all()
for level_name in application.config['USER_LEVELS']:
    if UserLevel.query.filter_by(level_name=level_name).first() is None:
        add(UserLevel(level_name=level_name))
        save()
default_user_level = lambda: UserLevel.query.filter_by(level_name=application.config['DEFAULT_USER_LEVEL']).first()