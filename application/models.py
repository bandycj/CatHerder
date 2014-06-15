from flask.ext.login import make_secure_token, UserMixin, AnonymousUserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import ClauseElement

from application import application


db = SQLAlchemy(application)
save = lambda: db.session.commit()
add = lambda object: db.session.add(object)
rollback = lambda: db.session.rollback()


class CatherderMixin(object):
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        instance = db.session.query(cls).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = cls(**params)
            add(instance)
            return instance, True

    def __repr__(self):
        attrs = []
        for key in self.__dict__:
            if not key.startswith('_'):
                attrs.append((key, getattr(self, key)))
        return self.__class__.__name__ + '(' + ', '.join(x[0] + '=' + repr(x[1]) for x in attrs) + ')'


class User(db.Model, CatherderMixin, UserMixin):
    __tablename__ = 'user'
    name = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    user_level_id = Column(Integer, ForeignKey('userlevel.id'), nullable=False, default=-1)
    auth_token = Column(String(256), nullable=False)
    placeranks = relationship('PlaceRank', backref='user', lazy='dynamic')
    oauth_identities = relationship('OAuthIdentity', backref='user', lazy='dynamic')

    def add_oauth_identity(self, service_name, service_id):
        try:
            oauth_id, created = OAuthIdentity.get_or_create(name=service_name, service_id=service_id, user_id=self.id)
            self.auth_token = make_secure_token(service_name, service_id, key="deterministic")
            save()
            return oauth_id, created
        except Exception as e:
            print e.message
            rollback()

    def get_auth_token(self):
        return self.auth_token


    @classmethod
    def add_user(cls, name, email, oauth_service_name, oauth_service_id):
        try:
            user, created = User.get_or_create(name=name, email=email)
            if created:
                user.user_level = default_user_level()
                user.auth_token = make_secure_token(args=[oauth_service_name, oauth_service_id], key="deterministic")
                save()
            oauth_id, created = OAuthIdentity.get_or_create(
                name=oauth_service_name,
                service_id=oauth_service_id,
                user_id=user.id)
            if created:
                save()
            return user, created
        except Exception as e:
            print e.message
            rollback()


class OAuthIdentity(db.Model, CatherderMixin):
    __tablename__ = 'oauthidentity'
    name = Column(String(64), nullable=False)
    service_id = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    __table_args__ = (
        UniqueConstraint('name', 'service_id', name='_service_id_uc'), {}
    )

    @classmethod
    def get_user(cls, oauth_service_name=None, oauth_service_id=None):
        if oauth_service_name is not None and oauth_service_id is not None:
            id = OAuthIdentity.query.filter_by(name=oauth_service_name, service_id=oauth_service_id).first()
            if id:
                return id.user


class UserLevel(db.Model, CatherderMixin):
    __tablename__ = 'userlevel'
    name = Column(String(16), unique=True, nullable=False)
    users = relationship('User', backref='user_level', lazy='dynamic')


class PlaceType(db.Model, CatherderMixin):
    __tablename__ = 'placetype'
    name = Column(String(32), unique=True, nullable=False)
    places = relationship('Place', backref='placetype', lazy='dynamic')


class Rank(db.Model, CatherderMixin):
    __tablename__ = 'rank'
    name = Column(String(16), unique=True, nullable=False)
    placeranks = relationship('PlaceRank', backref='rank', lazy='dynamic')


class Place(db.Model, CatherderMixin):
    __tablename__ = 'place'
    name = Column(String(32), nullable=False)
    address = Column(String(128), unique=True, nullable=False)
    placetype_id = Column(Integer, ForeignKey('placetype.id'), nullable=False)
    placeranks = relationship('PlaceRank', backref='place', lazy='dynamic')


class PlaceRank(db.Model, CatherderMixin):
    __tablename__ = 'placerank'
    place_id = Column(Integer, ForeignKey('place.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    rank_id = Column(Integer, ForeignKey('rank.id'), nullable=False)


class AnonymousUser(AnonymousUserMixin):
    """AnonymousUser definition"""


db.create_all()
for name in application.config['USER_LEVELS']:
    UserLevel.get_or_create(name=name)
save()
default_user_level = lambda: UserLevel.query.filter_by(name=application.config['DEFAULT_USER_LEVEL']).first()