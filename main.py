def main():
    N = 200
    max_t = 100
    beta = 0.152
    gamma = 0.053

    s = 199/200
    i = 1/200
    r = 0.0
    for t in range(max_t):
        print("Cycle: {:d}, S: {:d}, I: {:d}, R: {:d}".format(t, int(s * N), int(i * N), int(r * N)))
        s += - beta * s * i
        i += beta * s * i - gamma * i
        r += gamma * i

main()