def main():
    import random as rnd
    import matplotlib.pyplot as plt
    pos = 0
    plt.xlabel("Time")
    plt.ylabel("Position")
    plt.title("Squrrel Position Against Time")
    for i in range(0, 1000):
        random_num = rnd.random()
        if random_num > 0.5:
            pos = pos + 1
        else:
            pos = pos - 1

        plt.plot(i, pos, ".", color="hotpink")
    plt.show()



if __name__ == "__main__":
    main()
