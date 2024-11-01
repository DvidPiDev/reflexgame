U='off'
S=int
R=enumerate
M='blue'
L='yellow'
K='red'
J='green'
G='led'
E='button'
F=range
D=True
A=False
import machine as H
from neopixel import NeoPixel as T
import time as C,random as V
W=6
X=7
B={J:{E:4,G:8},K:{E:3,G:9},L:{E:2,G:10},M:{E:1,G:20}}
O=60
I=20
Y=5
P=15
N={U:(0,0,0),J:(0,255,0),K:(255,0,0),L:(255,255,0),M:(0,0,255)}
class Q:
	def __init__(B,color,button_pin,led_pin,score_start_idx):B.color=color;B.button=H.Pin(button_pin,H.Pin.IN,H.Pin.PULL_UP);B.button_led=H.Pin(led_pin,H.Pin.OUT);B.score=0;B.score_start_idx=score_start_idx;B.joined=A;B.qualified_for_round=D;B.last_press_time=0;B.button_led.value(0)
	def reset_round(A):A.qualified_for_round=D;A.button_led.value(1)
	def check_button(B):
		if not B.button.value():
			E=C.ticks_ms()
			if C.ticks_diff(E,B.last_press_time)>200:B.last_press_time=E;return D
		return A
class Z:
	def __init__(C):C.ring=T(H.Pin(W),O);C.score_leds=T(H.Pin(X),I);C.score_led_states=[(0,0,0)]*I;C.players={J:Q(J,B[J][E],B[J][G],0),K:Q(K,B[K][E],B[K][G],5),L:Q(L,B[L][E],B[L][G],10),M:Q(M,B[M][E],B[M][G],15)};C.round_active=A;C.fading=A;C.should_stop=A;C.clear_all_leds()
	def update_score_led_states(A):
		A.score_led_states=[(0,0,0)]*I
		for B in A.players.values():
			D,E,G=N[B.color]
			for C in F(Y):
				H=B.score_start_idx+C
				if C<B.score:A.score_led_states[H]=D,E,G
	def get_quadrant_colors(A):return[L,K,J,M]
	def write_score_leds(A):
		for(B,C)in R(A.score_led_states):A.score_leds[B]=C
		A.score_leds.write()
	def sequential_fade(B,duration_per_quadrant=.25):
		B.fading=D;I=B.get_quadrant_colors()
		for(J,K)in R(I):
			if B.should_stop:B.fading=A;return
			L=J*P;E=20
			for M in F(E+1):
				G=1.-M/E
				for O in F(P):Q=L+O;T,U,V=N[K];B.ring[Q]=S(T*G),S(U*G),S(V*G)
				B.ring.write();C.sleep(duration_per_quadrant/E)
				if not B.round_active:
					for H in B.players.values():
						if H.check_button()and H.qualified_for_round:B.fading=A;return H
		B.clear_ring();B.fading=A
	def clear_ring(A):
		for B in F(O):A.ring[B]=N[U]
		A.ring.write()
	def clear_all_leds(A):
		A.clear_ring();A.score_led_states=[(0,0,0)]*I
		for B in F(I):A.score_leds[B]=0,0,0
		A.score_leds.write()
	def setup_quadrants(A):
		B=A.get_quadrant_colors()
		for(C,D)in R(B):
			E=C*P
			for G in F(P):A.ring[E+G]=N[D]
		A.ring.write()
	def update_score_leds(A):A.update_score_led_states();A.write_score_leds()
	def boot_up_phase(A):
		A.setup_quadrants();A.update_score_leds()
		while not all(A.joined for A in A.players.values()):
			for B in A.players.values():
				if not B.joined and B.check_button():B.joined=D;B.button_led.value(1)
			C.sleep(.1)
		A.sequential_fade();C.sleep(1);return D
	def handle_round(B):
		for E in B.players.values():E.reset_round()
		B.setup_quadrants();B.update_score_leds();B.round_active=D;H=C.time();I=V.uniform(3,8)
		while C.time()-H<I:
			for E in B.players.values():
				if E.check_button():E.qualified_for_round=A;E.button_led.value(0)
			C.sleep(.01)
		B.round_active=A;G=B.sequential_fade()
		if not G:
			while any(A.qualified_for_round for A in B.players.values()):
				for E in B.players.values():
					if E.check_button()and E.qualified_for_round:G=E;break
				C.sleep(.01)
		if G:
			G.score+=1;B.update_score_leds()
			for J in F(O):B.ring[J]=N[G.color]
			B.ring.write();C.sleep(2)
		return G
	def run_game(B):
		while D:
			B.should_stop=A;B.score_led_states=[(0,0,0)]*I;B.boot_up_phase()
			while D:
				G=B.handle_round()
				if G and G.score>=5:
					H=N[G.color]
					for K in F(O):B.ring[K]=H
					B.ring.write();B.score_led_states=[H]*I;B.write_score_leds();J=A
					while not J:
						for E in B.players.values():
							if E.check_button():J=D;break
						C.sleep(.01)
					break
				B.clear_ring();B.update_score_leds();C.sleep(1)
			for E in B.players.values():E.score=0;E.joined=A;E.button_led.value(0)
			B.clear_all_leds()
if __name__=='__main__':a=Z();a.run_game()