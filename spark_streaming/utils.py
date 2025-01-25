import json
from collections import defaultdict

#This function should aggregate streaming data coming from spots sensors into closed parking lots.
#Data coming from sensors are supposed to be stored every 15 minutes thus this function follows that frequency.

def aggregate_parking_data(data):
    # Raggruppa i dati per coordinate e registra tutti i timestamp
    parking_areas = defaultdict(list)

    for spot in data:
        coordinates = (spot["location"]["latitude"], spot["location"]["longitude"])
        timestamp = spot["metadata_time"]
        park_flag = spot["payload_fields_park_flag"]

        # Conta i posti occupati e liberi
        occupied = 1 if park_flag == 1 else 0
        free = 1 if park_flag == 0 else 0

        # Aggiungi le informazioni al parcheggio corrispondente
        parking_areas[coordinates].append({
            "timestamp": timestamp,
            "occupied": occupied,
            "free": free
        })

    # Crea il risultato finale
    result = []
    for coords, records in parking_areas.items():
        # Aggrega i dati nel tempo per ogni parcheggio
        result.append({
            "coordinates": coords,
            "data": records
        })

    return result
