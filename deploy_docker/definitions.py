from pathlib import Path

from dagster import Definitions, AssetExecutionContext
from dagster_dbt import DbtCliResource, build_schedule_from_dbt_selection, dbt_assets, DbtProject

transformation_project = DbtProject(
    project_dir=Path(__file__).joinpath("..", "jaffle_shop").resolve(),
)
transformation_project.prepare_if_dev()

@dbt_assets(manifest=transformation_project.manifest_path)
def transformation_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

schedules = [
     build_schedule_from_dbt_selection(
         [transformation_dbt_assets],
         job_name="materialize_dbt_models",
         cron_schedule="0 0 * * *",
         dbt_select="fqn:*",
     ),
]

defs = Definitions(
    assets=[transformation_dbt_assets],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=transformation_project),
    },
)
