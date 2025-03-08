def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb).upper()

def interpolate_color(min_color, max_color, normalized_value):
    min_r, min_g, min_b = hex_to_rgb(min_color)
    max_r, max_g, max_b = hex_to_rgb(max_color)
    r = min_r + (max_r - min_r) * normalized_value
    g = min_g + (max_g - min_g) * normalized_value
    b = min_b + (max_b - min_b) * normalized_value
    return rgb_to_hex((int(r), int(g), int(b)))

def calculate_node_style(degree, min_degree, max_degree, min_color, max_color, avg_size):
    normalized_degree = (degree - min_degree) / (max_degree - min_degree) if max_degree > min_degree else 0
    size = avg_size * (1 + normalized_degree)
    color = interpolate_color(min_color, max_color, normalized_degree)
    border_color = interpolate_color(min_color, max_color, normalized_degree * 0.8)
    return size, color, border_color

def calculate_edge_style(source_degree, target_degree, min_degree, max_degree, min_color, max_color):
    avg_degree = (source_degree + target_degree) / 2
    normalized_degree = (avg_degree - min_degree) / (max_degree - min_degree) if max_degree > min_degree else 0
    color = interpolate_color(min_color, max_color, normalized_degree)
    return color