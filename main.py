from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

import serial
from kivy.clock import Clock

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1) 

tensaoAtual = '0.0'
resistenciaAtual = '0.0'


def lerArduino(*args):     
    serialMsg =  str(arduino.readline())[2:-5]
    print('a')
    if(len(serialMsg) > 1):
        if(serialMsg[0] == 'i' and serialMsg[-1] == 'f'):
            valores = serialMsg.split("|")
            global tensaoAtual 
            tensaoAtual = valores[0].strip()
            global resistenciaAtual 
            resistenciaAtual = valores[1].strip()

class Voltimetro(Screen):
    tensao = StringProperty('')

    def lerTensao(self, *args):
        self.tensao = tensaoAtual[1:] + " V"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.lerTensao, 0.3)

class Ohmimetro(Screen):
    resistencia = StringProperty('teste')

    def lerResistencia(self, *args):
        print("chamado ler")
        resistencia = resistenciaAtual
        if(float(resistencia[0:-1]) < 1):
            self.resistencia = "Possível\nContinuidade"
        else:
            self.resistencia = resistencia[0:-1] + " Ω"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.lerResistencia, 0.3)



class MenuScreen(Screen):
    pass

class MainApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(Voltimetro(name='voltimetro'))
        sm.add_widget(Ohmimetro(name='ohmimetro'))

        return sm
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(lerArduino, 0.4)

MainApp().run()