from datetime import datetime
from flask_login import UserMixin
from ssn import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


followers = db.Table('followers', db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

friends = db.Table('friends', db.Column('friend_l', db.Integer, db.ForeignKey('user.id')),
                   db.Column('friend_r', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_of_reg = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    phone = db.Column(db.String(15), nullable=False, default='None')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    online = db.Column(db.Boolean, nullable=False, default=False)
    date_of_birth = db.Column(db.DateTime)
    status = db.Column(db.String)
    profile_img = db.Column(db.String, nullable=False, default='default.jpg')
    messages_in = db.relationship('Message', backref='recipient', foreign_keys='Message.recipient_id', lazy='dynamic')
    messages_out = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    requests_in = db.relationship('RequestToAddToFriends', backref='recipient',
                                  foreign_keys='RequestToAddToFriends.recipient_id', lazy='dynamic')
    requests_out = db.relationship('RequestToAddToFriends', backref='sender',
                                   foreign_keys='RequestToAddToFriends.sender_id', lazy='dynamic')
    last_look_at_requests_time = db.Column(db.DateTime)
    followeds = db.relationship('User', secondary=followers, primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    friends = db.relationship('User', secondary=friends, primaryjoin=(friends.c.friend_l == id),
                              secondaryjoin=(friends.c.friend_r == id), lazy='dynamic')

    def is_friend(self, user):
        return user in self.friends

    def add_friend(self, user):
        if not self.is_friend(user):
            self.friends.append(user)
            user.friends.append(self)
            if user.is_following(self):
                user.followeds.remove(self)

    def del_friend(self, user):
        if self.is_friend(user):
            self.friends.remove(user)
            user.del_friend(self)

    def is_following(self, user):
        return self.followeds.filter(followers.c.followed_id == user.id).count()

    def follow(self, user):
        if not self.is_following(user) or not self.is_friend(user):
            self.followeds.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followeds.remove(user)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.date > last_read_time).count()

    def new_requests(self):
        last_look_time = self.last_look_at_requests_time or datetime(1900, 1, 1)
        return RequestToAddToFriends.query.filter_by(recipient=self). \
            filter(RequestToAddToFriends.date > last_look_time).count()

    def __repr__(self):
        return f'User - {self.username} email - {self.email}'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    image = db.Column(db.String, nullable=False, default=None)

    def __repr__(self):
        return f'Post - {self.id} author {self.author.username}'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class RequestToAddToFriends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Request from {self.sender.username} to {self.recipient.username}, {self.date.strftime("%d.%m.%Y %H:%M:%S")}!'
