from faker import Faker

from compyle.lib.factories import DEFAULT, sequence
from compyle.workflow import choices, models

_FAKER = Faker()
WORKFLOW_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-workflow-{i}")
WORKFLOW_STEP_REFERENCE_SEQUENCE = sequence(lambda i: f"auto-workflow-step-{i}")


# pylint: disable=missing-function-docstring
def get_workflow(
    *,
    commit: bool = DEFAULT,
    reference: str = DEFAULT,
    name: str = DEFAULT,
    description: str = DEFAULT,
) -> models.Workflow:
    if commit is DEFAULT:
        commit = True

    if reference is DEFAULT:
        reference = next(WORKFLOW_REFERENCE_SEQUENCE)

    if name is DEFAULT:
        name = _FAKER.word()
    if description is DEFAULT:
        description = None

    workflow = models.Workflow(
        reference=reference,
        name=name,
        description=description,
    )

    if commit:
        workflow.save()

    return workflow


# pylint: disable=missing-function-docstring
def get_workflow_step(
    *,
    commit: bool = DEFAULT,
    commit_related: bool = DEFAULT,
    reference: str = DEFAULT,
    status: choices.StepStatus = DEFAULT,
    workflow: models.Workflow = DEFAULT,
) -> models.WorkflowStep:
    if commit_related is DEFAULT:
        commit_related = True
    if commit is DEFAULT:
        commit = commit_related
    if commit and not commit_related:  # pragma: no cover
        raise ValueError("cannot commit when related models are not committed")

    if reference is DEFAULT:
        reference = next(WORKFLOW_STEP_REFERENCE_SEQUENCE)

    if status is DEFAULT:
        status = choices.StepStatus.PENDING

    if workflow is DEFAULT:
        workflow = get_workflow(commit=commit_related)

    workflow_step = models.WorkflowStep(
        reference=reference,
        status=status,
        workflow=workflow,
    )

    if commit:
        workflow_step.save()

    return workflow_step
