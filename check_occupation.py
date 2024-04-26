def point_in_polygon(point, polygon):
    """
    Determina si un punto está dentro de un polígono utilizando el método Ray-Casting.
    
    Parámetros:
        point (list): Coordenadas del punto [x, y].
        polygon (list): Lista de vértices del polígono [[x1, y1], [x2, y2], ..., [xn, yn]].
    
    Devuelve:
        bool: True si el punto está dentro del polígono, False en caso contrario.
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def check_point_in_items(point, items):
    """
    Revisa si un punto está dentro de los rectángulos de varios ítems.

    Parámetros:
        point (list): Coordenadas del punto [x, y].
        items (list): Lista de ítems con sus respectivos rectángulos.
    
    Devuelve:
        list: Lista de ítems que contienen el punto.
    """
    contained_in = []
    for item in items:
        for key, polygon in item["posiciones"].items():
            if point_in_polygon(point, polygon):
                contained_in.append(item["item"])
                break  # No need to check other objects if one already contains the point

    return contained_in


if __name__ == "__main__":
    # Datos de ejemplo
    items = [
        {"item": 1, "posiciones": {"objeto_1": [[274, 597], [396, 714], [698, 529], [532, 455]]}},
        {"item": 2, "posiciones": {"objeto_2": [[623, 375], [742, 312], [1180, 443], [1123, 565]]}},
        {"item": 3, "posiciones": {"objeto_3": [[850, 257], [900, 236], [720, 196], [687, 225]]}},
        {"item": 4, "posiciones": {"objeto_4": [[935, 215], [778, 184], [822, 160], [968, 188]]}},
        {"item": 5, "posiciones": {"objeto_5": [[988, 176], [847, 152], [875, 135], [1009, 162]]}}
    ]
    point = [395, 713]

    # Chequear si el punto está en algún ítem
    contained_items = check_point_in_items(point, items)
    print("El punto está contenido en los ítems:", contained_items)
