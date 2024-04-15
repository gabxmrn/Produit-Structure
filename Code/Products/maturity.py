from datetime import datetime

class Maturity:
    """
    A class representing the maturity of a financial instrument.

    Attributes:
        __day_count_convention (str): The day count convention used for calculating maturity.
        __maturity_in_years (float): The maturity value in years.
    """

    def __init__(
            self,
            maturity_in_years: float = None,
            begin_date: datetime = None,
            end_date: datetime = None,
            day_count_convention: str = "ACT/360",
            ) -> None:
        """
        Initialize a Maturity object.

        Inputs:
            maturity_in_years (float, optional): The maturity value in years. Defaults to None.
            begin_date (datetime, optional): The start date. Defaults to None.
            end_date (datetime, optional): The end date. Defaults to None.
            day_count_convention (str, optional): The day count convention. Defaults to "ACT/360".
        """
        
        self.__day_count_convention = day_count_convention
        self.end_date = end_date

        if maturity_in_years is not None:
            self.__maturity_in_years = maturity_in_years
        elif begin_date is not None and end_date is not None:
            self.__maturity_in_years = (end_date - begin_date).days / self._denom()
        else:
            raise ValueError("Either maturity_in_years or both begin_date and end_date must be provided")
    

    def _denom(self) -> float:
        """
        Determine the denominator value based on the day count convention.

        Returns:
            float: The denominator value determined by the day count convention.

        Raises:
            Exception: If the day count convention is not recognized.
        """
        
        if self.__day_count_convention == "ACT/360":
            return 360.0
        elif self.__day_count_convention == "ACT/365":
            return 365.0
        raise Exception("day_count_convention " + self.__day_count_convention + " error")
    
    
    def maturity(self) -> float:
        """
        Retrieve the maturity value in years.

        Returns:
            float: The maturity value in years.
        """

        return self.__maturity_in_years
    
    def get_new_maturity(self, new_begin_date:datetime=None, new_maturity_in_years:float=None) :
        if new_begin_date is None and not new_maturity_in_years is None :
            return Maturity(maturity_in_years=new_maturity_in_years, day_count_convention=self.__day_count_convention)
        elif not new_begin_date is None and not self.end_date is None :
            return Maturity(begin_date=new_begin_date, end_date=self.end_date, day_count_convention=self.__day_count_convention)
        else :
            raise ValueError("Either maturity_in_years or both begin_date and end_date must be provided")
