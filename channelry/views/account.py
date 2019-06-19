import datetime

import bcrypt
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    redirect,
    render_template,
    url_for
)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    jwt_refresh_token_required
)
from marshmallow import ValidationError

from libs import mailgun, token, dashboard
from channelry.models import db
from channelry.models.account import User
from channelry.schemas.account import SignupSchema, LoginSchema


account_bp = Blueprint('account', __name__)


def jsonify_validation_error(validation_error: ValidationError):
    """Convert validation error messages to be parsable in the Dashboard.

    :param validation_error: ValidationError raised by marshmallow
    """
    message = {}
    for field, reason in validation_error.messages.items():
        message = {'field': field, 'reason': reason[0]}
    return message


@account_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return dashboard.go('signup')

    try:
        schema = SignupSchema(strict=True)
        email = request.json.get('email')
        name = request.json.get('name')
        password = request.json.get('password')
        confirm = request.json.get('confirm')
        data, _ = schema.load({
            'email': email,
            'name': name,
            'password': password,
            'confirm': confirm
        })

        user = User(email, password, name)
        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            return jsonify(field='email', reason='Email is already taken'), 400
        else:
            db.session.add(user)
            db.session.commit()

            confirmation_token = token.generate_confirmation_token(email)
            uri = f'email/confirm?confirmation_token={confirmation_token}'
            confirmation_url = f'{dashboard.url()}/{uri}'
            html = render_template(
                'account/email/confirm_email.html',
                confirmation_url=confirmation_url
            )
            mailgun.send_email(
                'Confirm your Channelry email address!',
                [f'{name} {email}'],
                html=html,
            )

        return jsonify(email=email)

    except ValidationError as validation_error:
        return jsonify(jsonify_validation_error(validation_error)), 400


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return dashboard.go('login')

    try:
        schema = LoginSchema(strict=True)
        email = request.json.get('email')
        password = request.json.get('password')
        data, _ = schema.load({
            'email': email,
            'password': password
        })

        user = User.query.filter_by(email=email).first()
        if user and user.password_match(password):
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            return jsonify({
                'iss': 'channelry',
                'sub': user.email,
                'aud': ['all'],
                'accessToken': access_token,
                'refreshToken': refresh_token
            })
        else:
            return jsonify(message='Email or password is incorrect'), 400

    except ValidationError as validation_error:
        return jsonify(jsonify_validation_error(validation_error)), 400


@account_bp.route('/email/confirm', methods=['POST'])
def confirm_email():
    try:
        confirmation_token = request.json.get('confirmation_token')
        current_app.logger.debug(f'Confirmation token: {confirmation_token}')
        email = token.confirm_conformation_token(confirmation_token)
    except:
        current_app.logger.debug('Invalid confirmatiok token')
        return jsonify(message='Confirmation link is invalid or expired')

    current_app.logger.debug(f'Decrypted email: {email}')
    user = User.query.filter_by(email=email).first()

    if not user or user.is_confirmed:
        current_app.logger.debug('User does not exist or already confirmed')
        return jsonify(message='Confirmation link is invalid or expired')
    else:
        current_app.logger.debug(f'Confirmed email: {email}')
        user.is_confirmed = True
        db.session.add(user)
        db.session.commit()
        return jsonify(email=email)


@account_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    email = get_jwt_identity()
    return jsonify(accessToken=create_access_token(identity=email))


@account_bp.route('/details', methods=['POST'])
@jwt_required
def details():
    email = get_jwt_identity()
    current_app.logger.debug(f'Identity: {email}')
    user = User.query.filter_by(email=get_jwt_identity()).first()
    return jsonify(email=user.email, name=user.name)
