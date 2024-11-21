import psycopg2
from typing import Optional, Any


class CountryPostgreClient:
    def __init__(self, ps_connect: Optional[str]) -> None:
        """
        Initialize the CountryPostgreClient with a PostgreSQL connection string.

        Args:
        - ps_connect: A string representing the PostgreSQL connection string.
        """

        if ps_connect is None:
            raise ValueError("ps_connect cannot be None")
        self.ps_conn = ps_connect

    def filter_region(self, region: Optional[str]) -> Any:
        """
        Retrieve country information based on the specified region.

        Args:
        - region: An optional string representing the region to filter by.

        Returns:
        - A list of country information matching the specified region, or all countries if no region is provided.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()
            if region:
                cur.execute(
                    "SELECT name, alpha2, alpha3, region FROM countries WHERE region IN %s ORDER BY alpha2",
                    (tuple(region),),
                )
            else:
                cur.execute(
                    "SELECT name, alpha2, alpha3, region FROM countries ORDER BY alpha2"
                )
        return cur.fetchall()

    def get_country_by_alpha(self, alpha2: str) -> Any:
        """
        Retrieve country information based on the specified alpha2 code.

        Args:
        - alpha2: A string representing the alpha2 code of the country.

        Returns:
        - Country information matching the specified alpha2 code.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name, alpha2, alpha3, region FROM countries WHERE alpha2 = %s",
                (alpha2,),
            )
            return cur.fetchone()
