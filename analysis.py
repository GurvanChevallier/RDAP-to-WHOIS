from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np

errorstypes = {}
with open("error_save.txt", "r") as fp:
    for content in tqdm(fp, total=15008):
        if content.split(": ", 1)[0] not in errorstypes:
            errorstypes[content.split(": ", 1)[0]] = {errorstypes[content.split(": ", 1)[1]]:1}
        else:
            for key in errorstypes[content.split(": ", 1)[0]]:
                if key not in errorstypes[content.split(": ", 1)[1]]:
                    errorstypes[content.split(": ", 1)[1]][key] = 1
                else:
                    errorstypes[content.split(": ", 1)[0]][key] += 1

errorstypes = dict(sorted(errorstypes.items(), key=lambda item: item[1], reverse=True))
print(errorstypes)
"""
plt.xticks(range(len(errorstypes)), list(errorstypes.keys()), rotation=25)
plt.bar(range(len(errorstypes)), list(errorstypes.values()),edgecolor="white")
plt.tight_layout()
plt.show()
"""