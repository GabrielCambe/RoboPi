#!/usr/bin/python3
import plotly.express as px
import plotly.graph_objects as go
import pandas
import sys
import argparse

parser = argparse.ArgumentParser(description='Visualize data using line plots.')
parser.add_argument(
    '-f', '--csv_file',
    dest='file',
    type=str, nargs='?',
    action='store',
    const=None, default=None,
    help='Path to a csv file to plot the data from.'
)
parser.add_argument("--pwm", dest='plot_pwm', help="Plot PWM line.", action="store_true")
parser.add_argument("--steer", dest='plot_steer', help="Plot steer right and steer left discounts lines.", action="store_true")
parser.add_argument("--control", dest='plot_control', help="Plot gamepad's axis variables lines.", action="store_true")
parser.add_argument("--encoder", dest='plot_encoder', help="Plot right and left encoder variables lines.", action="store_true")
parser.add_argument("-v", "--verbose", help="Print verbose information and show scatered plot of the data.", action="store_true")

args = parser.parse_args()

df = pandas.read_csv(args.file)
df['tempo'] = df.index
fig = go.Figure()
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["frontSensor"], name="Frente", mode="lines",))
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["rightSensor"], name="Direita", mode="lines"))
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["leftSensor"], name="Esquerda", mode="lines"))
                
if args.plot_pwm:
    df.pwm = df.pwm.multiply(100.0)
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["pwm"], name="PWM", mode="lines"))
    
if args.plot_steer:
    df.steerRight = df.steerRight.multiply(100.0)
    df.steerLeft = df.steerLeft.multiply(100.0)
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerLeft"], name="steerR", mode="lines"))
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerRight"], name="steerL", mode="lines"))
        
if args.plot_control:
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["gamepadLx"], name="X Axis", mode="lines"))
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["gamepadLy"], name="Y Axis", mode="lines"))

if args.plot_encoder:
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["ticksRight"], name="Right Encoder", mode="lines"))
    fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["ticksLeft"], name="Left Encoder", mode="lines"))


fig.show()
