"""Small real-corpus controls for the frozen tube experiment."""

import unittest

import count_seeds as tube


class TubeCounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds = {rank: tube.enumerate_seeds(rank) for rank in tube.RANKS}

    def test_published_counts_and_each_sector(self):
        for rank, expected in ((4, 358), (5, 589), (6, 820)):
            with self.subTest(rank=rank):
                self.assertEqual(tube.validate(self.seeds[rank], rank), expected)
        self.assertEqual(len(tube.sectors()), 16)
        self.assertEqual(tube.sector_counts(4)[165], 8)  # Floor-one rank bound.
        self.assertEqual(tube.sector_counts(4)[167], 28)  # Sector exception.
        self.assertEqual(tube.sector_counts(4)[255], 35)  # Three-ISP base simplex.

    def test_adjacent_translation_overlap_is_deduplicated(self):
        first = set(self.seeds[4])
        shifted = {a[:-1] + (a[-1] - 1,) for a in first}
        self.assertEqual(len(first & shifted), 127)
        self.assertEqual(first | shifted, set(self.seeds[5]))
        self.assertEqual(len(shifted - first), 231)

    def test_absent_uncut_propagators_can_carry_numerators(self):
        self.assertIn((1, -1, 1, 0, 0, 1, 0, 1, 0, 0, 0), self.seeds[4])

    def test_duplicate_missing_and_extra_shift_reject(self):
        good = self.seeds[4]
        for bad in (good + [good[0]], good[:-1], self.seeds[5]):
            with self.subTest(size=len(bad)), self.assertRaises(ValueError):
                tube.validate(bad, 4)
        with self.assertRaises(ValueError):
            tube.validate(self.seeds[4], 5)  # Missing the final allowed shift.

    def test_wrong_cut_dot_positive_isp_and_rank_reject(self):
        for position, value in ((0, 0), (0, 2), (8, 1), (10, -5)):
            bad = [1] * 8 + [0, 0, 0]
            bad[position] = value
            with self.subTest(position=position, value=value), self.assertRaises(ValueError):
                tube.validate([bad], 4)
        for rank in (3, 4.0, True):
            with self.subTest(rank=rank), self.assertRaises(ValueError):
                tube.enumerate_seeds(rank)

    def test_floor_or_exception_omissions_are_rejected(self):
        for sector, maximum in ((165, 0), (167, 1)):
            bad = [a for a in self.seeds[4]
                   if sum(1 << i for i, x in enumerate(a) if x > 0) != sector
                   or sum(-x for x in a if x < 0) <= maximum]
            with self.subTest(sector=sector), self.assertRaises(ValueError):
                tube.validate(bad, 4)

    def test_tuple_integrity_and_trivial_fixture(self):
        for bad in ([1] * 10, [True] + [1] * 7 + [0] * 3):
            with self.assertRaises(ValueError):
                tube.validate([bad], 4)
        self.assertEqual(len(tube.trivial_sectors()), 466)


if __name__ == '__main__':
    unittest.main()
