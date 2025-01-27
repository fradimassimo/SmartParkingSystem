import random
def generate_fake_parking_data(start_time, end_time, time_interval, parking_ids):
    data = []

    for parking_id in parking_ids:
        current_time = start_time
        total_slots = random.randint(15, 110)

        while current_time >= end_time:
            occupancy = random.randint(0, total_slots)
            vacancy = total_slots - occupancy

            record = {
                "parking_id": parking_id,
                "timestamp": current_time.isoformat(),
                "occupancy": occupancy,
                "vacancy": vacancy
            }
            data.append(record)

            current_time -= time_interval

    return data

