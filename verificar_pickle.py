import pickle

with open("label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

equipos_guardados = list(le.classes_)
print("Equipos en el encoder:")
for equipo in equipos_guardados:
    print(equipo)