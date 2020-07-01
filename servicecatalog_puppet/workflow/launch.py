import logging

from servicecatalog_puppet.workflow import manifest as manifest_tasks
from servicecatalog_puppet.workflow import provisioning as provisioning_tasks
from servicecatalog_puppet.workflow import generate as generate_tasks

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LaunchSectionTask(manifest_tasks.SectionTask):
    def params_for_results_display(self):
        return {
            'puppet_account_id': self.puppet_account_id,
            'manifest_file_path': self.manifest_file_path,
        }

    def requires(self):
        if self.skip_shares:
            logger.info(f"Skipping share setup..")
            return {
                'manifest': manifest_tasks.ManifestTask(
                    manifest_file_path=self.manifest_file_path,
                    puppet_account_id=self.puppet_account_id,
                )
            }
        else:
            return {
                'generate_shares': generate_tasks.GenerateSharesTask(
                    manifest_file_path=self.manifest_file_path,
                    puppet_account_id=self.puppet_account_id,
                    should_use_sns=self.should_use_sns,
                    should_use_product_plans=self.should_use_product_plans,
                    include_expanded_from=self.include_expanded_from,
                    single_account=self.single_account,
                    is_dry_run=self.is_dry_run,
                    execution_mode=self.execution_mode,
                ),
                'manifest': manifest_tasks.ManifestTask(
                    manifest_file_path=self.manifest_file_path,
                    puppet_account_id=self.puppet_account_id,
                )
            }

    def run(self):
        manifest = self.load_from_input('manifest')
        if self.execution_mode == "spoke":
            yield [
                provisioning_tasks.LaunchTask(
                    launch_name=launch_name,
                    manifest_file_path=self.manifest_file_path,
                    puppet_account_id=self.puppet_account_id,
                    should_use_sns=self.should_use_sns,
                    should_use_product_plans=self.should_use_product_plans,
                    include_expanded_from=self.include_expanded_from,
                    single_account=self.single_account,
                    is_dry_run=self.is_dry_run,
                    execution_mode=self.execution_mode,
                ) for launch_name, launch_details in manifest.get('launches', {}).items() if
                launch_details.get('execution') == 'spoke'
            ]
        else:
            yield [
                provisioning_tasks.LaunchTask(
                    launch_name=launch_name,
                    manifest_file_path=self.manifest_file_path,
                    puppet_account_id=self.puppet_account_id,
                    should_use_sns=self.should_use_sns,
                    should_use_product_plans=self.should_use_product_plans,
                    include_expanded_from=self.include_expanded_from,
                    single_account=self.single_account,
                    is_dry_run=self.is_dry_run,
                    execution_mode=self.execution_mode,
                ) for launch_name, launch_details in manifest.get('launches', {}).items() if
                launch_details.get('execution') != 'spoke'
            ]
        self.write_output(manifest)
