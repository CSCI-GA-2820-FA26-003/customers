"""
Models for Customer

All of the models are stored in this module
"""

import logging
import re
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

US_STATE_CODES = frozenset(
    {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC", "AS", "GU", "MP", "PR", "VI", "FM", "MH", "PW",
    }
)  # fmt: skip

# US ZIP code: 12345 or 12345-6789
POSTAL_CODE_PATTERN = re.compile(r"[0-9]{5}(-[0-9]{4})?")


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a customer
    """

    ##################################################
    # Table Schema
    ##################################################

    __tablename__ = "customers"
    __table_args__ = (
        db.CheckConstraint(r"name ~ '\S'", name="customers_name_not_blank"),
        db.CheckConstraint(r"street ~ '\S'", name="customers_street_not_blank"),
        db.CheckConstraint(r"city ~ '\S'", name="customers_city_not_blank"),
        db.CheckConstraint(r"state ~ '\S'", name="customers_state_not_blank"),
        db.CheckConstraint(
            r"postal_code ~ '\S'", name="customers_postal_code_not_blank"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(63), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Customer name={self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        try:
            logger.info("Creating %s", self.name)
            self.id = None  # pylint: disable=invalid-name
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Customer to the database
        """
        try:
            logger.info("Saving %s", self.name)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        try:
            logger.info("Deleting %s", self.name)
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            name = data["name"]
            street = data["street"]
            city = data["city"]
            state = data["state"]
            postal_code = data["postal_code"]
        # This error will be raised when accessing method that doesn't exist on that object.
        # except AttributeError as error:
        #     raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Customer: body of request contained bad or no data "
                + str(error)
            ) from error

        # Validate everything before assigning so a failed update leaves the record untouched
        for field, value in (
            ("name", name),
            ("street", street),
            ("city", city),
            ("state", state),
            ("postal_code", postal_code),
        ):
            if not isinstance(value, str) or not value.strip():
                raise DataValidationError(
                    f"Invalid Customer: {field} must be a non-blank string"
                )
        state = state.upper()
        if state not in US_STATE_CODES:
            raise DataValidationError(f"Invalid Customer: invalid state code {state}")
        if not POSTAL_CODE_PATTERN.fullmatch(postal_code):
            raise DataValidationError(
                f"Invalid Customer: invalid postal_code {postal_code}"
            )

        self.name = name
        self.street = street
        self.city = city
        self.state = state
        self.postal_code = postal_code
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customer in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
