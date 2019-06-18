from marshmallow import (
    Schema,
    fields,
    validate,
    validates_schema,
    ValidationError
)


class SignupSchema(Schema):
    email = fields.Email(
        required=True, 
        validate=validate.Length(min=3, max=320)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(
            min=8, error='Password must be atleast 8 characters long'
        )
    )
    confirm = fields.Str(required=True)
    fullname = fields.Str(
        validate=validate.Length(
            max=100, 
            error='Enter a fullname that is less than 100 characters long'
        ),
    )

    @validates_schema
    def validate_password(self, data, **kwargs):
        print(data['password'], data['confirm'])
        if data['password'] != data['confirm']:
            raise ValidationError(
                'Re-enter your password confirmation so it matches your password'
            )


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        validate=validate.Length(min=3, max=320)
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(
            min=8, error='Password must be atleast 8 characters long'
        )
    )