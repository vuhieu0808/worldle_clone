import math

def get_arrow_direction(bearing):
    """
    Chuyển đổi góc phương vị (0-360 độ) sang 8 hướng mũi tên.
    (Hàm này không thay đổi)
    """
    # directions = [
    #     "⬆️ (Bắc)",       # 337.5 - 22.5
    #     "↗️ (Đông Bắc)",  # 22.5 - 67.5
    #     "➡️ (Đông)",      # 67.5 - 112.5
    #     "↘️ (Đông Nam)",  # 112.5 - 157.5
    #     "⬇️ (Nam)",       # 157.5 - 202.5
    #     "↙️ (Tây Nam)",  # 202.5 - 247.5
    #     "⬅️ (Tây)",      # 247.5 - 292.5
    #     "↖️ (Tây Bắc)"   # 292.5 - 337.5
    # ]
    directions = [
        "↑",       # 337.5 - 22.5
        "↗",  # 22.5 - 67.5
        "→",      # 67.5 - 112.5
        "↘",  # 112.5 - 157.5
        "↓",       # 157.5 - 202.5
        "↙",  # 202.5 - 247.5
        "←",      # 247.5 - 292.5
        "↖"   # 292.5 - 337.5
    ]
    index = int(((bearing + 22.5) % 360) / 45)
    return directions[index]

def get_distance_and_arrow(country_origin, country_destination):
    """
    Tính khoảng cách và hướng mũi tên giữa hai quốc gia.
    
    Tham số:
        - country_origin (dict): Dictionary của nước GỐC.
        - country_destination (dict): Dictionary của nước ĐÍCH.
    
    Trả về:
        - distance_km (float): Khoảng cách tính bằng km.
        - arrow (string): Hướng mũi tên trực quan.
    """
    
    # --- 1. Trích xuất tọa độ từ dictionary ---
    lat1_deg = country_origin["Latitude"]
    lon1_deg = country_origin["Longitude"]
    lat2_deg = country_destination["Latitude"]
    lon2_deg = country_destination["Longitude"]

    # --- 2. Hằng số và Chuyển đổi Radian ---
    R = 6371.0  # Bán kính Trái Đất (km)
    
    lat1_rad = math.radians(lat1_deg)
    lon1_rad = math.radians(lon1_deg)
    lat2_rad = math.radians(lat2_deg)
    lon2_rad = math.radians(lon2_deg)

    # --- 3. Tính khoảng cách (Haversine) ---
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = R * c

    # --- 4. Tính Hướng (Phương vị) ---
    Y = math.sin(dlon) * math.cos(lat2_rad)
    X = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing_rad = math.atan2(Y, X)
    bearing_deg = (math.degrees(bearing_rad) + 360) % 360
    
    # --- 5. Lấy hướng mũi tên ---
    arrow = get_arrow_direction(bearing_deg)

    return round(distance_km, 1), arrow
