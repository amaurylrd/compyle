# pylint: disable=missing-function-docstring

from django.test import TestCase

from compyle.workflow import utils
from compyle.workflow.tests.factories import get_workflow_step


class TestTopologicalSort(TestCase):
    """TestCase for the `utils.topological_sort` utility function."""

    def test_no_dependencies(self) -> None:
        steps = [get_workflow_step() for _ in range(3)]

        result = utils.topological_sort(steps)

        self.assertCountEqual(result, steps)

    def test_linear_dependencies(self) -> None:
        a, b, c = (get_workflow_step() for _ in range(3))  # pylint: disable=invalid-name
        b.depends_on.set([a])
        c.depends_on.set([b])

        result = utils.topological_sort([a, b, c])

        self.assertEqual(result, [a, b, c])

    def test_branching_dependencies(self) -> None:
        a, b, c, d = (get_workflow_step() for _ in range(4))  # pylint: disable=invalid-name
        b.depends_on.set([a])
        c.depends_on.set([b])
        d.depends_on.set([b, c])

        result = utils.topological_sort([a, b, c, d])

        self.assertTrue(result.index(a) < result.index(b))
        self.assertTrue(result.index(a) < result.index(c))
        self.assertTrue(result.index(b) < result.index(d))
        self.assertTrue(result.index(c) < result.index(d))

    def test_disconnected_graph(self) -> None:
        a, b, c, d = (get_workflow_step() for _ in range(4))  # pylint: disable=invalid-name
        b.depends_on.set([a])

        result = utils.topological_sort([a, b, c, d])

        self.assertTrue(result.index(a) < result.index(b))
        self.assertIn(c, result)
        self.assertIn(d, result)

    def test_cycle_detection_2_nodes(self) -> None:
        a, b = (get_workflow_step() for _ in range(2))  # pylint: disable=invalid-name

        a.depends_on.set([b])
        b.depends_on.set([a])

        with self.assertRaises(ValueError):
            utils.topological_sort([a, b])

    def test_cycle_detection_3_nodes(self) -> None:
        a, b, c = (get_workflow_step() for _ in range(3))  # pylint: disable=invalid-name

        a.depends_on.set([c])
        b.depends_on.set([a])
        c.depends_on.set([b])

        with self.assertRaises(ValueError):
            utils.topological_sort([a, b, c])
