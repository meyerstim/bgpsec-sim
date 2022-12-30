import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


def evaluate(input: str, output: str, threshold: int) -> None:
    data = np.loadtxt(input, delimiter=',')
    area = []
    x = []
    y = []
    z = []
    length = (100/round(len(data) ** (1. / 3))+1)

    deploymentsTierThree = np.arange(0, 101, length)
    deploymentsTierTwo = np.arange(0, 101, length)
    deploymentsTierOne = np.arange(0, 101, length)

    for deployment in deploymentsTierThree:
        for deployment2 in deploymentsTierTwo:
            for deployment3 in deploymentsTierOne:
                area.append([deployment, deployment2, deployment3])

    for elements in area:
        x.append(elements[0])
    for elements in area:
        y.append(elements[1])
    for elements in area:
        z.append(elements[2])


    #Evaluate first bare figure
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.grid()
    image = ax.scatter(x, y, z, c=data, cmap=plt.cm.tab10)
    cbar = fig.colorbar(image, shrink=0.6, pad=0.1)
    cbar.set_label('\n attacker-success-rate (in %)')
    ax.set_xlabel('Tier One (Deployment-rate in %)')
    ax.set_ylabel('Tier Two (Deployment-rate in %)')
    ax.set_zlabel('Tier Three (Deployment-rate in %)')
    plt.savefig(output)

    #Cleanup data for second figure
    data_clean = []
    xClean = x
    yClean = y
    zClean = z
    count = 0

    for elements in data:
        if elements > threshold:
            xClean.pop(count)
            yClean.pop(count)
            zClean.pop(count)
            count = count - 1
        else:
            data_clean.append(elements)
        count = count + 1

    # Evaluate second cleaned figure
    fig2 = plt.figure(figsize=(11, 11))
    aNeu = fig2.add_subplot(111, projection='3d')
    aNeu.grid()
    imageNeu = aNeu.scatter(xClean, yClean, zClean, c=data_clean, cmap=plt.cm.tab10)
    cBarNeu = fig2.colorbar(imageNeu, shrink=0.6, pad=0.1)
    cBarNeu.set_label('\n attacker-success-rate (in %)')
    aNeu.set_title('Cleaned up by values over ' + str(threshold) + '%')
    aNeu.set_xlabel('Tier One (Deployment-rate in %)')
    aNeu.set_ylabel('Tier Two (Deployment-rate in %)')
    aNeu.set_zlabel('Tier Three (Deployment-rate in %)')

    plt.savefig(output+'_cleanUp')

    print("Evaluation files stored at desired path.")