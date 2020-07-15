#!/usr/bin/python3
import plotly.express as px
import plotly.graph_objects as go
import pandas
import sys
import argparse

# parser = argparse.ArgumentParser(description='Visualize data using line plots.')
# parser.add_argument("")

df = pandas.read_csv(sys.argv[1])
df['tempo'] = df.index
fig = go.Figure()
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["frontSensor"], name="Frente", mode="lines",))
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["rightSensor"], name="Direita", mode="lines"))
fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["leftSensor"], name="Esquerda", mode="lines"))
                
try:
    if(sys.argv[2] == "pwm"):
        df.pwm = df.pwm.multiply(100.0)
        fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["pwm"], name="PWM", mode="lines"))
                
        try:
            if(sys.argv[3] == "steer"):
                df.steerRight = df.steerRight.multiply(100.0)
                df.steerLeft = df.steerLeft.multiply(100.0)
                fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerLeft"], name="steerR", mode="lines"))
                fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerRight"], name="steerL", mode="lines"))
        
        except (IndexError, IOError) as error:
           pass 
    
    elif(sys.argv[2] == "steer"):
        df.steerRight = df.steerRight.multiply(100.0)
        df.steerLeft = df.steerLeft.multiply(100.0)
        fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerLeft"], name="steerR", mode="lines"))
        fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["steerRight"], name="steerL", mode="lines"))
        
    elif(sys.argv[2] == "control"):
        fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["gamepadLx"], name="Lx", mode="lines"))
        fig.add_trace(trace=go.Scatter(x=df["tempo"], y=df["gamepadLy"], name="Ly", mode="lines"))

except (IndexError, IOError) as error:
    pass

fig.show()
