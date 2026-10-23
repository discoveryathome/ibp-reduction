"""Reject malformed native master metadata without external solver dependencies."""

import unittest

from trial_kira import integrals


class MasterMetadata(unittest.TestCase):
    def test_native_sector_annotation_and_unannotated_preference_agree(self):
        self.assertEqual(integrals('bubble_one_mass[0,1] # 2\n', 'bubble_one_mass', 2),
                         integrals('bubble_one_mass[0,1]\n', 'bubble_one_mass', 2))

    def test_invalid_native_metadata_rejects(self):
        for text in ('', '\n', 'other[0,1]\n', 'bubble_one_mass[1]\n',
                     'bubble_one_mass[0,1] # 1\n',
                     'bubble_one_mass[0,1]\nbubble_one_mass[0,1] # 2\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                integrals(text, 'bubble_one_mass', 2)


if __name__ == '__main__':
    unittest.main()
