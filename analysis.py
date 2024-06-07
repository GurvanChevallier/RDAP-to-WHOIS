from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
errorstypes = {}
total = 15008
with open("error_save.txt", "r") as fp:
    for content in tqdm(fp, total=total):
        if content.split("(", 1)[0] not in errorstypes:
            errorstypes[content.split("(", 1)[0]] = 1
        else:
            errorstypes[content.split("(", 1)[0]] += 1

errorstypes = dict(sorted(errorstypes.items(), key=lambda item: item[1], reverse=True))
print(errorstypes)
def my_fmt(x):
    print(x)
    return '{:.1f}%\n{:.0f}'.format(x, total*x/100)
plt.pie(errorstypes.values(), labels=errorstypes.keys(), autopct=my_fmt, startangle=0)

# Adding the legend at the top right corner

# Equal aspect ratio ensures that pie is drawn as a circle.
plt.axis('equal')

plt.show()

"""
plt.xticks(range(len(errorstypes)), list(errorstypes.keys()), rotation=25)
plt.bar(range(len(errorstypes)), list(errorstypes.values()),edgecolor="white")
plt.xlabel('Error types')
plt.ylabel('Error type occurences')
plt.tight_layout()
plt.show()"""


"""
samples_tested = 2148462
printed = {'domain_name': 2148462, 'registry_domain_id': 2148462, 'registrar_rdap_server': 2094580, 'updatedDate': 2141924, 'expirationDate': 2142743, 'iana_id': 2110159, 'registrar_infos': 2134682, 'abuse_infos': 2126703, 'epp_codes': 2143025, 'nameservers': 2137208, 'secure_dns': 2094989, 'registrant': 304060, 'technical': 191619, 'administrative': 186921, 'billing': 114601, 'sponsor': 1111, 'admin': 339, 'tech': 339, 'zone': 557, 'reseller': 4}
printed = dict(sorted(printed.items(), key=lambda item: item[1], reverse=True))

percentage = []
for elem in printed:
    pct = ( printed[elem] / samples_tested) * 100
    percentage.append(round(pct,1))


plt.figure(figsize=(12, 8))
graph = plt.bar(list(printed.keys()), list(printed.values()), color='skyblue')
plt.xlabel('Properties printed')
plt.ylabel('Occurences printed (in millions)')
plt.xticks(rotation=90)
plt.tight_layout()

i = 0
for p in graph:
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy()
    plt.text(x + width / 2,
             y + height * 1.01,
             str(percentage[i]) + '%',
             ha='center')
    i += 1

plt.show()
"""