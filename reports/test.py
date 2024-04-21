date = [
    "POD_Bordo_9.23",
    "SKP_Koroleva_10.22",
    "UDL_Orlova_12.23",
    "M31_Semenova_11.23",
]
prefix = ["POD_", "SKP_", "UDL_", "M31_"]

# Initialize a dictionary to store lists based on prefix
prefix_dict = {p: [] for p in prefix}


# Iterate over the date list and append each element to the corresponding list in prefix_dict
for item in date:
    for p in prefix:
        if item.startswith(p):
            prefix_dict[p].append(item)
            break

# Print the result
for p, items in prefix_dict.items():
    print(f"{p}: {items}")
