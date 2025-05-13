from collections import defaultdict, deque
from collections.abc import Iterable

from compyle.workflow import models


def topological_sort(steps: Iterable[models.WorkflowStep]) -> list[models.WorkflowStep]:
    """Sort the steps in topological order based on their dependencies.

    This function uses Kahn's algorithm to compute a valid topological order
    of the steps, such that for every step A that depends on step B, B comes
    before A in the resulting list

    Algorithm:
        Kahn's algorithm — Time complexity: O(N + E)
        where:
            N = number of steps (nodes)
            E = number of dependency relations (edges)

    Args:
        steps: An iterable of WorkflowStep instances.

    Returns:
        A list of WorkflowStep instances sorted in topological order.
    """
    graph = defaultdict(list)
    indegree = {}
    step_dict = {}

    for step in steps:
        step_dict[step.pk] = step
        indegree[step.pk] = 0

        for dep in step.depends_on.all():
            graph[dep.pk].append(step.pk)
            indegree[step.pk] += 1

    # start with nodes that have no incoming edges
    queue = deque([pk for pk, degree in indegree.items() if degree == 0])
    sorted_steps = []

    while queue:
        pk = queue.popleft()  # pylint: disable=invalid-name
        sorted_steps.append(step_dict[pk])

        for neighbor in graph[pk]:
            indegree[neighbor] -= 1

            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_steps) != len(step_dict):
        raise ValueError("Cycle detected in workflow steps.")

    return sorted_steps
