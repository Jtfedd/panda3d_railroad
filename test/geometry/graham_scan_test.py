import unittest

from src.geometry.graham_scan import *
from src.geometry.point import Point


class TestGrahamScan(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(AssertionError):
            graham_scan([])

    def test_single_point(self):
        p = Point(3, 6)
        result = graham_scan([p])
        self.assertListEqual([p], result)

    def test_two_points(self):
        p1 = Point(3, 6)
        p2 = Point(4, 7)
        result = graham_scan([p1, p2])
        self.assertListEqual([p1, p2], result)

    def test_duplicate_points(self):
        p1 = Point(3, 6)
        p2 = Point(4, 7)
        p3 = Point(4, 7)
        result = graham_scan([p1, p2, p3])
        self.assertListEqual([p1, p2], result)

    def test_duplicate_ref_points(self):
        p1 = Point(3, 6)
        p2 = Point(3, 6)
        p3 = Point(4, 7)
        result = graham_scan([p1, p2, p3])
        self.assertListEqual([p1, p3], result)

    def test_convex_hull(self):
        points = [
            Point(0, 7),
            Point(6, 9),
            Point(8, 7),
            Point(12, 4),
            Point(10, 2),
            Point(13, 7),
            Point(12, 11),
            Point(3, 2),
            Point(14, 2),
            Point(6, 5),
            Point(3, 2),
            Point(12, 4),
            Point(15, 5),
        ]

        expected = [
            Point(3, 2),
            Point(14, 2),
            Point(15, 5),
            Point(12, 11),
            Point(0, 7)
        ]

        result = graham_scan(points)

        self.assertListEqual(expected, result)


class TestPolarComparator(unittest.TestCase):
    def test_polar_comparisons(self):
        ref = Point(2, 2)

        p1 = Point(5, 2)
        p2 = Point(4, 3)
        p3 = Point(6, 4)
        p4 = Point(3, 5)
        p5 = Point(1, 3)

        self.assertEqual(0, polar_comparator(p1, p1, ref))
        self.assertEqual(-1, polar_comparator(p1, p2, ref))
        self.assertEqual(-1, polar_comparator(p1, p3, ref))
        self.assertEqual(-1, polar_comparator(p1, p4, ref))
        self.assertEqual(-1, polar_comparator(p1, p5, ref))

        self.assertEqual(1, polar_comparator(p2, p1, ref))
        self.assertEqual(0, polar_comparator(p2, p2, ref))
        self.assertEqual(-1, polar_comparator(p2, p3, ref))
        self.assertEqual(-1, polar_comparator(p2, p4, ref))
        self.assertEqual(-1, polar_comparator(p2, p5, ref))

        self.assertEqual(1, polar_comparator(p3, p1, ref))
        self.assertEqual(1, polar_comparator(p3, p2, ref))
        self.assertEqual(0, polar_comparator(p3, p3, ref))
        self.assertEqual(-1, polar_comparator(p3, p4, ref))
        self.assertEqual(-1, polar_comparator(p3, p5, ref))

        self.assertEqual(1, polar_comparator(p4, p1, ref))
        self.assertEqual(1, polar_comparator(p4, p2, ref))
        self.assertEqual(1, polar_comparator(p4, p3, ref))
        self.assertEqual(0, polar_comparator(p4, p4, ref))
        self.assertEqual(-1, polar_comparator(p4, p5, ref))

        self.assertEqual(1, polar_comparator(p5, p1, ref))
        self.assertEqual(1, polar_comparator(p5, p2, ref))
        self.assertEqual(1, polar_comparator(p5, p3, ref))
        self.assertEqual(1, polar_comparator(p5, p4, ref))
        self.assertEqual(0, polar_comparator(p5, p5, ref))


class TestGetReferencePoint(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(AssertionError):
            get_reference_point([])

    def test_basic_case(self):
        points = [
            Point(1, 2),
            Point(2, 8),
            Point(0, 6),
            Point(2, -1),
            Point(-1, 1),
            Point(5, 5)
        ]

        point, min_i = get_reference_point(points)

        self.assertEqual(3, min_i)
        self.assertEqual(2, point.x)
        self.assertEqual(-1, point.y)

    def test_two_min_points(self):
        points = [
            Point(1, 2),
            Point(2, 8),
            Point(0, 6),
            Point(2, -1),
            Point(-1, 1),
            Point(1, -1),
            Point(5, 5)
        ]

        point, min_i = get_reference_point(points)

        self.assertEqual(5, min_i)
        self.assertEqual(1, point.x)
        self.assertEqual(-1, point.y)
