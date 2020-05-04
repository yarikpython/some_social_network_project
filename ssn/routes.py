from ssn import app, db
from ssn.models import User, Post, Comment, RequestToAddToFriends, Message
from flask_login import current_user, login_required, login_user, logout_user
from flask import redirect, render_template, flash, request, url_for
from ssn.forms import RegistrationForm, LoginForm, EditPostForm, EditProfileForm, EditCommentForm, \
    SearchForm, PostForm, CommentForm, MessageForm

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import func
from ssn.utils import save_profile_image, save_post_image
from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user_page', user_id=current_user.id))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_page', user_id=current_user.id))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created, now you can log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_page', user_id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            current_user.online = True
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect(url_for('index'))
        else:
            flash('Please check email or password', 'danger')
    return render_template('login.html', title='Log in ', form=form)


@app.route('/user_page/<user_id>')
@login_required
def user_page(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    profile_img = url_for('static', filename='profile_pics/' + user.profile_img)
    return render_template('user_page.html', title='User Page', user=user, posts=posts, profile_img=profile_img)


@app.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    form = EditProfileForm()
    user = User.query.get_or_404(user_id)
    profile_img = url_for('static', filename='profile_pics/' + user.profile_img)
    if current_user == user:
        if form.validate_on_submit():
            if form.profile_img.data:
                new_profile_img = save_profile_image(form.profile_img.data)
                user.profile_img = new_profile_img
            user.username = form.username.data
            user.status = form.status.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.date_of_birth = form.date_of_birth.data
            db.session.commit()
            return redirect(url_for('user_page', user_id=user.id))
        elif request.method == 'GET':
            form.username.data = user.username
            form.status.data = user.status
            form.email.data = user.email
            form.phone.data = user.phone
            form.date_of_birth.data = user.date_of_birth
    else:
        return redirect(url_for('user_page', user_id=current_user.id))
    return render_template('edit_profile.html', title='Edit Profile', form=form, user=user,
                           profile_img=profile_img)


@app.route('/users', methods=['GET', 'POST'])
def users():
    form = SearchForm()
    if form.validate_on_submit():
        users = User.query.filter(func.lower(User.username).contains(form.target.data.lower())).order_by(
            User.username).all()
    else:
        users = User.query.order_by(User.username).all()
    return render_template('users.html', title='People', form=form, users=users)


@app.route('/logout')
def logout():
    current_user.online = False
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if form.post_image.data:
            new_post_image = save_post_image(form.post_image.data)
            post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id, image=new_post_image)
        else:
            post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('user_page', user_id=current_user.id))
    return render_template('new_post.html', title='New Post', form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_time.desc()).all()
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        new_comment = Comment(body=comment_form.content.data, post_id=post.id, user_id=current_user.id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    return render_template('post.html', title='Post', post=post, comment_form=comment_form, comments=comments)


@app.route('/post/<post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('user_page', user_id=current_user.id))


@app.route('/post/<post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditPostForm()
    if current_user == post.author:
        if form.validate_on_submit():
            if form.post_image.data:
                new_post_image = save_post_image(form.post_image.data)
                post.image = new_post_image
                db.session.commit()
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            return redirect(url_for('post', post_id=post.id))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
    else:
        return redirect(url_for('user_page', user_id=current_user.id))
    return render_template('edit_post.html', form=form, title='Edit Post', post=post)


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    form = SearchForm()
    if form.validate_on_submit():
        posts = Post.query.filter(func.lower(Post.content).contains(form.target.data.lower())).order_by(
            Post.date_posted.desc()).all()
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('posts.html', title='Posts', posts=posts, form=form)


@app.route('/comment/<comment_id>/delete')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post', post_id=post_id))


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment_form = EditCommentForm()
    comment = Comment.query.get_or_404(comment_id)
    if current_user == comment.author:
        if comment_form.validate_on_submit():
            comment.body = comment_form.content.data
            db.session.commit()
            return redirect(url_for('post', post_id=comment.post_id))
        elif request.method == 'GET':
            comment_form.content.data = comment.body
    else:
        return redirect(url_for('user_page', user_id=current_user.id))
    return render_template('edit_comment.html', title='Edit Comment', comment_form=comment_form,
                           post=comment.post, user=comment.author)


@app.route('/followers/<user_id>', methods=['GET', 'POST'])
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    form = SearchForm()
    if form.validate_on_submit():
        followers = []
        for follower in user.followers:
            if form.target.data.lower() in follower.username.lower():
                followers.append(follower)
    else:
        followers = current_user.followers
    return render_template('followers.html', title='Followers', followers=followers, form=form)


@app.route('/followeds/<user_id>', methods=['GET', 'POST'])
@login_required
def followeds(user_id):
    user = User.query.get_or_404(user_id)
    form = SearchForm()
    if form.validate_on_submit():
        followeds = []
        for followed in user.followeds:
            if form.target.data.lower() in followed.username.lower():
                followeds.append(followed)
    else:
        followeds = current_user.followeds
    return render_template('followeds.html', title='Followeds', followeds=followeds, form=form)


@app.route('/unfollow/<user_id>')
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.get_or_404(user_id)
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    return redirect(url_for('followeds', user_id=current_user.id))


@app.route('/leave_to_followers/<user_id>')
@login_required
def leave_in_followers(user_id):
    user_to_add = User.query.get_or_404(user_id)
    if current_user.new_requests() == 1:
        current_user.last_look_at_requests_time = datetime.utcnow()
    req = RequestToAddToFriends.query.filter_by(sender_id=user_to_add.id, recipient_id=current_user.id).first()
    db.session.delete(req)
    db.session.commit()
    return redirect(url_for('friends', user_id=current_user.id))


@app.route('/remove_for_friends/<friend_id>')
@login_required
def remove_for_friends(friend_id):
    user_for_remove = User.query.get_or_404(friend_id)
    current_user.del_friend(user_for_remove)
    current_user.followers.append(user_for_remove)
    db.session.commit()
    return redirect(url_for('friends', user_id=current_user.id))


@app.route('/friends/<user_id>', methods=['GET', 'POST'])
@login_required
def friends(user_id):
    user = User.query.get_or_404(user_id)
    form = SearchForm()
    if current_user.new_requests():
        all_new_requests = RequestToAddToFriends.query.filter_by(recipient=current_user). \
            order_by(RequestToAddToFriends.date.desc()).limit(current_user.new_requests()).all()
        return render_template('friends.html', title='Friends', form=form, all_new_requests=all_new_requests)
    else:
        if form.validate_on_submit():
            friends = []
            for friend in user.friends:
                if form.target.data.lower() in friend.username.lower():
                    friends.append(friend)
        else:
            friends = current_user.friends
    return render_template('friends.html', title='Friends', form=form, friends=friends)


@app.route('/add_to_friends_req/<user_id>')
@login_required
def add_to_friends_req(user_id):
    user_for_add = User.query.get_or_404(user_id)
    if RequestToAddToFriends.query.filter_by(sender_id=current_user.id, recipient_id=user_for_add.id).first():
        flash('You Have Already Sent Friend Request', 'info')
        return redirect(url_for('user_page', user_id=user_for_add.id))
    else:
        new_requests = RequestToAddToFriends(sender_id=current_user.id, recipient_id=user_for_add.id)
        db.session.add(new_requests)
        current_user.follow(user_for_add)
        db.session.commit()
        flash('Your request has been sent', 'success')
        return redirect(url_for('user_page', user_id=user_for_add.id))


@app.route('/add_to_friends/<user_id>')
@login_required
def add_to_friends(user_id):
    user_to_add = User.query.get_or_404(user_id)
    if current_user.new_requests() == 1:
        current_user.last_look_at_requests_time = datetime.utcnow()
    req = RequestToAddToFriends.query.filter_by(sender_id=user_to_add.id, recipient_id=current_user.id).first()
    current_user.add_friend(user_to_add)
    db.session.delete(req)
    db.session.commit()
    return redirect(url_for('friends', user_id=current_user.id))


@app.route('/send_message/<recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    form = MessageForm()
    recipient = User.query.get_or_404(recipient_id)
    if form.validate_on_submit():
        new_message = Message(body=form.body.data, sender_id=current_user.id, recipient_id=recipient_id)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('user_page', user_id=recipient_id))
    return render_template('send_message.html', title='Send Message', form=form, recipient=recipient)


@app.route('/messages/<recipient_id>', methods=['GET', 'POST'])
@login_required
def messages(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    recipient.last_message_read_time = datetime.utcnow()
    db.session.commit()
    form = SearchForm()
    if form.validate_on_submit():
        my_messages = Message.query.filter_by(recipient_id=recipient_id).filter(
            func.lower(Message.body).contains(form.target.data.lower())).order_by(Message.date.desc()).all()
    else:
        my_messages = Message.query.filter_by(recipient_id=recipient_id).order_by(Message.date.desc()).all()
    return render_template('my_messages.html', my_messages=my_messages, title='My Messages (In)', form=form)


@app.route('/messages/<sender_id>/out', methods=['GET', 'POST'])
@login_required
def messages_out(sender_id):
    sender = User.query.get_or_404(sender_id)
    form = SearchForm()
    if form.validate_on_submit():
        my_messages = Message.query.filter_by(sender_id=sender_id).filter(
            func.lower(Message.body).contains(form.target.data.lower())).order_by(Message.date.desc()).all()
    else:
        my_messages = Message.query.filter_by(sender_id=sender_id).order_by(Message.date.desc()).all()
    return render_template('my_messages_out.html', my_messages=my_messages, title='My Messages (Out)',
                           form=form)


@app.route('/messages/<message_id>/delete')
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('messages', recipient_id=current_user.id))
