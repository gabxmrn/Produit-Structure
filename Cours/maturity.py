from datetime import datetime

class Maturity:
    def __init__(
            self, 
            maturity_in_years:float=None,
            begin_date:datetime=None,
            end_date:datetime=None,
            day_count_convention:str = "ACT/360"
            ) -> None:
        
        self.__day_count_convention= day_count_convention
        if maturity_in_years != None:
            self.__maturity_in_years = maturity_in_years
        else :
            self.__maturity_in_years = (end_date - begin_date).days/self._denom()


    def _denom(self):
        if self.__day_count_convention == "ACT/360":
            return 360.0
        elif self.__day_count_convention == "ACT/365":
            return 365.0
        raise Exception("day_count_convention " + self.__day_count_convention + " error")
    

    def maturity(self):
        return self.__maturity_in_years