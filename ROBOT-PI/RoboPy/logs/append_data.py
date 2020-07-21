#!/usr/bin/python3
import plotly.express as px
import sys
import pandas
import numpy
import argparse

parser = argparse.ArgumentParser()
# parser.add_argument(
#     '-f', '--file',
#     dest='csv_files',
#     type=str, nargs='+',
#     action='store',
#     required=True,
#     const=None, default=None,
#     help='Path to one or more csv files.'
# )
parser.add_argument(
    "csv_files",
    type=str, nargs='+',
    action='store',
    const=None, default=None,
    help='Path to one or more csv files.'
)
parser.add_argument("-u", "--unfiltered", help="Save a raw version of the dataframe to a CSV file.", action="store_true")
parser.add_argument("-s", "--simple", help="Save a simply filtered version of the dataframe to a CSV file.", action="store_true")
parser.add_argument("-med", "--median", help="Save a median filtered version of the dataframe to a CSV file.", action="store_true")
parser.add_argument("-mea", "--mean", help="Save a mean filtered version of the dataframe to a CSV file.", action="store_true")
parser.add_argument("-mix", "--mixed", help="Save a mixed median-mean filtered version of the dataframe to a CSV file.", action="store_true")
parser.add_argument("-v", "--verbose", help="Print verbose information and show scatered plot of the data.", action="store_true")

class Filter(object):
    def __init__(self, maxsize, filtering_function):
        self.values = []
        self.maxsize = maxsize
        self.filtering_function = filtering_function

    def add_value(self, value):
        if(len(self.values) == self.maxsize):
            self.values.pop(0)
        self.values.append(value)

    def get_value(self):
        if(len(self.values) == self.maxsize):
            return self.filtering_function(self.values)
        else:
            return self.values[-1]
        
def id_function(l):
    return l[-1]

def simple_filtering(df, maxRight, maxLeft, maxFront):
    df = df[df.pwm >= 0.0]
    df = df[((df.frontSensor < 40.0) | (df.pwm != 0.0))]
    df = df[df.leftSensor < maxLeft]
    df = df[df.rightSensor < maxRight]
    df = df[df.frontSensor < maxFront]
    return df

def filter_data(df, column_names, windowSize, filteringFunction, filterPwm=False):    
    frontFilter = Filter(windowSize, filteringFunction)
    rightFilter = Filter(windowSize, filteringFunction)
    leftFilter = Filter(windowSize, filteringFunction)
    if(filterPwm):
        pwmFilter = Filter(windowSize, filteringFunction)
    
    df = simple_filtering(df, 200.0, 200.0, 300.0)
    filteredDf = pandas.DataFrame(columns = column_names)

    
    for index, row in df.iterrows():
        frontFilter.add_value(row['frontSensor'])
        rightFilter.add_value(row['rightSensor'])
        leftFilter.add_value(row['leftSensor'])
        
        # newRow = {}
        # for key in column_names:
        #     newRow[key] = row[key]

        if(filterPwm):
            pwmFilter.add_value(row['pwm'])
            filteredDf = filteredDf.append({
                'gamepadLx':row['gamepadLx'], 'gamepadLy':row['gamepadLy'],
                'frontSensor': frontFilter.get_value(),
                'rightSensor': rightFilter.get_value(),
                'leftSensor': leftFilter.get_value(),
                'pwm': pwmFilter.get_value(),'pwmLeft': row['pwmLeft'],'pwmRight': row['pwmRight'],
                'steerLeft': row['steerLeft'], 'steerRight': row['steerRight'],
                'ticksRight':row['ticksRight'] ,'ticksLeft':row['ticksLeft']
            }, ignore_index=True)

        else:
            filteredDf = filteredDf.append({
                'gamepadLx':row['gamepadLx'], 'gamepadLy':row['gamepadLy'],
                'frontSensor': frontFilter.get_value(),
                'rightSensor': rightFilter.get_value(),
                'leftSensor': leftFilter.get_value(),
                'pwm': row['pwm'],'pwmLeft': row['pwmLeft'],'pwmRight': row['pwmRight'],
                'steerLeft': row['steerLeft'], 'steerRight': row['steerRight'],
                'ticksRight':row['ticksRight'] ,'ticksLeft':row['ticksLeft']
                }, ignore_index=True)

    return filteredDf

def append_data(csvList, column_names):
    ret = {}

    if(args.unfiltered):
        ret['unfiltered'] = pandas.DataFrame(columns = column_names)
        
    if(args.simple):
        ret['simple'] = pandas.DataFrame(columns = column_names)
    
    if(args.median):
        ret['median'] = pandas.DataFrame(columns = column_names)

    if(args.mean):
        ret['mean'] = pandas.DataFrame(columns = column_names)
    
    if(args.mixed):
        ret['mixed'] = pandas.DataFrame(columns = column_names)
        
    for csvFile in csvList:
        if(args.unfiltered):
            auxDf = pandas.read_csv(csvFile)
            if(args.verbose):
                print(auxDf.head())

            ret['unfiltered'] = ret['unfiltered'].append(auxDf, ignore_index = True)
            
        if(args.simple):
            auxSimpleDf = simple_filtering(pandas.read_csv(csvFile), 150.0, 150.0, 240.0) 
            if(args.verbose):
                print(auxSimpleDf.head())
            
            ret['simple'] = ret['simple'].append(auxSimpleDf, ignore_index = True)
        
        if(args.median):
            auxMedianDf = filter_data(pandas.read_csv(csvFile), column_names, 7, numpy.median)
            if(args.verbose):
                print(auxMedianDf.head())
                    
            ret['median'] = ret['median'].append(auxMedianDf, ignore_index = True)
    

        if(args.mean):
            auxMeanDf = filter_data(pandas.read_csv(csvFile), column_names, 16, numpy.mean)
            if(args.verbose):
                print(auxMeanDf.head())
                
            ret['mean'] = ret['mean'].append(auxMeanDf, ignore_index = True)
            
        if(args.mixed):
            auxMedianMeanDf = filter_data(
                filter_data(
                    pandas.read_csv(csvFile), column_names,
                    16, numpy.mean
                    ), column_names,
                16, numpy.mean,
                True
            )
            if(args.verbose):
                print(auxMedianMeanDf.head())
                    
            ret['mixed'] = ret['mixed'].append(auxMedianMeanDf, ignore_index = True)
    
    return ret

def build_visual(df):
    fig = px.scatter_3d(df, x="rightSensor", y="leftSensor", z="frontSensor", color="pwm")
    fig.update_traces(marker=dict(size=4, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
    return fig

def save_and_show(Df, csvFileName, htmlFileName):
    Df.to_csv(csvFileName, index = False)
    if(args.verbose):
        print(Df.head())
        fig = build_visual(Df)
        fig.write_html(htmlFileName)
        fig.show()


if __name__ == "__main__":
    args = parser.parse_args()

    if args.verbose:
        print("FILES TO APPEND:")
        for item in args.csv_files:
            print(item)

    sample_df = pandas.read_csv(args.csv_files[0])    
    ret = append_data(
       csvList=args.csv_files, column_names=list(sample_df.columns.values)
    )        
    
    if(args.unfiltered):
        save_and_show(ret['unfiltered'], 'unfilteredSensorData.csv', 'unfilteredSensorData.html')
    
    if(args.simple):
        save_and_show(ret['simple'], 'filteredSensorData.csv', 'filteredSensorData.html')
        
    if(args.median):
        save_and_show(ret['median'], 'filteredMedianSensorData.csv', 'filteredMedianSensorData.html')
    
    if(args.mean):
        save_and_show(ret['mean'], 'filteredMeanSensorData.csv', 'filteredMeanSensorData.html')
        
    if(args.mixed):
        save_and_show(ret['mixed'], 'filteredMedianMeanSensorData.csv', 'filteredMedianMeanSensorData.html')

