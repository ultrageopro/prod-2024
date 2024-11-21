from flask import Blueprint, jsonify, Response, request
import psycopg2
from typing import Any, Optional


class CountryRoute:
    def __init__(self, country_database: Any) -> None:
        """
        Initialize the CountryRoute with the given country_database.

        Args:
            country_database (Any): The country database object.
        """

        self.country_database = country_database

        self.blueprint = Blueprint("countries", __name__)

        # First Part Server Routes
        @self.blueprint.route("/api/countries", methods=["GET"])
        def countries() -> tuple[Response, int]:
            """
            Retrieve a list of countries based on the filter_region query parameter.

            Returns:
                tuple[Response, int]: The countries data and HTTP status code.
            """

            filter_region = request.args.getlist("region")
            return self.__get_countries(filter_region)

        # Second Part Server Routes
        @self.blueprint.route("/api/countries/<alpha2>", methods=["GET"])
        def country(alpha2: str) -> tuple[Response, int]:
            """
            Retrieve a specific country based on the alpha2 code.

            Args:
                alpha2 (str): The alpha2 code of the country.

            Returns:
                tuple[Response, int]: The country data and HTTP status code.
            """

            return self.__get_country(alpha2)

    # First Part
    def __get_countries(self, filter_region: Optional[list]) -> tuple[Response, int]:
        """
        Retrieve a list of countries from the database based on the filter_region.

        Args:
            filter_region (Optional[list]): The optional list of regions to filter the countries.

        Returns:
            tuple[Response, int]: The countries data and HTTP status code.
        """

        country_data = self.__fetch_countries_from_db(filter_region)
        if country_data is None:
            return jsonify({"reason": "Bad data"}), 400

        countries = [
            {
                "name": row[0],
                "alpha2": row[1],
                "alpha3": row[2],
                "region": row[3],
            }
            for row in country_data
        ]

        return jsonify(countries), 200

    def __fetch_countries_from_db(self, filter_region: Optional[list]) -> Any:
        """
        Fetch countries from the database based on the filter_region.

        Args:
            filter_region (Optional[list]): The optional list of regions to filter the countries.

        Returns:
            Any: The fetched country data.
        """

        if filter_region is None:
            return self.country_database.filter_region(filter_region)

        regions = [i[-1] for i in self.country_database.filter_region(filter_region)]
        if len(filter_region) != len(set(regions)):
            return None

        return self.country_database.filter_region(filter_region)

    # Second Part
    def __get_country(self, alpha2: str) -> tuple[Response, int]:
        """
        Retrieve a specific country from the database based on the alpha2 code.

        Args:
            alpha2 (str): The alpha2 code of the country.

        Returns:
            tuple[Response, int]: The country data and HTTP status code.
        """

        row = self.country_database.get_country_by_alpha(alpha2)

        if not row:
            return jsonify({"reason": "Country not found"}), 404

        country = {"name": row[0], "alpha2": row[1], "alpha3": row[2], "region": row[3]}
        return jsonify(country), 200
