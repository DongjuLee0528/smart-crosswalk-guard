import unittest

from app.config import load_settings
from app.roi import RoiClassifier


def person(x, y):
    return (x - 5, y - 20, x + 5, y)


class RoiClassifierTests(unittest.TestCase):
    def test_foot_point_uses_configured_regions_and_three_frames(self):
        classifier = RoiClassifier()
        positions = {
            1: person(400, 50),
            2: person(400, 110),
            3: person(400, 200),
            4: person(400, 490),
            5: person(400, 550),
        }
        self.assertEqual(classifier.update(positions, 0), {})
        self.assertEqual(classifier.update(positions, 0.1), {})
        self.assertEqual(classifier.update(positions, 0.2), {
            1: "waiting_north", 2: "warning_north", 3: "crosswalk",
            4: "warning_south", 5: "waiting_south",
        })

    def test_intermittent_detection_and_zone_change_require_reconfirmation(self):
        classifier = RoiClassifier()
        north = {1: person(400, 50)}
        crossing = {1: person(400, 200)}
        classifier.update(north, 0)
        classifier.update({}, 0.1)
        classifier.update(north, 0.2)
        self.assertEqual(classifier.update(north, 0.3), {})
        self.assertEqual(classifier.update(north, 0.4), {1: "waiting_north"})
        self.assertEqual(classifier.update(crossing, 0.5), {1: "waiting_north"})
        self.assertEqual(classifier.update(crossing, 0.6), {1: "waiting_north"})
        self.assertEqual(classifier.update(crossing, 0.7), {1: "crosswalk"})

    def test_exit_after_two_seconds_without_roi_detection(self):
        classifier = RoiClassifier()
        north = {1: person(400, 50)}
        for timestamp in (0, 0.1, 0.2):
            classifier.update(north, timestamp)
        self.assertEqual(classifier.update({}, 2.19), {1: "waiting_north"})
        self.assertEqual(classifier.update({}, 2.2), {})
        self.assertEqual(classifier.update(north, 2.3), {})

    def test_roi_coordinates_and_confirmation_settings_are_adjustable(self):
        settings = load_settings()
        settings["entry_confirmation_frames"] = 1
        settings["exit_confirmation_seconds"] = 3
        settings["roi"]["crosswalk"] = [600, 140, 800, 460]
        classifier = RoiClassifier(settings)
        self.assertEqual(classifier.update({1: person(700, 200)}, 0), {1: "crosswalk"})
        self.assertEqual(classifier.update({}, 2), {1: "crosswalk"})
        self.assertEqual(classifier.update({}, 3), {})

    def test_boundary_and_invalid_inputs(self):
        classifier = RoiClassifier()
        for timestamp in (0, 1, 2):
            result = classifier.update({1: person(330, 90)}, timestamp)
        self.assertEqual(result, {1: "warning_north"})
        with self.assertRaises(ValueError):
            classifier.update({1: (1, 2, 1, 4)}, 3)
        with self.assertRaises(ValueError):
            classifier.update({}, 1)

    def test_crosswalk_takes_priority_when_configured_boxes_overlap(self):
        settings = load_settings()
        settings["roi"]["crosswalk"] = [330, 20, 570, 140]
        classifier = RoiClassifier(settings)
        for timestamp in (0, 0.1, 0.2):
            result = classifier.update({1: person(400, 50)}, timestamp)
        self.assertEqual(result, {1: "crosswalk"})


if __name__ == "__main__":
    unittest.main()
