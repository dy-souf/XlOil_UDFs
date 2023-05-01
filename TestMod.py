import xloil as xlo
import pandas as pd
from xloil.pandas import PDFrame
import numpy as np
from itertools import groupby
from operator import itemgetter
from num2words import num2words


#UTILITY FUNCTIONS
#F1 : Digits to letters
@xlo.func
def chiffre_en_lettre(chiffre : float,langu ='fr') -> str:
    return num2words(chiffre,lang=langu)

def serialDateToDatetime(DateCol):
    epoch = pd.Timestamp('1899-12-30')
    return pd.to_datetime(DateCol, unit='D', origin=epoch)

#F2 : Transform a range to dataframe with given headins and specifiy date column
@xlo.func
def TO_DF_HEADINGS(data, name_of_date_col: str = None) -> xlo.Cache:
    df = pd.DataFrame(data[1:], columns=data[0])
    if name_of_date_col is not None:
        df[name_of_date_col] = serialDateToDatetime(df[name_of_date_col]
                                                    .astype(int))
    return df


class Interv:
    def __init__(self, start, end, serial=0, ol_score=0) -> None:
        self.start = start
        self.end = end
        self.serial = serial
        self.ol_score = ol_score

    def return_as_tuple(self):
        st = self.start, 's', self.serial
        ed = self.end, 'e', self.serial
        return [st, ed]

    def __str__(self) -> str:
        return f'Interval [{self.start},{self.end}], Id={self.serial}, overlap score = {self.ol_score}'

#F3 : find overlaps in different intervals based on a scoring system
@xlo.func
def IntOverlap(int_range) -> PDFrame:
    arr = []
    for row in int_range:
        arr.append(Interv(row[0], row[1]))

    # Joining the end points of all intervals in one list of tuples
    Ls = []
    i = 0
    for ir in arr:
        ir.serial = i
        Ls = Ls + ir.return_as_tuple()
        i += 1
    Ls = sorted(Ls)

    scounter, ecounter = 0, 0
    idx = []
    for itm in Ls:

        # Tracking is it's a start or an end of an interval
        if itm[1] == 's':
            scounter += 1
        else:
            ecounter += 1
        idx += [(itm[2], scounter - ecounter)]

    ol_index = [(x, sum(map(itemgetter(1), y))) for x, y in groupby(sorted(idx), itemgetter(0))]
    todf = []
    for ir in arr:
        ir.ol_score = ol_index[ir.serial][1]
        todf += [(ir.start, ir.end, ir.ol_score)]
    df = pd.DataFrame(todf, columns=['Start', 'End', 'Overlap_Score'])
    df.sort_values(by=['Start'], inplace=True)
    return df

# Sample function with argument help
@xlo.func(args={'arr': 'Array to be squared'},
          name='SQUARE',
          help='Returns the square of an array')
def square(arr):
    return arr * arr
