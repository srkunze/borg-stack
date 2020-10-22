import os
import subprocess
from tempfile import mkdtemp
from unittest.case import TestCase


class BorgStackTestCase(TestCase):
    def setUp(self):
        self.tmdir = mkdtemp(prefix='borg_stack_test_')
        self.path_to_repo = os.path.join(self.tmdir, 'repo')
        subprocess.check_call(['borg', 'init', '--encryption', 'none', self.path_to_repo])
        self.source_dir_relative = 'source_dir'
        self.source_dir = os.path.join(self.tmdir, self.source_dir_relative)
        os.mkdir(self.source_dir)
        self.put_test_file('initial_content')
        self.mount_point = os.path.join(self.tmdir, 'mount_point')

    def put_test_file(self, content):
        self.test_file_path = os.path.join(self.source_dir, 'test_file')
        with open(self.test_file_path, 'w') as file:
            file.write(content)

    def test_create_and_list(self):
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertNotIn('test_stack_1', output)
        self.assertNotIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_1*', self.source_dir])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertNotIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_2*', self.test_file_path])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertIn('test_stack_2', output)
        self.assertNotIn('test_stack_3', output)

        subprocess.check_call(['borg-stack', 'create', self.path_to_repo + '::test_stack_3*', self.source_dir])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertIn('test_stack_1', output)
        self.assertIn('test_stack_2', output)
        self.assertIn('test_stack_3', output)

    def test_delete(self):
        subprocess.check_call(['borg-stack', 'delete', self.path_to_repo + '::test_stack_*'])
        output = subprocess.check_output(['borg-stack', 'list', self.path_to_repo + '::test_stack_*']).decode()
        self.assertFalse(output)

    def test_mount_and_umount(self):
        subprocess.check_call(
            ['borg-stack', 'create', self.path_to_repo + '::test_stack_1*', self.source_dir_relative],
            cwd=self.tmdir,
        )

        subprocess.check_call(['borg-stack', 'mount', self.path_to_repo + '::test_stack_*', self.mount_point])
        with open(os.path.join(self.mount_point, 'merged-repo-test_stack_/source_dir/test_file')) as file:
            self.assertEqual('initial_content', file.read())
        subprocess.check_call(['borg-stack', 'umount', self.mount_point])

        self.put_test_file('updated_content')
        subprocess.check_call(
            ['borg-stack', 'create', self.path_to_repo + '::test_stack_2*', self.source_dir_relative],
            cwd=self.tmdir,
        )

        subprocess.check_call(['borg-stack', 'mount', self.path_to_repo + '::test_stack_*', self.mount_point])
        with open(os.path.join(self.mount_point, 'merged-repo-test_stack_/source_dir/test_file')) as file:
            self.assertEqual('updated_content', file.read())
        subprocess.check_call(['borg-stack', 'umount', self.mount_point])
