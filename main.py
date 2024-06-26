from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.graph import  MeshLinePlot
from kivy.properties import StringProperty
from math import sin
import serial
from kivy.clock import Clock
import threading
from kivy.config import Config

#define tamanho da janela do app e define como não redimencionável
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '700')

# variável global que armazena em uma lista valores do multímetro
# corrente     posição 0
# tensao       posição 1
# resistencia  posição 2
resultados = ["0","0","100000000"]


#Função que vai se conectar com a porta serial e em loop ficara atualizando a lista de valores vindas do arduino
def ler_ultima_linha():
    global ultima_linha
    try:
        with serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.1)  as ser:
            while True:
                if ser.in_waiting > 0:
                    linha = ser.readline().decode('utf-8').strip()
                    if linha:
                        global resultados
                        resultados = linha.split("|")

    except serial.SerialException as e:
        print(f"Erro ao acessar a porta serial: {e}")


#define funcionamento na tela de Voltímetro
class Voltimetro(Screen):
    leitura = StringProperty('0 V')

    #define o que acontece quando entrar em tela de Voltímetro
    def on_enter(self):
        self.atualizarTensao()

    #define o que acontece quando deixar em telade Voltímetro
    def on_leave(self):
        Clock.unschedule(self.atualizacao)

    #atualiza interface        
    def atualizarTensao(self, *args):
        #define para chamar a propria função recursivamente em 0.3 segundos
        self.atualizacao = Clock.schedule_once(self.atualizarTensao, 0.3)

        global resultados
        tensao = resultados[1]
        tensaoString = '{0:.2f}'.format(float(tensao))
        self.leitura = tensaoString  + " V"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Ohmimetro(Screen):
    leitura = StringProperty('0 Ω')
    
    def on_enter(self):
        self.atualizarResistencia()

    def on_leave(self):
        Clock.unschedule(self.atualizacao)

    def atualizarResistencia(self, *args):
        self.atualizacao = Clock.schedule_once(self.atualizarResistencia, 0.3)

        global resultados
        resistencia = float(resultados[2])

        if(resistencia < 1 and resistencia >= 0):
            self.leitura = "Possível\nContinuidade"
        else:
            unidadeMedida = "Ω"
            if((resistencia - 1000000) > 0 or resistencia < 0):
                self.leitura = "---"
                return
            elif((resistencia - 1000) > 0):
                resistencia = resistencia / 1000
                unidadeMedida = "kΩ"

            self.leitura = '{0:.2f}'.format(resistencia) + " " + unidadeMedida

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Amperimetro(Screen):
    leitura = StringProperty('0 A')
    contador = 0

    def on_enter(self):
        self.atualizarCorrente()

    def on_leave(self):
        Clock.unschedule(self.atualizacao)
        self.plot.points = []
        self.contador = 0
        self.ids["graph_test"].xmin = 0
        self.ids["graph_test"].xmax = 100

    def atualizarCorrente(self, *args):
        self.atualizacao = Clock.schedule_once(self.atualizarCorrente, 0.1)
        
        global resultados
        corrente = float(resultados[0])
        correnteStr = '{0:.1f}'.format(corrente)
        self.leitura = correnteStr  + " A"
        self.atualizaGrafico(corrente)

    def atualizaGrafico(self, corrente):
        if(self.contador > 100):
            self.ids["graph_test"].xmin = self.contador - 100
            self.ids["graph_test"].xmax = self.contador
        
        self.plot.points.append((self.contador, corrente))
        self.contador += 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = []
        self.plot = plot
        self.ids["graph_test"].add_plot(plot)
    
class MenuScreen(Screen):
    pass

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(Voltimetro(name='voltimetro'))
        sm.add_widget(Ohmimetro(name='ohmimetro'))
        sm.add_widget(Amperimetro(name='amperimetro'))
        self.title = "Multímetro"
        return sm
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

def main():
    thread_serial = threading.Thread(target=ler_ultima_linha, args=())
    thread_serial.daemon = True
    thread_serial.start()

    MainApp().run()

main()