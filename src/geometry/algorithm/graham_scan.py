import functools

from src.geometry.vector import Vector


def graham_scan(points):
    ref_point, index = get_reference_point(points)
    points[0], points[index] = points[index], points[0]

    sorted_polar = sorted(points[1:], key=functools.cmp_to_key(lambda p1, p2: polar_comparator(p1, p2, ref_point)))

    to_remove = []
    for i in range(len(sorted_polar) - 1):
        d = direction(sorted_polar[i], sorted_polar[i + 1], ref_point)
        if d == 0:
            to_remove.append(i)
    sorted_polar = [i for j, i in enumerate(sorted_polar) if j not in to_remove]

    m = len(sorted_polar)
    if m == 0:
        return [ref_point]
    if m == 1:
        return [ref_point, sorted_polar[0]]

    else:
        stack = [points[0], sorted_polar[0], sorted_polar[1]]
        stack_size = 3

        for i in range(2, m):
            while True:
                d = direction(stack[stack_size - 2], stack[stack_size - 1], sorted_polar[i])
                if d < 0:  # if it makes left turn
                    break
                else:  # if it makes non left turn
                    stack.pop()
                    stack_size -= 1
            stack.append(sorted_polar[i])
            stack_size += 1
    return stack


def to_simple_comparator_value(value):
    if value < 0:
        return -1
    if value > 0:
        return 1
    return 0


def direction(p1, p2, ref_point):
    vec1 = Vector.from_points(ref_point, p1)
    vec2 = Vector.from_points(ref_point, p2)

    return vec2.cross(vec1)


def polar_comparator(p1, p2, ref_point):
    vec1 = Vector.from_points(ref_point, p1)
    vec2 = Vector.from_points(ref_point, p2)

    angle_cmp = direction(p1, p2, ref_point)

    if angle_cmp == 0:
        return to_simple_comparator_value(vec1.magnitude() - vec2.magnitude())

    return to_simple_comparator_value(angle_cmp)


def get_reference_point(points):
    if len(points) == 0:
        raise AssertionError('Must have at least one point')

    min_y = points[0].y
    min_i = 0
    for i, point in enumerate(points):
        if point.y < min_y:
            min_y = point.y
            min_i = i
        if point.y == min_y:
            if point.x < points[min_i].x:
                min_i = i
    return points[min_i], min_i


