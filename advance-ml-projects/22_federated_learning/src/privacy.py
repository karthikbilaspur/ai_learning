"""Privacy accounting helpers. The default training code is a pedagogical DP-FedAvg approximation.
For formal guarantees, plug in an RDP accountant using the actual client sampling process."""
import math

def gaussian_rdp(order: float, sigma: float) -> float:
    if sigma <= 0: return float('inf')
    return order/(2*sigma*sigma)

def approximate_epsilon(noise_multiplier: float, sample_rate: float, rounds: int, delta: float=1e-5, orders=(2,4,8,16,32,64)):
    """Conservative educational RDP-style estimate; clearly label as approximate."""
    if noise_multiplier<=0: return float('inf')
    eps=[]
    for a in orders:
        rdp=rounds*sample_rate*gaussian_rdp(a,noise_multiplier)
        eps.append(rdp + math.log(1/delta)/(a-1))
    return min(eps)
